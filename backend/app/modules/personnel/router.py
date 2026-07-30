import asyncio
import time

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List

from app.modules.personnel import push_jobs
from app.modules.personnel.models import Personnel
from app.modules.personnel.schemas import (
    PersonnelCreate,
    PersonnelUpdate,
    PersonnelResponse,
    PersonnelStats,
    PersonnelSearchFilters,
    PersonnelPushRequest,
    PersonnelPushResponse,
    BulkPushRequest,
    BulkPushJobResponse,
    PushJobSnapshot,
)
from app.modules.personnel.service import (
    create_personnel,
    get_personnel,
    update_personnel,
    delete_personnel,
    restore_personnel,
    list_personnel,
    get_personnel_stats,
    search_personnel,
    push_personnel_to_devices,
)
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.permissions import PermissionCode
from app.core.response import ok, Meta, SuccessResponse

router = APIRouter(prefix="/personnel", tags=["Personnel"])


@router.post("/", status_code=201, response_model=SuccessResponse[PersonnelResponse])
def create_personnel_endpoint(
    payload: PersonnelCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """
    Create a new personnel record.
    
    - **emp_no**: Employee number (unique per organization)
    - **full_name**: Full name (required)
    - **gender**: 0=Unknown, 1=Male, 2=Female
    - **org_id**: Organization ID (optional)
    """
    try:
        personnel = create_personnel(db, payload)
        return ok(PersonnelResponse.model_validate(personnel))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=SuccessResponse[List[PersonnelResponse]])
