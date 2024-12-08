import sqlite3
import logging
from typing import List, Dict
from datetime import datetime

def migrate_database(db_name: str = 'product_data.db') -> None:
    """
    Migrates the database to include unique constraints and removes duplicates.
    """
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            
            # Create a temporary table with the new structure
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,  -- Added UNIQUE constraint
                    price REAL NOT NULL,
                    delivery_time TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(product_name, url, price)  -- Composite unique constraint
                )
            ''')
            
            # Copy unique records to the new table
            cursor.execute('''
                INSERT OR IGNORE INTO products_new (product_name, url, price, delivery_time, timestamp)
                SELECT DISTINCT product_name, url, price, delivery_time, MIN(timestamp)
                FROM products
                GROUP BY product_name, url, price
            ''')
            
            # Drop the old table
            cursor.execute('DROP TABLE IF EXISTS products')
            
            # Rename the new table to the original name
            cursor.execute('ALTER TABLE products_new RENAME TO products')
            
            # Create an index for faster lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON products(url)')
            
            conn.commit()
            
        logging.info("Database migration completed successfully")
    except Exception as e:
        logging.error(f"Error during database migration: {e}")
        raise

def check_duplicates(db_name: str = 'product_data.db') -> List[Dict]:
    """
    Check for any remaining duplicate entries in the database.
    """
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT product_name, url, COUNT(*) as count
                FROM products
                GROUP BY product_name, url
                HAVING COUNT(*) > 1
            ''')
            duplicates = cursor.fetchall()
            return duplicates
    except Exception as e:
        logging.error(f"Error checking duplicates: {e}")
        raise

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    migrate_database()
    duplicates = check_duplicates()
    
    if duplicates:
        logging.warning(f"Found {len(duplicates)} duplicate entries after migration")
        for dup in duplicates:
            logging.warning(f"Duplicate: {dup}")
    else:
        logging.info("No duplicates found after migration")