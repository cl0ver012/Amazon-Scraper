import argparse
import random
import sys
import time
from bs4 import BeautifulSoup
import requests

# Products
class Item():
    def __init__(self, title, price, rating, reviews, availability, URL):
        self.title = title
        self.price = price
        self.rating = rating
        self.reviews = reviews
        self.availability = availability
        self.URL = URL

    def getPrice(self):
        return float(self.price.replace('$', '').replace(',', '')) if self.price != "NA" else self.price

    def writeToCSV(self):
        File.write(f"{self.title},")
        File.write(f"{self.price},")
        File.write(f"{self.rating},")
        File.write(f"{self.reviews},")
        File.write(f"{self.availability},")
        File.write(f"{self.URL},\n")

    def toString(self):
        return BLUE + f"Product's title: {self.title}\n" + f"Product's price: {self.price}\n" + f"Product's rating: {self.rating}\n" + f"Total number of product reviews: {self.reviews}\n" + f"Product's availability: {self.availability}\n" + f"Product's URL: {self.URL}\n" + NORM 

# Get the title of the product
def getTitle(soup):
    productTitle = soup.find("span", attrs={"id": 'productTitle'})

    if productTitle != None:
        productTitle = productTitle.text.strip()
    else:
        productTitle = "NA"

    return productTitle

# Get the price of the product and any discounts
def getPrice(soup):
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
def getProductRating(soup):
    productRating = soup.find("span", attrs={"class": "reviewCountTextLinkedHistogram"})
    
    if productRating != None:
        productRating = productRating["title"].strip()
    else:
        productRating = "NA"

    return productRating

# Get the total number of product reviews
def getProductReviews(soup):
    numberOfReviews = soup.find("span", attrs={'id': 'acrCustomerReviewText'})

    if numberOfReviews != None:
        numberOfReviews = numberOfReviews.text.strip().replace(',', '')
    else:
        numberOfReviews = "NA"

    return numberOfReviews

# Gets product's availability (e.g in stock, how many left, out of stock)
def getProductAvailability(soup):
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

def main(URL):
    HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5', "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"})

    # Making the HTTP Request
    # time.sleep(0.5 * random.random())
    webpage = requests.get(URL, headers=HEADERS)

    # Creating the Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")
    print(GREEN + "Collecting item data..." + NORM)

    # Getting product title
    productTitle = getTitle(soup)

    # Get product price
    productPrice = getPrice(soup)

    # Get product rating
    productRating = getProductRating(soup)

    # Get number of product reviews
    numberOfReviews = getProductReviews(soup)

    # Get product availability
    productAvailability = getProductAvailability(soup)

    print(productPrice)
    productPrice = float(productPrice.replace('$', '').replace(',', '')) if productPrice != "NA" else "NA"
    
    if productPrice != "NA":
        if args.lower and args.upper and args.lower <= productPrice and productPrice <= args.upper:
            item = Item(productTitle, "$" + str(productPrice), productRating, numberOfReviews, productAvailability, URL)
            allItems.append(item)
        elif args.lower == None and args.upper and productPrice <= args.upper:
            item = Item(productTitle, "$" + str(productPrice), productRating, numberOfReviews, productAvailability, URL)
            allItems.append(item)
        elif args.upper == None and args.lower and args.lower <= productPrice:
            item = Item(productTitle, "$" + str(productPrice), productRating, numberOfReviews, productAvailability, URL)
            allItems.append(item)
        elif args.upper == None and args.lower == None:
            item = Item(productTitle, "$" + str(productPrice), productRating, numberOfReviews, productAvailability, URL)
            allItems.append(item)

