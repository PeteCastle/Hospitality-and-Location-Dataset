from bs4 import BeautifulSoup
import pandas as pd
import logging
from tripadvisor_wrapper import TripadvisorWrapper
import traceback

class TripadvisorHotel(TripadvisorWrapper):
    def __init__(self, locations_file = "locations.json" , NUM_PAGES=1):
            super().__init__(locations_file, NUM_PAGES)
            return
    
    def getItemList(self,location) -> []:
        url = self.TRIPADVISOR_URL + self.getLocationUrl(location, "hotels")
        offset = 0
        hotel_links = []
        
        for _ in range(self.NUM_PAGES):
            index = url.index('-g')
            offset_url = url[:index] + f"-oa{offset}" + url[index:]
            self.driver.get(offset_url)
            hotel_list_page = BeautifulSoup(self.driver.page_source, "html.parser")

            hotel_items = []
            hotel_items.extend(hotel_list_page.find_all("div", class_="jsTLT K"))

            for item in hotel_items:
                hotel_links.append(item.contents[0].get("href"))

            offset += 30
        logging.info(f"Scraped the URLS of {len(hotel_items)} selected restaurants in {location}") 
        return hotel_links
    
    def getItemInfo(self, page: BeautifulSoup, url):
        hotel_info = {}
        hotel_info["name"] = page.find("h1","QdLfr b d Pn").contents[0]
        hotel_info["url"] = url
        hotel_info["address"] = page.find("span", "fHvkI PTrfg").contents[0]
        hotel_info["about"] = page.find("div", "fIrGe _T").contents[0]
        hotel_info["review_count"] = int(page.find("span", "qqniT").contents[0].replace(",",""))
        hotel_info["rating"] = float(page.find("span", "uwJeR P").contents[0])
        hotel_info["rating_description"] = page.find("div", "kkzVG").contents[0]

        #Ratings
        ratings = page.find_all("div", "HXCfp")
        for rating in ratings:
            rating_type = rating.find("div", "hLoRK").contents[0]
            classes = rating.find("span", "ui_bubble_rating")
            rating_value = self.getRating(classes.get("class"))
            hotel_info[f"rating_{rating_type}"] = rating_value

        # More Info
        try:
            more_info = page.find("div", "aeQAp S5 b Pf ME").parent.contents # gets parent of the classs
            current_info_type = ""
            for element in more_info:
                if element.get("class") == None:
                    continue
                if " ".join(element.get("class")) == "aeQAp S5 b Pf ME" :
                    current_info_type = element.contents[0].replace(" ","_")
                elif " ".join(element.get("class")) == "OsCbb K":
                    details = []
                    detail_elements = element.find_all("div", "yplav f ME H3 _c")
                    for detail_element in detail_elements:
                        details.append(detail_element.contents[1])
                    hotel_info[current_info_type] = ",".join(details)
        except:
            pass

        try:
            hotel_info["hotel_class"] = page.find("svg", "JXZuC d H0").get("aria-label").split(" ")[0]
        except:
            hotel_info["hotel_class"] = None

        # To add:
        # hotel style
        # languages spoken

        # Proximity Details
        try:
            hotel_info["walkability_score"] = page.find("span","iVKnd fSVJN").contents[0]
            hotel_info["walkability_description"] = page.find("span","lSyvc H3 b zpbpA").contents[0]
            hotel_info["nearby_restaurant_count"] = page.find("span","iVKnd Bznmz").contents[0]
            hotel_info["nearby_attraction_count"] = page.find("span","iVKnd rYxbA").contents[0]
        except:
            pass

        # Tags
        tags_elements = page.find("div", "GFCJJ").contents[0].contents
        current_tag = ""
        for tag_element in tags_elements:
            if tag_element.get("class") == None:
                continue
            if " ".join(tag_element.get("class")) == "mpDVe Ci b":
                current_tag = tag_element.contents[0].replace(" ","_").lower()

                # modify tag elements:
                current_tag = "other_name" if current_tag == "also_known_as" else current_tag
                current_tag = "old_name" if current_tag == "formerly_known_as" else current_tag
                current_tag = "room_count" if current_tag == "number_of_rooms" else current_tag
            elif " ".join(tag_element.get("class")) == "IhqAp Ci":
                hotel_info[current_tag] = tag_element.contents[0].replace("<!-- -->","")
        del hotel_info["location"] #redundant

        # Reviews
        hotel_review = []
        for review in page.find_all("div", "YibKl MC R2 Gi z Z BB pBbQr"):
            review_info = {}
            review_info["restaurantName"] = hotel_info["name"]
            review_info["rating"] = self.getRating(review.find("span", "ui_bubble_rating").get("class"))
            review_info["ratingDate"] = review.find("div", "cRVSd").contents[0].contents[1].replace(" wrote a review ","")
            review_info["title"] = review.find("div", "KgQgP MC _S b S6 H5 _a").contents[0].contents[0].contents[0].contents[0]
            review_info["content"] = review.find("span", "QewHA H4 _a").contents[0].contents[0]
            review_info["visitDate"] = review.find("span", "teHYY _R Me S4 H3").contents[1].strip()
            
            review_info["url"] = review.find("a", "Qwuub").get("href")
            hotel_review.append(review_info)
        logging.info(f"Scraped all details from {hotel_info['name']}")
        return hotel_info, hotel_review
    
    def extractData(self, locations=[]):
        for location in locations:
            for link in self.getItemList(location):
                try:
                    url = self.TRIPADVISOR_URL + link
                    self.driver.get(url)

                    hotel_info, hotel_review = self.getItemInfo( BeautifulSoup(self.driver.page_source, "html.parser") , url)

                    self.scraped_infos.append(hotel_info)
                    self.scraped_reviews.extend(hotel_review)
                except Exception as e:
                    logging.warn(f"An error has occured on {link}:{traceback.print_exc()}")
                    continue
        logging.info(f"Scraped all {len(self.scraped_infos)} hotels in {location}")
        return 
        
    
 
    
