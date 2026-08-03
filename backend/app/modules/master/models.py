from app.core.database import Base, TimestampMixin
from datetime import time

from sqlalchemy import String, Boolean, Integer, ForeignKey, Enum, UniqueConstraint, Time, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from app.modules.device.models import Device
    from app.modules.personnel.models import Personnel


class UnitType(str, enum.Enum):
    FORCE = "force"
    COMMAND = "command"
    BATTALION = "battalion"
    UNIT = "unit"


class LocationType(str, enum.Enum):
    EMIRATE = "emirate"
    BASE = "base"
    LOCATION = "location"
    BUILDING = "building"
    AREA = "area"


class Location(Base, TimestampMixin):
    __tablename__ = "locations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[LocationType] = mapped_column(Enum(LocationType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=LocationType.LOCATION)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    unit_id: Mapped[Optional[int]] = mapped_column(ForeignKey("units.id"), nullable=True)
    path: Mapped[str] = mapped_column(String(1000), nullable=False, default="/")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    parent: Mapped[Optional["Location"]] = relationship(
        foreign_keys=[parent_id],
        remote_side=[parent_id]
    )
    children: Mapped[list["Location"]] = relationship(
        foreign_keys=[parent_id],
        overlaps="parent"
    )
    unit: Mapped[Optional["Unit"]] = relationship(
        foreign_keys=[unit_id]
    )
    devices: Mapped[list["Device"]] = relationship(back_populates="location")
    personnel: Mapped[list["Personnel"]] = relationship(
        back_populates="organization",
        foreign_keys="Personnel.org_id"
    )


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    path: Mapped[str] = mapped_column(String(1000), nullable=False, default="/")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    parent: Mapped[Optional["Department"]] = relationship(
        foreign_keys=[parent_id],
        remote_side=[parent_id],
    )
    children: Mapped[list["Department"]] = relationship(
        foreign_keys=[parent_id],
        overlaps="parent",
    )
    personnel: Mapped[list["Personnel"]] = relationship(
        back_populates="department",
        foreign_keys="Personnel.department_id",
    )
    timings: Mapped[list["Timing"]] = relationship(
        back_populates="department",
        cascade="all, delete-orphan",
    )


class Weekday(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Timing(Base, TimestampMixin):
    __tablename__ = "timings"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_day: Mapped[Weekday] = mapped_column(
        Enum(Weekday, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    end_day: Mapped[Weekday] = mapped_column(
        Enum(Weekday, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department: Mapped["Department"] = relationship(back_populates="timings")

    __table_args__ = (
        Index(
            "uq_timings_one_active_per_department",
            "department_id",
            unique=True,
            postgresql_where=(is_active.is_(True)),
        ),
    )


class Unit(Base, TimestampMixin):
    __tablename__ = "units"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    type: Mapped[UnitType] = mapped_column(Enum(UnitType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=UnitType.UNIT)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("units.id"), nullable=True)
    path: Mapped[str] = mapped_column(String(1000), nullable=False, default="/")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    parent: Mapped[Optional["Unit"]] = relationship(
        foreign_keys=[parent_id],
        remote_side=[parent_id]
    )
    children: Mapped[list["Unit"]] = relationship(
        foreign_keys=[parent_id],
        overlaps="parent"
    )
    locations: Mapped[list["Location"]] = relationship(
        foreign_keys="Location.unit_id",
        overlaps="unit"
    )
    
    __table_args__ = (
        UniqueConstraint("parent_id", "code", name="uq_units_parent_code"),
    )
