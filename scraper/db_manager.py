import sqlite3
import logging
from typing import List, Dict

class DatabaseManager:
    def __init__(self, db_name: str = 'product_data.db'):
        """Initialize database connection and create table if it doesn't exist"""
        self.db_name = db_name
        self.create_table()

    def create_table(self) -> None:
        """Create the products table if it doesn't exist"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        url TEXT NOT NULL UNIQUE,
                        price REAL NOT NULL,
                        delivery_time TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index for faster lookups
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_url 
                    ON products(url)
                ''')
                
                conn.commit()
            logging.info(f"Database '{self.db_name}' initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    def insert_product(self, product_data: Dict) -> None:
        """
        Insert a product into the database, updating if it already exists.
        
        Args:
            product_data: Dictionary containing product information with keys:
                         'og:title', 'og:url', 'product:price:amount', 'product-delivery-time'
        """
        try:
            # Validate required fields
            if not all(key in product_data for key in ['og:title', 'og:url', 'product:price:amount']):
                raise ValueError("Missing required product data fields")

            # Ensure price is a valid float
            try:
                price = float(product_data.get('product:price:amount', 0))
            except (TypeError, ValueError):
                raise ValueError("Invalid price format")

            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO products (product_name, url, price, delivery_time)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        product_name = excluded.product_name,
                        price = excluded.price,
                        delivery_time = excluded.delivery_time,
                        timestamp = CURRENT_TIMESTAMP
                ''', (
                    product_data.get('og:title'),
                    product_data.get('og:url'),
                    price,
                    product_data.get('product-delivery-time')
                ))
                conn.commit()
            logging.info(f"Product data upserted successfully: {product_data.get('og:title')}")
        except Exception as e:
            logging.error(f"Error upserting product data: {e}")
            raise

    def get_all_products(self) -> List[Dict]:
        """
        Retrieve all products from the database.
        
        Returns:
            List of dictionaries containing product information with formatted prices
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        id,
                        product_name,
                        url,
                        price,
                        delivery_time,
                        timestamp
                    FROM products 
                    ORDER BY timestamp DESC
                ''')
                rows = cursor.fetchall()
                return [{
                    'Product name': row['product_name'],
                    'URL': row['url'],
                    'Price': f"€ {float(row['price']):.2f}",
                    'Delivery time': row['delivery_time']
                } for row in rows]
        except Exception as e:
            logging.error(f"Error retrieving products: {e}")
            raise

    def clear_table(self) -> None:
        """Clear all records from the products table"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM products')
                conn.commit()
            logging.info("Products table cleared successfully")
        except Exception as e:
            logging.error(f"Error clearing products table: {e}")
            raise

    def close(self) -> None:
        """Close any open database connections"""
        try:
            logging.info(f"Database '{self.db_name}' closed successfully.")
        except Exception as e:
            logging.error(f"Error closing database: {e}")
            raise