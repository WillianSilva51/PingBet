from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.bet import Bet
    from app.models.match import Match
    from app.models.player import Player


class Team(SQLModel, table=True):
    __tablename__ = "Team"  # type: ignore

    id: int | None = Field(primary_key=True, default=None)
    player1_id: int = Field(foreign_key="Player.id")
    player2_id: int | None = Field(foreign_key="Player.id", nullable=True)

    player1: "Player" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Team.player1_id]"},
        back_populates="teams_as_player1",
    )

    player2: "Player | None" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Team.player2_id]"},
        back_populates="teams_as_player2",
    )

    matches_as_team_a: list["Match"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.team_a_id]"},
        back_populates="team_a",
    )

    matches_as_team_b: list["Match"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.team_b_id]"},
        back_populates="team_b",
    )

    matches_as_team_winning: list["Match"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.winning_team_id]"},
        back_populates="winning_team",
    )

    bets: list["Bet"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Bet.team_id]"},
        back_populates="team",
    )
