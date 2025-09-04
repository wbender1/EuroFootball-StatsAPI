# Import libraries
import requests
import config

# Define API URL
url = "https://v3.football.api-sports.io/leagues"

# Define payload, body is not needed for a GET request
payload = {}

# Define API headers
headers = {
    'x-rapidapi-key': config.API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# Send GET request and receive response
response = requests.request("GET", url, headers=headers, data=payload)

# Print response text
print(response.text)