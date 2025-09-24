# Import libraries
from typing import Optional

import typer
from sqlmodel import Session, select, delete, SQLModel, or_, and_
import requests, json
from rich.console import Console
from rich.progress import track
from datetime import datetime
import time
from tabulate import tabulate

# Import modules
from models import Country, Competition, Venue, Team, Season, Standing, Fixture, FixtureStats
# Import print functions
from display_utils import (print_comps, print_country_type_comps, print_type_comps, print_countries, print_fixtures,
                           print_team_fixtures, print_fixture_stats, print_seasons, print_comp_seasons, print_country_seasons,
                           print_year_seasons, print_year_country_seasons, print_standings_table, print_teams,
                           print_teams_country, print_teams_season, print_national_teams, print_national_teams_season,
                           print_venues, print_venues_country, print_venues_season)
from database import engine
import config
from api_request import api_request

from helper_functions import (make_country, fetch_competitions, fetch_teams, fetch_venues, make_season, fetch_standings,
                              fetch_fixtures, make_meta_join_table)

# Create Typer app and console
app = typer.Typer()
console = Console()


# Initialize Database
@app.command()
def init_db():
    SQLModel.metadata.create_all(engine)
    console.print("Database tables created!", style="green")

#**********************************     Fetch Data Functions    *************************************#
# Fetch Country
@app.command()
def fetch_country(input_country_name: str):
    with Session(engine) as session:
        console.print(f'Fetching all data for {input_country_name}', style="blue")

        make_country(session, input_country_name)
        comps_added = fetch_competitions(session, input_country_name)
        teams_added = fetch_teams(session, input_country_name)
        venues_added = fetch_venues(session, input_country_name)

        summary_table = [
            ("Competitions Added", comps_added),
            ("Teams Added", teams_added),
            ("Venues Added", venues_added)
        ]
        headers = ["Entity", "Added Count"]
        console.print(f"\n[bold]Data added for[/bold] [green]{input_country_name}")
        print(tabulate(summary_table, headers=headers, tablefmt="pretty"))


# Fetch Season
@app.command()
def fetch_season(competition_name: str, year: int):
    with Session(engine) as session:
        # Find or Make Season
        season, competition = make_season(session, competition_name, year)
        if competition.comp_type == 'League':
            fetch_standings(session, season, competition)
        else:
            console.print(f'No Standings Data for League Competitions.', style="yellow")
        # Find Fixtures
        fetch_fixtures(session, season, competition)
        # Make Team-Season Join Table Entries
        make_meta_join_table(session, season)


#**********************************     Show Data Functions     *************************************#
# Show Countries
@ app.command()
def show_countries():
    with Session(engine) as session:
        print_countries(session)

# Show Competitions
@ app.command()
def show_competitions(country_name: Optional[str] = typer.Option(None, "--country", "-c"),
                      comp_type: Optional[str] = typer.Option(None, "--type", "-t")):
    with Session(engine) as session:
        if comp_type and country_name:
            print_country_type_comps(session, country_name, comp_type)
            return
        if comp_type:
            print_type_comps(session, comp_type)
            return
        else:
            print_comps(session, country_name)

# Show Seasons
@ app.command()
def show_seasons(competition_name: Optional[str] = typer.Option(None, "--competition", "-c"),
                 year: Optional[int] = typer.Option(None, "--year", "-y"),
                 country_name: Optional[str] = typer.Option(None, "--country")):
    with Session(engine) as session:
        if country_name and year:
            print_year_country_seasons(session, year, country_name)
            return
        if competition_name:
            print_comp_seasons(session, competition_name)
            return
        if year:
            print_year_seasons(session, year)
            return
        if country_name:
            print_country_seasons(session, country_name)
            return
        else:
            print_seasons(session)

# Show Teams
@ app.command()
def show_teams(competition_name: Optional[str] = typer.Option(None, "--competition", "-c"),
                 year: Optional[int] = typer.Option(None, "--year", "-y"),
                 country_name: Optional[str] = typer.Option(None, "--country"),
               national: bool = typer.Option(False, "--national", help="Show only national teams")):
    with Session(engine) as session:
        if national and competition_name and year:
            print_national_teams_season(session, competition_name, year)
            return
        if national:
            print_national_teams(session)
            return
        if competition_name and year:
            print_teams_season(session, competition_name, year)
            return
        if country_name:
            print_teams_country(session, country_name)
            return
        else:
            print_teams(session)

# Show Venues


# Show Standings function
@app.command()
def show_standings(competition_name: str, year: int):
    with Session(engine) as session:
        print_standings_table(session, competition_name, year)

# Show Fixtures function
@app.command()
def show_fixtures(competition_name: str, year: int, team_name: Optional[str] = typer.Argument(None)):
    with Session(engine) as session:
        if team_name:
            print_team_fixtures(session, competition_name, year, team_name)
        else:
            print_fixtures(session, competition_name, year)

# Show Fixture Stats function
@app.command()
def show_fixture_stats(competition_name: str, year: int, team_name1: str, team_name2: str):
    with Session(engine) as session:
        print_fixture_stats(session, competition_name, year, team_name1, team_name2)


# Run App
if __name__ == "__main__":
    app()