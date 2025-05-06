import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def _normalize_url(url: str) -> str:
    """Ensure that the URL starts with a proper scheme."""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    return url

def _fetch_page(url: str) -> str:
    """Fetch the webpage content with error handling."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.RequestException as e:
        return Exception(f"Error fetching the page: {e}")

def _extract_info(html: str, url: str) -> dict:
    """Extract title, meta description, and main text content from the webpage."""
    soup = BeautifulSoup(html, 'html.parser')

    # Get the title text if available
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else 'No title found'

    # Get the meta description, if available
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_desc_tag.get('content', '').strip() if meta_desc_tag else 'No meta description found'

    # Extract visible text by joining all stripped strings. This may include extra site navigation text.
    text_list = list(soup.stripped_strings)
    text_content = " ".join(text_list)

    # Other pertinent information can include parsed URL components.
    parsed_url = urlparse(url)
    info = {
        'url': url,
        'domain': parsed_url.netloc,
        'page_title': title,
        'meta_description': meta_description,
        'content_preview': text_content[:1000]  # limiting to the first 1000 characters
    }
    return info

def get_website_info(url):
    # Normalize the URL (add scheme if missing)
    input_url = _normalize_url(url)
    
    # Fetch webpage data
    try: 
        html = _fetch_page(input_url)
    
        # Extract information from the HTML
        info = _extract_info(html, input_url)
    except Exception as e:
        # print(f"Error with {url}")
        info = {"url": input_url,
                "domain": urlparse(input_url).netloc}
    return info 

