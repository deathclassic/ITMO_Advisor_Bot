# Download HTML pages
import requests
from bs4 import BeautifulSoup

def fetch_html(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")

def download_pdf(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()
    return response.content

