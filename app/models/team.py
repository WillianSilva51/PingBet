from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
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
