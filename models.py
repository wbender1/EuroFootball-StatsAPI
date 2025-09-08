# Import libraries
from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional

# Define Team Model
class Team(SQLModel, table=True):
    api_id: int = Field(default=None, primary_key=True)
    name: str
    short_name: Optional[str] = None
    logo_url: Optional[str] = None

# Define Season Model
class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    league_id: int
    league_name: str
    __table_args__ = (UniqueConstraint("year", "league_id"),)

# Define Standing Model, links Team and Season
class Standing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    competition: str
    team_id: int = Field(foreign_key="team.api_id")
    season_id: int = Field(foreign_key="season.id")

    name: str
    year: int
    position: int
    points: int
    goals_for: int
    goals_against: int
    goal_diff: int
    played: int
    wins: int
    draws: int
    losses: int
    home_goals_for: int
    home_goals_against: int
    home_goal_diff: int
    home_played: int
    home_wins: int
    home_draws: int
    home_losses: int
    away_goals_for: int
    away_goals_against: int
    away_goal_diff: int
    away_played: int
    away_wins: int
    away_draws: int
    away_losses: int

    __table_args = (UniqueConstraint("team_id", "season_id"),)

