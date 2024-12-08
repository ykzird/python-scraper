import pytest
import os
import sqlite3
from scraper.db_manager import DatabaseManager
from typing import Dict

@pytest.fixture
def db_manager():
    """Fixture to provide a test database manager"""
    test_db = 'test.db'
    db = DatabaseManager(test_db)
    yield db
    if os.path.exists(test_db):
        os.remove(test_db)

@pytest.fixture
def sample_product() -> Dict:
    """Fixture to provide sample product data"""
    return {
        'og:title': 'Test Product',
        'og:url': 'http://test.com',
        'product:price:amount': '99.99',
        'product-delivery-time': '1-2 days'
    }

def test_database_initialization(db_manager):
    """Test if database is properly initialized"""
    assert os.path.exists(db_manager.db_name)
    
    # Check if table exists and has correct structure
    with sqlite3.connect(db_manager.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        assert cursor.fetchone() is not None

def test_product_insertion(db_manager, sample_product):
    """Test if products can be inserted correctly"""
    db_manager.insert_product(sample_product)
    products = db_manager.get_all_products()
    
    assert len(products) == 1
    assert products[0]['Product name'] == sample_product['og:title']
    assert products[0]['URL'] == sample_product['og:url']
    assert float(products[0]['Price'].replace('€ ', '')) == float(sample_product['product:price:amount'])
    assert products[0]['Delivery time'] == sample_product['product-delivery-time']

def test_duplicate_prevention(db_manager, sample_product):
    """Test if duplicate entries are properly handled"""
    # Insert same data twice
    db_manager.insert_product(sample_product)
    db_manager.insert_product(sample_product)
    
    products = db_manager.get_all_products()
    assert len(products) == 1  # Should still only have one entry

def test_product_update(db_manager, sample_product):
    """Test if products can be updated correctly"""
    # Insert initial product
    db_manager.insert_product(sample_product)
    
    # Update product with new price
    updated_product = sample_product.copy()
    updated_product['product:price:amount'] = '149.99'
    db_manager.insert_product(updated_product)
    
    products = db_manager.get_all_products()
    assert len(products) == 1  # Should still have only one entry
    assert float(products[0]['Price'].replace('€ ', '')) == 149.99  # Price should be updated

def test_multiple_products(db_manager):
    """Test handling of multiple different products"""
    products = [
        {
            'og:title': 'Product 1',
            'og:url': 'http://test.com/1',
            'product:price:amount': '99.99',
            'product-delivery-time': '1-2 days'
        },
        {
            'og:title': 'Product 2',
            'og:url': 'http://test.com/2',
            'product:price:amount': '199.99',
            'product-delivery-time': '2-3 days'
        }
    ]
    
    for product in products:
        db_manager.insert_product(product)
    
    stored_products = db_manager.get_all_products()
    assert len(stored_products) == 2  # Should have both products

def test_invalid_product_data(db_manager):
    """Test handling of invalid product data"""
    invalid_product = {
        'og:title': None,
        'og:url': None,
        'product:price:amount': 'invalid',
        'product-delivery-time': None
    }
    
    with pytest.raises(Exception):
        db_manager.insert_product(invalid_product)

def test_get_all_products_empty(db_manager):
    """Test getting products from empty database"""
    products = db_manager.get_all_products()
    assert len(products) == 0  # Should return empty list