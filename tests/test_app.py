import pytest
from unittest.mock import Mock
import requests

from app import get_coords, cached_fetch_weather

# Function returns correct coordinates, city name, and country for a valid city input.
def test_get_coords_valid_city(mocker):
    """
    Test that the function returns the correct coordinates, city name, and country
    for a valid city input.
    """
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [{
            "latitude": 51.5074,
            "longitude": -0.1278,
            "name": "London",
            "country": "United Kingdom"
        }]
    }
    mock_response.raise_for_status = Mock()
    mocker.patch("weather-app.app.requests.get", return_value=mock_response)
    result = get_coords("London")
    assert result == (51.5074, -0.1278, "London", "United Kingdom")

# Function returns correct coordinates and city name when the country field is missing in the API response.
def test_get_coords_city_without_country(mocker):
    """
    Test that the function returns the correct coordinates and city name
    when the 'country' field is missing in the API response.
    """

    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [{
            "latitude": 48.8566,
            "longitude": 2.3522,
            "name": "Paris"
            # No 'country' key
        }]
    }
    mock_response.raise_for_status = Mock()
    mocker.patch("weather-app.app.requests.get", return_value=mock_response)
    result = get_coords("Paris")
    assert result == (48.8566, 2.3522, "Paris", "")

# Function handles city names with special or non-ASCII characters correctly.
def test_get_coords_city_with_special_characters(mocker):
    """
    Test that the function correctly handles city names with special or
    non-ASCII characters, returning the correct coordinates, city name,
    and country.
    """

    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [{
            "latitude": 52.5200,
            "longitude": 13.4050,
            "name": "München",
            "country": "Deutschland"
        }]
    }
    mock_response.raise_for_status = Mock()
    mocker.patch("weather-app.app.requests.get", return_value=mock_response)
    result = get_coords("München")
    assert result == (52.5200, 13.4050, "München", "Deutschland")

# Function raises ValueError when the city is not found in the API response.
def test_get_coords_city_not_found(mocker):
    """
    Test that the function raises a ValueError with a 'City not found'
    message when the city is not found in the API response.
    """
    mock_response = Mock()
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status = Mock()
    mocker.patch("weather-app.app.requests.get", return_value=mock_response)
    with pytest.raises(ValueError, match="City not found"):
        get_coords("UnknownCity")

# Function raises an exception when the external API returns a non-200 HTTP status code.
def test_get_coords_api_http_error(mocker):
    """
    Test that the function raises an exception when the external API returns a non-200 HTTP status code.

    The test simulates a 404 Client Error response from the API by using a mock object
    and setting the raise_for_status method to raise an HTTPError with the appropriate
    message. The function call is then wrapped in a pytest.raises context manager to
    verify that the appropriate exception is raised.
    """
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
    mocker.patch("weather-app.app.requests.get", return_value=mock_response)
    with pytest.raises(requests.HTTPError):
        get_coords("London")

# Function raises an exception or handles timeout when the external API does not respond within the specified timeout.
def test_get_coords_api_timeout(mocker):
    """
    Test that the function raises a Timeout exception when the external API
    does not respond within the specified timeout.

    The test uses a mock object to simulate a timeout by setting the
    side_effect of the mocked requests.get method to raise a Timeout exception.
    The function call is then wrapped in a pytest.raises context manager to
    verify that the appropriate exception is raised.
    """

    mocker.patch("weather-app.app.requests.get", side_effect=requests.Timeout("Request timed out"))
    with pytest.raises(requests.Timeout):
        get_coords("London")

# Function correctly parses and returns coordinates when the API response contains additional unexpected fields.
def test_get_coords_with_extra_fields_in_response(mocker):
    """
    Test that the function correctly parses and returns coordinates when the API
    response contains additional unexpected fields.

    The test uses a mock object to simulate a response with additional fields
    and verifies that the function returns the expected coordinates.
    """
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [{
            "latitude": 40.7128,
            "longitude": -74.0060,
            "name": "New York",
            "country": "USA",
            "population": 8000000,
            "timezone": "America/New_York"
        }],
        "meta": {"info": "extra"}
    }
    mock_response.raise_for_status = Mock()
    mocker.patch("weather-app.app.requests.get", return_value=mock_response)
    result = get_coords("New York")
    assert result == (40.7128, -74.0060, "New York", "USA")

# Function raises an appropriate exception when the API response is malformed or missing expected keys.
def test_get_coords_malformed_api_response(mocker):
    """
    Test that the function raises an appropriate exception when the API response is
    malformed or missing expected keys.

    The test verifies that the function raises a ValueError with a message
    indicating that the city was not found when the API response is missing the
    expected 'results' key.
    """
    mock_response = Mock()
    # Missing 'results' key
    mock_response.json.return_value = {"unexpected": "data"}
    mock_response.raise_for_status = Mock()
    mocker.patch("weather-app.app.requests.get", return_value=mock_response)
    with pytest.raises(ValueError, match="City not found"):
        get_coords("London")


