# Import libraries
from sqlalchemy import Boolean
from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional

# Define Country Model
class Country(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    country_name: str = Field(unique=True)
    num_comps: int
    code: str
    flag: str

# Define Competition Model
class Competition(SQLModel, table=True):
    comp_api_id: int = Field(primary_key=True)
    comp_country_id: int = Field(foreign_key="country.id")
    comp_name: str
    comp_type: str
    comp_logo: str

# Define Venue Model
class Venue(SQLModel, table=True):
    venue_api_id: int = Field(primary_key=True)
    name: str
    address: str
    city: str
    capacity: int
    surface: str
    image: str

# Define Team Model
class Team(SQLModel, table=True):
    team_api_id: int = Field(primary_key=True)
    name: str
    short_name: str
    country: str
    founded: int
    national: bool
    logo_url: str
    venue_id: int = Field(foreign_key="venue.venue_api_id", unique=True)

# Define Season Model
class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    league_id: int = Field(foreign_key="competition.comp_api_id")
    __table_args__ = (UniqueConstraint("year", "league_id"),)

# Define Standing Model, links Team and Season
class Standing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="team.team_api_id")
    season_id: int = Field(foreign_key="season.id")

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

    __table_args__ = (UniqueConstraint("team_id", "season_id"),)

