# Usage Documentation for Functions

## Initialize Database
Initialize the database using: `python src/functions.py init-db`

## Fetch Competitions
Retrieve all the competitions for a COUNTRY using:

`python src/functions.py fetch-competitions "COUNTRY"`

## Show Competitions
Display all the competitions for a COUNTRY_NAME using:

`python src/functions.py show-competitions --country "COUNTRY_NAME"`

Display all the competitions for a COMPETITION_TYPE (League or Cup) using:

`python src/functions.py show-competitions --type "COMPETITION_TYPE"`

Display all the competitions for a COUNTRY_NAME and COMPETITION_TYPE (League or Cup) using:

`python src/functions.py show-competitions --country "COUNTRY_NAME" --type "COMPETITION_TYPE"`

## Show Countries
Display all the countries using:

`python src/functions.py show-countries`

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
Display the standings/league table for a league COMPETITION_NAME and YEAR using:

`python src/functions.py show-standings "COMPETITION_NAME" YEAR`

## Fetch Fixtures
Retrieve all the fixtures for a COMPETITION_NAME and YEAR using:

`python src/functions.py fetch-fixtures "COMPETITION_NAME" YEAR`

## Show Fixtures
Display all fixtures for a COMPETITION_NAME from one YEAR using:

`python src/functions.py show-fixtures "COMPETITION_NAME" YEAR`

Display the fixtures for one TEAM for a COMPETITION_NAME from one YEAR:

`python src/functions.py show-fixtures "COMPETITION_NAME" YEAR "TEAM"`

## Fetch Fixture Stats
Retrieve all the fixture statistics for a COMPETITION_NAME, YEAR, and TEAM using:

`python src/functions.py fetch-fixture-stats "COMPETITION_NAME" YEAR "TEAM"`

## Show Fixture Stats
Display fixture stats for two teams from one competition and year

## Fetch Season
Retrieve all the competitions, teams, standings, a

## Delete Fixture Stats