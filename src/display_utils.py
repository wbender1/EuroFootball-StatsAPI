# Import libraries
from sqlmodel import Session, select, or_, and_
from rich.console import Console
from tabulate import tabulate
from sqlalchemy.orm import aliased

# Import Models
from models import Competition, Country, Fixture, FixtureStats, Season, Standing, Team,  Venue

# Create console
console = Console()

#**********************************     Competitions    *************************************#

# Display all Competitions for a Country
def print_comps(session: Session, country_name):
    # Find Country
    country_stmt = select(Country).where(Country.country_name == country_name)
    country = session.exec(country_stmt).first()
    if not country:
        raise ValueError(f'Country: {country_name} not found.')
    # Find Competitions
    comps_stmt = (
        select(Competition).where(Competition.comp_country_id == country.id)
        .order_by(Competition.comp_type.desc())
        .order_by(Competition.comp_name))
    competitions = session.exec(comps_stmt).all()
    if not competitions:
        raise ValueError(f'No Competitions found for {country.country_name}.')
    # Print Table
    data = []
    for comp in competitions:
        data.append([
            comp.comp_name,
            comp.comp_type,
            comp.comp_logo
        ])
    headers = [
        "Name", "Type", "Logo"
    ]

    console.print(f"\n[bold] All[/bold] [bold]Competitions for[/bold] [green]{country.country_name}")
    print(tabulate(data, headers=headers, tablefmt="pretty"))

# Display all League or Cup Competitions for a Country
def print_country_type_comps(session: Session, country_name, comp_type):
    # Find Country
    country_stmt = select(Country).where(Country.country_name == country_name)
    country = session.exec(country_stmt).first()
    if not country:
        raise ValueError(f'Country: {country_name} not found.')
    # Find Competitions
    comps_stmt = select(Competition).where(
        (Competition.comp_country_id == country.id) & (Competition.comp_type == comp_type)).order_by(Competition.comp_name)
    competitions = session.exec(comps_stmt).all()
    if not competitions:
        raise ValueError(f'No {comp_type} Competitions found for {country.country_name}.')
    # Print Table
    data = []
    for comp in competitions:
        data.append([
            comp.comp_name,
            comp.comp_logo
        ])
    headers = [
        "Name", "Logo"
    ]

    console.print(f"\n[bold] All[/bold] [green]{comp_type}[/green] [bold]Competitions for[/bold] [green]{country.country_name}")
    print(tabulate(data, headers=headers, tablefmt="pretty"))

# Display all League or Cup Competitions for all Countries
def print_type_comps(session: Session, comp_type):
    # Find Competitions
    comps_stmt = (
        select(Competition, Country).where(Competition.comp_type == comp_type)
        .join(Country, Country.id == Competition.comp_country_id)
        .order_by(Country.country_name)
        .order_by(Competition.comp_name))
    competitions = session.exec(comps_stmt).all()
    if not competitions:
        raise ValueError(f'No {comp_type} Competitions found.')
    # Print Table
    data = []
    for comp, country in competitions:
        data.append([
            comp.comp_name,
            country.country_name,
            comp.comp_logo
        ])
    headers = [
        "Name", "Country", "Logo"
    ]

    console.print(f"\n[green]{comp_type}[/green] [bold]Competitions for all Countries")
    print(tabulate(data, headers=headers, tablefmt="pretty"))


#**********************************     Countries       *************************************#

# Display all Countries
def print_countries(session: Session):
    # Find Countries
    countries_stmt = select(Country).order_by(Country.country_name)
    countries = session.exec(countries_stmt).all()
    if not countries:
        raise ValueError(f' No Countries found.')
    # Print Table
    data = []
    for country in countries:
        data.append([
            country.country_name,
            country.num_comps,
            country.code,
            country.flag
        ])
    headers = [
        "Name", "Number of Competitions", "Code", "Flag"
    ]

    console.print(f"\n[bold]Countries")
    print(tabulate(data, headers=headers, tablefmt="pretty"))


