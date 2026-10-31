from decimal import Decimal
from typing import Any

from sqlalchemy import Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

SCHEMA = {"schema": "in"}


class BusinessMatch(Base):
    __tablename__ = "business_match"
    __table_args__ = SCHEMA

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()")
    )
    query_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    business_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    score: Mapped[Decimal] = mapped_column(Numeric(6, 3))
    rank: Mapped[int] = mapped_column(Integer)
    score_breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class Lead(Base):
    """Business-visible snapshot of a query. Never copy the private chat here."""

    __tablename__ = "lead"
    __table_args__ = SCHEMA

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    query_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    business_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    source_action: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), server_default="NEW")
    snapshot_summary: Mapped[str] = mapped_column(Text)
    snapshot_category: Mapped[str | None] = mapped_column(Text)
    snapshot_location_city: Mapped[str | None] = mapped_column(Text)
    snapshot_location_state: Mapped[str | None] = mapped_column(Text)
    snapshot_budget_min: Mapped[int | None] = mapped_column(Integer)
    snapshot_budget_max: Mapped[int | None] = mapped_column(Integer)
    snapshot_budget_currency: Mapped[str | None] = mapped_column(String(8))
