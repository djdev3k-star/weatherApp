import requests

def fetch_weather_data(city_name):
  
    """
    Fetches current weather data for a given city name.

    Args:
        city_name (str): City name to fetch weather data for.

    Returns:
        dict: A dictionary containing the following keys:
            - location (str): The name of the city or location.
            - temperature (float): The current temperature in degrees Celsius.
            - windspeed (float): The current wind speed in km/h.
            - weathercode (int): A code indicating the current weather condition.
            - error (str): An error message if the request fails or weather data is unavailable.

    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    try:
        # Step 1: Get coordinates from Geocoding API
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city_name, "count": 1, "format": "json"}
        geo_response = requests.get(geo_url, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return {"error": f"City '{city_name}' not found."}

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        location = f"{geo_data['results'][0]['name']}, {geo_data['results'][0].get('country', '')}"

        # Step 2: Get weather from Forecast API
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data.get("current_weather", {})
        if not current:
            return {"error": "Weather data unavailable."}

        return {
            "location": location,
            "temperature": current.get("temperature"),
            "windspeed": current.get("windspeed"),
            "weathercode": current.get("weathercode")
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}