import argparse
import copy
import random
import sys
import time
from bs4 import BeautifulSoup
import requests

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

parser = argparse.ArgumentParser(description=GREEN + "Welcome to Amazon Scraper! Use this program to scrape amazon for your desired items.\nFor more information on how to use it run the program using -h or --help. (* = required field)" + RED + "\nCreator " + tag + NORM)
parser.add_argument("-i", "--item", help="enter the item you want to search for (*)", type=str, nargs="+")
parser.add_argument("-l", "--lower", help="enter the lower bound product price", type=int)
parser.add_argument("-u", "--upper", help="enter the upper bound product price", type=int)
parser.add_argument("-n", "--num", help="enter the number of links you want the program to look through (recommended 50+) (*)", type=int)
parser.add_argument("-c", dest="cheap", help="add this argument if you want the program to return the cheapest item at the end of scraping", action="store_true")

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

    def getPrice(self):
        return float(self.price.replace('$', '').replace(',', '')) if self.price != "NA" else self.price

    def writeToCSV(self, file):
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
        
    def toString(self):
        # item num, link, price, rank
        output = " {:^7} | {:<60} | {:<7} | {:^7} "
        output = output.format(GREEN + f"{self.num}" + NORM, f"{self.URL[:95]}", GREEN + f"{self.price}" + NORM, self.eval(), width=90)

        return output + "\n" + NORM
    