def list_personnel_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    sort_by: str = Query("emp_no", description="Sort field"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(None, description="Search term"),
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_READ)),
):
    """
    List personnel records with pagination and filtering.
    
    - **page**: Page number (1-indexed)
    - **page_size**: Number of items per page (max 100)
    - **org_id**: Filter by organization
    - **sort_by**: Field to sort by
    - **order**: asc or desc
    - **search**: Search across name, email, phone
    """
    # Build filters
    filters = None
    if search:
        filters = PersonnelSearchFilters(search=search, org_id=org_id)
    
    items, total = list_personnel(
        db,
        org_id=org_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        filters=filters,
    )
    
    pages = max(1, -(-total // page_size))  # Ceiling division
    response_items = [PersonnelResponse.model_validate(i) for i in items]
    
    return ok(response_items, meta=Meta(page=page, page_size=page_size, total=total, pages=pages))


# ── Bulk push background jobs ──────────────────────────────────────────────
# These literal routes must stay above the /{personnel_id} handlers.

@router.post("/push-bulk", status_code=202, response_model=SuccessResponse[BulkPushJobResponse])
def start_bulk_push_endpoint(
    payload: BulkPushRequest,
    user = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """
    Start a background job that pushes multiple personnel records to devices.

    Returns a job id immediately; follow progress via
    GET /personnel/push-jobs/{job_id} (polling) or
    GET /personnel/push-jobs/{job_id}/events (Server-Sent Events).
    """
    job = push_jobs.create_job(user.id, payload)
    return ok(BulkPushJobResponse(job_id=job.id, total=job.total))


def _get_job_or_404(job_id: str, user_id: int) -> push_jobs.PushJob:
    job = push_jobs.get_job(job_id, user_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Push job not found")
    return job


@router.get("/push-jobs/{job_id}", response_model=SuccessResponse[PushJobSnapshot])
def get_push_job_endpoint(
    job_id: str,
    user = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """Snapshot of a bulk push job (polling fallback for the SSE stream)."""
    job = _get_job_or_404(job_id, user.id)
    return ok(job.snapshot())


@router.get("/push-jobs/{job_id}/events")
async def stream_push_job_events(
    job_id: str,
    user = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """
    Server-Sent Events stream of job snapshots. Each event's data is the same
    JSON as the polling endpoint's `data` field; the stream closes after the
    terminal (completed/cancelled) snapshot.
    """
    job = _get_job_or_404(job_id, user.id)

    async def _event_stream():
        yield "retry: 5000\n\n"
        last_version = -1
        last_send = time.monotonic()
        while True:
            # Read version before building the snapshot so a bump that lands
            # in between is picked up on the next tick instead of lost.
            version = job.version
            if version != last_version:
                snapshot = job.snapshot()
                yield f"data: {snapshot.model_dump_json()}\n\n"
                last_version = version
                last_send = time.monotonic()
                if snapshot.status != "running":
                    return
            elif time.monotonic() - last_send > 15:
                yield ": ping\n\n"
                last_send = time.monotonic()
            await asyncio.sleep(0.5)

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/push-jobs/{job_id}/cancel", response_model=SuccessResponse[PushJobSnapshot])
def cancel_push_job_endpoint(
    job_id: str,
    user = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """
    Cancel a bulk push job. Workers finish the person they are on; queued
    persons are skipped and reported in skipped_personnel_ids.
    """
    job = _get_job_or_404(job_id, user.id)
    push_jobs.cancel_job(job)
    return ok(job.snapshot())


@router.get("/{personnel_id}", response_model=SuccessResponse[PersonnelResponse])
def get_personnel_endpoint(
    personnel_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_READ)),
):
    """
    Get a single personnel record by ID.
    
    - **personnel_id**: Personnel ID
    """
    personnel = get_personnel(db, personnel_id)
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
    return ok(PersonnelResponse.model_validate(personnel))


@router.put("/{personnel_id}", response_model=SuccessResponse[PersonnelResponse])
def update_personnel_endpoint(
    personnel_id: int,
    payload: PersonnelUpdate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """
    Update a personnel record.
    
    - **personnel_id**: Personnel ID
    - **payload**: Fields to update (all optional)
    """
    try:
        personnel = update_personnel(db, personnel_id, payload)
        if not personnel:
            raise HTTPException(status_code=404, detail="Personnel not found")
        return ok(PersonnelResponse.model_validate(personnel))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{personnel_id}", status_code=204)
def delete_personnel_endpoint(
    personnel_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """
    Soft delete a personnel record (set is_active=False).
    
    - **personnel_id**: Personnel ID
    """
    personnel = delete_personnel(db, personnel_id)
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")


@router.post("/{personnel_id}/restore", response_model=SuccessResponse[PersonnelResponse])
def restore_personnel_endpoint(
    personnel_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """
    Restore a soft-deleted personnel record (set is_active=True).
    
    - **personnel_id**: Personnel ID
    """
    personnel = restore_personnel(db, personnel_id)
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
    return ok(PersonnelResponse.model_validate(personnel))


@router.post("/{personnel_id}/push", response_model=SuccessResponse[PersonnelPushResponse])
def push_personnel_endpoint(
    personnel_id: int,
    payload: PersonnelPushRequest,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """
    Push a personnel record to one or more devices (device /person/create API).

    Sends personnel info (and registration photo as face1 when available) to
    each target device, then records a device_person_mapping for each success.

    - **personnel_id**: Personnel ID
    - **device_ids**: Target device IDs (required, at least one)
    - **include_photo**: Send registration photo if available (default true)

    Returns per-device results; a device failure does not abort the others.
    """
    try:
        result = push_personnel_to_devices(db, personnel_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Personnel not found")
    return ok(result)


@router.get("/stats", response_model=SuccessResponse[PersonnelStats])
def get_stats_endpoint(
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_READ)),
):
    """
    Get personnel statistics.
    
    Returns total, active, inactive counts and breakdown by gender.
    
    - **org_id**: Filter by organization (optional)
    """
    stats = get_personnel_stats(db, org_id=org_id)
    return ok(stats)


@router.get("/search", response_model=SuccessResponse[List[PersonnelResponse]])
def search_personnel_endpoint(
    q: str = Query(..., min_length=1, description="Search query"),
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_READ)),
):
    """
    Search personnel by query across multiple fields.
    
    Searches: emp_no, full_name, email, phone, nationality
    
    - **q**: Search query (required)
    - **org_id**: Filter by organization
    - **limit**: Maximum results (default 50)
    """
    results = search_personnel(db, search_term=q, org_id=org_id, limit=limit)
    response_results = [PersonnelResponse.model_validate(r) for r in results]
    return ok(response_results)
