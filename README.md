# Euro Football Statistics API Project

A python script to fetch and analyze European Football data from the API-Sports.io API.

## Features
* Fetch a variety of Football related data including:
  * Competitions for a Country.
  * Teams from a Competition and Year.
  * Standings for a League and Year.
  * Fixtures for a Competition and Year.
  * Fixture Statistics for a Teams Competition for a Year.
* Stores data in local database.
* Print Standings, Fixtures, and Fixture Statistics to console.

## Technologies Used
* Python
* SQLModel (ORM)
* SQLite (Database)
* Typer (CLI Framework)
* Requests (HTTP API Calls)
* Rich (Console Output Formatting)

## Database
Data is stored locally in a SQLite database file, `database.db`. The database schema includes tables for Countries, Competitions, Teams, Venues, Seasons, Standings, Fixtures, and Fixture Statistics.

## Setup
1. Files are in the `src` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Rename `config_example.py` to `config.py`
4. Replace `"api_key_goes_here"` in `config.py` with your personal API key from [API-Sports](https://api-sports.io/).

## Usage
1. Use `python functions.py init-db` to initialize the database.
2. There are several functions for retrieving data from the API and are described in depth in `USAGE.md`.