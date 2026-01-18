import traceback
import openmeteo_requests
import asyncio
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta

class WeatherClient:
    def __init__(self, cache_file='.cache', expire_after=3600):
        # Setup a session with a cache and retry logic
        cache_session = requests_cache.CachedSession(cache_file, expire_after=expire_after)
        self.retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo_client = openmeteo_requests.Client(session=self.retry_session)

    # 
    def get_weather_1h(self, lat: float, lon: float, departure: datetime):
        start = departure - timedelta(hours=1)
        end = departure

        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "windspeed_10m,"
                      "cloudcover,"
                      "rain,"
                      "snowfall",
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "timezone": "UTC"
        }


        try:            
            # Make request to the Open-Meteo API
            responses = self.openmeteo_client.weather_api(url, params=params)
            # Process the first response
            response = responses[0]
        
            # Extract and print relevant information
            print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
            print(f"Elevation: {response.Elevation()} m asl")
            print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
        
            # Process hourly data
            hourly = response.Hourly()
            hourly_windspeed = hourly.Variables(0).ValuesAsNumpy()  # Exemplo de como acessar os dados
            hourly_cloudcover = hourly.Variables(1).ValuesAsNumpy()
            hourly_rain = hourly.Variables(2).ValuesAsNumpy()
            hourly_snowfall = hourly.Variables(3).ValuesAsNumpy()

            hourly_data = {
                    "date": pd.date_range(
                        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                        freq=pd.Timedelta(seconds=hourly.Interval()),
                        inclusive="left"
                    ),
                    "windspeed_10m": hourly_windspeed,
                    "cloudcover": hourly_cloudcover,
                    "rain": hourly_rain,
                    "snowfall": hourly_snowfall
                }
            # Return the data as a DataFrame
            return pd.DataFrame(data=hourly_data)
        # As exceções que você tinha antes estão corretas para o openmeteo_requests também
        except Exception as exc:
            print(f"An unexpected error occurred in WeatherClient.get_weather_1h: {exc}")
            # --- ADICIONE ESTA LINHA ---
            print(traceback.format_exc()) # Isso imprimirá o traceback completo
            # --------------------------
            return None
        
  
