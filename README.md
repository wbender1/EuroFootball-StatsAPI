# ManUtd API Project

A python script to fetch and analyze data from the API-Sports.io API.

## Features
* Fetches Country, League, Venue, Team, Season, and Standings data.
* Stores data in local database.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Rename `config_example.py` to `config.py`
3. Replace `"api_key_goes_here"` in `config.py` with your personal API key from [API-Sports](https://api-sports.io/).

## Usage
1. Use `python functions.py init-db` to initialize the database.
2. To add the competitions for a country, use `python functions.py fetch-comps COUNTRY_NAME`.
3. Add the teams, venues, and standings for a specific season for one of the added leagues: `python functions.py fetch-season LEAGUE_ID LEAGUE_YEAR`.