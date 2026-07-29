from datetime import UTC, datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"  # type: ignore

    id: int | None = Field(primary_key=True)
    telegram_id: int | None = Field(unique=True, nullable=True)
    name: str
    balance: Decimal = Field(default="10")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
