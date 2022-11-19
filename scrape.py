import argparse
import random
import sys
import time
from bs4 import BeautifulSoup
import requests

def getTitle(soup):
    try:
        productTitle = soup.find("span", attrs={"id": 'productTitle'}).text.strip()
    except:
        productTitle = "No title."

    print(BLUE + f"Product's title: {productTitle}" +  NORM)
    File.write(f"{productTitle},")

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

    priceValue = float(productPrice.replace('$', ''))

    if args.lower and args.upper == None and priceValue >= args.lower:
        print(BLUE + f"Product's price: {productPrice}" + NORM)
        print(BLUE + f"Product's discount: {discount}" + NORM)
    elif args.upper and args.lower == None and priceValue <= args.upper:
        print(BLUE + f"Product's price: {productPrice}" + NORM)
        print(BLUE + f"Product's discount: {discount}" + NORM)
    elif args.upper and args.lower and args.lower <= priceValue <= args.upper:
        print(BLUE + f"Product's price: {productPrice}" + NORM)
        print(BLUE + f"Product's discount: {discount}" + NORM)
    elif args.upper == None and args.lower == None:
        print(BLUE + f"Product's price: {productPrice}" + NORM)
        print(BLUE + f"Product's discount: {discount}" + NORM)

    File.write(f"{productPrice},")
    File.write(f"{discount},")

def getProductRating(soup):
    try:
        productRating = soup.find("span", attrs={"class": "reviewCountTextLinkedHistogram"})["title"].strip()
    except:
        productRating = "No rating."

    print(BLUE + f"Product's rating: {productRating}" + NORM)
    File.write(f"{productRating},")

def getProductReviews(soup):
    try:
        numberOfReviews = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.strip().replace(',', '')
    except:
        numberOfReviews = "No reviews."
    
    print(BLUE + f"Total number of product reviews: {numberOfReviews}" + NORM)
    File.write(f"{numberOfReviews},")

def getProductAvailability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip().replace(',', '')
    except:
        available = "No availability."
    
    print(BLUE + f"Product's availability: {available}" + NORM)
    File.write(f"{available},")

def main(URL):
    HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5', "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"})

    # Making the HTTP Request
    webpage = requests.get(URL, headers=HEADERS)

    # Creating the Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")

    # Getting product title
    getTitle(soup)

    # Get product price
    getPrice(soup)

    # Get product rating
    getProductRating(soup)

    # Get number of product reviews
    getProductReviews(soup)

    # Get product availability
    getProductAvailability(soup)
    
    print(BLUE + f"Product's URL: {URL}\n" + NORM)
    File.write(f"{URL},\n")

if __name__ == '__main__':
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

    File = open("./out.csv", "a", encoding="utf-8")

    parser = argparse.ArgumentParser(description=GREEN + "Welcome to Amazon Scraper! Use this program to scrape amazon for your desired items.\nFor more information on how to use it run the program using -h or --help." + RED + "\nCreator: " + tag + NORM)
    parser.add_argument("-i", "--item", help="enter the item you want to search for", type=str)
    parser.add_argument("-l", "--lower", help="enter the lower bound product price", type=int)
    parser.add_argument("-u", "--upper", help="enter the upper bound product price", type=int)
    parser.print_help()
    args = parser.parse_args()

    # If the user doesn't give an item, close the program.
    if args.item == None:
        print("Item argument not specified. Program terminating...")
        time.sleep(1)
        sys.exit()

    # item = input("Enter an item")
    # Request information. Using headers to trick Amazon webpage
    HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36 Gecko/20100101 Firefox/50.0','Accept-Language': 'en-US'})
    URL = f"https://www.amazon.com/s?k={args.item}"
    
    # HTTP Request with random delay
    time.sleep(0.5 * random.random())
    webpage = requests.get(URL, headers=HEADERS)
    print(webpage)

    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")
    
    # Find all of the links connected to the item search
    links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})

    # List where are the links are going to be stored
    linksList = []

    # Loop for extracting the link content from the href tag
    for link in links:
        linksList.append(link.get('href'))
    
    # Finally get the data from each URL from the search
    count = 1
    for link in linksList:
        print(GREEN + f"Item #{count}:" + NORM)
        main("http://amazon.com" + link)
        count += 1

    File.close()
    

    

