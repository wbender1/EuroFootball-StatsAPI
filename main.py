# Import libraries
import requests
import config

# Define API URL
url = "https://v3.football.api-sports.io/standings"

# Define params for query
params = {
    'league': 39,
    'season': 2023
}

# Define API headers
headers = {
    'x-rapidapi-key': config.API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# Send GET request and receive response
response = requests.get(url, headers=headers, params=params)

# Print response text
print(response.text)