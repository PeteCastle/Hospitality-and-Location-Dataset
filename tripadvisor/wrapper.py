from abc import ABC, abstractmethod
import json
import os
from dotenv import load_dotenv
import requests
import coloredlogs
import logging.config
import pandas as pd
from bs4 import BeautifulSoup
from seleniumwire import webdriver

class TripadvisorWrapper(ABC):
    # locations : dict = {}
    driver: webdriver.Chrome
    TRIPADVISOR_URL : str = "https://www.tripadvisor.com.ph"
    NUM_PAGES : int = 1
    RAPIDAPI_KEY : str = ""
    RAPIDAPI_HOST : str = ""
    
    def __init__(self,  NUM_PAGES=1, locations_file = "raw_data/locations_url.json"):
        # self.locations = json.load(open(locations_file, "r"))
        load_dotenv('credentials.env')
        self.RAPIDAPI_KEY = os.getenv("RAPIDAPI-KEY")
        self.RAPIDAPI_HOST = os.getenv("RAPIDAPI-HOST")
        self.locations_file = locations_file
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
        })
        coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s')
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.javascript": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

        self.NUM_PAGES = NUM_PAGES
        self.scraped_infos = []
        self.scraped_reviews = []
        return
    
    @abstractmethod
    def extractData(self, locations):
        pass

    @abstractmethod
    def getItemList(self, location) -> []:
        pass
    
    @abstractmethod
    def getItemInfo(self, page: BeautifulSoup, url, location):
        pass

    def getDataframe(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        return  \
            pd.DataFrame(self.scraped_infos), \
            pd.DataFrame(self.scraped_reviews)

    def getRating(self, element_classes):
        rating_value = None
        if "bubble_50" in element_classes:
            rating_value = 5.0
        elif "bubble_45" in element_classes:
            rating_value = 4.5
        elif "bubble_40" in element_classes:
            rating_value = 4.0
        elif "bubble_35" in element_classes:
            rating_value = 3.5
        elif "bubble_30" in element_classes:
            rating_value = 3.0
        elif "bubble_25" in element_classes:
            rating_value = 2.5
        elif "bubble_20" in element_classes:
            rating_value = 2.0
        elif "bubble_15" in element_classes:
            rating_value = 1.5
        elif "bubble_10" in element_classes:
            rating_value = 1.0
        return rating_value

    def getRatingDescription(self,rating: float):
        if rating > 4.5:
            return "Excellent"
        elif rating > 3.5:
            return "Very Good"
        elif rating > 2.5:
            return "Average"
        elif rating > 1.5:
            return "Poor"
        elif rating > 0.5:
            return "Terrible"
        else:
            return None
        
    def getLocationUrl(self, location, type) -> str:
        '''
        location : str 
        type : str -  only accepts the following: Attractions, Hotels, Restaurants, Tourism
        '''
        location = location.title()
        type = type.lower()
        with open(self.locations_file, "r") as infile:
            locations = json.load(infile)
            pass



        if location not in locations.keys():
            url = "https://travel-advisor.p.rapidapi.com/locations/v2/auto-complete"

            querystring = {"query":location,"lang":"en_US","units":"km"}

            headers = {
                "X-RapidAPI-Key": self.RAPIDAPI_KEY,
                "X-RapidAPI-Host": self.RAPIDAPI_HOST
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

            with open(self.locations_file, "w") as outfile:
                json.dump(locations, outfile)

            return locations[location][type]

        else:
            return locations[location][type]


