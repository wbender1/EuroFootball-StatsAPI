# Import libraries
from typing import Optional

import typer
from sqlmodel import Session, select, delete, SQLModel, or_, and_
import requests, json
from rich.console import Console
from rich.progress import track
from datetime import datetime
import time

# Import modules
from models import Country, Competition, Venue, Team, Season, Standing, Fixture, FixtureStats
# Import print functions
from display_utils import (print_comps, print_country_type_comps, print_type_comps, print_countries, print_fixtures,
                           print_team_fixtures, print_fixture_stats, print_seasons, print_comp_seasons, print_country_seasons,
                           print_year_seasons, print_year_country_seasons, print_standings_table, print_teams,
                           print_comp_teams, print_venues, print_country_venues, print_comp_venues)
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


#**********************************     Fetch Data Functions    *************************************#
# Fetch Competitions and Create Country
@app.command()
def fetch_competitions(input_country_name: str):
    # Fetch Country and Competitions
    console.print(f'Fetching {input_country_name} competitions data from API.', style="blue")
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
    # Process Data
    with Session(engine) as session:
        # Create or get Country
        country_stmt = select(Country).where(
            Country.country_name == input_country_name
        )
        country = session.exec(country_stmt).first()
        country_name = comps_data['parameters']['country']
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
        else:
            console.print(f'Country found in records: {country_name}.', style="green")
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
        # Print Console Output
        if num_comps_added > 0:
            console.print(f'Successfully added {num_comps_added} competitions for {country_name}!', style="bold green")
        else:
            console.print(f'No new competitions added for {country_name}!', style="bold green")


# Fetch Venues and Teams while Creating Season
@app.command()
def fetch_teams(competition_name: str, year: int):
    with Session(engine) as session:
        # Find League ID
        competition_stmt = select(Competition).where(Competition.comp_name == competition_name)
        competition = session.exec(competition_stmt).first()
        if not competition:
            console.print(f'{competition_name} competition not found.', style="yellow")
            return
        else:
            league_id = competition.comp_api_id
        # Fetch Teams and Venues
        console.print(f'Fetching teams & venue data for {year} {competition_name} (Competition ID: {league_id}) season.', style="blue")
        # API Request Setup
        teams_url = "https://v3.football.api-sports.io/teams"
        headers = {
            'x-rapidapi-key': config.API_KEY,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
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
        # Process Data
        # Create or get season
        season_stmt = select(Season).where(
            (Season.year == year) & (Season.league_id == league_id)
        )
        season = session.exec(season_stmt).first()
        if not season:
            season = Season(year=year, league_id=league_id, total_teams=0)
            session.add(season)
            session.commit()
            session.refresh(season)
            console.print(f'Created new season. {year} {competition_name} (Competition ID: {league_id}).', style="green")
        else:
            if season.total_teams > 0:
                console.print(f'Found season in records. {year} {competition_name} (Competition ID: {league_id}). Contains {season.total_teams} Teams',
                    style="green")
                console.print(f'No teams will be added... ending program', style="green")
                return
            else:
                console.print(f'Found season in records. {year} {competition_name} (Competition ID: {league_id}). Contains 0 Teams',
                              style="green")
        # Process each Venue and Team in Response
        teams_response = teams_data['response']
        teams_added = 0
        for entry in track(teams_response, description="Processing Venues and Teams."):
            venue_data = entry['venue']
            team_data = entry['team']
            venue_stmt = select(Venue).where(Venue.venue_api_id == venue_data['id'])
            venue = session.exec(venue_stmt).first()
            if not venue:
                # Check negative venue
                neg_venue_id = -1 * team_data['id']
                venue_stmt = select(Venue).where(Venue.venue_api_id == neg_venue_id)
                venue_check = session.exec(venue_stmt).first()
                if venue_check:
                    continue
                # Create Venue
                if venue_data['id'] == None:
                    venue = Venue(
                        venue_api_id= -1 * team_data['id'],
                        name=None,
                        address=None,
                        city=None,
                        capacity=None,
                        surface=None,
                        image=None
                    )
                    session.add(venue)
                    session.flush()
                else:
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
                )
                session.add(team)
                teams_added += 1
                session.commit()
                console.print(f'Created new team: {team.name}. Venue: {venue.name}', style="green")
            season.total_teams += 1
            session.commit()
        if teams_added > 0:
            console.print(f'Successfully added {teams_added} teams and venues!', style="bold green")
        else:
            console.print(f'No new teams or venues were added to {year} with League ID: {league_id}!',
                          style="bold green")
            console.print(f'There are {season.total_teams} in year {year} with League ID: {league_id}!',
                          style="bold green")


