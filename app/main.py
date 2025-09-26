import requests as req
from urllib.parse import urlencode
import datetime as dt

METEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Today's date
now = dt.datetime.now()
today = now.strftime("%Y-%m-%d")

# Get latitude and longitude for Cork
geo_params = {
    "name": "Cork",
    "count": 1,
    "language": "en",
    "format": "json"
}

print(f"About to run query: {METEO_GEO_URL}?{urlencode(geo_params)}")
res_geo = req.get(url=METEO_GEO_URL, params=geo_params)
geo_data = res_geo.json()
latitude = geo_data["results"][0]["latitude"]
longitude = geo_data["results"][0]["longitude"]
print(f"Coords for {geo_params['name']}: latitude={latitude}, longitude={longitude}")

# Get weather data
weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": "temperature_2m,apparent_temperature,rain",
    "timezone": "GMT",
    "start_date": today,
    "end_date": today
}

print(f"About to run query: {METEO_WEATHER_URL}?{urlencode(weather_params)}")
res_weather = req.get(METEO_WEATHER_URL, params=weather_params)
weather_data = res_weather.json()
time = weather_data["hourly"]["time"]
temp = weather_data["hourly"]["temperature_2m"]
real_feel = weather_data["hourly"]["apparent_temperature"]
rain = weather_data["hourly"]["rain"]
idx_max_real_feel = real_feel.index(max(real_feel))
idx_min_real_feel = real_feel.index(min(real_feel))
idx_max_rain = rain.index(max(rain))

max_time = time[idx_max_real_feel].split("T")[1]
max_real_feel = real_feel[idx_max_real_feel]
max_temp = temp[idx_max_real_feel]

min_time = time[idx_min_real_feel].split("T")[1]
min_real_feel = real_feel[idx_min_real_feel]
min_temp = temp[idx_min_real_feel]

rain_time = time[idx_max_rain].split("T")[1]
max_rain = rain[idx_max_rain]

print(f"Highest real feel of the day: {max_temp} (real feel {max_real_feel}) at {max_time}")
print(f"Lowest real feel of the day: {min_temp} (real feel {min_real_feel}) at {min_time}")
print(f"Highest rainfall of the day: {max_rain} at {rain_time}")