# Import libraries
from sqlmodel import Session, select
from rich.console import Console
from tabulate import tabulate
from sqlalchemy.orm import aliased

# Import modules
from models import Team, Season, Standing, Fixture, Venue

# Create console
console = Console()

# Display Standings for a season
def print_standings_table(session: Session, league_id: int, year: int):
    # Find season
    season = session.exec(
        select(Season).where(
            (Season.year == year) & (Season.league_id == league_id)
        )
    ).first()
    if not season:
        console.print(f'[red]Error:[/red] No season found for {year} and league ID {league_id}.')
        return
    # Query standings and Teams
    standings = session.exec(
        select(Standing, Team).join(Team, Standing.team_id == Team.team_api_id).where(Standing.season_id == season.id).order_by(Standing.position)
    ).all()
    # Print Table
    data = []
    for standing, team in standings:
        data.append([
            standing.position,
            team.name,
            standing.played,
            standing.wins,
            standing.draws,
            standing.losses,
            standing.goals_for,
            standing.goals_against,
            standing.goal_diff,
            standing.points
        ])
    headers = [
        "", "Team", "GP", "W", "D", "L", "F", "A", "GD", "P"
    ]

    console.print(f"\n[bold]Standings for {year}.")
    print(tabulate(data, headers=headers, tablefmt="pretty"))


# Display Fixtures for a Season
def print_fixtures(session: Session, league_id: int, year: int):
    # Find season
    season = session.exec(
        select(Season).where(
            (Season.year == year) & (Season.league_id == league_id)
        )
    ).first()
    if not season:
        console.print(f'[red]Error:[/red] No season found for {year} and league ID {league_id}.')
        return
    # Create aliases to join Team table twice
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    # Query Fixtures, teams, venue
    fixtures = session.exec(
        select(Fixture, HomeTeam.name.label("home_team_name"), AwayTeam.name.label("away_team_name"), Venue)
        .join(HomeTeam, Fixture.home_team_id == HomeTeam.team_api_id)
        .join(AwayTeam, Fixture.away_team_id == AwayTeam.team_api_id)
        .join(Venue, Fixture.venue_id == Venue.venue_api_id)
        .where(Fixture.season_id == season.id)
        .order_by(Fixture.date)
    ).all()
    # Print Table
    data = []
    # Premier League
    if league_id == 39:
        for fixture, home_team_name, away_team_name, venue in fixtures:
            round_str = fixture.round
            matchday_num = int(round_str.split(" - ")[-1])
            data.append([
                matchday_num,
                fixture.date,
                home_team_name,
                fixture.home_goals,
                away_team_name,
                fixture.away_goals,
                fixture.referee
            ])
        headers = [
            "Match Day", "Date", "Home Team", "Home Score", "Away Team", "Away Score", "Referee"
        ]
        console.print(f"\n[bold]Fixtures for {year}.")
        print(tabulate(data, headers=headers, tablefmt="pretty"))

    elif league_id == 45:
        for fixture, home_team_name, away_team_name, venue in fixtures:
            data.append([
                fixture.round,
                fixture.date,
                home_team_name,
                fixture.home_goals,
                away_team_name,
                fixture.away_goals,
                fixture.referee
            ])
        headers = [
            "Round", "Date", "Home Team", "Home Score", "Away Team", "Away Score", "Referee"
        ]
        console.print(f"\n[bold]Fixtures for {year}.")
        print(tabulate(data, headers=headers, tablefmt="pretty"))