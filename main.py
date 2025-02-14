import argparse
import asyncio
import logging
import os
import time
from urllib.parse import urlparse
from collections import defaultdict
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
from modules.selenium_setup import setup_selenium
from modules.input_extractor import extract_input_fields
from modules.network_analyzer import analyze_network_requests
from modules.hidden_parameter_extractor import extract_hidden_parameters
from modules.js_analyzer import search_js_files
from modules.reflected_value_tester import test_reflected_values
from modules.crawler import crawl_website
from modules.utils import ensure_url_scheme, save_results_to_json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("analysis.log"), logging.StreamHandler()]
)

# Schema for results validation
SCHEMA = {
    "type": "object",
    "properties": {
        "input_fields": {"type": "array"},
        "network_requests": {"type": "array"},
        "hidden_parameters": {"type": "object"},
        "js_files": {"type": "array"},
        "reflected_values": {"type": "array"},
        "errors": {"type": "array"},
    },
    "required": ["input_fields", "network_requests", "hidden_parameters", "js_files", "reflected_values", "errors"],
}

# Metrics tracking
metrics = defaultdict(list)

def track_metrics(func):
    """Decorator to track performance metrics."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        metrics[func.__name__].append(elapsed_time)
        return result
    return wrapper

@track_metrics
async def analyze_url(url, args):
    """Analyze a single URL."""
    url = ensure_url_scheme(url)
    logging.info(f"Using URL: {url}")

    base_domain = urlparse(url).netloc
    results = {
        'input_fields': [],
        'network_requests': [],
        'hidden_parameters': {},
        'js_files': [],
        'reflected_values': [],
        'errors': []
    }

    try:
        logging.info("Setting up Selenium to fetch JavaScript-rendered content...")
        driver = setup_selenium(url)
        if not driver:
            results['errors'].append("Failed to set up Selenium.")
            return results

        if args.input_fields:
            logging.info("Extracting input fields from the page...")
            try:
                results['input_fields'] = extract_input_fields(driver)
            except Exception as e:
                results['errors'].append(f"Error extracting input fields: {e}")

        if args.network_requests:
            logging.info("Analyzing network requests...")
            try:
                results['network_requests'] = analyze_network_requests(driver, base_domain)
            except Exception as e:
                results['errors'].append(f"Error analyzing network requests: {e}")

        if args.hidden_parameters:
            logging.info("Extracting hidden parameters...")
            try:
                results['hidden_parameters'] = extract_hidden_parameters(driver)
            except Exception as e:
                results['errors'].append(f"Error extracting hidden parameters: {e}")

        if args.js_files:
            logging.info("Searching JavaScript files for parameters...")
            try:
                results['js_files'] = await search_js_files(driver, url, base_domain)
            except Exception as e:
                results['errors'].append(f"Error searching JavaScript files: {e}")

        if args.reflected_values:
            logging.info("Testing for reflected values using 'MrColonel'...")
            try:
                results['reflected_values'] = test_reflected_values(driver, base_domain)
            except Exception as e:
                results['errors'].append(f"Error testing reflected values: {e}")

        if args.crawl:
            logging.info("Crawling the website to discover additional pages...")
            try:
                visited_urls = crawl_website(driver, url, base_domain, max_depth=args.crawl_depth)
                logging.info(f"Visited URLs: {visited_urls}")
            except Exception as e:
                results['errors'].append(f"Error crawling website: {e}")

    finally:
        if driver:
            driver.quit()

    if validate_results(results):
        save_results_to_json(results, base_domain)
    else:
        logging.error("Results validation failed. Not saving to JSON.")

    return results

async def main():
    parser = argparse.ArgumentParser(description="Analyze a website for input fields, network requests, hidden parameters, and reflected values.")
    parser.add_argument('-u', '--url', required=True, help="Input [Filename | URL]")
    parser.add_argument('--input-fields', action='store_true', help="Extract input fields from the page.")
    parser.add_argument('--network-requests', action='store_true', help="Analyze network requests.")
    parser.add_argument('--hidden-parameters', action='store_true', help="Extract hidden parameters.")
    parser.add_argument('--js-files', action='store_true', help="Search JavaScript files for parameters.")
    parser.add_argument('--reflected-values', action='store_true', help="Test for reflected values.")
    parser.add_argument('--crawl', action='store_true', help="Crawl the website to discover additional pages.")
    parser.add_argument('--crawl-depth', type=int, default=2, help="Maximum depth for crawling (default: 2).")
    args = parser.parse_args()

    if args.url.endswith('.txt'):
        with open(args.url, 'r') as file:
            urls = file.read().splitlines()
    else:
        urls = [args.url]

    tasks = [analyze_url(url, args) for url in urls]
    results = await asyncio.gather(*tasks)

    for result in results:
        logging.info(f"Results for {result.get('url')}: {result}")

if __name__ == "__main__":
    asyncio.run(main())