#**********************************     Fixtures        *************************************#

# Display All Fixtures for a Season
def print_fixtures(session: Session, competition_name: str, year: int):
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
            f'[red]Error:[/red] There is no season in database for the {year} {competition_name} (Competition ID: {league_id}) season.',
            style="yellow")
        console.print('Please add the required season & teams before adding standings data.',
                      style="yellow")
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
    if competition.comp_type == 'League':
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
        console.print(f"\n[bold]Fixtures from the[/bold] "
                      f"[green]{year} {competition_name}[/green] [bold]season")
        print(tabulate(data, headers=headers, tablefmt="pretty"))

    else:
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
        console.print(f"\n[bold]Fixtures from the[/bold] "
                      f"[green]{year} {competition_name}[/green] [bold]season")
        print(tabulate(data, headers=headers, tablefmt="pretty"))


# Display All Fixtures of one Team for a Season
def print_team_fixtures(session: Session, competition_name: str, year: int, team_name: str):
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
            f'[red]Error:[/red] There is no season in database for the {year} {competition_name} (Competition ID: {league_id}) season.',
            style="yellow")
        console.print('Please add the required season & teams before adding standings data.',
                      style="yellow")
        return
    # Find Team
    team_stmt = select(Team).where(Team.name == team_name)
    team = session.exec(team_stmt).first()
    # Create aliases for Team
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    # Query Fixtures, teams, venue
    fixtures = session.exec(
        select(Fixture, HomeTeam.name.label("home_team_name"), AwayTeam.name.label("away_team_name"), Venue)
        .join(HomeTeam, Fixture.home_team_id == HomeTeam.team_api_id)
        .join(AwayTeam, Fixture.away_team_id == AwayTeam.team_api_id)
        .join(Venue, Fixture.venue_id == Venue.venue_api_id)
        .where(
            (Fixture.season_id == season.id) & or_((Fixture.home_team_id == team.team_api_id), Fixture.away_team_id == team.team_api_id))
        .order_by(Fixture.date)
    ).all()
    # Print Table
    data = []
    # Premier League
    if competition.comp_type == 'League':
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
        console.print(f"\n[bold]Fixtures for[/bold] [green]{team_name}[/green] [bold]from the[/bold] "
                      f"[green]{year} {competition_name}[/green] [bold]season")
        print(tabulate(data, headers=headers, tablefmt="pretty"))

    else:
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
        console.print(f"\n[bold]Fixtures for[/bold] [green]{team_name}[/green] [bold]from the[/bold] "
                      f"[green]{year} {competition_name}[/green] [bold]season")
        print(tabulate(data, headers=headers, tablefmt="pretty"))


#**********************************     Fixture Stats    *************************************#

