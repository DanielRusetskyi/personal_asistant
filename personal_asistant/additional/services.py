import requests
import os
from django.conf import settings
from dotenv import load_dotenv

load_dotenv(settings.BASE_DIR / '.env')


API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # градуси Цельсія
        "lang": "uk"        # українська мова
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        return {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "description": data["weather"][0]["description"]
        }
    else:
        return {"error": data.get("message", "Не вдалося отримати дані")}