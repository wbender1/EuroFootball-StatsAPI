# Import libraries
from sqlmodel import Session, select, or_, and_
from rich.console import Console
from tabulate import tabulate
from sqlalchemy.orm import aliased

# Import modules
from models import Team, Season, Standing, Fixture, Venue, FixtureStats, Competition

# Create console
console = Console()

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

    console.print(f"\n[bold]Standings for {year}.")
    print(tabulate(data, headers=headers, tablefmt="pretty"))


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
        console.print(f"\n[bold]Fixtures for {year}.")
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
        console.print(f"\n[bold]Fixtures for {year}.")
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
        console.print(f"\n[bold]Fixtures for {year}.")
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
        console.print(f"\n[bold]Fixtures for {year}.")
        print(tabulate(data, headers=headers, tablefmt="pretty"))


# Display Fixture Statistics for a Teams Season
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
        console.print(f"\n[bold]Fixture for {fixture.date}.")
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