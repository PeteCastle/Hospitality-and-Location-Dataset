import os
from pathlib import Path
from http_methods import getRestaurantsList
import json
import math
import pandas as pd

locations = ["Manila"]

restaurant_list = [] 

for location in locations:
    file = Path(f"raw_files/restaurant_list/{location}.json")
    if not file.exists():
        print(f"Getting raw HTTP restaurant list for {location}")
        getRestaurantsList(location)
    else:
        print(f"Raw HTTP restaurant list for {location} already exists")

    raw_data = json.load(open(file))
    for cards in raw_data["data"]["AppPresentation_queryAppListV2"][0]["mapSections"][1]["content"]:
        restaurant_info = {}

        restaurant_info["id"] = cards["saveId"]["id"]
        restaurant_info["name"] = cards["cardTitle"]["string"]

        if cards["badge"]:
            restaurant_info["badge"] = cards["badge"]["type"]
            restaurant_info["badge_year"] = cards["badge"]["year"]
        else:
            restaurant_info["badge"] = None
            restaurant_info["badge_year"] = None
   
        restaurant_info["primary_info"] = cards["primaryInfo"]["text"]

        if cards["secondaryInfo"]:
            restaurant_info["secondary_info"] = cards["secondaryInfo"]["text"]
        else:
            restaurant_info["secondary_info"] = None

        cardPhotoUrl = cards["cardPhoto"]["sizes"]["urlTemplate"]
        maxHeight = math.floor(cards["cardPhoto"]["sizes"]["maxHeight"] / 100) * 100
        maxWidth = math.floor(cards["cardPhoto"]["sizes"]["maxWidth"] / 100) * 100

        restaurant_info["cardPhotoUrl"] = cardPhotoUrl.replace("{height}", str(maxHeight)).replace("{width}", str(maxWidth))

        restaurant_info["rating"] = cards["bubbleRating"]["rating"]
        restaurant_info["number_reviews"] = cards["bubbleRating"]["numberReviews"]["string"]

        restaurant_info["contentId"] = cards["cardLink"]["route"]["typedParams"]["contentId"]
        restaurant_info["content_type"] = cards["cardLink"]["route"]["typedParams"]["contentType"]

        restaurant_list.append(restaurant_info)

        # break


restaurant_list = pd.DataFrame(restaurant_list)
print(restaurant_list)
restaurant_list.to_csv("restaurant_list.csv", index=False)
    
