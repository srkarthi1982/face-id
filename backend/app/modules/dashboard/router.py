"""Thin authenticated HTTP routes for attendance analytics."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from app.core.deps import get_db, require_permission
from app.core.permissions import PermissionCode
from app.core.response import SuccessResponse, ok

from . import service
from .constants import (
    EXCEPTIONS_MAX_DAYS,
    OVERVIEW_MAX_DAYS,
    RANKING_MAX_DAYS,
    TREND_MAX_DAYS,
)
from .schemas import (
    AttendanceExceptionItem,
    DashboardDepartmentOption,
    DashboardOverview,
    DashboardTrend,
    DashboardTrendGranularity,
    EmployeeWorkHoursRanking,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_READ))],
)


def _safe_call(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except DashboardRangeError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from None


DashboardRangeError = service.DashboardRangeError


@router.get("/departments", response_model=SuccessResponse[list[DashboardDepartmentOption]])
def departments(db: Session = Depends(get_db)):
    return ok(_safe_call(service.get_departments, db))


@router.get("/overview", response_model=SuccessResponse[DashboardOverview])
def overview(
    start_date: date | None = None,
    end_date: date | None = None,
    department_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return ok(_safe_call(service.get_overview, db, start_date, end_date, department_id, OVERVIEW_MAX_DAYS))


@router.get("/work-hours/trend", response_model=SuccessResponse[DashboardTrend])
def work_hours_trend(
    start_date: date | None = None,
    end_date: date | None = None,
    department_id: int | None = Query(None),
    granularity: DashboardTrendGranularity = DashboardTrendGranularity.WEEK,
    db: Session = Depends(get_db),
):
    return ok(_safe_call(
        service.get_trend, db, start_date, end_date, department_id, granularity, TREND_MAX_DAYS[granularity.value]
    ))


@router.get("/work-hours/ranking", response_model=SuccessResponse[EmployeeWorkHoursRanking])
def work_hours_ranking(
    start_date: date | None = None,
    end_date: date | None = None,
    department_id: int | None = Query(None),
    limit: int = Query(10, ge=1, le=100),
    include_all: bool = False,
    period: DashboardTrendGranularity | None = None,
    db: Session = Depends(get_db),
):
    return ok(_safe_call(
        service.get_ranking,
        db, start_date, end_date, department_id, limit, RANKING_MAX_DAYS, include_all, period,
    ))


@router.get("/attendance-exceptions", response_model=SuccessResponse[list[AttendanceExceptionItem]])
def attendance_exceptions(
    start_date: date | None = None,
    end_date: date | None = None,
    department_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, meta = _safe_call(
        service.get_attendance_exceptions,
        db, start_date, end_date, department_id, page, page_size, EXCEPTIONS_MAX_DAYS,
    )
    return ok(items, meta)
