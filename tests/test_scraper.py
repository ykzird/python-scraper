import pytest
import requests
from scraper.scraper import validate_url, scrape_and_save_to_db
from unittest.mock import patch, MagicMock

def test_validate_url_success():
    """Test URL validation with valid URL"""
    with patch('requests.head') as mock_head:
        mock_head.return_value = MagicMock(status_code=200)
        assert validate_url('http://valid-url.com') == True

def test_validate_url_failure():
    """Test URL validation with invalid URL"""
    with patch('requests.head') as mock_head:
        mock_head.side_effect = requests.RequestException
        assert validate_url('http://invalid-url.com') == False

def test_scrape_with_invalid_url():
    """Test scraping behavior with invalid URL"""
    test_urls = ['http://invalid-url.com']
    test_properties = ['og:title', 'og:url']
    test_file = 'test_output.csv'
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException
        scrape_and_save_to_db(test_urls, test_properties, test_file)
        # Should not raise exception but log error

@patch('requests.get')
def test_scrape_empty_response(mock_get):
    """Test scraping with empty response"""
    mock_response = MagicMock()
    mock_response.text = ''
    mock_get.return_value = mock_response
    
    test_urls = ['http://test.com']
    test_properties = ['og:title', 'og:url']
    test_file = 'test_output.csv'
    
    scrape_and_save_to_db(test_urls, test_properties, test_file)
    # Should handle empty response gracefully