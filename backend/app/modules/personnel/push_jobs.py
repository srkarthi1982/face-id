"""
In-memory background-job manager for bulk personnel push.

Jobs live in a module-level registry, so this only works when uvicorn runs as
a single process (the deploy.ps1 / NSSM setup). The Docker entrypoint's
``--workers 2`` mode is incompatible: a job created on one worker would be
invisible to the other.
"""
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.core.database import SessionLocal
from app.modules.personnel.schemas import (
    BulkPushRequest,
    PersonPushJobResult,
    PushJobSnapshot,
)
from app.modules.personnel.service import push_one_for_job

# DB pool is 20 + 10 overflow shared with request handlers; keep the worker
# count well below that since every worker holds a session for its person.
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="push-job")

_registry: dict[str, "PushJob"] = {}
_registry_lock = threading.Lock()

_FINISHED_JOB_TTL_SECONDS = 3600


@dataclass
class PushJob:
    id: str
    user_id: int
    device_ids: list[int]
    include_photo: bool
    total: int
    pending_count: int
    status: str = "running"  # running | completed | cancelled
    done: int = 0
    person_results: list[PersonPushJobResult] = field(default_factory=list)
    skipped_personnel_ids: list[int] = field(default_factory=list)
    cancel_event: threading.Event = field(default_factory=threading.Event)
    version: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_monotonic: Optional[float] = None

    def snapshot(self) -> PushJobSnapshot:
        with self.lock:
            return PushJobSnapshot(
                job_id=self.id,
                status=self.status,
                total=self.total,
                done=self.done,
                results=list(self.person_results),
                skipped_personnel_ids=list(self.skipped_personnel_ids),
            )


def create_job(user_id: int, payload: BulkPushRequest) -> PushJob:
    job = PushJob(
        id=uuid4().hex,
        user_id=user_id,
        device_ids=list(payload.device_ids),
        include_photo=payload.include_photo,
        total=len(payload.personnel_ids),
        pending_count=len(payload.personnel_ids),
    )
    with _registry_lock:
        _prune_locked()
        _registry[job.id] = job
    for personnel_id in payload.personnel_ids:
        _executor.submit(_run_person, job, personnel_id)
    return job


def get_job(job_id: str, user_id: int) -> Optional[PushJob]:
    """Creator-only lookup; a foreign job id behaves like a missing one."""
    with _registry_lock:
        job = _registry.get(job_id)
    if job is None or job.user_id != user_id:
        return None
    return job


def cancel_job(job: PushJob) -> None:
    job.cancel_event.set()
    with job.lock:
        job.version += 1


def _run_person(job: PushJob, personnel_id: int) -> None:
    if job.cancel_event.is_set():
        with job.lock:
            job.skipped_personnel_ids.append(personnel_id)
            _person_finished_locked(job)
        return

    db = SessionLocal()
    # Audit rows must attribute to the initiating user: the request's
    # ContextVar does not cross into executor threads (see app/core/deps.py).
    db.info["current_user_id"] = job.user_id
    try:
        result = push_one_for_job(
            db, personnel_id, job.device_ids, job.include_photo, job.cancel_event,
        )
    finally:
        db.close()

    with job.lock:
        job.person_results.append(result)
        job.done += 1
        _person_finished_locked(job)


def _person_finished_locked(job: PushJob) -> None:
    job.pending_count -= 1
    job.version += 1
    if job.pending_count == 0:
        job.status = "cancelled" if job.cancel_event.is_set() else "completed"
        job.finished_monotonic = time.monotonic()
        job.version += 1


def _prune_locked() -> None:
    now = time.monotonic()
    stale = [
        job_id for job_id, job in _registry.items()
        if job.finished_monotonic is not None
        and now - job.finished_monotonic > _FINISHED_JOB_TTL_SECONDS
    ]
    for job_id in stale:
        del _registry[job_id]
