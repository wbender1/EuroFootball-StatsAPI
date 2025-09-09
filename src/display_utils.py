# Import libraries
from sqlmodel import Session, select
from rich.console import Console
from tabulate import tabulate

# Import modules
from models import Team, Season, Standing

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
        "",
        "Team",
        "GP",
        "W",
        "D",
        "L",
        "F",
        "A",
        "GD",
        "P"
    ]

    console.print(f"\n[bold]Standings for {year}.")
    print(tabulate(data, headers=headers, tablefmt="pretty"))