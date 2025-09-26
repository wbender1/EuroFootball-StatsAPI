# Usage Documentation for Functions

## Initialize Database
Initialize the database using: `python src/functions.py init-db`

## Fetch Country
Create a COUNTRY and retrieve all the competitions, teams, and venues data for it using:

`python src/functions.py fetch-country "COUNTRY"`

## Show Countries
Display all the countries using:

`python src/functions.py show-countries`

## Show Competitions
Display all the competitions using:

`python src/functions.py show-competitions`

Display all the competitions for a COUNTRY_NAME using:

`python src/functions.py show-competitions --country "COUNTRY_NAME"`

Display all the competitions for a COMPETITION_TYPE (League or Cup) using:

`python src/functions.py show-competitions --type "COMPETITION_TYPE"`

Display all the competitions for a COUNTRY_NAME and COMPETITION_TYPE (League or Cup) using:

`python src/functions.py show-competitions --country "COUNTRY_NAME" --type "COMPETITION_TYPE"`

## Show Teams
Display all the teams using:

`python src/functions.py show-teams`

Display all the teams for a COUNTRY_NAME using:

`python src/functions.py show-teams --country "COUNTRY_NAME"`

Display all the teams for a COMPETITION_NAME using:

`python src/functions.py show-teams --competition "COMPETITION_NAME"`

Display all the teams for a YEAR using:

`python src/functions.py show-teams --year YEAR`

Display all the teams for a COMPETITION_NAME and YEAR using:

`python src/functions.py show-teams --competition "COMPETITION_NAME" --year YEAR`

Display all the International teams using:

`python src/functions.py show-teams --national`

## Show Venues
Display all the venues using:

`python src/functions.py show-venues`

Display all the venues for a COUNTRY_NAME using:

`python src/functions.py show-venues --country "COUNTRY_NAME"`

Display all the venues for a COMPETITION_NAME using:

`python src/functions.py show-venues --competition "COMPETITION_NAME"`

Display all the venues for a YEAR using:

`python src/functions.py show-venues --year YEAR`

Display all the venues for a COMPETITION_NAME and YEAR using:

`python src/functions.py show-venues --competition "COMPETITION_NAME" --year YEAR`


## Fetch Season
Create a season and retrieve all the standings (League Only) and fixtures data for it.
Also links Team, Season, Venue, and Competition.
Input is a COMPETITION_NAME and YEAR using:

`python src/functions.py fetch-season "COMPETITION_NAME" YEAR`

## Show Seasons
Display all seasons using:

`python src/functions.py show-seasons`

Display all seasons for a COUNTRY_NAME using:

`python src/functions.py show-seasons --country "COUNTRY_NAME"`

Display all seasons for a COMPETITION_NAME using:

`python src/functions.py show-seasons --competition "COMPETITION_NAME"`

Display all seasons for a YEAR using:

`python src/functions.py show-seasons --year YEAR`

Display all seasons for a COUNTRY_NAME from a YEAR using:

`python src/functions.py show-seasons --year YEAR --country "COUNTRY_NAME"`

## Show Standings
Display the standings/league table for a league COMPETITION_NAME and YEAR using:

`python src/functions.py show-standings "COMPETITION_NAME" YEAR`

## Show Fixtures
Display all fixtures for a COMPETITION_NAME from one YEAR using:

`python src/functions.py show-fixtures "COMPETITION_NAME" YEAR`

Display the fixtures for one TEAM for a COMPETITION_NAME from one YEAR:

`python src/functions.py show-fixtures "COMPETITION_NAME" YEAR "TEAM"`


## Fetch Fixture Stats
Retrieve all the fixture statistics for a YEAR and TEAM using:

`python src/functions.py fetch-fixture-stats YEAR "TEAM"`

Retrieve all the fixture statistics for a COMPETITION_NAME, YEAR, and TEAM using:

`python src/functions.py fetch-fixture-stats YEAR "TEAM" "COMPETITION_NAME"`

## Show Fixture Stats
Display all the fixture statistics for a COMPETITION_NAME, YEAR, and TEAM using:

`python src/functions.py show-fixture-stats "COMPETITION_NAME" YEAR "TEAM"`

Display all the fixture statistics for a COMPETITION_NAME, YEAR, between TEAM1 and TEAM2 using:

`python src/functions.py show-fixture-stats "COMPETITION_NAME" YEAR "TEAM1" "TEAM2"`
