"""Explicit response DTOs for read-only attendance analytics."""

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DashboardDataStatus(str, Enum):
    AVAILABLE = "available"
    EMPTY = "empty"


class DashboardTrendGranularity(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class DashboardDepartmentOption(BaseModel):
    department_id: int
    department_name: str


class DashboardDateRange(BaseModel):
    effective_start_date: date | None
    effective_end_date: date | None
    source_latest_report_date: date | None
    department_id: int | None


class DurationTotals(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scheduled_seconds: int = Field(ge=0)
    actual_seconds: int = Field(ge=0)
    normal_seconds: int = Field(ge=0)
    overtime_seconds: int = Field(ge=0)
    late_seconds: int = Field(ge=0)
    early_seconds: int = Field(ge=0)
    absent_seconds: int = Field(ge=0)


class DashboardOverview(DashboardDateRange, DurationTotals):
    data_status: DashboardDataStatus
    duration_unit: Literal["seconds"] = "seconds"
    report_row_count: int = Field(ge=0)
    report_day_count: int = Field(ge=0)
    employee_count: int = Field(ge=0)
    reported_exception_count: int = Field(ge=0)


class DashboardTrendPoint(DurationTotals):
    period_key: str
    period_start: date
    period_end: date
    report_row_count: int = Field(ge=0)
    employee_count: int = Field(ge=0)


class DashboardTrend(DashboardDateRange):
    data_status: DashboardDataStatus
    duration_unit: Literal["seconds"] = "seconds"
    granularity: DashboardTrendGranularity
    points: list[DashboardTrendPoint]


class EmployeeWorkHoursRankingItem(DurationTotals):
    rank: int = Field(ge=1)
    department_id: int | None
    department_name: str | None
    employee_key: str
    person_id: str | None
    person_no: str | None
    person_name: str | None
    report_day_count: int = Field(ge=0)


class EmployeeWorkHoursRanking(DashboardDateRange):
    data_status: DashboardDataStatus
    duration_unit: Literal["seconds"] = "seconds"
    items: list[EmployeeWorkHoursRankingItem]


class AttendanceExceptionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    exception_type: str
    department_id: int | None
    department_name: str | None
    person_id: str | None
    person_no: str | None
    person_name: str | None
    report_date: date | None
    clock_time: datetime | None
    device_key: str | None
    device_name: str | None
