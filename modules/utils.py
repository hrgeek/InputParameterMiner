import base64
import json
import os
import re
import logging
import requests
import requests_cache
from urllib.parse import urlparse, urlunparse, unquote
from tenacity import retry, stop_after_attempt, wait_exponential
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

# Enable caching
requests_cache.install_cache('http_cache', expire_after=3600)  # Cache for 1 hour

def ensure_url_scheme(url):
    """Ensure the URL has a scheme (http:// or https://). If not, add https://."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "https://" + url
        parsed_url = urlparse(url)  # Re-parse to validate the new URL
    
    # Validate the URL
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {url} - Missing domain or invalid format.")
    
    return url

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_url(url):
    """Fetch the content of a URL with retries."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        raise

def process_url(url):
    """Process a single URL."""
    try:
        content = fetch_url(url)
        return {"url": url, "content": content}
    except Exception as e:
        logging.error(f"Error processing {url}: {e}")
        return None

def process_urls_parallel(urls):
    """Process a list of URLs in parallel."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_url, urls))
    return results

# Example usage
if __name__ == "__main__":
    urls = ["https://example.com", "https://example.org"]
    results = process_urls_parallel(urls)
    print(results)