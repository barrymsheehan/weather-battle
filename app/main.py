import json
import sys
from GeocodingAPIClient import GeocodingAPIClient
from WeatherAPIClient import WeatherAPIClient

DEGREE = chr(176) # degree symbol

config = {}

def load_config() -> dict:
    global config

    try:
        with open("../config.json", "r") as file:
            config = json.load(file)

    except FileNotFoundError as e:
        print(f"ERROR: Config file not found {e}")
        sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config file {e}")
        sys.exit(1)

    except OSError as e:
        print(f"ERROR: OS error while reading config file {e}")
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: Unexpected error while loading config file {e}")
        sys.exit(1)

def get_weather_for_city(city: str, geo_client: GeocodingAPIClient, weather_client: WeatherAPIClient) -> dict:
    """
    Return weather data for city
    1. Get coordinates (latitude, longitude) for city
    2. Get hourly weather data for today for these coordinates
    """
    coords = geo_client.get_coords_for_city(city)
    weather = weather_client.get_weather_for_coords(coords)

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

    if city_1["max_rain"] > 0 or city_2["max_rain"] > 0:
        if city_1["max_rain"] > city_2["max_rain"]:
            return (city_1["name"], "max_rain")
        elif city_2["max_rain"] > city_1["max_rain"]:
            return (city_2["name"], "max_rain")

    return ("None", "tie")

def create_result_string(city_1: dict, city_2: dict, winning_city: tuple) -> str:
    result = []
    result.append("\nMax temperature")
    result.append(f"{city_1['name']} : {city_1['max_temp']}{DEGREE}C (Real Feel {city_1['max_real_feel']}{DEGREE}C) - {city_2['max_temp']}{DEGREE}C (Real Feel {city_2['max_real_feel']}{DEGREE}C) : {city_2['name']}")
    result.append("Min temperature")
    result.append(f"{city_1['name']} : {city_1['min_temp']}{DEGREE}C (Real Feel {city_1['min_real_feel']}{DEGREE}C) - {city_2['min_temp']}{DEGREE}C (Real Feel {city_2['min_real_feel']}{DEGREE}C) : {city_2['name']}")
    result.append("Max rain")
    result.append(f"{city_1['name']} : {city_1['max_rain']}mm - {city_2['max_rain']}mm : {city_2['name']}")
    result.append("\n")
    result.append(f"Winner: {winning_city[0]} on {winning_city[1]}!\n")

    return ("\n").join(result)

def main():
    """Main function, fetches coords, then weather data for both cities"""

    load_config()

    geo_client = GeocodingAPIClient()
    weather_client = WeatherAPIClient()

    print("Welcome to weather battle!\n")

    try:
        city_1_weather = get_weather_for_city(config["cities"]["city_1"], geo_client, weather_client)
        city_2_weather = get_weather_for_city(config["cities"]["city_2"], geo_client, weather_client)
        winner = compare_weather(city_1_weather, city_2_weather)
        result = create_result_string(city_1_weather, city_2_weather, winner)

        print(result)

    except KeyError as e:
        print(f"ERROR: Key {e} not found in weather response")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error in main() {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()