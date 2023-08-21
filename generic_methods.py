from dotenv import load_dotenv
import os
import requests
import json
from pathlib import Path

load_dotenv('credentials.env')

RAPIDAPI_KEY = os.getenv("RAPIDAPI-KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI-HOST")

def getLocationUrl(location, type) -> str:
    '''
    location : str 
    type : str -  only accepts the following: Attractions, Hotels, Restaurants, Tourism
    '''
    location = location.title()
    type = type.lower()
    locations = json.load(open("locations.json"))

    if location not in locations.keys():
        url = "https://travel-advisor.p.rapidapi.com/locations/v2/auto-complete"

        querystring = {"query":location,"lang":"en_US","units":"km"}

        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }
        
        response = requests.get(url, headers=headers, params=querystring)

        suggestion = response.json()["data"]["Typeahead_autocomplete"]["results"]

        locations[location] = {}
        for i in range(4):
            if suggestion[i]["__typename"] == "Typeahead_QuerySuggestionItem":
                type = suggestion[i]["buCategory"].lower()

                locations[location][type]  = suggestion[i]["route"]["url"]
            elif suggestion[i]["__typename"] == "Typeahead_LocationItem":
                locations[location]["location"] = suggestion[i]["detailsV2"]["route"]["url"]

        with open("locations.json", "w") as outfile:
            json.dump(locations, outfile)

        return locations[location][type]

    else:
        return locations[location][type]


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