# Fetch Standings for a Season
@app.command()
def fetch_standings(competition_name: str, year: int):
    with Session(engine) as session:
        # Find League ID
        competition_stmt = select(Competition).where(Competition.comp_name == competition_name)
        competition = session.exec(competition_stmt).first()
        if not competition:
            console.print(f'{competition_name} competition not found.', style="yellow")
            return
        else:
            league_id = competition.comp_api_id
        # Find Season ID
        season_stmt = select(Season).where(
            (Season.league_id == league_id) & (Season.year == year)
        )
        season = session.exec(season_stmt).first()
        if not season:
            console.print(f'There is no season in database for the {year} {competition_name} (Competition ID: {league_id}) season.',
                          style="yellow")
            console.print('Please add the required season & teams before adding standings data.',
                          style="yellow")
            return
    # Fetch Standings if league
        if competition.comp_type == 'League':
            console.print(f'Fetching standings data for {year} {competition_name} (Competition ID: {league_id}) season.', style="blue")
            # Api Request Setup
            standings_url = "https://v3.football.api-sports.io/standings"
            headers = {
                'x-rapidapi-key': config.API_KEY,
                'x-rapidapi-host': 'v3.football.api-sports.io'
            }
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
            # Checks Standings records
            standings_query = select(Standing).where(
                Standing.season_id == season.id
            )
            existing_standings = session.exec(standings_query).all()
            num_standings = len(existing_standings)
            if num_standings == 20:
                console.print(f'{year} {competition_name} (Competition ID: {league_id}) season already has full standings records. Skipping and ending program.',
                              style="yellow")
                return
            else:
                console.print(
                    f'Found {num_standings} standings records. Proceeding to clear season standings and add fresh records.',
                    style="yellow")
                delete_stmt = delete(Standing).where(Standing.season_id == season.id)
                session.exec(delete_stmt)
                console.print(f'Deleted existing standings for {season.year}.', style="yellow")
            # Process Data
            standings_response = standings_data['response'][0]['league']['standings'][0]
            num_standings_entries_added = 0
            # Process each team in standings
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
            console.print(f'Successfully added {num_standings_entries_added} standings entries for {year} {competition_name} (Competition ID: {league_id}) season!',
                      style="bold green")
            # Print Standings table
            console.print(f'Displaying standings for {year} season.', style="bold green")
            print_standings_table(session, competition_name, year)
        else:
            console.print(f'The {year} {competition_name} (Competition ID: {league_id}) season belongs to a cup competition which does not have standings records.',
                          style="bold green")


