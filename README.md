# Amazon-Scraper: Find your perfect item!
          
Welcome to Amazon Scraper! Use this program to scrape amazon for your desired items. Functionality: scraping multiple amazon web pages for your item, setting a price range for your item, csv output, and more to come!

## Dependencies:

* bs4 (BeautifulSoup4)
* requests
* lxml (for parsing)

## How to use:

Get the repository: 

```
mkdir Amazon Scraper
cd Amazon Scraper
git clone https://github.com/Moffi-bit/Amazon-Scraper.git
```

Install the dependencies:

```
pip install bs4 requests lxml
```

Moving into the cloned repository:

```
cd Amazon-Scraper
```

Usage: 

```
usage: scrape.py [-h] [-i ITEM] [-l LOWER] [-u UPPER] [-n NUM]
```

Get all items within a price range (USD):

```
python3 scrape.py -i xbox s -l 200 -u 400 -n 100
```

Get all items above a price (USD):

```
python3 scrape.py -i yoga mats -l 10 -n 150
```

Get all items below a price (USD):

```
python3 scrape.py -i playstation -u 400 -n 100
```

Get all items no matter the price:

```
python3 scrape.py -i car tires -n 100
```

## CSV: 

Formatting:

```
title,price,rating,reviews,availability,url
```

The CSV contains **ALL** of the web page links scraped (even the ones that were not included in the output)

## Demo:

Coming soon...

## Future Improvements

* [x] Pulling product information
* [x] Output CSV
* [x] Multiple page scraping
* [ ] Consistency of finding product information
 
