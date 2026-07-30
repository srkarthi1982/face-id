from datetime import date

from sqlalchemy import Date, ForeignKey, String, DateTime, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import AuditedMixin, Base

from datetime import datetime
import re
from base64 import b64encode, b64decode


class Profile(AuditedMixin, Base):
    __tablename__ = "profiles"
    __audit_exclude__ = frozenset({"_photo", "_signature"})

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    first_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    country: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(50))
    mobile_no: Mapped[str] = mapped_column(String(50), nullable=True)
    ext_no: Mapped[str] = mapped_column(String(20), nullable=True)
    rank: Mapped[str] = mapped_column(String(20), default="CIVILIAN")
    command: Mapped[str] = mapped_column(String(20), nullable=True)
    qualification: Mapped[str] = mapped_column(String(255), nullable=True)
    _photo: Mapped[bytes | None] = mapped_column(
        LargeBinary, nullable=True, deferred=True, name="photo")
    _signature: Mapped[bytes | None] = mapped_column(
        LargeBinary, nullable=True, deferred=True, name="signature")
    esnaad_sync_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(
        back_populates="profile", foreign_keys=[user_id])

    @property
    def full_name(self) -> str:
        return re.sub(r'\s+', ' ', ' '.join([self.first_name, self.middle_name or '', self.last_name or '']).strip())

    @full_name.setter
    def full_name(self, value: str):
        self.first_name, self.middle_name, self.last_name = self.split_full_name(value)

    @classmethod
    def split_full_name(cls, full_name: str):
        first_name, mid_name, last_name = None, None, None
        splitted_str = full_name.split()
        if len(splitted_str) > 1:
            first_name, mid_name, last_name = splitted_str[0], ' '.join(
                splitted_str[1:-1]), splitted_str[-1]
        else:
            first_name = full_name

        return first_name, mid_name, last_name

    @property
    def photo(self) -> str:
        return None if self._photo is None else b64encode(self._photo).decode("utf-8")

    @photo.setter
    def photo(self, value: str):
        self._photo = None if not value else b64decode(value)

    @property
    def signature(self) -> str:
        return None if self._signature is None else b64encode(self._signature).decode("utf-8")

    @signature.setter
    def signature(self, value: str):
        self._signature = None if not value else b64decode(value)
