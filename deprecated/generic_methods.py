
import os
import requests
import json
from pathlib import Path









# Deprecated in favor of webscrape
def getRestaurantsList(location) -> Path:
    geoIds = {
        "Manila" : 298573,
    }
    geoId = geoIds[location]

    url = "https://travel-advisor.p.rapidapi.com/restaurants/v2/list"
    querystring = {"currency":"USD","units":"km","lang":"en_US"}
    payload = {
        "geoId": geoId,
        "sort": "POPULARITY",
        "sortOrder": "desc",
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    response = requests.post(url, json=payload, headers=headers, params=querystring)

    file_path = Path(f"raw_files/restaurant_list/{location}.json")

    with open(file_path, 'w') as outfile:
        json.dump(response.json(), outfile)

    return file_path

def getWebDriver():
    locations = json.load(open("locations.json", "r"))

    

    return driver

