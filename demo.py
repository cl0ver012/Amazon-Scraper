from scrape import Scraper

# Demonstrates how you can re-use the same object to keep on scraping if you decide you want more chairs
def scrape_again():
    # Scrapes for data from 50 chairs
    s = Scraper("chairs", 50, cheap=True, out="chairs")

    # Scrapes for data from another 50 chairs (new chairs)
    s.scrape()

# Demo code for how to use the scraper without running the script with arguments
def main():
    # Scraper("garden sheers", 3, cheap=True)
    # Scraper("xbox", 10, 100, cheap=True)
    # Scraper("yoga mats", 80, 20, 50, False, "test")
    scrape_again()

if __name__ == "__main__":
    main()