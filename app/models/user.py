from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.bet import Bet


class User(SQLModel, table=True):
    __tablename__ = "User"  # type: ignore

    id: int | None = Field(primary_key=True, default=None)
    telegram_id: int | None = Field(unique=True, nullable=True)
    name: str
    account_test: bool = Field(default=True)
    balance: Decimal = Field(default="10")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    bets: list["Bet"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Bet.user_id]"},
        back_populates="user",
    )