# Display Fixture Statistics for two Teams in a Season
def print_fixture_stats(session: Session, competition_name: str, year: int, team_name1: str, team_name2: str):
    # Find League ID
    competition_stmt = select(Competition).where(Competition.comp_name == competition_name)
    competition = session.exec(competition_stmt).first()
    if not competition:
        raise ValueError(f'{competition_name} competition not found.')
    # Find Season ID
    season_stmt = select(Season).where(
        and_(Season.league_id == competition.comp_api_id, Season.year == year)
    )
    season = session.exec(season_stmt).first()
    if not season:
        raise ValueError(f'There is no season in database for the {year} {competition_name} season.')
    # Find Team IDs
    team1 = session.exec(select(Team).where(Team.name == team_name1)).first()
    team2 = session.exec(select(Team).where(Team.name == team_name2)).first()
    if not team1 or not team2:
        raise ValueError(f'One or both teams not found')
    # Create aliases to join Team table twice
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    # Query Fixtures, teams, venue
    fixtures = session.exec(
        select(Fixture, HomeTeam.name.label("home_team_name"), AwayTeam.name.label("away_team_name"), Venue, FixtureStats)
        .outerjoin(HomeTeam, Fixture.home_team_id == HomeTeam.team_api_id)
        .outerjoin(AwayTeam, Fixture.away_team_id == AwayTeam.team_api_id)
        .outerjoin(Venue, Fixture.venue_id == Venue.venue_api_id)
        .outerjoin(FixtureStats, Fixture.id == FixtureStats.fixture_id)
        .where(
            and_(
                Fixture.season_id == season.id,
                or_(
                    and_(Fixture.home_team_id == team1.team_api_id,
                         Fixture.away_team_id == team2.team_api_id),
                    and_(Fixture.home_team_id == team2.team_api_id,
                         Fixture.away_team_id == team1.team_api_id)
                )
            )
        )
        .order_by(Fixture.date)
    ).all()
    # Print Table
    print(f'number fixtures {len(fixtures)}')
    headers = [
        "Match Day", "Date", "Home Team", "Away Team", "Referee", "Venue"
    ]
    for fixture, home_team_name, away_team_name, venue, fixturestats in fixtures:
        data = []
        round_str = fixture.round
        matchday_num = int(round_str.split(" - ")[-1])
        data.append([
            matchday_num,
            fixture.date,
            home_team_name,
            away_team_name,
            fixture.referee,
            venue.name
        ])
        console.print(f"\n[bold]Fixture stats for[/bold] [green]{home_team_name}[/green] " 
                      f" [bold]vs.[/bold] [green]{away_team_name}[/green] " 
                      f"[bold]on[/bold] [green]{fixture.date}[/green]")
        print(tabulate(data, headers=headers, tablefmt="pretty"))
        stats = []
        headers_stats = [f'{home_team_name}', '', f'{away_team_name}']
        stats.append([fixture.home_goals, "GOALS", fixture.away_goals])
        stats.append([fixturestats.home_ex_goals, "EXPECTED GOALS", fixturestats.away_ex_goals])
        stats.append([fixturestats.home_sh_on_goal, "SHOTS ON GOAL", fixturestats.away_sh_on_goal])
        stats.append([fixturestats.home_sh_off_goal, "SHOTS OFF GOAL", fixturestats.away_sh_off_goal])
        stats.append([fixturestats.home_total_sh, "TOTAL SHOTS", fixturestats.away_total_sh])
        stats.append([fixturestats.home_blocked_sh, "BLOCKED SHOTS", fixturestats.away_blocked_sh])
        stats.append([fixturestats.home_sh_inside, "SHOTS INSIDE BOX", fixturestats.away_sh_inside])
        stats.append([fixturestats.home_sh_outside, "SHOTS OUTSIDE BOX", fixturestats.away_sh_outside])
        stats.append([fixturestats.home_fouls, "FOULS", fixturestats.away_fouls])
        stats.append([fixturestats.home_corners, "CORNERS", fixturestats.away_corners])
        stats.append([fixturestats.home_offsides, "OFFSIDES", fixturestats.away_offsides])
        stats.append([fixturestats.home_possession, "BALL POSSESSION", fixturestats.away_possession])
        stats.append([fixturestats.home_yellows, "YELLOW CARDS", fixturestats.away_yellows])
        stats.append([fixturestats.home_reds, "RED CARDS", fixturestats.away_reds])
        stats.append([fixturestats.home_saves, "SAVES", fixturestats.away_saves])
        stats.append([fixturestats.home_tot_passes, "TOTAL PASSES", fixturestats.away_tot_passes])
        stats.append([fixturestats.home_accurate_pass, "ACCURATE PASSES", fixturestats.away_accurate_pass])
        stats.append([fixturestats.home_percent_pass, "PASSING %", fixturestats.away_percent_pass])
        print(tabulate(stats, headers=headers_stats, tablefmt="pretty"))


#**********************************     Seasons         *************************************#

