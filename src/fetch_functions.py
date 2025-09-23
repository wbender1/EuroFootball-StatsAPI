from sqlmodel import Session, select
from api_request import api_request
from models import Country, Competition, Venue, Team

from rich.progress import track
from rich.console import Console

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
    num_comps_added = 0
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
    teams_added = 0
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


# Fetch Standings



# Fetch Fixtures



# Fetch Fixture Statistics


