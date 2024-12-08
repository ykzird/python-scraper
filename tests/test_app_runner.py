import pytest
import pandas as pd
from app.app_runner import fetch_data
from scraper.db_manager import DatabaseManager
import dash

@pytest.fixture
def sample_db_manager():
    """Fixture to provide a test database manager with sample data"""
    db = DatabaseManager('test.db')
    sample_products = [
        {
            'og:title': 'Test Product 1',
            'og:url': 'http://test.com/1',
            'product:price:amount': '99.99',
            'product-delivery-time': '1-2 days'
        },
        {
            'og:title': 'Test Product 2',
            'og:url': 'http://test.com/2',
            'product:price:amount': '199.99',
            'product-delivery-time': '2-3 days'
        }
    ]
    
    for product in sample_products:
        db.insert_product(product)
    
    yield db
    db.clear_table()

def test_fetch_data_structure(sample_db_manager):
    """Test if fetch_data returns correct DataFrame structure"""
    df = fetch_data(sample_db_manager)
    
    expected_columns = ['Product name', 'URL', 'Price', 'Delivery time']
    assert all(col in df.columns for col in expected_columns)
    assert len(df.columns) == len(expected_columns)
    assert isinstance(df, pd.DataFrame)

def test_fetch_data_content(sample_db_manager):
    """Test if fetch_data returns correct data content"""
    df = fetch_data(sample_db_manager)
    
    assert len(df) == 2  # Should have two products
    assert df['Price'].str.startswith('€').all()  # All prices should start with €
    assert df['URL'].str.startswith('http').all()  # All URLs should start with http