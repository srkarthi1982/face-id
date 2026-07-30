"""Thin authenticated HTTP routes for attendance analytics."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import require_permission
from app.core.permissions import PermissionCode
from app.core.response import SuccessResponse, ok

from . import service
from .constants import (
    EXCEPTIONS_MAX_DAYS,
    OVERVIEW_MAX_DAYS,
    RANKING_MAX_DAYS,
    TREND_MAX_DAYS,
    UNAVAILABLE_MESSAGE,
)
from .db import LunaConfigurationError, LunaUnavailableError
from .schemas import (
    AttendanceExceptionItem,
    DashboardOverview,
    DashboardOrganizationOption,
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
    except (LunaConfigurationError, LunaUnavailableError):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=UNAVAILABLE_MESSAGE) from None


DashboardRangeError = service.DashboardRangeError


@router.get("/organizations", response_model=SuccessResponse[list[DashboardOrganizationOption]])
def organizations():
    return ok(_safe_call(service.get_organizations))


@router.get("/overview", response_model=SuccessResponse[DashboardOverview])
def overview(
    start_date: date | None = None,
    end_date: date | None = None,
    org_id: str | None = Query(None, max_length=64),
):
    return ok(_safe_call(service.get_overview, start_date, end_date, org_id, OVERVIEW_MAX_DAYS))


@router.get("/work-hours/trend", response_model=SuccessResponse[DashboardTrend])
def work_hours_trend(
    start_date: date | None = None,
    end_date: date | None = None,
    org_id: str | None = Query(None, max_length=64),
    granularity: DashboardTrendGranularity = DashboardTrendGranularity.WEEK,
):
    return ok(_safe_call(
        service.get_trend, start_date, end_date, org_id, granularity, TREND_MAX_DAYS[granularity.value]
    ))


@router.get("/work-hours/ranking", response_model=SuccessResponse[EmployeeWorkHoursRanking])
def work_hours_ranking(
    start_date: date | None = None,
    end_date: date | None = None,
    org_id: str | None = Query(None, max_length=64),
    limit: int = Query(10, ge=1, le=100),
):
    return ok(_safe_call(service.get_ranking, start_date, end_date, org_id, limit, RANKING_MAX_DAYS))


@router.get("/attendance-exceptions", response_model=SuccessResponse[list[AttendanceExceptionItem]])
def attendance_exceptions(
    start_date: date | None = None,
    end_date: date | None = None,
    org_id: str | None = Query(None, max_length=64),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, meta = _safe_call(
        service.get_attendance_exceptions,
        start_date, end_date, org_id, page, page_size, EXCEPTIONS_MAX_DAYS,
    )
    return ok(items, meta)
