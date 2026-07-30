from datetime import datetime

from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.personnel.models import Personnel
    from app.modules.device.models import Device


class DevicePersonMapping(Base):
    __tablename__ = "device_person_mapping"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id_internal: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("personnel.person_id_internal", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    device_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    person_id_device: Mapped[str | None] = mapped_column(String(64), nullable=True)
    photo_ids: Mapped[dict] = mapped_column(JSON, server_default="{}", nullable=False)
    synced_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    personnel: Mapped[Optional["Personnel"]] = relationship(
        back_populates="device_mappings",
        foreign_keys=[person_id_internal]
    )
    
    device: Mapped[Optional["Device"]] = relationship(
        back_populates="person_mappings",
        foreign_keys=[device_id]
    )
