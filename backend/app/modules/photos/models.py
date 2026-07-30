from datetime import datetime

from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.personnel.models import Personnel
    from app.modules.device.models import Device


class PhotoRegistration(Base):
    __tablename__ = "photo_registrations"

    # Raw image bytes must never be snapshotted into the JSONB audit log
    __audit_exclude__ = frozenset({"img_data"})

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id_internal: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("personnel.person_id_internal", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    person_id_device: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    face_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    feature: Mapped[str | None] = mapped_column(String(100), nullable=True)
    feature_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    img_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    img_data: Mapped[bytes | None] = mapped_column(nullable=True)
    img_content_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    @property
    def has_image(self) -> bool:
        return self.img_data is not None or self.img_url is not None

    # Relationships
    personnel: Mapped[Optional["Personnel"]] = relationship(
        back_populates="photo_registrations",
        foreign_keys=[person_id_internal]
    )
    
    device: Mapped[Optional["Device"]] = relationship(
        back_populates="photo_registrations",
        foreign_keys=[device_id]
    )
