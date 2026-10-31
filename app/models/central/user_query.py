from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserQuery(Base):
    """Maps Nest `central.user_query` — only the columns matching reads or updates."""

    __tablename__ = "user_query"
    __table_args__ = {"schema": "central"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    status: Mapped[str] = mapped_column(String(16))
    raw_text: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    location_city: Mapped[str | None] = mapped_column(Text)
    location_state: Mapped[str | None] = mapped_column(Text)
    budget_min: Mapped[int | None] = mapped_column(Integer)
    budget_max: Mapped[int | None] = mapped_column(Integer)
    budget_currency: Mapped[str | None] = mapped_column(String(8))
    model_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
