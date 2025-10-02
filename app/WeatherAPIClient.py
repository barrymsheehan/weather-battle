from urllib.parse import urlencode
import datetime as dt
import requests as req
import sys

class WeatherAPIClient:
    METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self.hourly = "temperature_2m,apparent_temperature,rain"
        self.timezone = "GMT"
        self.today = self.get_todays_date()
        self.timeout = 10  # Request timeout in seconds


    def get_todays_date(self) -> str:
        """Get today's date in the required format for the API call"""
        now = dt.datetime.now()
        return now.strftime("%Y-%m-%d")

    def get_weather_for_coords(self, coords: dict) -> dict:
        """Return hourly weather data for coords"""

        try:

            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "hourly": self.hourly,
                "timezone": self.timezone,
                "start_date": self.today,
                "end_date": self.today
            }

            print(f"About to run weather query for {coords["city"]}: {WeatherAPIClient.METEO_WEATHER_URL}?{urlencode(params)}")
            res = req.get(WeatherAPIClient.METEO_WEATHER_URL, params=params, timeout=self.timeout)
            res.raise_for_status()

            data = res.json()

            # Validate data in response
            if "hourly" not in data:
                raise ValueError("Weather API response missing hourly data")

            required_keys = ["time", "temperature_2m", "apparent_temperature", "rain"]
            for key in required_keys:
                if key not in data["hourly"]:
                    raise ValueError(f"Key {key} not found in hourly data") 

            # These are the features we want from the returned weather data
            time = data["hourly"]["time"]
            temp = data["hourly"]["temperature_2m"]
            real_feel = data["hourly"]["apparent_temperature"]
            rain = data["hourly"]["rain"]

            if not time or not temp or not real_feel or not rain:
                raise ValueError("Weather API returned empty data array(s)")

            if not (len(time) == len(temp) == len(real_feel) == len(rain)):
                raise ValueError("Weather data arrays have different lengths")

            # Calculate min and max values for comparison
            idx_max_real_feel = real_feel.index(max(real_feel))
            idx_min_real_feel = real_feel.index(min(real_feel))
            idx_max_rain = rain.index(max(rain))

            # Only the values we want to compare
            return {
                "name": coords["city"],
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
            sys.exit(1)

        except Exception as e:
            print(f"ERROR: Unexpected error in get_weather_for_coords() {e}")
            sys.exit(1)