from sqlmodel import Session, select, or_
from api_request import api_request
from display_utils import print_standings_table
from models import Country, Competition, Venue, Team, Season, Standing, Fixture, FixtureStats, TeamSeasonCompetition

from rich.progress import track
from rich.console import Console
from datetime import datetime
import time

console = Console()

# Fetch Country
def make_country(session: Session, input_country_name: str):
    # Create or get Country
    country_stmt = select(Country).where(Country.country_name == input_country_name)
    country = session.exec(country_stmt).first()
    if not country:
        # Fetch Competitions with Country
        console.print(f'Fetching {input_country_name} competitions data from API.', style="blue")
        # API Request Setup
        url = "https://v3.football.api-sports.io/leagues"
        params = {'country': input_country_name}
        # API Request
        comps_data = api_request(url, params)
        comps = comps_data['response']
        # Process Data
        country_name = comps_data['parameters']['country']
        country = Country(country_name=country_name,
                          num_comps=comps_data['results'],
                          code=comps_data['response'][0]['country']['code'],
                          flag=comps_data['response'][0]['country']['flag'])
        session.add(country)
        session.commit()
        console.print(f'Created new Country: {country_name}.', style="green")
    else:
        console.print(f'Country found in records: {input_country_name}.', style="green")


# Fetch Competitions
def fetch_competitions(session: Session, input_country_name: str):
    # Get Country
    country_stmt = select(Country).where(Country.country_name == input_country_name)
    country = session.exec(country_stmt).first()
    # Fetch Competitions with Country
    console.print(f'Fetching {input_country_name} competitions data from API.', style="blue")
    # API Request Setup
    url = "https://v3.football.api-sports.io/leagues"
    params = {'country': input_country_name}
    # API Request
    comps_data = api_request(url, params)
    comps = comps_data['response']
    new_comps = []
    for comp_entry in track(comps, description="Processing Competitions."):
        # Find or create Competition
        comp_stmt = select(Competition).where(Competition.comp_api_id == comp_entry['league']['id'])
        comp = session.exec(comp_stmt).first()
        if not comp:
            comp = Competition(
                comp_api_id=comp_entry['league']['id'],
                comp_country_id=country.id,
                country_name=country.country_name,
                comp_name=comp_entry['league']['name'],
                comp_type=comp_entry['league']['type'],
                comp_logo=comp_entry['league']['logo']
            )
            new_comps.append(comp)
            console.print(f'Created new Competition: {comp.comp_name}', style="green")
    if new_comps:
        session.add_all(new_comps)
        session.commit()
        console.print(f'Successfully added {len(new_comps)} venues!', style="bold green")
    else:
        console.print(f'No new venues were added!', style="bold red")

    return len(new_comps)


# Fetch Teams
def fetch_teams(session: Session, input_country_name: str):
    # Get Country
    country_stmt = select(Country).where(Country.country_name == input_country_name)
    country = session.exec(country_stmt).first()
    # Fetch Teams with Country
    console.print(f'Fetching {input_country_name} Teams data from API.', style="blue")
    # API Request Setup
    url = "https://v3.football.api-sports.io/teams"
    params = {'country': input_country_name}
    # API Request
    teams_data = api_request(url, params)
    teams_response = teams_data['response']
    # Process each Team in Response
    new_teams = []
    for entry in track(teams_response, description="ProcessingTeams."):
        team_data = entry['team']
        # Find or create Team
        team_stmt = select(Team).where(Team.team_api_id == team_data['id'])
        team = session.exec(team_stmt).first()
        if not team:
            team = Team(
                team_api_id=team_data['id'],
                name=team_data['name'],
                short_name=team_data['code'],
                country=team_data['country'],
                country_id=country.id,
                founded=team_data['founded'],
                national=team_data['national'],
                logo_url=team_data['logo'],
            )
            new_teams.append(team)
            console.print(f'Created new team: {team.name}.', style="green")
    if new_teams:
        session.add_all(new_teams)
        session.commit()
        console.print(f'Successfully added {len(new_teams)} venues!', style="bold green")
    else:
        console.print(f'No new venues were added!', style="bold red")

    return len(new_teams)


