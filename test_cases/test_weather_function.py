import pytest
from unittest.mock import patch, Mock
from weather_function import fetch_weather_data
import requests

# Test when city is found and weather data is available
def test_fetch_weather_data_success():
    """
    Test that fetch_weather_data successfully retrieves and returns weather data
    for a valid city input when both geocoding and weather APIs return expected
    responses.

    The test verifies that the function returns the correct location, temperature,
    windspeed, and weathercode when the APIs return valid data for "New York".
    """

    geo_mock = {
        "results": [{
            "latitude": 40.7128,
            "longitude": -74.0060,
            "name": "New York",
            "country": "US"
        }]
    }
    weather_mock = {
        "current_weather": {
            "temperature": 20.5,
            "windspeed": 5.2,
            "weathercode": 1
        }
    }
    geo_response = Mock()
    geo_response.json.return_value = geo_mock
    geo_response.raise_for_status = Mock()
    weather_response = Mock()
    weather_response.json.return_value = weather_mock
    weather_response.raise_for_status = Mock()
    with patch("weather_function.requests.get", side_effect=[geo_response, weather_response]):
        result = fetch_weather_data("New York")
        assert result["location"].startswith("New York")
        assert result["temperature"] == 20.5
        assert result["windspeed"] == 5.2
        assert result["weathercode"] == 1

# Test when city is not found
def test_fetch_weather_data_city_not_found():
    """
    Test that fetch_weather_data returns an error message when the city is not found.

    This test verifies that the function returns a dictionary containing an "error" key
    with a message indicating that the city was not found when the Geocoding API returns
    an empty results list for the provided city name.
    """

    geo_mock = {"results": []}
    geo_response = Mock()
    geo_response.json.return_value = geo_mock
    geo_response.raise_for_status = Mock()
    with patch("weather_function.requests.get", return_value=geo_response):
        result = fetch_weather_data("UnknownCity")
        assert "error" in result
        assert "not found" in result["error"]

# Test when weather data is unavailable
def test_fetch_weather_data_no_weather():
    """
    Test that fetch_weather_data returns an error message when the weather data is unavailable.

    This test verifies that the function returns a dictionary containing an "error" key
    with a message indicating that the weather data is unavailable when the Forecast API
    returns an empty response for the provided latitude and longitude.
    """
    geo_mock = {
        "results": [{
            "latitude": 40.7128,
            "longitude": -74.0060,
            "name": "New York",
            "country": "US"
        }]
    }
    weather_mock = {}
    geo_response = Mock()
    geo_response.json.return_value = geo_mock
    geo_response.raise_for_status = Mock()
    weather_response = Mock()
    weather_response.json.return_value = weather_mock
    weather_response.raise_for_status = Mock()
    with patch("weather_function.requests.get", side_effect=[geo_response, weather_response]):
        result = fetch_weather_data("New York")
        assert "error" in result
        assert "unavailable" in result["error"]

# Test when a request exception occurs
def test_fetch_weather_data_request_exception():
    """
    Test that fetch_weather_data handles request exceptions properly.

    This test verifies that the function returns a dictionary containing an "error"
    key with a message indicating that the request failed when a RequestException
    is raised during the API call.
    """

    with patch("weather_function.requests.get", side_effect=requests.exceptions.RequestException("Network error")):
        result = fetch_weather_data("New York")
        assert "error" in result
        assert "Request failed" in result["error"]
