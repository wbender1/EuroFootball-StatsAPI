# Import libraries
from markdown_it.rules_block import table
from sqlalchemy import Boolean
from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional
from datetime import datetime

# Define Country Model
class Country(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    country_name: str = Field(unique=True)
    num_comps: int
    code: str
    flag: str

# Define Competition Model, links to Country
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

# Define Team Model, links to Venue
class Team(SQLModel, table=True):
    team_api_id: int = Field(primary_key=True)
    name: str
    short_name: str
    country: str
    founded: int
    national: bool
    logo_url: str
    venue_id: int = Field(foreign_key="venue.venue_api_id", unique=True)

# Define Season Model, links to Competition
class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    league_id: int = Field(foreign_key="competition.comp_api_id")
    __table_args__ = (UniqueConstraint("year", "league_id"),)

# Define Standing Model, links to Team and Season
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

# Define a Fixture Model, links to Season, Team (both), Venue, and Competition
class Fixture(SQLModel, table=True):
    id: int = Field(primary_key=True)
    # Relationships: Fixture is many, other models are one
    season_id: int = Field(foreign_key="season.id") # Many-to-one
    home_team_id: int = Field(foreign_key="team.team_api_id") # Many-to-one
    away_team_id: int = Field(foreign_key="team.team_api_id") # Many-to-one
    venue_id: int = Field(foreign_key="venue.venue_api_id") # Many-to-one
    competition_id: int = Field(foreign_key="competition.comp_api_id") # Many-to-one
    referee: str
    date: datetime
    short_status: str
    elapsed: int
    round: str
    home_goals: int
    away_goals: int
    half_home_goals: int
    half_away_goals: int
    full_home_goals: int
    full_away_goals: int
    et_home_goals: Optional[int] = Field(default=None)
    et_away_goals: Optional[int] = Field(default=None)
    pen_home_goals: Optional[int] = Field(default=None)
    pen_away_goals: Optional[int] = Field(default=None)

# Define a FixtureStats Model, links to Fixture and Team (one)
class FixtureStats(SQLModel, table=True):
    id: int = Field(primary_key=True)
    fixture_id: int = Field(foreign_key="fixture.id")
    team_id: int = Field(foreign_key="team.team_api_id")
    sh_on_goal: int
    sh_off_goal: int
    total_sh: int
    blocked_sh: int
    sh_inside: int
    sh_outside: int
    fouls: int
    corners: int
    offsides: int
    possession: str
    yellows: Optional[int] = Field(default=None)
    reds: Optional[int] = Field(default=None)
    saves: int
    tot_passes: int
    accurate_pass: int
    percent_pass: str
    ex_goals: str

    __table_args__ = (UniqueConstraint("fixture_id", "team_id"),)