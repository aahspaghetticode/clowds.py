#if not opened in tty
import sys
import os
import subprocess

def ensure_terminal():
    if sys.stdout.isatty():
        return  # already in a terminal, do nothing
    
    # Not in a terminal, relaunch in one
    script = os.path.abspath(__file__)
    
    # Try common terminal emulators
    for terminal in ["gnome-terminal", "konsole", "xterm", "alacritty", "kitty"]:
        try:
            subprocess.Popen([terminal, "--", "bash", "-c", f"python3 {script}; read -p 'Press enter to exit...'"])
            sys.exit()
        except FileNotFoundError:
            continue
    
    print("Couldn't find a terminal emulator!")
    sys.exit(1)

ensure_terminal()
#get location
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
    "Severe Thunderstorm Warning", "Severe Thunderstorm Watch",
    "Flash Flood Warning", "Flash Flood Watch",
    "Flood Warning", "Flood Watch",
    "Extreme Wind Warning",
    "High Wind Warning", "High Wind Watch",
    "Hurricane Warning", "Hurricane Watch",
    "Typhoon Warning", "Typhoon Watch",
    "Tropical Storm Warning", "Tropical Storm Watch",
    "Blizzard Warning",
    "Ice Storm Warning",
    "Snow Squall Warning",
    "Dust Storm Warning",
    "Extreme Heat Warning",
    "Extreme Cold Warning",
    "Tsunami Warning", "Tsunami Watch",  # if you live near water i guess
    "Shelter In Place Warning",
    "Evacuation Immediate",
    #doesnt really apply to me (chicagoland area) but eh why not
    "Coastal Flood Warning", "Coastal Flood Watch",
    "Lakeshore Flood Warning", "Lakeshore Flood Watch",
    "Storm Surge Warning", "Storm Surge Watch",
    "Hazardous Seas Warning", "Hazardous Seas Watch",
    "Gale Warning", "Gale Watch",
    "Hurricane Force Wind Warning", "Hurricane Force Wind Watch",
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
check_alerts(location[0], location[1])
#Is the current weather appropriate(prob spelled diffrently lol) for biking?
danger_reasons = []
if not current_is_day: danger_reasons.append("It's dark out")
if current_temperature_2m > 80: danger_reasons.append("It's hot")
elif current_temperature_2m < 60: danger_reasons.append("It's cold")
if current_rain > 0 or current_showers > 0: danger_reasons.append("It's raining")
danger_level = len(danger_reasons)
if danger_level == 0: overveiw = "It's perfect outside! Have fun!"
elif danger_level == 1: overveiw = "Bike with caution... Dangers: "
else: overveiw = "Nope. Dangers: "
print(overveiw, str(danger_reasons)[1:-1])
print("""SOURCE: api.weather.gov, open-meteo.com
made with <3 from h3nw :)""")
