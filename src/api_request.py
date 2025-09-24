import config
import requests
from rich.console import Console

console = Console()


def api_request(url: str, params: dict = None):
    headers = {
        'x-rapidapi-key': config.API_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    # Try API Request and user error handling
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('results', 0) == 0:
            raise ValueError(f'No results returned. API response: {data}')
        return data
    except requests.exceptions.RequestException as e:
        console.print(f'API Request failed: {e}', style="red")
        return {}
    except ValueError as ve:
        console.print(str(ve), style="red")
        return {}