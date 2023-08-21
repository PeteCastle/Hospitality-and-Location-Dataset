
from bs4 import BeautifulSoup
import pandas as pd
import logging
from tripadvisor_wrapper import TripadvisorWrapper
import traceback

# pip install webdriver-manager
# pip install selenium-wire
# pip install bs4
# pip install pandas
# pip install coloredlogs

class TripadvisorRestaurant(TripadvisorWrapper):
    def __init__(self, locations_file = "locations.json" , NUM_PAGES=1):
        super().__init__(locations_file, NUM_PAGES)
        return

    def getItemList(self,location) -> []:
        url = self.TRIPADVISOR_URL + self.getLocationUrl(location, "restaurants")
        offset = 0
        restaurant_items = []
        for i in range(self.NUM_PAGES):
            index = url.index('-g')
            offset_url = url[:index] + f"-oa{offset}" + url[index:]
            self.driver.get(offset_url)
            restaurant_list_page = BeautifulSoup(self.driver.page_source, "html.parser")
            if i==0:
                restaurant_items.extend(restaurant_list_page.find_all("div", class_="vIjFZ Gi o VOEhq"))
            else:
                restaurant_items.extend(restaurant_list_page.find_all("div", class_="biGQs _P fiohW alXOW NwcxK GzNcM ytVPx UTQMg RnEEZ ngXxk"))

            offset += 30
        logging.info(f"Scraped the URLS of {len(restaurant_items)} selected restaurants in {location}") 
        return restaurant_items

    # %%
    def getItemInfo(self, page: BeautifulSoup, url):
        restaurant_info = {}
        restaurant_info["url"] = url.get("href")
        restaurant_info["name"] = page.find("h1","HjBfq").contents[0]
        restaurant_info["review_count"] = int(page.find("span","AfQtZ").contents[0].replace(",",""))
        restaurant_info["address"] = page.find("span", "yEWoV").contents[0]
        restaurant_info["rating"] = float(page.find("span", "ZDEqb").contents[0])
        restaurant_info["rating_description"] = self.getRatingDescription(restaurant_info["rating"])
        # TO ADD
        # website url (requires js)
        # email (requires js)
        # phone number (skill issue)

        #Operating Hours
        operating_hours = []
        try:
            for i ,span in enumerate(page.find("span", "mMkhr").contents[0]):
                if i == 0:
                    continue   
                elif span.contains("See all hours"):
                    continue
                operating_hours.append(str(span).replace("<span>","").replace("</span>","").replace("<!-- -->","").replace(u'\xa0', u' '))
            
            restaurant_info["operating_hours"] = ",".join(operating_hours)
            print(",".join(operating_hours))
        except Exception as e:
            pass

        try:
            restaurant_info["about"] = page.find("div", "VOzxM").contents[0]
        except:
            pass
        #Tag V1 and V2
        tag = page.find_all("div","CtTod Wf b") + page.find_all("div","tbUiL b") # v1 + v2
        description = page.find_all("div","AGRBq") + page.find_all("div","SrqKb") # v1 + v2
        for i in range(len(tag)):
            restaurant_info[tag[i].contents[0].lower().replace(" ","_")] = description[i].contents[0]

        #Ratings
        ratings = page.find_all("div", "DzMcu")
        for rating in ratings:
            rating_type = rating.find("span", "BPsyj").contents[0]
            classes = rating.find("span", "ui_bubble_rating")
            rating_value = self.getRating(classes.get("class"))
            restaurant_info[f"rating_{rating_type}"] = rating_value
        
        restaurant_review = []
        for review in page.find_all("div", "reviewSelector"):
            review_info = {}
            review_info["restaurantName"] = restaurant_info["name"]
            review_info["rating"] = self.getRating(review.find("span", "ui_bubble_rating").get("class"))
            review_info["ratingDate"] = review.find("span", "ratingDate").get("title")
            review_info["title"] = review.find("span", "noQuotes").contents[0]
            review_info["content"] = review.find("p", "partial_entry").contents[0]

            if review.find("span", "stay_date_label"):
                review_info["visitDate"] = review.find("span", "stay_date_label").contents[0]
            
            if review.find("span", "postSnippet"):
                review_info["content"] += review.find("span", "postSnippet").contents[0]
                
            review_info["url"] = review.find("div", "quote").find("a").get("href")
            restaurant_review.append(review_info)
            logging.info(f"Scraped all details from {restaurant_info['name']}")
            return restaurant_info, restaurant_review

        # %%
    def extractData(self, locations=[]):
        for location in locations:
            for restaurant_item in self.getItemList(location):
                try:
                    url = restaurant_item.find("a", class_="BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS") # Class of the URL hyperlink
                    restaurant_url = self.TRIPADVISOR_URL + url.get("href")
                    self.driver.get(restaurant_url)

                    restaurant_info, restaurant_review = self.getItemInfo( BeautifulSoup(self.driver.page_source, "html.parser") , url)

                    self.scraped_infos.append(restaurant_info)
                    self.scraped_reviews.extend(restaurant_review)
                except Exception as e:
                    logging.warn(f"An error has occured on {restaurant_url}:{traceback.print_exc()}")
                    continue
            logging.info(f"Scraped all {len(self.scraped_infos)} restaurants in {location}")
        return
    

        