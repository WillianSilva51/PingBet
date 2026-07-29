from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.core.enums import MatchStatus, MatchType

if TYPE_CHECKING:
    from app.models.bet import Bet
    from app.models.team import Team


class Match(SQLModel, table=True):
    __tablename__ = "Match"  # type: ignore

    id: int | None = Field(primary_key=True, default=None)
    match_type: MatchType = Field(default=MatchType.SOLO)
    team_a_id: int = Field(foreign_key="Team.id")
    team_b_id: int = Field(foreign_key="Team.id")
    winning_team_id: int = Field(foreign_key="Team.id", nullable=True)
    status: MatchStatus = Field(default=MatchStatus.SCHEDULED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    team_a: "Team" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.team_a_id]"},
        back_populates="matches_as_team_a",
    )

    team_b: "Team" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.team_b_id]"},
        back_populates="matches_as_team_b",
    )

    winning_team: "Team" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.winning_team_id]"},
        back_populates="matches_as_team_winning",
    )

    bets: list["Bet"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Bet.match_id]"},
        back_populates="match",
    )