if __name__ == '__main__':
    # Different possible colors
    BLUE = '\033[34m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    NORM = '\x1b[0m'
    tag = "@Moffi-bit"

    allItems = []

    # Print the banner to the console
    print(GREEN + """
    _                            ___                            
   /_\  _ __  __ _ ______ _ _   / __| __ _ _ __ _ _ __  ___ _ _ 
  / _ \| '  \/ _` |_ / _ \ ' \  \__ \/ _| '_/ _` | '_ \/ -_) '_|
 /_/ \_\_|_|_\__,_/__\___/_||_| |___/\__|_| \__,_| .__/\___|_|  
                                                 |_|                                                                                                                   
    """ + NORM)
    time.sleep(1)

    File = open("./out.csv", "a", encoding="utf-8")

    parser = argparse.ArgumentParser(description=GREEN + "Welcome to Amazon Scraper! Use this program to scrape amazon for your desired items.\nFor more information on how to use it run the program using -h or --help. (* = required field)" + RED + "\nCreator " + tag + NORM)
    parser.add_argument("-i", "--item", help="enter the item you want to search for (*)", type=str, nargs="+")
    parser.add_argument("-l", "--lower", help="enter the lower bound product price", type=int)
    parser.add_argument("-u", "--upper", help="enter the upper bound product price", type=int)
    parser.add_argument("-n", "--num", help="enter the number of links you want the program to look through (recommended 50+) (*)", type=int)
    parser.add_argument("-c", dest="cheap", help="add this argument if you want the program to return the cheapest item at the end of scraping", action="store_true")
    # parser.print_help()
    args = parser.parse_args()

    # If the user doesn't give an item, close the program.
    if args.item == None:
        print("Item argument not specified. Program terminating...")
        time.sleep(1)
        sys.exit()

    # If the user doesn't give the number of links to scrape, close the program.
    if args.num == None:
        print("Number of links argument not specified. Program terminating...")
        time.sleep(1)
        sys.exit()

    # Get all the parts of the search
    search = ""
    for element in args.item:
        search += element + " "

    args.item = search

    # Request information. Using headers to trick Amazon webpage
    HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36 Gecko/20100101 Firefox/50.0','Accept-Language': 'en-US'})
    URL = f"https://www.amazon.com/s?k={args.item}"

    page = 0
    i = 0
    linksList = []
    # Loop for extracting the link content from the href tag
    while i < args.num:
        # HTTP Request with random delay
        time.sleep(0.5 * random.random())
        webpage = requests.get(URL, headers=HEADERS)
        print(BLUE + "Successfully connected to the webpage...\n" + RED + "Starting the soup...\n" + GREEN + "Exracting all page item links..." + NORM if webpage.status_code == 200 else "Connection failed.")

        # Soup Object containing all data
        soup = BeautifulSoup(webpage.content, "lxml")
        
        # Find all of the links connected to the item search
        links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})

        # List where are the links are going to be stored
        for link in links:
            if i == args.num:
                break
            linksList.append(link.get('href'))
            i += 1

        page += 1
        URL += f"&page={page}"

    # Finally get the data from each URL from the search
    for link in linksList:
        main("http://amazon.com" + link)

    print(RED + "Your soup is ready!\n" + NORM)
    print(RED + "Your selected settings for this soup were:\nItem: " + args.item + "\nLower bounds: " + str(args.lower) + "\nUpper bounds: " + str(args.upper) + "\nNumber of links: " + str(args.num) + NORM)

    itemNum = 1
    # Print the items to the console
    for item in allItems:
        print(GREEN + f"Item #{itemNum}:\n" + NORM)
        print(item.toString())
        item.writeToCSV()
        itemNum += 1

    # If they specified that they want the cheapest item, return the cheapest.
    if args.cheap:
        lowestPrice = 100000000
        indexOfLowest = 0

        for i in range(len(allItems)):
            if allItems[i].getPrice() < lowestPrice:
                lowestPrice = allItems[i].getPrice()
                indexOfLowest = i

        print(GREEN + f"The cheapest item out of all the data pulled is: \n" + NORM)
        print(allItems[indexOfLowest].toString())

    File.close()