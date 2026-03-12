"""Skill: Weather — Open-Meteo (free, no API key required)."""

import httpx

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


def get_weather(location: str) -> dict:
    """Get current weather and 3-day forecast for a location."""
    # Geocode
    geo = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": location, "count": 1},
        timeout=10,
    ).json()

    if not geo.get("results"):
        return {"error": f"Location '{location}' not found."}

    r = geo["results"][0]
    lat, lon, name, country = r["latitude"], r["longitude"], r["name"], r.get("country", "")

    # Fetch weather
    weather = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,apparent_temperature",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
            "forecast_days": 3,
            "timezone": "auto",
        },
        timeout=10,
    ).json()

    c = weather.get("current", {})
    daily = weather.get("daily", {})

    forecast = []
    for i in range(len(daily.get("time", []))):
        forecast.append({
            "date": daily["time"][i],
            "max_temp": daily["temperature_2m_max"][i],
            "min_temp": daily["temperature_2m_min"][i],
            "precipitation_mm": daily["precipitation_sum"][i],
            "condition": WMO_CODES.get(daily["weather_code"][i], "Unknown"),
        })

    return {
        "location": f"{name}, {country}",
        "temperature_c": c.get("temperature_2m"),
        "feels_like_c": c.get("apparent_temperature"),
        "humidity_pct": c.get("relative_humidity_2m"),
        "wind_speed_kmh": c.get("wind_speed_10m"),
        "condition": WMO_CODES.get(c.get("weather_code", -1), "Unknown"),
        "forecast_3_days": forecast,
    }