# Display all Seasons
def print_seasons(session: Session):
    # Find Seasons
    season_stmt = (
        select(Season, Competition, Country)
        .outerjoin(Competition, Competition.comp_api_id == Season.league_id)
        .outerjoin(Country, Country.id == Competition.comp_country_id)
        .order_by(Season.year)
        .order_by(Competition.comp_type.desc())
        .order_by(Competition.comp_name))
    seasons = session.exec(season_stmt).all()
    if not seasons:
        raise ValueError(f'No Seasons found.')
    # Print Table
    data = []
    for season, competition, country in seasons:
        data.append([
            season.year,
            country.country_name,
            competition.comp_name,
            competition.comp_type,
            season.total_teams
        ])
    headers = [
        "Year", "Country", "Competition", "Type", "Total Teams"
    ]

    console.print(f"\n[bold]All Seasons")
    print(tabulate(data, headers=headers, tablefmt="pretty"))

# Display Seasons for a Competition
def print_comp_seasons(session: Session, competition_name: str):
    # Find Competition
    comp_stmt = select(Competition).where(Competition.comp_name == competition_name)
    competition = session.exec(comp_stmt).first()
    if not competition:
        raise ValueError(f'{competition_name} Competition not found.')
    # Find Seasons
    season_stmt = (
        select(Season, Competition, Country).where(Competition.comp_api_id == competition.comp_api_id)
        .outerjoin(Competition, Competition.comp_api_id == Season.league_id)
        .outerjoin(Country, Country.id == Competition.comp_country_id)
        .order_by(Season.year)
        .order_by(Competition.comp_type.desc()))
    seasons = session.exec(season_stmt).all()
    if not seasons:
        raise ValueError(f'No Seasons found for {competition_name} Competition.')
    # Print Table
    data = []
    for season, competition, country in seasons:
        data.append([
            season.year,
            season.total_teams
        ])
    headers = [
        "Year", "Total Teams"
    ]

    console.print(
        f"\n[bold]Country:[/bold] [green]{seasons[0].Country.country_name}[/green], "
        f"[bold]Competition:[/bold] [green]{competition_name}[/green], "
        f"[bold]Type:[/bold] [green]{seasons[0].Competition.comp_type}[/green]")
    print(tabulate(data, headers=headers, tablefmt="pretty"))

# Display Seasons for a Year
def print_year_seasons(session: Session, year: int):
    # Find Seasons
    season_stmt = (
        select(Season, Competition, Country).where(Season.year == year)
        .outerjoin(Competition, Competition.comp_api_id == Season.league_id)
        .outerjoin(Country, Country.id == Competition.comp_country_id)
        .order_by(Country.country_name)
        .order_by(Competition.comp_type.desc())
        .order_by(Competition.comp_name))
    seasons = session.exec(season_stmt).all()
    if not seasons:
        raise ValueError(f'No Seasons found for {year}.')
    # Print Table
    data = []
    for season, competition, country in seasons:
        data.append([
            country.country_name,
            competition.comp_name,
            competition.comp_type,
            season.total_teams
        ])
    headers = [
        "Country", "Competition", "Type", "Total Teams"
    ]

    console.print(
        f"\n[bold]All Seasons for[/bold] [green]{year}")
    print(tabulate(data, headers=headers, tablefmt="pretty"))

