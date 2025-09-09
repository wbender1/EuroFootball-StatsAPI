# Import libraries
import typer
from sqlmodel import Session, select, delete, SQLModel
import requests
from rich.console import Console
from rich.progress import track
from tabulate import tabulate

# Import modules
from models import Country, Competition, Venue, Team, Season, Standing
from database import engine
import config

# Create Typer app and console
app = typer.Typer()
console = Console()

# Initialize Database
@app.command()
def init_db():
    SQLModel.metadata.create_all(engine)
    console.print("Database tables created!", style="green")

# Fetch the Competitions for a Country and add the Teams, Venues, and Standings for 1 Season
@app.command()
def fetch_season(input_country_name: str, league_id: int, year: int):

    # Fetch Country and Competitions first
    console.print(f'Fetching {input_country_name} competitions.', style="blue")
    # API Request Setup
    comps_url = "https://v3.football.api-sports.io/leagues"
    headers = {
        'x-rapidapi-key': config.API_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    comps_params = {'country': input_country_name}
    # Try API Request and user error handling
    try:
        response = requests.get(comps_url, headers=headers, params=comps_params)
        response.raise_for_status()
        comps_data = response.json()
    except requests.exceptions.RequestException as e:
        console.print(f'API Request failed: {e}', style="red")
        return
    if comps_data.get('results', 0) == 0:
        console.print('No data returned from API.', style="red")
        console.print(comps_data['error'])
        return


    # Fetch Teams and Venues second
    console.print(f'Fetching teams for {year} season with league ID {league_id}.', style="blue")
    # API Request Setup
    teams_url = "https://v3.football.api-sports.io/teams"
    params = {'league': league_id,
              'season': year}
    # Try API Request and user error handling
    try:
        response = requests.get(teams_url, headers=headers, params=params)
        response.raise_for_status()
        teams_data = response.json()
    except requests.exceptions.RequestException as e:
        console.print(f'API Request failed: {e}', style="red")
        return
    if teams_data.get('results', 0) == 0:
        console.print('No data returned from API.', style="red")
        console.print(teams_data['error'])
        return


    # Fetch Standings last
    console.print(f'Fetching {year} season for league ID {league_id}.', style="blue")
    # Api Request Setup
    standings_url = "https://v3.football.api-sports.io/standings"
    params = {'league': league_id,
              'season': year}
    # Try API Request and use error handling
    try:
        response = requests.get(standings_url, headers=headers, params=params)
        response.raise_for_status()
        standings_data = response.json()
    except requests.exceptions.RequestException as e:
        console.print(f'API Request failed: {e}', style="red")
        return
    if standings_data.get('results', 0) == 0:
        console.print("No data returned from API.", style="red")
        console.print(standings_data['errors'])
        return


    # Process Data
    with Session(engine) as session:

        # Create or get Country
        country_name = comps_data['parameters']['country']
        country_stmt = select(Country).where(
            Country.country_name == input_country_name
        )
        country = session.exec(country_stmt).first()
        if not country:
            country_data = comps_data['response'][0]['country']
            country = Country(country_name=country_name,
                              num_comps=comps_data['results'],
                              code=country_data['code'],
                              flag=country_data['flag'])
            session.add(country)
            session.commit()
            session.refresh(country)
            console.print(f'Created new Country: {country_name}.', style="green")

        # Process each Competition in Country
        comps = comps_data['response']
        num_comps_added = 0
        for comp_entry in track(comps, description="Processing Competitions."):
            comp_id = comp_entry['league']['id']
            # Find or create Competition
            comp_stmt = select(Competition).where(Competition.comp_api_id == comp_id)
            comp = session.exec(comp_stmt).first()
            if not comp:
                comp = Competition(
                    comp_api_id=comp_id,
                    comp_country_id=country.id,
                    comp_name=comp_entry['league']['name'],
                    comp_type=comp_entry['league']['type'],
                    comp_logo=comp_entry['league']['logo']
                )
                num_comps_added += 1
                session.add(comp)
                session.commit()
                session.refresh(comp)
                console.print(f'Created new Competition: {comp.comp_name}', style="green")

        console.print(f'Successfully added {num_comps_added} competitions for {country_name}!', style="bold green")

        # Create or get season
        season_stmt = select(Season).where(
            (Season.year == year) & (Season.league_id == league_id)
        )
        season = session.exec(season_stmt).first()
        if not season:
            season = Season(year=year, league_id=league_id)
            session.add(season)
            session.commit()
            session.refresh(season)
            console.print(f'Created new season. League ID: {league_id}. Year: {year}', style="green")
        else:
            console.print(f'Found season in records. League ID: {league_id}. Year: {year}', style="green")
            standings_query = select(Standing).where(
                Standing.season_id == season.id
            )
            existing_standings = session.exec(standings_query).all()
            num_standings = len(existing_standings)
            if num_standings == 20:
                console.print(f'Season already has full standings records. Skipping and ending program.', style="yellow")
                return
            else:
                console.print(f'Found {num_standings} standings records. Proceeding to clear season standings and add fresh records.', style="yellow")
                delete_stmt = delete(Standing).where(Standing.season_id == season.id)
                session.exec(delete_stmt)
                console.print(f'Deleted existing standings for {season.year}.', style="yellow")

        # Process each Venue and Team in Response
        teams_response = teams_data['response']
        num_venues_added = 0
        for entry in track(teams_response, description="Processing Venues and Teams."):
            venue_data = entry['venue']
            team_data = entry['team']
            venue_stmt = select(Venue).where(Venue.venue_api_id == venue_data['id'])
            venue = session.exec(venue_stmt).first()
            if not venue:
                # Create Venue
                venue = Venue(
                    venue_api_id=venue_data['id'],
                    name=venue_data['name'],
                    address=venue_data['address'],
                    city=venue_data['city'],
                    capacity=venue_data['capacity'],
                    surface=venue_data['surface'],
                    image=venue_data['image']
                )
                session.add(venue)
                session.flush()
                # Create Team
                team = Team(
                    team_api_id=team_data['id'],
                    name=team_data['name'],
                    short_name=team_data['code'],
                    country=team_data['country'],
                    founded=team_data['founded'],
                    national=team_data['national'],
                    logo_url=team_data['logo'],
                    venue_id=venue.venue_api_id
                )
                session.add(team)
                session.commit()
                num_venues_added += 1
                console.print(f'Created new team: {team.name}. Venue: {venue.name}', style="green")

        console.print(f'Successfully added {num_venues_added} teams and venues!', style="bold green")

        # Process each team in standings
        standings_response = standings_data['response'][0]['league']['standings'][0]
        num_standings_entries_added = 0
        for team_entry in track(standings_response, description="Processing teams."):
            team_info = team_entry['team']
            stats = team_entry['all']
            home_stats = team_entry['home']
            away_stats = team_entry['away']

            # Find or create the team
            team_stmt = select(Team).where(Team.team_api_id == team_info['id'])
            team = session.exec(team_stmt).first()

            # Create standings entry
            standing = Standing(
                team_id=team.team_api_id,
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
            num_standings_entries_added += 1

        session.commit()
        console.print(f'Successfully added {num_standings_entries_added} standings entries for {year} season!', style="bold green")


# Run App
if __name__ == "__main__":
    app()