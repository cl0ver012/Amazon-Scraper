import argparse
import copy
import random
import sys
from threading import Thread
import time
import json
import os
from bs4 import BeautifulSoup
import requests
from headers import generate_headers
from queue import Queue
from rich.progress import Progress

# Different possible colors
BLUE = '\033[34m'
RED = '\033[91m'
GREEN = '\033[92m'
NORM = '\x1b[0m'
tag = "@Moffi-bit"

# Print the banner to the console
print(GREEN + """
   _                            ___                            
  /_\  _ __  __ _ ______ _ _   / __| __ _ _ __ _ _ __  ___ _ _ 
 / _ \| '  \/ _` |_ / _ \ ' \  \__ \/ _| '_/ _` | '_ \/ -_) '_|
/_/ \_\_|_|_\__,_/__\___/_||_| |___/\__|_| \__,_| .__/\___|_|  
                                                |_|                                                                                                                   
""" + NORM)
time.sleep(1)

parser = argparse.ArgumentParser(
    description=GREEN + "Welcome to Amazon Scraper! Use this program to scrape amazon for your desired items. (* = required field)" + RED + "\nCreator " + tag + NORM)
parser.add_argument(
    "-i", "--item", help="enter the item you want to search for (*)", type=str, nargs="+")
parser.add_argument(
    "-l", "--lower", help="enter the lower bound product price", type=int)
parser.add_argument(
    "-u", "--upper", help="enter the upper bound product price", type=int)
parser.add_argument(
    "-n", "--num", help="enter the number of links you want the program to look through (recommended 100+) (*)", type=int)
parser.add_argument(
    "-o", "--out", help="enter the name of the csv/json you want the product information to go to", type=str)
parser.add_argument("-c", dest="cheap",
                    help="add this argument if you want the program to return the cheapest item at the end of scraping", action="store_true")

# Products
class Item():
    def __init__(self, num, title, price, rating, reviews, availability, URL):
        self.num = num
        self.title = title
        self.price = price
        self.rating = rating
        self.reviews = reviews
        self.availability = availability
        self.URL = URL

    def get_item_price(self):
        return float(self.price.replace('$', '').replace(',', '')) if self.price != "NA" else self.price

    def write_to_csv(self, file):
        file.write(f"{self.title},")
        file.write(f"{self.price},")
        file.write(f"{self.rating},")
        file.write(f"{self.reviews},")
        file.write(f"{self.availability},")
        file.write(f"{self.URL},\n")

    def eval(self):
        rating = str(self.rating).split(" ")
        reviews = str(self.reviews).split(" ")

        try:
            if float(rating[0]) <= 3 and int(reviews[0]) >= 500:
                return RED + "BAD"
            else:
                return GREEN + "GOOD"
        except:
            return NORM + "N/A"
        
    def json_format(self):
        output = {
            "title": f"{self.title}",
            "price": f"{self.price}",
            "rating": f"{self.rating}",
            "reviews": f"{self.reviews}",
            "availability": f"{self.availability}",
            "url": f"{self.URL}"
        }

        return output
    
    def get_num(self):
        return self.num
    
    def convert_price_to_float(self):
        self.price = float(self.price.replace("$", ""))

    def to_string(self):
        if "$" not in str(self.price):
            self.price = "$" + str(self.price)

        # item num, link, price, rank
        output = " {:^7} | {:<60} | {:<7} | {:^7} "
        output = output.format(
            GREEN + f"{self.num}" + NORM, f"{self.URL[:95]}", GREEN + f"{self.price}" + NORM, self.eval(), width=90)

        return output + "\n" + NORM

