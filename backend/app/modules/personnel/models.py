from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.master.models import Department, Location
    from app.modules.photos.models import PhotoRegistration
    from app.modules.person_mapping.models import DevicePersonMapping


class Personnel(Base):
    __tablename__ = "personnel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Organization/Location mapping (multi-tenancy)
    org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Employee identification
    emp_no: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    person_id_internal: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    person_id_device: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Personal information
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    gender: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0=Unknown, 1=Male, 2=Female
    
    # Contact information
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Additional personal details
    date_of_birth: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    idcard_num: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    id_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    card_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Employment information
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    position: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    hire_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Device sync and access control
    permissions: Mapped[dict] = mapped_column(JSON, server_default="{}", nullable=False)
    pass_time: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    push_to_device: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    organization: Mapped[Optional["Location"]] = relationship(
        foreign_keys=[org_id],
        back_populates="personnel"
    )
    
    department: Mapped[Optional["Department"]] = relationship(
        foreign_keys=[department_id],
        back_populates="personnel"
    )
    
    # One row per (person, device); device_id NULL = master photo not tied to a device
    photo_registrations: Mapped[list["PhotoRegistration"]] = relationship(
        back_populates="personnel",
        primaryjoin="Personnel.person_id_internal == PhotoRegistration.person_id_internal"
    )
    
    device_mappings: Mapped[list["DevicePersonMapping"]] = relationship(
        back_populates="personnel"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("emp_no", "org_id", name="uq_personnel_emp_no_org"),
    )

    def __repr__(self) -> str:
        return f"<Personnel(id={self.id}, emp_no='{self.emp_no}', full_name='{self.full_name}')>"
