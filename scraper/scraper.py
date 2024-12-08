import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Optional
from .db_manager import DatabaseManager

def scrape_and_save_to_db(urls: List[str], properties: List[str], db_manager: DatabaseManager) -> List[dict]:
    """
    Iterates over URLs, scrapes the required properties, and saves the data to the database.
    
    Args:
        urls: List of URLs to scrape
        properties: List of meta properties to extract
        db_manager: DatabaseManager instance for saving data
        
    Returns:
        List of dictionaries containing the scraped data
    
    Raises:
        RequestException: If there's an error fetching the URL
        Exception: For any other unexpected errors
    """
    results = []
    
    for url in urls:
        try:
            # Set up headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            meta_data = {}
            # Scrape meta properties
            for prop in properties:
                meta_tag = soup.find('meta', {'property': prop})
                meta_data[prop] = meta_tag.get('content', '') if meta_tag else None

            # Scrape delivery time
            span_tag = soup.find('span', class_='product-delivery-time')
            meta_data['product-delivery-time'] = span_tag.get_text(strip=True).replace('timer', '') if span_tag else None

            # Validate required fields
            if not all(meta_data.get(prop) for prop in properties):
                logging.warning(f"Missing required properties for URL: {url}")
                continue

            # Save to database
            db_manager.insert_product(meta_data)
            results.append(meta_data)
            
            logging.info(f"Data successfully scraped and saved for URL: {url}")
            
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            continue
        except Exception as e:
            logging.error(f"Unexpected error processing {url}: {e}")
            continue

    return results

def validate_url(url: str) -> bool:
    """
    Validates if the given URL is properly formatted and accessible.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False