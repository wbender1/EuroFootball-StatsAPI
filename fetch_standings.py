# Import libraries
import typer
from sqlmodel import Session, select, SQLModel
import requests
from rich.console import Console
from rich.progress import track

# Import modules
from models import Team, Season, Standing
from database import engine
import config

# Create Typer app and console
app = typer.Typer()
console = Console()

@app.command()
def init_db():
    SQLModel.metadata.create_all(engine)
    console.print("Database tables created!", style="green")

@app.command()
def fetch_season(league_id: int, year: int):
    console.print(f'Fetching {year} season for league ID {league_id}.', style="blue")

    # Api Request Setup
    url = "https://v3.football.api-sports.io/standings"
    headers = {
        'x-rapidapi-key': config.API_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    params = { 'league': league_id, 'season': year}

    # Try API Request and use error handling
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        console.print(f'API Request failed: {e}', style="red")
        return

    if data.get('results', 0) == 0:
        console.print("No data returned from API.", style="red")
        return

    # Process data
    with Session(engine) as session:
        # Create or get season
        league_name = data['response'][0]['league']['name']
        season_stmt = select(Season).where(
            (Season.year == year) & (Season.league_id == league_id)
        )
        season = session.exec(season_stmt).first()

        if not season:
            season = Season(year=year, league_id=league_id, league_name=league_name)
            session.add(season)
            session.commit()
            session.refresh(season)
            console.print(f'Created new season: {league_name} {year}', style="green")

        # Process each team in standings
        standings_data = data['response'][0]['league']['standings'][0]

        for team_entry in track(standings_data, description="Processing teams."):
            team_info = team_entry['team']
            stats = team_entry['all']
            home_stats = team_entry['home']
            away_stats = team_entry['away']

            # Find or create the team
            team_stmt = select(Team).where(Team.api_id == team_info['id'])
            team = session.exec(team_stmt).first()

            if not team:
                team = Team(
                    api_id=team_info['id'],
                    name=team_info['name'],
                    short_name=team_info.get('code', None),
                    logo_url=team_info.get('logo', None)
                )
                session.add(team)
                session.commit()
                session.refresh(team)
                console.print(f'Created new team: {team.name}', style="green")

            # Create standings entry
            standing = Standing(
                team_id=team.id,
                season_id=season.id,
                position=team_entry['rank'],
                points=team_entry['points'],
                goals_for=stats['goals']['for'],
                goals_against=stats['goals']['against'],
                goal_diff=(stats['goals']['for'] - stats['goals']['against']),
                played=stats['played'],
                wins=stats['win'],
                draws=stats['draw'],
                losses=stats['lose'],
                home_goals_for=home_stats['goals']['for'],
                home_goals_against=home_stats['goals']['against'],
                home_goal_diff=(home_stats['goals']['for'] - home_stats['goals']['against']),
                home_played=home_stats['played'],
                home_wins=home_stats['win'],
                home_draws=home_stats['draw'],
                home_losses=home_stats['lose'],
                away_goals_for=away_stats['goals']['for'],
                away_goals_against=away_stats['goals']['against'],
                away_goal_diff=(away_stats['goals']['for'] - away_stats['goals']['against']),
                away_played=away_stats['played'],
                away_wins=away_stats['win'],
                away_draws=away_stats['draw'],
                away_losses=away_stats['lose'],
            )
            session.add(standing)

        session.commit()

    console.print(f'Successfully added {len(standings_data)} teams for {year} season!', style="bold green")


@app.command()
def list_seasons():
    """List all seasons in the database."""
    with Session(engine) as session:
        seasons = session.exec(select(Season)).all()
        if not seasons:
            console.print("No seasons found in database.", style="yellow")
            return

        console.print("\n[bold]Seasons in database:[/bold]")
        for season in seasons:
            console.print(f"ID: {season.id} - {season.league_name} {season.year}")

@app.command()
def list_team():
    with Session(engine) as session:
        teams = session.exec(select(Team)).all()
        if not teams:
            console.print("No teams found in database.", style="yellow")
            return

        console.print("\n[bold]Teams in database:[/bold]")
        for team in teams:
            console.print(f'ID: {team.id} - {team.name} (API ID: {team.api_id})')


if __name__ == "__main__":
    app()












