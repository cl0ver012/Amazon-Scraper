# Amazon-Scraper: Find your perfect item!

![Amazon Scraper](https://i.imgur.com/Dh9IW25.png)

Functionality: scraping multiple amazon web pages for your item, setting a price range for your item, csv output, and more!

## Dependencies:

* bs4 (BeautifulSoup4)
* requests
* lxml 

## How to use (NOTE: -i or --item and -n or --num are required fields):

### Get the repository: 

```
mkdir Amazon Scraper
cd Amazon Scraper
git clone https://github.com/Moffi-bit/Amazon-Scraper.git
```

### Install the dependencies:

```
py -m pip install bs4 requests lxml
```

### Moving into the cloned repository:

```
cd Amazon-Scraper
```

### Usage: 

```
usage: scrape.py [-h] [-i ITEM [ITEM ...]] [-l LOWER] [-u UPPER] [-n NUM] [-c]
Note: Adding -c to the arguments will cause the program to print the cheapest item at the end of scraping
```

#### Individual Commands:

**-i or --item:**

```
py scrape.py -i xbox 
```
OR
```
py scrape.py --item xbox 
```

Tells the program that the item you're looking for is a xbox.

**-l or --lower:**

```
py scrape.py -l 50
```
OR
```
py scrape.py --lower 50
```

Tells the program that the price minimum (lower bound) is 50.

**-u or --upper:**

```
py scrape.py -u 500
```
OR
```
py scrape.py --upper 500
```

Tells the program that the price maximum (upper bound) is 500.

**-n or --num:**

```
py scrape.py -n 100
```
OR
```
py scrape.py --num 100
```

Tells the program that the number of item links you want to pull data from is 100.

**-c:**

```
py scrape.py -c
```

Tells the program that you want it to output the cheapest item after it's scraped all links.

#### Examples of Possible Run Commands:

Get all items within a price range (USD):

```
py scrape.py -i xbox s -l 200 -u 400 -n 100
```

Get all items above a price (USD):

```
py scrape.py -i yoga mats -l 10 -n 150
```

Get all items below a price (USD):

```
py scrape.py -i playstation -u 400 -n 100
```

Get all items no matter the price:

```
py scrape.py -i car tires -n 100
```

Get the cheapest item of the items scraped:

```
py scrape.py -i rtx 3090 -n 50 -c
```

## CSV: 

Formatting:

```
title,price,rating,reviews,availability,url
```

The CSV contains **ALL** of the relevant items scraped

## Future Improvements

* [x] Pulling product information
* [x] Output CSV
* [x] Multiple page scraping
* [x] Return the cheapest item 
* [ ] Becoming stealthier (e.g optimized headers, etc)
* [x] Consistency of finding product information
 
