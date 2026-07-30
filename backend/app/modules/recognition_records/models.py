from datetime import datetime

from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RecognitionRecord(Base):
    __tablename__ = "recognition_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(Integer, nullable=False)
    person_id_internal: Mapped[str | None] = mapped_column(String(64), nullable=True)
    person_id_device: Mapped[str | None] = mapped_column(String(64), nullable=True)
    record_type: Mapped[str] = mapped_column(String(30), nullable=False)
    mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    event_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    event_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    event_time: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    img_data: Mapped[bytes | None] = mapped_column(nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="callback", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
