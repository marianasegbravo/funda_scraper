from fundascraping.scraper import FundaKoopScraping
import sys

# example usage: python main rotterdam 1 250000 500000 test

def main(city, nr_pages, min_price, max_price, filename):
    # Create an instance of the class
    scraping = FundaKoopScraping(city=city, nr_pages=nr_pages, min_price=min_price, max_price=max_price,
                                 filename=filename)

    # Step 2: Scrape data
    urls = scraping.retrieving_urls()

    # Step 3: Scrape information from each URL
    scraping.scrape_info()

    # Step 4: Clean the scraped data
    scraping.clean_data()

    # Step 5: Clean the scraped data
    scraping.clean_table()

    # Step 6: Save cleaned data to a CSV file
    scraping.save_to_csv()

    scraping.update_google_sheet()

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python main.py city nr_pages min_price max_price filename")
        sys.exit(1)

    city = sys.argv[1]
    nr_pages = int(sys.argv[2])
    min_price = int(sys.argv[3])
    max_price = int(sys.argv[4])
    filename = sys.argv[5]

    main(city, nr_pages, min_price, max_price, filename, )