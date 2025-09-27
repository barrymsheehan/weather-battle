import requests as req
from urllib.parse import urlencode
import datetime as dt
import sys
import json

METEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
DEGREE = chr(176) # degree symbol

config = {}

# Today's date
now = dt.datetime.now()
today = now.strftime("%Y-%m-%d")

def load_config() -> dict:
    global config

    try:
        with open("../config.json", "r") as file:
            config = json.load(file)

    except FileNotFoundError as e:
        print(f"ERROR: Config file not found {e}")
        sys.exit(1)

    except OSError as e:
        print(f"ERROR: OS error while reading config file {e}")
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: Unexpected error while loading config file {e}")

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

        res = req.get(url=METEO_GEO_URL, params=geo_params)
        res.raise_for_status()  # Raise HTTPError for bad status codes

        data = res.json()

        return {
            "latitude": data["results"][0]["latitude"],
            "longitude": data["results"][0]["longitude"]
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
        res = req.get(METEO_WEATHER_URL, params=weather_params)
        res.raise_for_status()

        data = res.json()

        # These are the features we want from the returned weather data
        time = data["hourly"]["time"]
        temp = data["hourly"]["temperature_2m"]
        real_feel = data["hourly"]["apparent_temperature"]
        rain = data["hourly"]["rain"]
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
    weather = get_weather_for_coords(coords)
    weather["name"] = city

    return weather

def compare_weather(city_1: dict, city_2: dict) -> tuple:
    """
    Compare the weather in city_1 and city_2
    return 1 if city_1 wins, 2 if city_2 wins and 0 for a tie
    """

    if city_1["max_real_feel"] >= config["thresholds"]["hot"] or city_2["max_real_feel"] >= config["thresholds"]["hot"]:
        if city_1["max_real_feel"] > city_2["max_real_feel"]:
            return (city_1["name"], "max_real_feel")
        elif city_2["max_real_feel"] > city_1["max_real_feel"]:
            return (city_2["name"], "max_real_feel")

    if city_1["min_real_feel"] <= config["thresholds"]["cold"] or city_2["min_real_feel"] <= config["thresholds"]["cold"]:
        if city_1["min_real_feel"] < city_2["min_real_feel"]:
            return (city_1["name"], "min_real_feel")
        elif city_2["min_real_feel"] < city_1["min_real_feel"]:
            return (city_2["name"], "min_real_feel")

    if city_1["max_rain"] > 0 or city_1["max_rain"] > 0:
        if city_1["max_rain"] > city_2["max_rain"]:
            return (city_1["name"], "max_rain")
        elif city_2["max_rain"] > city_1["max_rain"]:
            return (city_2["name"], "max_rain")

    return ("None", "tie")

def create_result_string(city_1: dict, city_2: dict, winning_city: tuple) -> str:
    result = []

    result.append("Welcome to weather battle!")
    result.append("\n")
    result.append("Max temperature")
    result.append(f"{city_1['name']} : {city_1['max_temp']}{DEGREE} (Real Feel {city_1['max_real_feel']}{DEGREE}) - {city_2['max_temp']}{DEGREE} (Real Feel {city_2['max_real_feel']}{DEGREE}) : {city_2['name']}")
    result.append("Min temperature")
    result.append(f"{city_1['name']} : {city_1['min_temp']}{DEGREE} (Real Feel {city_1['min_real_feel']}{DEGREE}) - {city_2['min_temp']}{DEGREE} (Real Feel {city_2['min_real_feel']}{DEGREE}) : {city_2['name']}")
    result.append("Max rain")
    result.append(f"{city_1['name']} : {city_1['max_rain']}mm - {city_2['max_rain']}mm : {city_2['name']}")
    result.append("\n")
    result.append(f"Winner: {winning_city[0]} on {winning_city[1]}!")

    return ("\n").join(result)

def main():
    """Main function, fetches coords, then weather data for both cities"""

    load_config()

    try:
        city_1_weather = get_weather_for_city(config["cities"]["city_1"])
        city_2_weather = get_weather_for_city(config["cities"]["city_2"])
        winner = compare_weather(city_1_weather, city_2_weather)
        result = create_result_string (city_1_weather, city_2_weather, winner)

        print(result)

    except KeyError as e:
        print(f"ERROR: Key {e} not found in weather response")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error in main() {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()