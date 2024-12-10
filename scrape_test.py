import os
import requests
from bs4 import BeautifulSoup

url = 'https://azerty.nl/componenten'


response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
soup.find('<a href="/componenten/cpu"')
print(soup.prettify())