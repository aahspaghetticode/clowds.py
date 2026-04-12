import geocoder
g = geocoder.ip('me')
print("Estimated location:", g.latlng)
location = g.latlng
#Get api info; yes, this is ripped from https://open-meteo.com/en/docs?forecast_days=1&hourly=&wind_speed_unit=mph&temperature_unit=fahrenheit&precipitation_unit=inch&current=is_day,temperature_2m,showers,rain, sue me goddamnit
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": location[0],
    "longitude": location[1],
    "current": ["is_day", "temperature_2m", "showers", "rain"],
    "wind_speed_unit": "mph",
    "temperature_unit": "fahrenheit",
    "precipitation_unit": "inch",
}
responses = openmeteo.weather_api(url, params = params)
response = responses[0]
current = response.Current()
current_is_day = bool(current.Variables(0).Value())
current_temperature_2m = current.Variables(1).Value()
current_showers = current.Variables(2).Value()
current_rain = current.Variables(3).Value()
#for the memes (and, you know, safety)
import requests
BAD_ALERTS = [
    "Tornado Warning", "Tornado Watch",
    "Thunderstorm Warning", "Severe Thunderstorm Warning", "Severe Thunderstorm Watch",
    "Flash Flood Warning", "Flash Flood Watch",
    "Extreme Wind Warning", "Hurricane Warning", "Hurricane Watch",
    "Blizzard Warning", "Ice Storm Warning",
]

def check_alerts(lat, lon):
    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
    response = requests.get(url, headers={"User-Agent": "clowds.py"})
    alerts = response.json()["features"]
    
    for alert in alerts:
        event = alert["properties"]["event"]
        if event in BAD_ALERTS:
            print("OH SHIT TAKE COVER!!! NO BIKING!!!")
            quit()
#Is the current weather appropriate(prob spelled diffrently lol) for biking?
danger_reasons = []
if not current_is_day: danger_reasons += "It's dark out"
if current_temperature_2m > 80: danger_reasons += "It's hot"
elif current_temperature_2m < 60: danger_reasons += "It's cold"
if current_rain > 0 or current_showers > 0: danger_reasons += "It's raining"
danger_level = len(danger_reasons)
if danger_level == 0: overveiw = "It's perfect outside! Have fun!"
elif danger_level == 1: overveiw = "Bike with caution... Dangers: "
else: overveiw = "Nope. Dangers: "
print(overveiw, str(danger_reasons)[1:-1])