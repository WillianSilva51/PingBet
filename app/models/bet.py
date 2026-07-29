from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.core.enums import BetStatus

if TYPE_CHECKING:
    from app.models.match import Match
    from app.models.team import Team
    from app.models.user import User


class Bet(SQLModel, table=True):
    __tablename__ = "Bet"  # type: ignore

    id: int | None = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="User.id")
    match_id: int = Field(foreign_key="Match.id")
    team_id: int = Field(foreign_key="Team.id")
    amount: Decimal = Field(default="1")
    status: BetStatus = Field(default=BetStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Bet.user_id]"},
        back_populates="bets",
    )

    match: "Match" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Bet.match_id]"},
        back_populates="bets",
    )

    team: "Team" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Bet.team_id]"},
        back_populates="bets",
    )
