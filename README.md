# ManUtd API Project

A python script to fetch and analyze data from the API-Sports.io API.

## Features
* Fetch the Competitions for a Country and adds the Teams, Venues, and Standings for 1 Season.
* Stores data in local database.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Rename `config_example.py` to `config.py`
3. Replace `"api_key_goes_here"` in `config.py` with your personal API key from [API-Sports](https://api-sports.io/).

## Usage
1. Use `python functions.py init-db` to initialize the database.
2. There is one function to add all associated data for a season: `python functions.py fetch-season COUNTRY_NAME LEAGUE_ID LEAGUE_YEAR`.