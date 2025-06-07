
import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPEN_METEO_BASE = os.getenv("OPEN_METEO_BASE", "https://api.open-meteo.com/v1/forecast")
GEOCODING_API = os.getenv("GEOCODING_API", "https://geocoding-api.open-meteo.com/v1/search")

def get_coords(city):
    """
    Return the coordinates for a given city name.

    :param city: City name
    :return: Tuple of latitude, longitude, city name, country name
    :raises ValueError: if city not found
    """
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    resp = requests.get(GEOCODING_API, params=params, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    if "results" in data and data["results"]:
        r = data["results"][0]
        return r["latitude"], r["longitude"], r["name"], r.get("country", "")
    raise ValueError("City not found")

def fetch_weather(lat, lon, units, forecast_type):
    """
    Fetch the weather data for a given location and parameters.

    :param lat: Latitude
    :param lon: Longitude
    :param units: "celsius" or "fahrenheit"
    :param forecast_type: "hourly" or "daily"
    :return: The JSON response from the Open-Meteo API
    :raises requests.exceptions.RequestException: on request errors
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,precipitation,relative_humidity_2m,uv_index",
        "timezone": "auto",
    }
    if forecast_type == "hourly":
        params["hourly"] = "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,precipitation,precipitation_probability,relative_humidity_2m,uv_index"
    else:
        params["daily"] = "temperature_2m_max,temperature_2m_min,weather_code,wind_speed_10m_max,wind_direction_10m_dominant,precipitation_sum,precipitation_probability_max,relative_humidity_2m_max,uv_index_max"
    if units == "fahrenheit":
        params["temperature_unit"] = "fahrenheit"
        params["wind_speed_unit"] = "mph"
    else:
        params["temperature_unit"] = "celsius"
        params["wind_speed_unit"] = "kmh"
    params["precipitation_unit"] = "mm"
    resp = requests.get(OPEN_METEO_BASE, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

@app.route("/", methods=["GET"])
def index():
    """
    Display the weather dashboard.

    :return: The rendered HTML template.
    """
    return render_template("dashboard.html")

@app.route("/api/weather", methods=["POST"])
def api_weather():
    """
    Handle a POST request with the following JSON body:
    {
        "city": string (optional),
        "lat": float (optional),
        "lon": float (optional),
        "units": string (optional, default "celsius"),
        "forecast_type": string (optional, default "hourly")
    }
    If "city" is provided, fetch the coordinates from the Geocoding API.
    If "lat" and "lon" are provided, use them directly.
    Otherwise, return a 400 error.
    Fetch the weather data from the Forecast API with the given parameters.
    Return the weather data in JSON format.
    On error, return a JSON object with an "error" key and a 500 status code.
    """

    try:
        data = request.json
        city = data.get("city")
        lat = data.get("lat")
        lon = data.get("lon")
        units = data.get("units", "celsius")
        forecast_type = data.get("forecast_type", "hourly")

        if city:
            lat, lon, city_found, country = get_coords(city)
        elif lat is not None and lon is not None:
            try:
                lat = float(lat)
                lon = float(lon)
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    return jsonify({"error": "Invalid latitude or longitude range"}), 400
            except (TypeError, ValueError):
                return jsonify({"error": "Latitude and longitude must be valid numbers"}), 400
            city_found, country = "Coordinates", ""

        else:
            return jsonify({"error": "No location provided"}), 400

        weather = fetch_weather(lat, lon, units, forecast_type)
        return jsonify({
            "location": f"{city_found}, {country}".strip(", "),
            "units": units,
            "forecast_type": forecast_type,
            "weather": weather
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
