from scrape import Scraper

# Demo code for how to use the scraper without running the script with arguments
def main():
    # Scraper("garden sheers", 3, cheap=True)
    Scraper("xbox", 10, 100, cheap=True, out="xboxes")
    # Scraper("yoga mats", 80, 20, 50, False, "test")
    # Scraper("water balloon", 80, 20, 50, False, "test")
    # Scraper("chairs", 50, cheap=True, out="chairs")

if __name__ == "__main__":
    main()