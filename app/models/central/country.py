from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Country(Base):
    """Maps Nest Sequelize model `central.country` (read-only in V1; DDL from server migrations)."""

    __tablename__ = "country"
    __table_args__ = {"schema": "central"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(2))
    name: Mapped[str] = mapped_column(Text)
    schema_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean)
