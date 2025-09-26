import requests as req
from urllib.parse import urlencode
import datetime as dt
import sys

METEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
CITY_1 = "Cork"
CITY_2 = "Oxford"

# Today's date
now = dt.datetime.now()
today = now.strftime("%Y-%m-%d")

def get_coords_for_city(city: str) -> dict:
    """Return coords (latitude and longitude) for city"""

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
        print(f"ERROR: Request failed while fetching coords {e}")
        sys.exit(1)
    
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    except KeyError as e:
        print(f"ERROR: key {e} not found in coords response")
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: Unexpected error in get_coords_for_city() {e}")
        sys.exit(1)

def get_weather_for_coords(coords: dict) -> dict:
    """Return hourly weather data for coords"""

    try:

        weather_params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "hourly": "temperature_2m,apparent_temperature,rain",
            "timezone": "GMT",
            "start_date": today,
            "end_date": today
        }

        print(f"About to run query: {METEO_WEATHER_URL}?{urlencode(weather_params)}")
        res_weather = req.get(METEO_WEATHER_URL, params=weather_params)
        res_weather.raise_for_status()

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
        print(f"ERROR: Unexpected error in get_weather_for_coords() {e}")
        sys.exit(1)

def get_weather_for_city(city: str) -> dict:
    """
    Return weather data for city
    1. Get coordinates (latitude, longitude) for city
    2. Get hourly weather data for today for these coordinates
    """

    coords = get_coords_for_city(city)

    print(f"Latitude: {coords['latitude']}, longitude: {coords['longitude']}")

    return get_weather_for_coords(coords)


def main():
    """Main function, fetches coords, then weather data for both cities"""

    try:
        city_1_weather = get_weather_for_city(CITY_1)
        city_2_weather = get_weather_for_city(CITY_2)

        print(f"{CITY_1} stats")
        print(f"Highest real feel of the day: {city_1_weather['max_temp']} (real feel {city_1_weather['max_real_feel']}) at {city_1_weather['max_time']}")
        print(f"Lowest real feel of the day: {city_1_weather['min_temp']} (real feel {city_1_weather['min_real_feel']}) at {city_1_weather['min_time']}")
        print(f"Highest rainfall of the day: {city_1_weather['max_rain']} at {city_1_weather["rain_time"]}")

        print(f"{CITY_2} stats")
        print(f"Highest real feel of the day: {city_2_weather['max_temp']} (real feel {city_2_weather['max_real_feel']}) at {city_2_weather['max_time']}")
        print(f"Lowest real feel of the day: {city_2_weather['min_temp']} (real feel {city_2_weather['min_real_feel']}) at {city_2_weather['min_time']}")
        print(f"Highest rainfall of the day: {city_2_weather['max_rain']} at {city_2_weather["rain_time"]}")

    except KeyError as e:
        print(f"Error: Key {e} not found in weather response")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error in main() {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()