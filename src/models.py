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
    country_name: str = Field(foreign_key="country.country_name")
    comp_name: str
    comp_type: str
    comp_logo: str

# Define Venue Model
class Venue(SQLModel, table=True):
    venue_api_id: int = Field(primary_key=True)
    name: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    country: str
    country_id: int
    capacity: Optional[int] = Field(default=None)
    surface: Optional[str] = Field(default=None)
    image: Optional[str] = Field(default=None)

# Define Team Model, links to Venue
class Team(SQLModel, table=True):
    team_api_id: int = Field(primary_key=True)
    name: str
    short_name: Optional[str] = Field(default=None)
    country: str
    country_id: int = Field(foreign_key="country.id")
    founded: Optional[int] = Field(default=None)
    national: bool
    logo_url: str

# Define Season Model, links to Competition
class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    league_id: int = Field(foreign_key="competition.comp_api_id")
    total_teams: int
    __table_args__ = (UniqueConstraint("year", "league_id"),)

# Define TeamVenue Model, links Team and Venue with Season and Competition



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
    referee: Optional[str] = Field(default=None)
    date: datetime
    short_status: str
    elapsed: Optional[int] = Field(default=None)
    round: str
    home_goals: Optional[int] = Field(default=None)
    away_goals: Optional[int] = Field(default=None)
    half_home_goals: Optional[int] = Field(default=None)
    half_away_goals: Optional[int] = Field(default=None)
    full_home_goals: Optional[int] = Field(default=None)
    full_away_goals: Optional[int] = Field(default=None)
    et_home_goals: Optional[int] = Field(default=None)
    et_away_goals: Optional[int] = Field(default=None)
    pen_home_goals: Optional[int] = Field(default=None)
    pen_away_goals: Optional[int] = Field(default=None)

# Define a FixtureStats Model, links to Fixture and Team (one)
class FixtureStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fixture_id: int = Field(foreign_key="fixture.id")
    home_team_id: int = Field(foreign_key="team.team_api_id")
    home_sh_on_goal: Optional[int] = Field(default=None)
    home_sh_off_goal: Optional[int] = Field(default=None)
    home_total_sh: Optional[int] = Field(default=None)
    home_blocked_sh: Optional[int] = Field(default=None)
    home_sh_inside: Optional[int] = Field(default=None)
    home_sh_outside: Optional[int] = Field(default=None)
    home_fouls: Optional[int] = Field(default=None)
    home_corners: Optional[int] = Field(default=None)
    home_offsides: Optional[int] = Field(default=None)
    home_possession: Optional[str] = Field(default=None)
    home_yellows: Optional[int] = Field(default=None)
    home_reds: Optional[int] = Field(default=None)
    home_saves: Optional[int] = Field(default=None)
    home_tot_passes: Optional[int] = Field(default=None)
    home_accurate_pass: Optional[int] = Field(default=None)
    home_percent_pass: Optional[str] = Field(default=None)
    home_ex_goals: Optional[str] = Field(default=None)
    away_team_id: int = Field(foreign_key="team.team_api_id")
    away_sh_on_goal: Optional[int] = Field(default=None)
    away_sh_off_goal: Optional[int] = Field(default=None)
    away_total_sh: Optional[int] = Field(default=None)
    away_blocked_sh: Optional[int] = Field(default=None)
    away_sh_inside: Optional[int] = Field(default=None)
    away_sh_outside: Optional[int] = Field(default=None)
    away_fouls: Optional[int] = Field(default=None)
    away_corners: Optional[int] = Field(default=None)
    away_offsides: Optional[int] = Field(default=None)
    away_possession: Optional[str] = Field(default=None)
    away_yellows: Optional[int] = Field(default=None)
    away_reds: Optional[int] = Field(default=None)
    away_saves: Optional[int] = Field(default=None)
    away_tot_passes: Optional[int] = Field(default=None)
    away_accurate_pass: Optional[int] = Field(default=None)
    away_percent_pass: Optional[str] = Field(default=None)
    away_ex_goals: Optional[str] = Field(default=None)

    __table_args__ = (UniqueConstraint("fixture_id", "home_team_id", "away_team_id"),)