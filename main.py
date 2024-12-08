from scraper.db_manager import DatabaseManager
from scraper.scraper import scrape_and_save_to_db, validate_url
from app.app_runner import run_application
import logging
import os

# Set up logging
log_file = os.path.join("logs", "scraping_bot.log")
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    #file_name = 'product_data.csv'
    db_manager = DatabaseManager('product_data.db')
    db_manager.create_table()
    urls = [
        'https://azerty.nl/product/amd-ryzen-7-9800x3d-processor-4-7-ghz-5-2-ghz/8739079',
        'https://azerty.nl/product/asrock-x870-pro-rs-wifi-moederbord/8599265',
        'https://azerty.nl/product/g-skill-trident-z5-neo-rgb-f5-6000j3038f16gx2-tz5nr-geheugen/4975893'
    ]
    properties = [
        "og:title",
        "og:url",
        "product:price:amount"
    ]
    #headers = properties + ['product-delivery-time']

    # Initialize the CSV
   # initialize_csv(file_name, headers)

    # Scrape data and write it to the CSV
    #scrape_and_write_to_csv(urls, properties, file_name)

    valid_urls = [url for url in urls if validate_url(url)]
    if len(valid_urls) != len(urls):
        logging.warning(f"{len(urls) - len(valid_urls)} invalid URLs were skipped")

    scraped_data = scrape_and_save_to_db(urls, properties, db_manager)



    # Run the Dash application
    run_application(db_manager)