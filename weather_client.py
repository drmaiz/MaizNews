import requests

LATITUDE = 30.3322
LONGITUDE = -81.6557
CITY = "Jacksonville, FL"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Heavy showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm w/ hail", 99: "Thunderstorm w/ heavy hail",
}


def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "forecast_days": 1,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    current = resp.json()["current"]

    return {
        "city": CITY,
        "temp": round(current["temperature_2m"]),
        "feels_like": round(current["apparent_temperature"]),
        "humidity": round(current["relative_humidity_2m"]),
        "wind": round(current["wind_speed_10m"]),
        "condition": WEATHER_CODES.get(current["weather_code"], "Unknown"),
    }
