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

    def toString(self):
        return BLUE + f"Product's title: {self.title}\n" + f"Product's price: {self.price}\n" + f"Product's rating: {self.rating}\n" + f"Total number of product reviews: {self.reviews}\n" + f"Product's availability: {self.availability}\n" + f"Product's URL: {self.URL}\n" + NORM 

# Get the title of the product
def getTitle(soup):
    try:
        productTitle = soup.find("span", attrs={"id": 'productTitle'}).text.strip()
    except:
        productTitle = "No title."

    File.write(f"{productTitle},")

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

    File.write(f"{productPrice},")
    File.write(f"{discount},")

    return productPrice

# Get the product's rating out of 5.0
def getProductRating(soup):
    try:
        productRating = soup.find("span", attrs={"class": "reviewCountTextLinkedHistogram"})["title"].strip()
    except:
        productRating = "No rating."

    File.write(f"{productRating},")

    return productRating

# Get the total number of product reviews
def getProductReviews(soup):
    try:
        numberOfReviews = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.strip().replace(',', '')
    except:
        numberOfReviews = "No reviews."

    File.write(f"{numberOfReviews},")

    return numberOfReviews

# Gets product's availability (e.g in stock, how many left, out of stock)
def getProductAvailability(soup):
    try:
        productAvailabilityDiv = soup.find("div", attrs={'id': 'availability'})
        productAvailability = productAvailabilityDiv.find("span").string.strip().replace(',', '')
    except:
        productAvailability = "No availability."
    
    File.write(f"{productAvailability},")

    return productAvailability

def main(URL):
    HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5', "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"})

    # Making the HTTP Request
    webpage = requests.get(URL, headers=HEADERS)

    # Creating the Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")
    print(GREEN + "Collecting website data..." + NORM)

    # Getting product title
    productTitle = getTitle(soup)

    # Get product price
    productPrice = float(getPrice(soup).replace('$', ''))

    # Get product rating
    productRating = getProductRating(soup)

    # Get number of product reviews
    numberOfReviews = getProductReviews(soup)

    # Get product availability
    productAvailability = getProductAvailability(soup)

    if args.lower and args.upper and args.lower <= productPrice <= args.upper:
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

    File.write(f"{URL},\n")

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
    parser.add_argument("-i", "--item", help="enter the item you want to search for (*)", type=str)
    parser.add_argument("-l", "--lower", help="enter the lower bound product price", type=int)
    parser.add_argument("-u", "--upper", help="enter the upper bound product price", type=int)
    parser.add_argument("-n", "--num", help="enter the number of links you want the program to look through (recommended n <= 50) (*)", type=int)
    parser.print_help()
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

    # Request information. Using headers to trick Amazon webpage
    HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36 Gecko/20100101 Firefox/50.0','Accept-Language': 'en-US'})
    URL = f"https://www.amazon.com/s?k={args.item}"
    
    # HTTP Request with random delay
    time.sleep(0.5 * random.random())
    webpage = requests.get(URL, headers=HEADERS)
    print(BLUE + "Successfully connected to the webpage...\n" + RED + "Starting the soup..." + NORM if webpage.status_code == 200 else "Connection failed.")

    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")
    
    # Find all of the links connected to the item search
    links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})

    # List where are the links are going to be stored
    linksList = []

    # Loop for extracting the link content from the href tag
    i = 0
    for link in links:
        if i < args.num:
            linksList.append(link.get('href'))
            i += 1
        else:
            break
    
    # Finally get the data from each URL from the search
    for link in linksList:
        main("http://amazon.com" + link)

    print(RED + "Your soup is ready!\n" + NORM)
    print(RED + "Your selected settings for this soup were:\nItem: " + args.item + "\nLower bounds: " + str(args.lower) + "\nUpper bounds: " + str(args.upper) + "\nNumber of links: " + str(args.num) + NORM)

    count = 1
    # Print the items to the console
    for item in allItems:
        print(GREEN + f"Item #{count}:\n" + NORM)
        print(item.toString())
        count += 1

    File.close()
    

    

