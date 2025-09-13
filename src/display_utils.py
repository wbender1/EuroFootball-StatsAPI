# Import libraries
from sqlmodel import Session, select, or_
from rich.console import Console
from tabulate import tabulate
from sqlalchemy.orm import aliased

# Import modules
from models import Team, Season, Standing, Fixture, Venue, FixtureStats

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

# Display Fixture Statistics for a Teams Season
def print_fixture_stats(session: Session, league_id: int, year: int, team_name1: str, team_name2: str):
    # Find season
    season = session.exec(
        select(Season).where(
            (Season.year == year) & (Season.league_id == league_id)
        )
    ).first()
    if not season:
        console.print(f'[red]Error:[/red] No season found for {year} and league ID {league_id}.')
        return
    # Find Team IDs
    team_stmt1 = select(Team).where(Team.name == team_name1)
    team1 = session.exec(team_stmt1).first()
    team_stmt2 = select(Team).where(Team.name == team_name2)
    team2 = session.exec(team_stmt2).first()
    # Create aliases to join Team table twice
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    # Query Fixtures, teams, venue
    fixtures = session.exec(
        select(Fixture, HomeTeam.name.label("home_team_name"), AwayTeam.name.label("away_team_name"), Venue, FixtureStats)
        .join(HomeTeam, Fixture.home_team_id == HomeTeam.team_api_id)
        .join(AwayTeam, Fixture.away_team_id == AwayTeam.team_api_id)
        .join(Venue, Fixture.venue_id == Venue.venue_api_id)
        .join(FixtureStats, Fixture.id == FixtureStats.fixture_id)
        .where(
            (Fixture.season_id == season.id) &
            or_(
                (Fixture.home_team_id == team1.team_api_id) & (Fixture.away_team_id == team2.team_api_id),
                (Fixture.home_team_id == team2.team_api_id) & (Fixture.away_team_id == team1.team_api_id)
            )
        )
        .order_by(Fixture.date)
    ).all()
    # Print Table
    headers = [
        "Match Day", "Date", "Home Team", "Away Team", "Referee"
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
            fixture.referee
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