# Object for scraping amazon products 
class Scraper():
    def __init__(self, item: str = None, num: int = 0, lower: int = 0, upper: int = 0, cheap: bool = False, out: str = "out.csv"):
        self.parse_args()

        self.page = 1
        # All the items the scraper will collect
        self.allItems = []
        # All the links of the items the scraper will look through (this resets after each scrape) to always provide new links.
        self.linksList = Queue(0)
        self.itemNum = 1

        if self.args.item and self.args.num and self.args.num > 0:
            self.provided = True
            self.scrape()
            return

        self.args.out = out
        self.args.item = item
        self.args.lower = lower
        self.args.upper = upper
        self.args.num = num
        self.args.cheap = cheap
        self.provided = False

        self.scrape()

    def scrape(self):
        self.process_args()
        self.HEADERS = generate_headers()

        # Only update URL if it's the object's first time scraping
        if self.page == 1:
            self.URL = f"https://www.amazon.com/s?k={self.args.item}"

        # Get all the item links from every page needed
        self.get_all_item_links()
        self.starting_amount = self.linksList.qsize()
        start_time = time.time()

        with Progress() as self.progress:
            self.task = self.progress.add_task("Collecting item data... ", total=self.starting_amount)
        
            for _ in range(int(self.starting_amount / 2)):
                worker = Thread(target=self.process_item_links, daemon=True)
                worker.start()

            self.linksList.join()

        print(GREEN + "It took %s seconds " % (time.time() - start_time) + f"to process {self.starting_amount} relevant items that were found." + NORM)
        # Soup is done
        print(RED + "Your soup is ready!\n" + NORM)

        # Output the data
        self.output_data()

    # Get the title of the product
    def get_item_title(self, soup):
        productTitle = soup.find("span", attrs={"id": 'productTitle'})

        if productTitle != None:
            productTitle = productTitle.text.strip()
        else:
            productTitle = "NA"

        return productTitle

    # Get the price of the product and any discounts
    def get_item_price(self, soup):
        discount = soup.find("span", attrs={
                             "class": "reinventPriceSavingsPercentageMargin savingsPercentage"})
        priceSpan = soup.select_one(
            "span.a-price.reinventPricePriceToPayMargin.priceToPay, span.a-price.apexPriceToPay")

        # Check to see if there is a price
        if priceSpan:
            price = priceSpan.find(
                "span", {"class": "a-offscreen"}).text.strip()
        else:
            price = None

        # Check to see if there is a discounted price, else just use the normal price or to NA.
        if discount:
            discount = discount.text.strip()
            productPrice = soup.find(
                "span", attrs={"class": "a-price a-text-price"}).text.strip()
        elif price:
            productPrice = price
            discount = False
        else:
            productPrice = "NA"

        if productPrice == "NA":
            otherPriceOption = soup.find("span", {"id": "priceblock_ourprice"})
            productPrice = otherPriceOption.text.strip() if otherPriceOption != None else "NA"

        if productPrice == "NA":
            productPrice = soup.find("span", {"class": "a-offscreen"})
            productPrice = productPrice.text.strip() if productPrice != None else "NA"

        if productPrice == "NA":
            productPrice = soup.find("span", {"class": "a-price-whole"})
            productPrice = productPrice.text.strip() if productPrice != None else "NA"

        return productPrice

    # Get the product's rating out of 5.0
    def get_product_rating(self, soup):
        productRating = soup.find(
            "span", attrs={"class": "reviewCountTextLinkedHistogram"})

        if productRating != None:
            productRating = productRating["title"].strip()
        else:
            productRating = "NA"

        return productRating

    # Get the total number of product reviews
    def get_product_reviews(self, soup):
        numberOfReviews = soup.find(
            "span", attrs={'id': 'acrCustomerReviewText'})

        if numberOfReviews != None:
            numberOfReviews = numberOfReviews.text.strip().replace(',', '')
        else:
            numberOfReviews = "NA"

        return numberOfReviews

    # Gets product's availability (e.g in stock, how many left, out of stock)
    def get_product_avail(self, soup):
        productAvailabilityDiv = soup.find("div", attrs={'id': 'availability'})

        if productAvailabilityDiv != None:
            productAvailability = productAvailabilityDiv.find("span")
            if productAvailability != None:
                productAvailability = productAvailability.text.strip().replace(',', '')
        else:
            productAvailability = "NA"

        if productAvailability == "NA":
            productAvailability = soup.find(
                "span", attrs={"class": "a-size-medium"})
            productAvailability = productAvailability.text.strip(
            ) if productAvailability != None else "NA"

        return productAvailability

    # Get the args the user passed in
    def parse_args(self):
        # parser.print_help()
        args = parser.parse_args()

        self.args = copy.deepcopy(args)

    # Make sure that the mandatory args are passed in
    def process_args(self):
        # If the user doesn't give an item, close the program.
        if not self.args.item:
            print("Item argument not specified. Program terminating...")
            time.sleep(1)
            sys.exit(1)

        # If the user doesn't give the number of links to scrape, close the program.
        if not self.args.num or self.args.num <= 0:
            print("Number of links argument not specified. Program terminating...")
            time.sleep(1)
            sys.exit(1)

        if self.args.out == None:
            self.args.out = "out"

        if ".csv" not in self.args.out:
            self.args.out += ".csv"

        # Get all the parts of the search
        if self.provided:
            search = ""
            for element in self.args.item:
                search += element + " "

            self.args.item = search

    # Get all the necessary pages need to collect the amount of links the user wants
    def get_all_item_links(self):
        i = 0
        prevI = -1
        print("Headers: " + str(self.HEADERS))
        # Loop for extracting the link content from the href tag
        while i < self.args.num:
            # HTTP Request with random delay
            time.sleep(0.5 * random.random())
            webpage = requests.get(self.URL, headers=self.HEADERS)
            
            print(BLUE + f"Successfully connected to the #{self.page} webpage...\n" + RED + "Starting the soup...\n" +
                  GREEN + "Exracting all item links..." + NORM if webpage.status_code == 200 else "Connection failed.")

            # Soup Object containing all data
            soup = BeautifulSoup(webpage.content, "lxml")

            # Find all of the links connected to the item search
            links = soup.find_all(
                "a", attrs={'class': 'a-link-normal s-no-outline'})

            # List where are the links are going to be stored
            for link in links:
                if i == self.args.num:
                    break
                if "picassoRedirect" not in link.get('href'):
                    self.linksList.put(link.get('href'))
                    i += 1

            # Sometimes there are not enough items to gather data from so break out of connecting to webpages if the item counter isn't updating.
            if prevI != i:
                prevI = i
                self.page += 1
                self.URL = self.URL.split("&page=")[0] + f"&page={self.page}"
            else: 
                prevI = -1
                print(RED + "Could not find anymore plate links... Initiating data processing...\n" + NORM)
                return

    # Loop through all the item links retrieved and collect the data based on the args
    def process_item_links(self):
        # Finally get the data from each URL from the search
        while True:
            URL = "http://amazon.com" + self.linksList.get()
            # Making the HTTP Request
            time.sleep(0.5 * random.random())
            webpage = requests.get(URL, headers=self.HEADERS)

            if webpage.status_code != 200:
                print(f"Connection failed: {webpage.status_code}")

            # Creating the Soup Object containing all data
            soup = BeautifulSoup(webpage.content, "lxml")

            # Getting product title
            productTitle = self.get_item_title(soup)

            # Get product price
            productPrice = self.get_item_price(soup)

            # Get product rating
            productRating = self.get_product_rating(soup)

            # Get number of product reviews
            numberOfReviews = self.get_product_reviews(soup)

            # Get product availability
            productAvailability = self.get_product_avail(soup)

            productPrice = productPrice.replace(' ', '')

            if not productPrice.isalnum():
                productPrice = float(
                    productPrice.replace('$', '').replace(',', ''))
                if (self.args.lower and self.args.lower != 0) and (self.args.upper and self.args.upper != 0) and self.args.lower <= productPrice and productPrice <= self.args.upper:
                    item = Item(self.itemNum, productTitle, "$" + str(productPrice),
                                productRating, numberOfReviews, productAvailability, URL)
                    self.allItems.append(item)
                elif (self.args.lower == None or self.args.lower == 0) and self.args.upper and productPrice <= self.args.upper:
                    item = Item(self.itemNum, productTitle, "$" + str(productPrice),
                                productRating, numberOfReviews, productAvailability, URL)
                    self.allItems.append(item)
                elif (self.args.upper == None or self.args.upper == 0) and self.args.lower and self.args.lower <= productPrice:
                    item = Item(self.itemNum, productTitle, "$" + str(productPrice),
                                productRating, numberOfReviews, productAvailability, URL)
                    self.allItems.append(item)
                elif (self.args.upper == None or self.args.upper == 0) and (self.args.lower == None or self.args.lower == 0):
                    item = Item(self.itemNum, productTitle, "$" + str(productPrice),
                                productRating, numberOfReviews, productAvailability, URL)
                    self.allItems.append(item)
                self.itemNum += 1

            self.progress.update(self.task, advance=1)
            self.linksList.task_done()

    # Output the results to the console
    def output_data(self):
        output = "Item # |{:^95}| Price | Rank\n"
        output = output.format("Link")

        for _ in range(len(output)):
            output += "-"
        output += "\n"

        dir_path = "./csvs/"

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        
        # Print the items to the console
        with open("./csvs/" + self.args.out, "w", encoding="utf-8") as file:
            for item in self.allItems:
                output += item.to_string()
                item.write_to_csv(file)
        file.close()
        print(output)

        dir_path = "./jsons/"

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        # Open in write mode, we want to overwrite what was previously there
        items = {f"{self.args.item.strip()}": {}}
        with open("./jsons/" + self.args.out.split(".csv")[0] + ".json", "w", encoding="utf-8") as json_file:
            for item in self.allItems:
                items[f"{self.args.item.strip()}"][f"{item.get_num()}"] = item.json_format()
                item.convert_price_to_float()
            json_file.write(json.dumps(items, indent=4))
        json_file.close()

        # If they specified that they want the cheapest item, return the cheapest.
        if self.args.cheap:
            sorted(self.allItems, key=lambda item: item.price)
            print(GREEN + f"The cheapest item out of all the data pulled is: \n" + NORM)
            if len(self.allItems) > 0:
                print(sorted(self.allItems, key=lambda item: item.price)[0].to_string())
            else:
                print("No items were found that fit the arguments used.")

        # Print the selected settings
        print(RED + "Your selected settings for this soup were:\nItem: " + self.args.item + "\nLower bounds: " + str(self.args.lower) +
              "\nUpper bounds: " + str(self.args.upper) + "\nNumber of links: " + str(self.args.num) + "\nReturn the cheapest: " + str(self.args.cheap) + NORM)

        # Ask the user if they want to do additional scraping.
        if self.itemNum > 1:
            resp = input(f"Do you want to scrape an additional {self.args.num} {self.args.item.strip()}? (y/n)\n")
            if resp.lower() == "y":
                self.provided = False
                self.scrape()

def main():
    Scraper()

if __name__ == '__main__':
    main()
