from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.person_mapping.models import DevicePersonMapping
    from app.modules.photos.models import PhotoRegistration


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    device_name: Mapped[str] = mapped_column(String(200), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=8090, nullable=False)
    api_password: Mapped[str] = mapped_column(String(255), nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sdk_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="unknown", nullable=False)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    settings: Mapped[dict] = mapped_column(JSON, server_default="{}", nullable=False)
    callback_urls: Mapped[dict] = mapped_column(JSON, server_default="{}", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    location: Mapped[Optional["Location"]] = relationship(back_populates="devices")
    
    # Reverse relationships for join queries
    person_mappings: Mapped[list["DevicePersonMapping"]] = relationship(
        back_populates="device"
    )
    
    photo_registrations: Mapped[list["PhotoRegistration"]] = relationship(
        back_populates="device"
    )