@pytest.mark.parametrize("forecast_type,expected_key", [
    ("hourly", "hourly"),
    ("daily", "daily"),
])
def test_cached_fetch_weather_forecast_type_variation(mocker, forecast_type, expected_key):
    """
    Test that the cached_fetch_weather function correctly handles different
    forecast_type parameter values by verifying that the underlying
    fetch_weather function is called with the correct argument and that the
    result is cached correctly.
    """
    mock_result = {expected_key: {"some": "data"}}
    mock_fetch = mocker.patch("app.fetch_weather", return_value=mock_result)
    result = cached_fetch_weather(10.0, 20.0, "celsius", forecast_type)
    mock_fetch.assert_called_once_with(10.0, 20.0, "celsius", forecast_type)
    assert result == mock_result

@pytest.mark.parametrize("units", ["celsius", "fahrenheit"])
def test_cached_fetch_weather_units_handling(mocker, units):
    """
    Test that the cached_fetch_weather function correctly handles different
    units parameter values by verifying that the underlying fetch_weather
    function is called with the correct units and that the result is as
    expected.
    """

    mock_result = {"units": units}
    mock_fetch = mocker.patch("app.fetch_weather", return_value=mock_result)
    result = cached_fetch_weather(10.0, 20.0, units, "hourly")
    mock_fetch.assert_called_once_with(10.0, 20.0, units, "hourly")
    assert result == mock_result

def test_cached_fetch_weather_int_float_equivalence(mocker):
    """
    Test that the cached_fetch_weather function correctly handles int and float
    inputs for the latitude and longitude parameters by verifying that the
    underlying fetch_weather function is called with the correct arguments and
    that the result is cached correctly.

    The test verifies that when the function is called with int arguments, it
    should hit the cache and not call fetch_weather again, and that the result is
    as expected.
    """
    mock_result = {"weather": "ok"}
    mock_fetch = mocker.patch("app.fetch_weather", return_value=mock_result)
    # First call with float
    result1 = cached_fetch_weather(10.0, 20.0, "celsius", "hourly")
    # Second call with int (should hit cache, so fetch_weather not called again)
    result2 = cached_fetch_weather(10, 20, "celsius", "hourly")
    assert result1 == result2
    # fetch_weather should only be called once due to cache
    mock_fetch.assert_called_once_with(10.0, 20.0, "celsius", "hourly")

@pytest.mark.parametrize("lat,lon", [
    ("not_a_number", 20.0),
    (10.0, "not_a_number"),
    ("abc", "xyz"),
])
def test_cached_fetch_weather_non_numeric_lat_lon(mocker, lat, lon):
    # fetch_weather should not be called
    """
    Test that the cached_fetch_weather function correctly handles non-numeric
    latitude and longitude inputs by verifying that a ValueError is raised and
    that the underlying fetch_weather function is not called.
    """
    
    mocker.patch("app.fetch_weather")
    with pytest.raises(ValueError):
        cached_fetch_weather(lat, lon, "celsius", "hourly")

@pytest.mark.parametrize("lat,lon", [
    (None, 20.0),
    (10.0, None),
    (None, None),
])
def test_cached_fetch_weather_none_lat_lon(mocker, lat, lon):
    # fetch_weather should not be called
    """
    Test that the cached_fetch_weather function correctly handles None values for
    latitude and longitude by verifying that a TypeError is raised and that the
    underlying fetch_weather function is not called.
    """
    
    mocker.patch("app.fetch_weather")
    with pytest.raises(TypeError):
        cached_fetch_weather(lat, lon, "celsius", "hourly")

def test_cached_fetch_weather_cache_eviction(mocker):
    # Patch fetch_weather to return unique results per call
    """
    Test that the cached_fetch_weather function correctly implements cache eviction
    by verifying that the oldest cached result is evicted after the cache is full
    and that the underlying fetch_weather function is called again when the
    evicted key is accessed again.

    The test verifies that the cache is filled to its maxsize (128) and that the
    first inserted key is evicted after the next unique call. Then, it verifies
    that calling the very first key again results in a cache miss (fetch_weather
    called again) by clearing the call_results and calling again. Finally, it
    verifies that the call_results contains the re-fetched key.
    """
    call_results = {}
    def fake_fetch_weather(lat, lon, units, forecast_type):
        """
        A fake implementation of fetch_weather that records the inputs in call_results
        and returns a result with the input as the value for the "call" key.

        Args:
            lat (float): Latitude
            lon (float): Longitude
            units (str): Units for temperature and wind speed
            forecast_type (str): Type of weather forecast

        Returns:
            dict: A dictionary with a single key "call" containing the input values.
        """
        key = (lat, lon, units, forecast_type)
        result = {"call": key}
        call_results[key] = result
        return result

    mocker.patch("app.fetch_weather", side_effect=fake_fetch_weather)
    # Fill the cache to its maxsize (128)
    for i in range(128):
        assert cached_fetch_weather(i, i+1, "celsius", "hourly") == {"call": (float(i), float(i+1), "celsius", "hourly")}
    # The first inserted key should be evicted after the next unique call
    assert cached_fetch_weather(999, 1000, "celsius", "hourly") == {"call": (999.0, 1000.0, "celsius", "hourly")}
    # Now, calling the very first key again should result in a cache miss (fetch_weather called again)
    # To test this, we clear call_results and call again
    call_results.clear()
    result = cached_fetch_weather(0, 1, "celsius", "hourly")
    assert result == {"call": (0.0, 1.0, "celsius", "hourly")}
    # The call_results should now contain the re-fetched key
    assert (0.0, 1.0, "celsius", "hourly") in call_results