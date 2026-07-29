from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.team import Team


class Player(SQLModel, table=True):
    __tablename__ = "Player"  # type: ignore

    id: int | None = Field(primary_key=True, default=None)
    name: str

    teams_as_player1: list["Team"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Team.player1_id]"},
        back_populates="player1",
    )

    teams_as_player2: list["Team"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Team.player2_id]"},
        back_populates="player2",
    )