class Scraper():
    def __init__(self, item: str = None, num: int = 0, lower: int = 0, upper: int = 0, cheap: bool = False):
        self.parseArgs()
        if self.args.item and self.args.num and self.args.num != 0:
            self.provided = True
            self.processArgs()
            return

        self.args.item = item
        self.args.lower = lower
        self.args.upper = upper
        self.args.num = num
        self.args.cheap = cheap
        self.provided = False
        
        self.processArgs()

    def scrape(self):
        self.HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36 Gecko/20100101 Firefox/50.0','Accept-Language': 'en-US', "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"})
        self.URL = f"https://www.amazon.com/s?k={self.args.item}"
        # Get all the item links from every page needed
        linksList = self.getItemLinksFromPages()
        
        # Process all the item links and get the list including the relevant ones
        allItems = self.processItemLinks(linksList)

        # Soup is done
        print(RED + "Your soup is ready!\n" + NORM)

        # Output the data
        self.outputData(allItems)

        # Print the selected settings
        print(RED + "Your selected settings for this soup were:\nItem: " + self.args.item + "\nLower bounds: " + str(self.args.lower) + "\nUpper bounds: " + str(self.args.upper) + "\nNumber of links: " + str(self.args.num) + "\nReturn the cheapest: " + str(self.args.cheap) + NORM)

    # Get the title of the product
    def getTitle(self, soup):
        productTitle = soup.find("span", attrs={"id": 'productTitle'})

        if productTitle != None:
            productTitle = productTitle.text.strip()
        else:
            productTitle = "NA"

        return productTitle

    # Get the price of the product and any discounts
    def getPrice(self, soup):
        discount = soup.find("span", attrs={"class": "reinventPriceSavingsPercentageMargin savingsPercentage"})
        priceSpan = soup.select_one("span.a-price.reinventPricePriceToPayMargin.priceToPay, span.a-price.apexPriceToPay") 

        # Check to see if there is a price
        if priceSpan:
            price = priceSpan.find("span", {"class": "a-offscreen"}).text.strip() 
        else:
            price = None
    
        # Check to see if there is a discounted price, else just use the normal price or to NA.
        if discount: 
            discount = discount.text.strip() 
            productPrice = soup.find("span", attrs={"class": "a-price a-text-price"}).text.strip() 
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
    def getProductRating(self, soup):
        productRating = soup.find("span", attrs={"class": "reviewCountTextLinkedHistogram"})
        
        if productRating != None:
            productRating = productRating["title"].strip()
        else:
            productRating = "NA"

        return productRating

    # Get the total number of product reviews
    def getProductReviews(self, soup):
        numberOfReviews = soup.find("span", attrs={'id': 'acrCustomerReviewText'})

        if numberOfReviews != None:
            numberOfReviews = numberOfReviews.text.strip().replace(',', '')
        else:
            numberOfReviews = "NA"

        return numberOfReviews

    # Gets product's availability (e.g in stock, how many left, out of stock)
    def getProductAvailability(self, soup):
        productAvailabilityDiv = soup.find("div", attrs={'id': 'availability'})

        if productAvailabilityDiv != None:
            productAvailability = productAvailabilityDiv.find("span")
            if productAvailability != None:
                productAvailability = productAvailability.text.strip().replace(',', '')
        else:
            productAvailability = "NA"

        if productAvailability == "NA":
            productAvailability = soup.find("span", attrs={"class": "a-size-medium"})
            productAvailability = productAvailability.text.strip() if productAvailability != None else "NA"

        return productAvailability

    # Get the args the user passed in
    def parseArgs(self):
        # parser.print_help()
        args = parser.parse_args()

        self.args = copy.deepcopy(args)

    # Make sure that the mandatory args are passed in
    def processArgs(self):
        # If the user doesn't give an item, close the program.
        if self.args.item == None:
            print("Item argument not specified. Program terminating...")
            time.sleep(1)
            sys.exit(1)

        # If the user doesn't give the number of links to scrape, close the program.
        if self.args.num == None or self.args.num == 0:
            print("Number of links argument not specified. Program terminating...")
            time.sleep(1)
            sys.exit(1)
        
        # Get all the parts of the search
        if self.provided:
            search = ""
            for element in self.args.item:
                search += element + " "

            self.args.item = search

        self.scrape()

    # Get all the necessary pages need to collect the amount of links the user wants
    def getItemLinksFromPages(self):
        page = 1
        i = 0
        linksList = []
        # Loop for extracting the link content from the href tag
        while i < self.args.num:
            # HTTP Request with random delay
            time.sleep(0.5 * random.random())
            webpage = requests.get(self.URL, headers=self.HEADERS)
            print(BLUE + f"Successfully connected to the #{page} webpage...\n" + RED + "Starting the soup...\n" + GREEN + "Exracting all item links..." + NORM if webpage.status_code == 200 else "Connection failed.")

            # Soup Object containing all data
            soup = BeautifulSoup(webpage.content, "lxml")
            
            # Find all of the links connected to the item search
            links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})

            # List where are the links are going to be stored
            for link in links:
                if i == self.args.num:
                    break
                linksList.append(link.get('href'))

                # Don't use links where you were redirected
                if "picassoRedirect" in linksList[i]:
                    linksList.remove(linksList[i])
                    i -= 1 

                i += 1

            self.URL += f"&page={page}"
            page += 1
        
        return linksList

    # Loop through all the item links retrieved and collect the data based on the args
    def processItemLinks(self, linksList):
        # Where the items will be stored
        allItems = []
        itemNum = 1

        # Finally get the data from each URL from the search
        for link in linksList:
            URL = "http://amazon.com" + link
            # Making the HTTP Request
            time.sleep(0.5 * random.random())
            webpage = requests.get(URL, headers=self.HEADERS)

            # Creating the Soup Object containing all data
            soup = BeautifulSoup(webpage.content, "lxml")
            print(GREEN + "Collecting item data..." + NORM)

            # Getting product title
            productTitle = self.getTitle(soup)

            # Get product price
            productPrice = self.getPrice(soup)

            # Get product rating
            productRating = self.getProductRating(soup)

            # Get number of product reviews
            numberOfReviews = self.getProductReviews(soup)

            # Get product availability
            productAvailability = self.getProductAvailability(soup)

            productPrice = productPrice.replace(' ', '')

            if not productPrice.isalnum():
                productPrice = float(productPrice.replace('$', '').replace(',', '')) 
                if (self.args.lower and self.args.lower != 0) and (self.args.upper and self.args.upper != 0) and self.args.lower <= productPrice and productPrice <= self.args.upper:
                    item = Item(itemNum, productTitle, "$" + str(productPrice), productRating, numberOfReviews, productAvailability, URL)
                    allItems.append(item)
                elif (self.args.lower == None or self.args.lower == 0) and self.args.upper and productPrice <= self.args.upper:
                    item = Item(itemNum, productTitle, "$" + str(productPrice), productRating, numberOfReviews, productAvailability, URL)
                    allItems.append(item)
                elif (self.args.upper == None or self.args.upper == 0) and self.args.lower and self.args.lower <= productPrice:
                    item = Item(itemNum, productTitle, "$" + str(productPrice), productRating, numberOfReviews, productAvailability, URL)
                    allItems.append(item)
                elif (self.args.upper == None or self.args.upper == 0) and (self.args.lower == None or self.args.lower == 0):
                    item = Item(itemNum, productTitle, "$" + str(productPrice), productRating, numberOfReviews, productAvailability, URL)
                    allItems.append(item)
                itemNum += 1

        return allItems

    # Output the results to the console
    def outputData(self, allItems):
        output = "Item # |{:^95}| Price | Rank\n"
        output = output.format("Link")
        
        for _ in range(len(output)):
            output += "-"
        output += "\n"

        # Print the items to the console
        with open("./out.csv", "a", encoding="utf-8") as file:
            for item in allItems:
                output += item.toString()
                item.writeToCSV(file)
        file.close()
        print(output)

        # If they specified that they want the cheapest item, return the cheapest.
        if self.args.cheap:
            allItems = sorted(allItems, key=lambda item: item.price)
            print(GREEN + f"The cheapest item out of all the data pulled is: \n" + NORM)
            print(allItems[0].toString())

def main():
    Scraper()

if __name__ == '__main__':
    main()