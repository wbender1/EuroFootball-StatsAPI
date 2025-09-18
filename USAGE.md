# Usage Documentation for Functions

## Initialize Database
Initialize the database using: `python src/functions.py init-db`

## Fetch Competitions
Retrieve all the competitions for a COUNTRY using:

`python src/functions.py fetch-competitions "COUNTRY"`

## Show Competitions
show all competitions for a country
optional league/cup input

## Show Countries
show all countries in table


## Fetch Teams
Retrieve all the teams for a COMPETITION_NAME and YEAR using:

`python src/functions.py fetch-teams "COMPETITION_NAME" YEAR`

## Show Teams
show all seasons
optional competition input
optional year input

## Show Venues
show all venues
optional country input
optional competition & year input

## Show Seasons
show all seasons
optional competition input
optional year input

## Fetch Standings
Retrieve the standings/league table for a league COMPETITION_NAME and YEAR using:

`python src/functions.py fetch-standings "COMPETITION_NAME" YEAR`

## Show Standings
Show the standings/league table for a league COMPETITION_NAME and YEAR using:

`python src/functions.py show-standings "COMPETITION_NAME" YEAR`

## Fetch Fixtures
Retrieve all the fixtures for a COMPETITION_NAME and YEAR using:

`python src/functions.py fetch-fixtures "COMPETITION_NAME" YEAR`

## Show Fixtures
display all league fixtures for one season
optional 1 team & one season input

## Fetch Fixture Stats
Retrieve all the fixture statistics for a COMPETITION_NAME, YEAR, and TEAM using:

`python src/functions.py fetch-fixture-stats "COMPETITION_NAME" YEAR "TEAM"`

## Show Fixture Stats
Retrieve fixture stats for two teams from one competition and year

## Fetch Season
Retrieve all the competitions, teams, standings, a

## Delete Fixture Stats