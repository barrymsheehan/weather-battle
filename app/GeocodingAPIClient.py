from urllib.parse import urlencode
import requests as req
import sys

class GeocodingAPIClient:
    """
    Handle interactions with the Geocoding API
    """

    METEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self):
        """
        Initialise a new GeocodingAPIClient instance
        """
        self.count = 1 # Number of results to return from API
        self.language = "en"
        self.format = "json"
        self.timeout = 10  # Request timeout in seconds

    def get_coords_for_city(self, city:str) -> dict:
        """Return coords (latitude and longitude) for city"""

        try:

            params = {
                "name": city,
                "count": self.count,
                "language": self.language,
                "format": self.format
            }
            print(f"About to run query: {GeocodingAPIClient.METEO_GEO_URL}?{urlencode(params)}")

            res = req.get(url=GeocodingAPIClient.METEO_GEO_URL, params=params, timeout=self.timeout)
            res.raise_for_status()  # Raise HTTPError for bad status codes

            data = res.json()

            if not data.get("results") or len(data["results"]) == 0:
                raise ValueError(f"No coordinates returned in API response for {city}")

            required_keys = ["latitude", "longitude"]

            for key in required_keys:
                if key not in data["results"][0]:
                    raise ValueError(f"Key {key} not found in results data")

            latitude = data["results"][0]["latitude"]
            longitude = data["results"][0]["longitude"]

            return {
                "latitude": latitude,
                "longitude": longitude
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