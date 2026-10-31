from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

SCHEMA = {"schema": "in"}


class Business(Base):
    __tablename__ = "business"
    __table_args__ = SCHEMA

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    slug: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    verification: Mapped[str] = mapped_column(String(16))
    rating_avg: Mapped[Decimal] = mapped_column(Numeric(3, 2))
    response_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    price_hint: Mapped[str | None] = mapped_column(Text)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class BusinessLocation(Base):
    __tablename__ = "business_location"
    __table_args__ = SCHEMA

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    business_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey(Business.id))
    city_name: Mapped[str] = mapped_column(Text)
    state_name: Mapped[str] = mapped_column(Text)
    is_primary: Mapped[bool] = mapped_column(Boolean)


class Category(Base):
    __tablename__ = "category"
    __table_args__ = SCHEMA

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    slug: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean)


class BusinessCategory(Base):
    __tablename__ = "business_category"
    __table_args__ = SCHEMA

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    business_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey(Business.id))
    category_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey(Category.id))
