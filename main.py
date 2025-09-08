# Import libraries
import requests
import config

# Define API URL
url = "https://v3.football.api-sports.io/fixtures"

# Define params for query
params = {
    'league': 39,
    'season': 2023,

}

# Define API headers
headers = {
    'x-rapidapi-key': config.API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# Send GET request and receive response
response = requests.get(url, headers=headers, params=params)

# Parse JSON into Python Dictionary
data = response.json()

#league = data['response'][0]['league']['name']
#country = data['response'][0]['league']['country']
#season = data['response'][0]['league']['season']
#teams = []
#for team in data['response'][0]['league']['standings'][0]:
#    name = team['team']['name']
#    points = team['points']
#    rank = team['rank']
#    teams.append(f'{rank} - {name} : {points}')

#output = f'The standings for the {season} {country} {league} are: '
#print(output)
#for team in teams:
#    print(team)
print(data)