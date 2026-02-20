import requests
import json

try:
    health = requests.get('http://localhost:8000/health').json()
    with open('api_health.json', 'w') as f:
        json.dump(health, f, indent=2)
except Exception as e:
    print(f"Health fail: {e}")

try:
    payload = {"make":"Ford","model":"Focus","year":2019,"mileage":45000,"fuel_type":"petrol","channel":"dealer","damage_flag":False}
    quote = requests.post('http://localhost:8000/quote', json=payload).json()
    with open('api_quote.json', 'w') as f:
        json.dump(quote, f, indent=2)
except Exception as e:
    print(f"Quote fail: {e}")