# Fetch Venues
def fetch_venues(session: Session, input_country_name: str):
    # Get Country
    country_stmt = select(Country).where(Country.country_name == input_country_name)
    country = session.exec(country_stmt).first()
    # Fetch Venues with Country
    console.print(f'Fetching {input_country_name} Venues data from API.', style="blue")
    # API Request Setup
    url = "https://v3.football.api-sports.io/venues"
    params = {'country': input_country_name}
    # API Request
    venues_data = api_request(url, params)
    venues_response = venues_data['response']
    # Process each Venue in Response
    new_venues = []
    for entry in track(venues_response, description="ProcessingVenues."):
        venue_stmt = select(Venue).where(Venue.venue_api_id == entry['id'])
        venue = session.exec(venue_stmt).first()
        if not venue:
            # Create Venue
            venue = Venue(
                venue_api_id=entry['id'],
                name=entry['name'],
                address=entry['address'],
                city=entry['city'],
                country=entry['country'],
                country_id=country.id,
                capacity=entry['capacity'],
                surface=entry['surface'],
                image=entry['image']
            )
            new_venues.append(venue)
            console.print(f'Created new venue: {venue.name}.', style="green")
    if new_venues:
        session.add_all(new_venues)
        session.commit()
        console.print(f'Successfully added {len(new_venues)} venues!', style="bold green")
    else:
        console.print(f'No new venues were added!', style="bold red")

    return len(new_venues)


# Make Season
def make_season(session: Session, competition_name: str, year: int):
    # Find Competition
    competition_stmt = select(Competition).where(Competition.comp_name == competition_name)
    competition = session.exec(competition_stmt).first()
    if not competition:
        raise ValueError(f'{competition_name} not found.')
    # Find Season ID
    season_stmt = select(Season).where(
        (Season.league_id == competition.comp_api_id) & (Season.year == year)
    )
    season = session.exec(season_stmt).first()
    if not season:
        season = Season(year=year, league_id=competition.comp_api_id)
        session.add(season)
        session.commit()
        session.refresh(season)
        console.print(f'Created new season. {year} {competition_name} (Competition ID: {competition.comp_api_id}).',
                      style="green")
    else:
        console.print(f'Found season for {year} {competition_name} (Competition ID: {competition.comp_api_id}).',
                      style="green")

    return season, competition



