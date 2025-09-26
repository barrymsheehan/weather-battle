import requests as req
from urllib.parse import urlencode
import datetime as dt
import sys

METEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
CITY_1 = "Cork"

# Today's date
now = dt.datetime.now()
today = now.strftime("%Y-%m-%d")

def get_geolocation(city: str) -> dict:
    """Return latitude and longitude for city"""

    try:

        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        print(f"About to run query: {METEO_GEO_URL}?{urlencode(geo_params)}")

        res_geo = req.get(url=METEO_GEO_URL, params=geo_params)
        res_geo.raise_for_status()  # Raise HTTPError for bad status codes

        geo_data = res_geo.json()

        return {
            "latitude": geo_data["results"][0]["latitude"],
            "longitude": geo_data["results"][0]["longitude"]
        }

    except req.exceptions.RequestException as e:
        print(f"ERROR: Request failed while fetching geolocation data {e}")
        sys.exit(1)
    
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    except KeyError as e:
        print(f"ERROR: key {e} not found in geolocation response")
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: Unexpected error in get_geolocation() {e}")
        sys.exit(1)

def get_weather(location: dict) -> dict:
    """Return specific hourly weather data for location"""

    try:

        weather_params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "hourly": "temperature_2m,apparent_temperature,rain",
            "timezone": "GMT",
            "start_date": today,
            "end_date": today
        }

        print(f"About to run query: {METEO_WEATHER_URL}?{urlencode(weather_params)}")
        res_weather = req.get(METEO_WEATHER_URL, params=weather_params)
        weather_data = res_weather.json()

        # These are the features we want from the returned weather data
        time = weather_data["hourly"]["time"]
        temp = weather_data["hourly"]["temperature_2m"]
        real_feel = weather_data["hourly"]["apparent_temperature"]
        rain = weather_data["hourly"]["rain"]
        idx_max_real_feel = real_feel.index(max(real_feel))
        idx_min_real_feel = real_feel.index(min(real_feel))
        idx_max_rain = rain.index(max(rain))

        # Only the values we want to compare
        return {
            "max_time": time[idx_max_real_feel].split("T")[1],
            "max_real_feel": real_feel[idx_max_real_feel],
            "max_temp": temp[idx_max_real_feel],
            "min_time": time[idx_min_real_feel].split("T")[1],
            "min_real_feel": real_feel[idx_min_real_feel],
            "min_temp": temp[idx_min_real_feel],
            "rain_time": time[idx_max_rain].split("T")[1],
            "max_rain": rain[idx_max_rain]
        }

    except req.exceptions.RequestException as e:
        print(f"ERROR: Request failed while fetching weather data {e}")
        sys.exit(1)
    
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    except KeyError as e:
        print(f"ERROR: key {e} not found in weather response")
        sys.exit(1)

    except IndexError as e:
        print(f"ERROR: Index not found in weather response {e}")

    except Exception as e:
        print(f"ERROR: Unexpected error in get_weather() {e}")
        sys.exit(1)

def main():
    """Main function, fetches geolocation data then weather data"""

    try:
        city_location = get_geolocation(CITY_1)
        print(f"{CITY_1} location: {city_location}")

        weather_data = get_weather(city_location)
        print(f"Highest real feel of the day: {weather_data['max_temp']} (real feel {weather_data['max_real_feel']}) at {weather_data['max_time']}")
        print(f"Lowest real feel of the day: {weather_data['min_temp']} (real feel {weather_data['min_real_feel']}) at {weather_data['min_time']}")
        print(f"Highest rainfall of the day: {weather_data['max_rain']} at {weather_data["rain_time"]}")

    except KeyError as e:
        print(f"Error: Key {e} not found in weather response")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error in main() {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()