# Display Seasons for a Country
def print_country_seasons(session: Session, country_name: str):
    # Find Country
    country_stmt = select(Country).where(Country.country_name == country_name)
    country = session.exec(country_stmt).first()
    if not country:
        raise ValueError(f'{country_name} not found.')
    # Find Seasons
    season_stmt = (
        select(Season, Competition, Country).where(Country.id == country.id)
        .outerjoin(Competition, Competition.comp_api_id == Season.league_id)
        .outerjoin(Country, Country.id == Competition.comp_country_id)
        .order_by(Competition.comp_type.desc())
        .order_by(Competition.comp_name))
    seasons = session.exec(season_stmt).all()
    if not seasons:
        raise ValueError(f'No Seasons found for {country_name}.')
    # Print Table
    data = []
    for season, competition, country in seasons:
        data.append([
            season.year,
            competition.comp_name,
            competition.comp_type,
            season.total_teams
        ])
    headers = [
        "Year", "Competition", "Type", "Total Teams"
    ]

    console.print(
        f"\n[bold]All Seasons from[/bold] [green]{country_name}")
    print(tabulate(data, headers=headers, tablefmt="pretty"))

# Display Seasons for a Year and Country
def print_year_country_seasons(session: Session, year: int, country_name: str):
    # Find Country
    country_stmt = select(Country).where(Country.country_name == country_name)
    country = session.exec(country_stmt).first()
    if not country:
        raise ValueError(f'{country_name} not found.')
    # Find Seasons
    season_stmt = (
        select(Season, Competition, Country).where(
            (Season.year == year) & (Country.id == country.id))
        .outerjoin(Competition, Competition.comp_api_id == Season.league_id)
        .outerjoin(Country, Country.id == Competition.comp_country_id)
        .order_by(Competition.comp_type.desc())
        .order_by(Competition.comp_name))
    seasons = session.exec(season_stmt).all()
    if not seasons:
        raise ValueError(f'No Seasons found for {year}.')
    # Print Table
    data = []
    for season, competition, country in seasons:
        data.append([
            competition.comp_name,
            competition.comp_type,
            season.total_teams
        ])
    headers = [
        "Competition", "Type", "Total Teams"
    ]

    console.print(
        f"\n[bold]All Seasons from[/bold] [green]{country_name}[/green] [bold]for[/bold] [green]{year}")
    print(tabulate(data, headers=headers, tablefmt="pretty"))


#**********************************     Standings       *************************************#

# Display Standings for a season
def print_standings_table(session: Session, competition_name: str, year: int):
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
            f'[red]Error:[/red] There is no season in database for the {year} {competition_name} (Competition ID: {league_id}) season.',
            style="yellow")
        console.print('Please add the required season & teams before adding standings data.',
                      style="yellow")
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

    console.print(f"\n[bold]Standings for[/bold] [green]{year} {competition_name}[/green]")
    print(tabulate(data, headers=headers, tablefmt="pretty"))


#**********************************     Teams           *************************************#

# Display all Teams
def print_teams(session: Session):
    # Find Teams
    teams_stmt = select(Team).order_by(Team.country).order_by(Team.name)
    teams = session.exec(teams_stmt).all()
    # Print Table
    data = []
    for team in teams:
        if team.national == 0:
            type = "Club"
        elif team.national == 1:
            type = "National"
        data.append([
            team.country,
            team.name,
            team.short_name,
            team.founded,

        ])
    headers = [
        "Country", "Name", "Short Name", "Founded", "Type", "Logo"
    ]

    console.print(f"\n[bold]Standings for[/bold] [green]{year} {competition_name}[/green]")
    print(tabulate(data, headers=headers, tablefmt="pretty"))

# Display all Teams for a Country
def print_teams_country(session: Session, country_name: str):
    console.print('Function not added')

# Display Teams for a Season (Competition and Year)
def print_teams_season(session: Session, competition_name: str, year: int):
    console.print('Function not added')


# Display all National Teams
def print_national_teams(session: Session):
    console.print('Function not added')

# Display National Teams for a Season (Competition and Year)
def print_national_teams_season(session: Session, competition_name: str, year: int):
    console.print('Function not added')

#**********************************     Venues          *************************************#

# Display all Venues
def print_venues():
    console.print('Function not added')

# Display all Venues for a Country
def print_venues_country():
    console.print('Function not added')

# Display Venues for a Season (Competition and Year)
def print_venues_season():
    console.print('Function not added')