# Fetch Standings
def fetch_standings(session: Session, season: Season, competition: Competition):
    console.print(f'Fetching standings data for {season.year} {competition.comp_name} (Competition ID: {competition.comp_api_id}) season.',
                  style="blue")
    # API Request Setup
    url = "https://v3.football.api-sports.io/standings"
    params = {'league': competition.comp_api_id, 'season': season.year}
    # API Request
    standings_data = api_request(url, params)
    standings_response = standings_data['response'][0]['league']['standings'][0]
    # Process each Standing in Response
    new_standings = []
    for team_entry in track(standings_response, description="Processing teams."):
        team_info = team_entry['team']
        stats = team_entry['all']
        home_stats = team_entry['home']
        away_stats = team_entry['away']
        # Find or create the Standing
        standing_stmt = select(Standing).where((Standing.team_id == team_info['id']) & (Standing.season_id == season.id))
        standing = session.exec(standing_stmt).first()
        if not standing:
            # Create standings entry
            standing = Standing(
                team_id=team_info['id'],
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
            new_standings.append(standing)

    if new_standings:
        session.add_all(new_standings)
        session.commit()
        console.print(f'New standings were added!', style="bold green")
    else:
        console.print(f'No new standings were added!', style="bold red")

    # Print Standings table
    console.print(f'Displaying standings for {season.year} season.', style="bold green")
    print_standings_table(session, competition.comp_name, season.year)


# Fetch Fixtures
def fetch_fixtures(session: Session, season: Season, competition: Competition):
    console.print(f'Fetching fixture data for {season.year} season with league ID {competition.comp_api_id}.',
                  style="blue")
    # API Request Setup
    url = "https://v3.football.api-sports.io/fixtures"
    params = {'league': competition.comp_api_id, 'season': season.year}
    # API Request
    fixture_data = api_request(url, params)
    fixtures_response = fixture_data['response']
    # Process each Fixture in Response
    new_fixtures = []
    for entry in track(fixtures_response, description="Processing Fixtures."):
        fixture_id = entry['fixture']['id']
        fixture_data = entry['fixture']
        # Find or create the Fixture
        fixture_stmt = select(Fixture).where(Fixture.id == fixture_id)
        fixture = session.exec(fixture_stmt).first()
        if not fixture:
            # Create fixture entry
            fixture = Fixture(
                id=fixture_id,
                season_id=season.id,
                home_team_id=entry['teams']['home']['id'],
                away_team_id=entry['teams']['away']['id'],
                venue_id=entry['fixture']['venue']['id'],
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
        new_fixtures.append(fixture)
    if new_fixtures:
        session.add_all(new_fixtures)
        session.commit()
        console.print(f'{len(new_fixtures)} new fixtures were added!', style="bold green")
    else:
        console.print(f'No new fixtures were added!', style="bold red")


# Make MetaData join table
def make_meta_join_table(session: Session, season: Season):
    # Find Fixtures
    fixtures_stmt = select(Fixture).where(Fixture.season_id == season.id)
    fixtures = session.exec(fixtures_stmt).all()
    home_venue = []
    for fixture in fixtures:
        home_venue.append((
            fixture.home_team_id,
            fixture.venue_id
        ))
    unique_home_venue = set(home_venue)
    new_meta_entries = []
    for pair in unique_home_venue:
        # Find or Make Meta Instance
        meta_instance_stmt = select(TeamSeasonCompetition).where(
            (TeamSeasonCompetition.season_id == season.id) & (TeamSeasonCompetition.team_id == pair[0])
        )
        meta_instance = session.exec(meta_instance_stmt).first()
        if not meta_instance:
            meta_instance = TeamSeasonCompetition(
                team_id=pair[0],
                season_id=season.id,
                competition_id=season.league_id,
                venue_id=pair[1]
            )
            new_meta_entries.append(meta_instance)
            console.print(f'Created new meta instance: {pair}.', style="green")
    if new_meta_entries:
        session.add_all(new_meta_entries)
        session.commit()
        console.print(f'Successfully added {len(new_meta_entries)} meta instances!', style="bold green")
    else:
        console.print(f'No new meta instances were added!', style="bold red")

# Safely Pull Fixture Statistics
def safe_stats(stats, index):
    try:
        return stats['statistics'][index]['value']
    except (IndexError, KeyError, TypeError):
        return None

# Parse Safely Pulled Fixture Statistics
def parse_stats(stats: dict) -> dict:
    values = [safe_stats(stats, i) for i in range(17)]
    return dict(
        sh_on_goal=values[0],
        sh_off_goal=values[1],
        total_sh=values[2],
        blocked_sh=values[3],
        sh_inside=values[4],
        sh_outside=values[5],
        fouls=values[6],
        corners=values[7],
        offsides=values[8],
        possession=values[9],
        yellows=values[10],
        reds=values[11],
        saves=values[12],
        tot_passes=values[13],
        accurate_pass=values[14],
        percent_pass=values[15],
        ex_goals=values[16]
    )
# Fetch Fixture Statistics for one Team for all Competitions in a Year
def fetch_fixture_stats_team(session: Session, year: int, team_name: str):
    # Find Team ID
    team_stmt = select(Team).where(Team.name == team_name)
    team = session.exec(team_stmt).first()
    if not team:
        raise ValueError(f'Could not find Team: {team_name}')
    # Find Season ID
    season_stmt = (select(TeamSeasonCompetition, Season)
                   .where((Season.year == year) & (TeamSeasonCompetition.team_id == team.team_api_id))
                   .join(Season, TeamSeasonCompetition.season_id == Season.id))
    seasons = session.exec(season_stmt).all()
    if not seasons:
        raise ValueError(f'Could not find Season for: {year}')
    for comp, season in seasons:
        # Pull Fixtures list for Team and Season
        fixtures_stmt = select(Fixture).where(
            (Fixture.season_id == comp.season_id) &
            or_(
                Fixture.home_team_id == team.team_api_id,
                Fixture.away_team_id == team.team_api_id
            )
        )
        fixtures = session.exec(fixtures_stmt).all()
        if not fixtures:
            raise ValueError(f'Could not find Fixtures for: {team_name} with Season ID: {comp.season_id}')
        # Iterate through Fixture IDs
        new_fix_stats = []
        for fixture in fixtures:
            fix_stats_stmt = select(FixtureStats).where(FixtureStats.fixture_id == fixture.id)
            fix_stats = session.exec(fix_stats_stmt).first()
            if not fix_stats:
                # Fetch Fixture Stats
                time.sleep(8)
                # API Request Setup
                url = "https://v3.football.api-sports.io/fixtures/statistics"
                params = {'fixture': fixture.id}
                # API Request
                fix_stats_data = api_request(url, params)
                # Parse Statistics
                home_stats = fix_stats_data['response'][0]
                away_stats = fix_stats_data['response'][1]
                home = parse_stats(home_stats)
                away = parse_stats(away_stats)
                fixture_instance = FixtureStats(
                    fixture_id=fix_stats_data['parameters']['fixture'],
                    home_team_id=home_stats['team']['id'],
                    **{f"home_{k}": v for k, v in home.items()},
                    away_team_id=away_stats['team']['id'],
                    **{f"away_{k}": v for k, v in away.items()}
                )
                new_fix_stats.append(fixture_instance)
                if len(new_fix_stats) > 1:
                    break
        if new_fix_stats:
            session.add_all(new_fix_stats)
            session.commit()
            console.print(f'{len(new_fix_stats)} new fixture statistics were added!', style="bold green")
        else:
            console.print(f'No new fixture statistics were added!', style="bold red")


def fetch_fixture_stats_team_season(session: Session, year: int, team_name: str, competition_name: str):
    # Find League ID
    competition_stmt = select(Competition).where(Competition.comp_name == competition_name)
    competition = session.exec(competition_stmt).first()
    if not competition:
        raise ValueError(f'Could not find Competition: {competition_name}')
    # Find Season ID
    season_stmt = select(Season).where(
        (Season.league_id == competition.comp_api_id) & (Season.year == year)
    )
    season = session.exec(season_stmt).first()
    if not season:
        raise ValueError(f'Could not find Season for: {year} {competition_name}')
    # Find Team ID
    team_stmt = select(Team).where(Team.name == team_name)
    team = session.exec(team_stmt).first()
    if not team:
        raise ValueError(f'Could not find Team: {team_name}')
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
        raise ValueError(f'Could not find Fixtures for: {team_name} from {year} {competition_name}')
    # Iterate through Fixture IDs
    new_fix_stats = []
    for fixture in fixtures:
        fix_stats_stmt = select(FixtureStats).where(FixtureStats.fixture_id == fixture.id)
        fix_stats = session.exec(fix_stats_stmt).first()
        if not fix_stats:
            # Fetch Fixture Stats
            time.sleep(8)
            # API Request Setup
            url = "https://v3.football.api-sports.io/fixtures/statistics"
            params = {'fixture': fixture.id}
            # API Request
            fix_stats_data = api_request(url, params)
            # Parse Statistics
            home_stats = fix_stats_data['response'][0]
            away_stats = fix_stats_data['response'][1]
            home = parse_stats(home_stats)
            away = parse_stats(away_stats)
            fixture_instance = FixtureStats(
                fixture_id=fix_stats_data['parameters']['fixture'],
                home_team_id=home_stats['team']['id'],
                **{f"home_{k}": v for k, v in home.items()},
                away_team_id=away_stats['team']['id'],
                **{f"away_{k}": v for k, v in away.items()}
            )
            new_fix_stats.append(fixture_instance)
            if len(new_fix_stats) > 1:
                break
    if new_fix_stats:
        session.add_all(new_fix_stats)
        session.commit()
        console.print(f'{len(new_fix_stats)} new fixture statistics were added!', style="bold green")
    else:
        console.print(f'No new fixture statistics were added!', style="bold red")


