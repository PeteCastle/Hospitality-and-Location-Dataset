from bs4 import BeautifulSoup
import pandas as pd
import logging
from tripadvisor_wrapper import TripadvisorWrapper
import traceback

class TripadvisorTouristSite(TripadvisorWrapper):
    def __init__(self, locations_file = "locations.json" , NUM_PAGES=1):
            super().__init__(locations_file, NUM_PAGES)
            return
    
    def getItemList(self,location) -> []:
        url = self.TRIPADVISOR_URL + self.getLocationUrl(location, "attractions")
        offset = 0
        attraction_links = []
        for i in range(self.NUM_PAGES):
            index = url.index('-g')
            offset_url = url[:index] + f"-oa{offset}" + url[index:]
            self.driver.get(offset_url)
            attraction_list_page = BeautifulSoup(self.driver.page_source, "html.parser")

            attraction_items = []
        
            attraction_items.extend(attraction_list_page.find_all("div", class_="alPVI eNNhq PgLKC tnGGX"))

            for item in attraction_items:
                attraction_links.append(item.contents[0].get("href"))

            offset += 30
        logging.info(f"Scraped the URLS of {len(attraction_links)} selected tourist destinations in {location}") 
        return attraction_links
    
    def getItemInfo(self, page: BeautifulSoup, url):
        attraction_info = {}
        attraction_info["name"] = page.find("div", class_="iSVKr").contents[0].contents[0]
        attraction_info["url"] = url
        try:
            attraction_info["about"] = page.find("div", class_="pqqta _d").contents[0].contents[0].contents[0].contents[0]
        except:
            pass
        try:
            attraction_info["operating_hours"] = page.find("span", class_="EFKKt").contents[0]
        except:
            pass
        try:
            attraction_info["trip_duration"] = page.find("div", class_="nvXSy f _Y Q2").contents[0].contents[1].contents[0].contents[0]
        except:
            pass
        try:
            attraction_info["site_type"] = page.find_all("div", class_="kUaIL")[2].contents[0].contents[0].contents[0].contents[0].replace(" • ",",")
        except:
            pass

        try:
            review_info = page.find_all("div", class_="jVDab o W f u w GOdjs")[1]
            attraction_info["rating"] = float(review_info.contents[0].get("aria-label").split(" ")[0])
            attraction_info["review_count"] = int(review_info.contents[1].contents[0].split(" ")[0].replace(",",""))
            attraction_info["rating_description"] = self.getRatingDescription(attraction_info["rating"])
            
        except:
            pass

        prices = []
        for price_element in page.find_all("div", class_="biGQs _P fiohW avBIb fOtGX"):
            try:
                prices.append(float(price_element.contents[0].replace("₱","").replace(",","")))
            except:
                continue
        attraction_info["entrance_fee"] = sum(prices)/len(prices) if len(prices) > 0 else None

        try:
            attraction_info["address"] = page.find("div", class_="AcNPX A").contents[0].contents[0].contents[0].contents[0].contents[0].contents[1].contents[0].contents[0]
        except:
            pass

        attraction_reviews = []
        for review_elements in page.find("div","LbPSX").contents[0].contents:
            try:
                review = {}
                review["link"] = review_elements.find_all("a",class_="BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS")[1].get("href")
                review["title"] = review_elements.find_all("a", class_="BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS")[1].contents[0].contents[0]
                review["user_link"] = review_elements.find_all("a",class_="BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS")[0].get("href")
                review["user_name"] = review_elements.find_all("a", class_="BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS")[0].contents[0]

                review["rating"] = review_elements.find("svg","UctUV d H0").get("aria-label").split(" ")[0]
                review["content"] = review_elements.find("div","biGQs _P pZUbB KxBGd").contents[0].contents[0]

                addtl_details = review_elements.find("div", class_="RpeCd").contents[0].split(" • ")
                review["visit_date"] = addtl_details[0]
                review["purpose"] = addtl_details[1] if len(addtl_details) >1 else None

                review["review_date"] = review_elements.find("div", class_="TreSq").contents[0].contents[0].replace("Written ",",")
            except:
                pass
            attraction_reviews.append(review)

        logging.info(f"Scraped all details from {attraction_info['name']}")
        return attraction_info, attraction_reviews
    
    def extractData(self, locations):
        for location in locations:
            for link in self.getItemList(location):
                try:
                    attraction_url = self.TRIPADVISOR_URL + link
                    self.driver.get(attraction_url)

                    attraction_info, attraction_review = self.getItemInfo( BeautifulSoup(self.driver.page_source, "html.parser") , attraction_url)

                    self.scraped_infos.append(attraction_info)
                    self.scraped_reviews.extend(attraction_review)
                except Exception as e:
                    logging.warn(f"An error has occured on {link}:{traceback.print_exc()}")
                    continue
        logging.info(f"Scraped all {len(self.scraped_infos)} tourist destinations in {location}")
        return