# Fetch Fixtures
@app.command()
def fetch_fixtures(competition_name: str, year: int):
    with Session(engine) as session:
        # Find League ID
        competition_stmt = select(Competition).where(Competition.comp_name == competition_name)
        competition = session.exec(competition_stmt).first()
        if not competition:
            console.print(f'{competition_name} competition not found.', style="yellow")
            return
        else:
            league_id = competition.comp_api_id
        # Find Season ID
        season_stmt = select(Season).where(
            (Season.league_id == league_id) & (Season.year == year)
        )
        season = session.exec(season_stmt).first()
        if not season:
            console.print(f'There is no season in database for the {year} {competition_name} (Competition ID: {league_id}) season.',
                          style="yellow")
            console.print('Please add the required season & teams before adding standings data.',
                          style="yellow")
            return
    # Fetch Fixtures
    console.print(f'Fetching fixture data for {year} season with league ID {league_id}.', style="blue")
    # Api Request Setup
    standings_url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        'x-rapidapi-key': config.API_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    params = {'league': league_id,
              'season': year}
    # Try API Request and use error handling
    try:
        response = requests.get(standings_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        console.print(f'API Request failed: {e}', style="red")
        return
    if data.get('results', 0) == 0:
        console.print("No data returned from API.", style="red")
        console.print(data['errors'])
        return
    # Process Data
    # Write to file
    with open('output.json', 'w') as f:
        json.dump(data, f, indent=4)
    fixture_data = data['response']
    num_comps_added = 0
    num_fixtures_added = 0
    for entry in track(fixture_data, description="Processing Fixtures."):
        fixture_id = entry['fixture']['id']
        fixture_data = entry['fixture']
        venue_stmt = select(Venue).where(Venue.venue_api_id == fixture_data['venue']['id'])
        venue = session.exec(venue_stmt).first()
        if not venue:
            # Check negative venue
            neg_venue_id = -1 * entry['teams']['home']['id']
            venue_stmt = select(Venue).where(Venue.venue_api_id == neg_venue_id)
            venue_check = session.exec(venue_stmt).first()
            if venue_check:
                continue
            # Create Venue
            if fixture_data['venue']['id'] is None:
                venue = Venue(
                    venue_api_id= -1 * entry['teams']['home']['id'],
                    name=None,
                    address=None,
                    city=None,
                    capacity=None,
                    surface=None,
                    image=None
                )
                session.add(venue)
                session.commit()
            else:
                venue = Venue(
                    venue_api_id=fixture_data['venue']['id'],
                    name=fixture_data['venue']['name'],
                    address=None,
                    city=fixture_data['venue']['city'],
                    capacity=None,
                    surface=None,
                    image=None
                )
                session.add(venue)
                session.commit()
        # Find or create Fixture
        fixture_stmt = select(Fixture).where(Fixture.id == fixture_id)
        fixture = session.exec(fixture_stmt).first()
        if not fixture:
            fixture = Fixture(
                id=fixture_id,
                season_id=season.id,
                home_team_id=entry['teams']['home']['id'],
                away_team_id=entry['teams']['away']['id'],
                venue_id=venue.venue_api_id,
                competition_id=competition.comp_api_id,
                referee=fixture_data['referee'],
                date=datetime.fromisoformat(fixture_data['date']),
                short_status=fixture_data['status']['short'],
                elapsed=fixture_data['status']['elapsed'],
                round=entry['league']['round'],
                home_goals=entry['goals']['home'],
                away_goals=entry['goals']['away'],
                half_home_goals=entry['score']['halftime']['home'],
                half_away_goals=entry['score']['halftime']['away'],
                full_home_goals=entry['score']['fulltime']['home'],
                full_away_goals=entry['score']['fulltime']['away'],
                et_home_goals=entry['score']['extratime']['home'],
                et_away_goals=entry['score']['extratime']['away'],
                pen_home_goals=entry['score']['penalty']['home'],
                pen_away_goals=entry['score']['penalty']['away']
            )
            num_fixtures_added += 1
            session.add(fixture)
            session.commit()
            session.refresh(fixture)
            console.print(f'Created new Fixture: {entry['teams']['home']['name']} vs. {entry['teams']['away']['name']}',
                          style="green")
    if num_fixtures_added > 0:
        console.print(f'Successfully added {num_fixtures_added} fixtures for {year} {competition_name} (Competition ID: {league_id}) season!',
                      style="bold green")
    else:
        console.print(f'No new fixtures added for {year} {year} {competition_name} (Competition ID: {league_id}) season!', style="bold green")
    print_fixtures(session, competition_name, year)


# Fetch Fixture Stats for a Season for one Team
@app.command()
def fetch_fixture_stats(competition_name: str, year: int, team_name: str):
    with Session(engine) as session:
        # Find League ID
        competition_stmt = select(Competition).where(Competition.comp_name == competition_name)
        competition = session.exec(competition_stmt).first()
        if not competition:
            console.print(f'{competition_name} competition not found.', style="yellow")
            return
        else:
            league_id = competition.comp_api_id
        # Find Season ID
        season_stmt = select(Season).where(
            (Season.league_id == league_id) & (Season.year == year)
        )
        season = session.exec(season_stmt).first()
        if not season:
            console.print(
                f'There is no season in database for the {year} {competition_name} (Competition ID: {league_id}) season.',
                style="yellow")
            console.print('Please add the required season & teams before adding standings data.',
                          style="yellow")
            return
        # Find Team ID
        team_stmt = select(Team).where(Team.name == team_name)
        team = session.exec(team_stmt).first()
        # Pull Fixtures list for Team and Season
        fixtures_stmt = select(Fixture).where(
            (Fixture.season_id == season.id) &
            or_(
                Fixture.home_team_id == team.team_api_id,
                Fixture.away_team_id == team.team_api_id
            )
        )
        fixtures = session.exec(fixtures_stmt).all()
        if not fixtures:
            console.print(
                f'There are no fixtures found for the {year} {competition_name} (Competition ID: {league_id}) season.',
                style="yellow")
            return
        fixtures_added = 0
        # Iterate through Fixture IDs
        for fixture in fixtures:
            fix_stats_stmt = select(FixtureStats).where(FixtureStats.fixture_id == fixture.id)
            fix_stats = session.exec(fix_stats_stmt).first()
            if not fix_stats:
                # Fetch Fixture Stats
                time.sleep(8)
                console.print(f'Fetching fixture statistics for Fixture with ID: {fixture.id}.',
                              style="blue")
                # Api Request Setup
                standings_url = "https://v3.football.api-sports.io/fixtures/statistics"
                headers = {
                    'x-rapidapi-key': config.API_KEY,
                    'x-rapidapi-host': 'v3.football.api-sports.io'
                }
                params = {'fixture': fixture.id}
                # Try API Request and use error handling
                try:
                    response = requests.get(standings_url, headers=headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                except requests.exceptions.RequestException as e:
                    console.print(f'API Request failed: {e}', style="red")
                    return
                if data.get('results', 0) == 0:
                    console.print("No data returned from API.", style="red")
                    console.print(data['errors'])
                    return
                # Add Home Team Stats
                home_stats = data['response'][0]
                # Add Away Team Stats
                away_stats = data['response'][1]
                fixture_instance = FixtureStats(
                    fixture_id=data['parameters']['fixture'],
                    home_team_id=home_stats['team']['id'],
                    home_sh_on_goal=home_stats['statistics'][0]['value'],
                    home_sh_off_goal=home_stats['statistics'][1]['value'],
                    home_total_sh=home_stats['statistics'][2]['value'],
                    home_blocked_sh=home_stats['statistics'][3]['value'],
                    home_sh_inside=home_stats['statistics'][4]['value'],
                    home_sh_outside=home_stats['statistics'][5]['value'],
                    home_fouls=home_stats['statistics'][6]['value'],
                    home_corners=home_stats['statistics'][7]['value'],
                    home_offsides=home_stats['statistics'][8]['value'],
                    home_possession=home_stats['statistics'][9]['value'],
                    home_yellows=home_stats['statistics'][10]['value'],
                    home_reds=home_stats['statistics'][11]['value'],
                    home_saves=home_stats['statistics'][12]['value'],
                    home_tot_passes=home_stats['statistics'][13]['value'],
                    home_accurate_pass=home_stats['statistics'][14]['value'],
                    home_percent_pass=home_stats['statistics'][15]['value'],
                    home_ex_goals= None,
                    away_team_id=away_stats['team']['id'],
                    away_sh_on_goal=away_stats['statistics'][0]['value'],
                    away_sh_off_goal=away_stats['statistics'][1]['value'],
                    away_total_sh=away_stats['statistics'][2]['value'],
                    away_blocked_sh=away_stats['statistics'][3]['value'],
                    away_sh_inside=away_stats['statistics'][4]['value'],
                    away_sh_outside=away_stats['statistics'][5]['value'],
                    away_fouls=away_stats['statistics'][6]['value'],
                    away_corners=away_stats['statistics'][7]['value'],
                    away_offsides=away_stats['statistics'][8]['value'],
                    away_possession=away_stats['statistics'][9]['value'],
                    away_yellows=away_stats['statistics'][10]['value'],
                    away_reds=away_stats['statistics'][11]['value'],
                    away_saves=away_stats['statistics'][12]['value'],
                    away_tot_passes=away_stats['statistics'][13]['value'],
                    away_accurate_pass=away_stats['statistics'][14]['value'],
                    away_percent_pass=away_stats['statistics'][15]['value'],
                    away_ex_goals=None
                )
                if len(home_stats['statistics']) == 17:
                    fixture_instance.home_ex_goals = home_stats['statistics'][16]['value']
                    fixture_instance.away_ex_goals = away_stats['statistics'][16]['value']
                session.add(fixture_instance)
                session.commit()
                fixtures_added += 1
                console.print(
                    f'Created new Fixture Statistics: {home_stats['team']['name']} vs. {away_stats['team']['name']}',
                    style="green")
        if fixtures_added > 0:
            console.print(f'Successfully added Statistics for {fixtures_added} fixtures for {year} {competition_name} (Competition ID: {league_id}) season!',
                        style="bold green")
        else:
            console.print(f'No new fixture statistics added for {year} {competition_name} (Competition ID: {league_id}) season.', style="bold green")



# Fetch Season
@app.command()
def fetch_season(input_country_name: str, competition_name: str, year: int):
    fetch_competitions(input_country_name)
    fetch_teams(competition_name, year)
    fetch_standings(competition_name, year)
    fetch_fixtures(competition_name, year)

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