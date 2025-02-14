#!/usr/bin/env python3


import argparse
import asyncio
from modules.selenium_setup import setup_selenium
from modules.input_extractor import extract_input_fields
from modules.network_analyzer import analyze_network_requests
from modules.hidden_parameter_extractor import extract_hidden_parameters
from modules.js_analyzer import search_js_files
from modules.reflected_value_tester import test_reflected_values
from modules.crawler import crawl_website
from modules.utils import ensure_url_scheme, save_results_to_json

def print_welcome_message():
    welcome_message = """
    ========================================================
    Welcome to Input Parameter Miner!
    A tool to analyze websites for input fields, network requests,
    hidden parameters, and reflected values.
    Created by MrColonel\!/
    ========================================================
    """
    print(welcome_message)

async def analyze_url(url, output_dir=None, crawl=False, max_depth=2):
    """Analyze a single URL."""
    url = ensure_url_scheme(url)
    print(f"Using URL: {url}")

    base_domain = urlparse(url).netloc

    # Set up Selenium
    print("\nSetting up Selenium to fetch JavaScript-rendered content...")
    driver = setup_selenium(url)
    if not driver:
        print("Failed to set up Selenium. Exiting.")
        return

    # Collect all results
    results = {
        'input_fields': extract_input_fields(driver),
        'network_requests': analyze_network_requests(driver, base_domain),
        'hidden_parameters': extract_hidden_parameters(driver),
        'js_files': await search_js_files(driver, url, base_domain),
        'reflected_values': test_reflected_values(driver, base_domain),
    }

    # Crawl if enabled
    if crawl:
        print(f"\nCrawling the website (max depth: {max_depth})...")
        visited_urls = crawl_website(driver, url, base_domain, max_depth=max_depth)
        print(f"Visited URLs: {visited_urls}")

    # Save results
    save_results_to_json(results, base_domain, output_dir)

    # Close the browser
    driver.quit()

async def main():
    print_welcome_message()
    parser = argparse.ArgumentParser(description="Analyze a website for input fields, network requests, hidden parameters, and reflected values.")
    parser.add_argument('-u', '--url', required=True, help="Input [Filename | URL]")
    parser.add_argument('-o', '--output', help="Directory to save output files")
    parser.add_argument('-c', '--crawl', action='store_true', help="Crawl pages to extract their parameters")
    parser.add_argument('-d', '--depth', type=int, default=2, help="Maximum depth to crawl (default 2)")
    args = parser.parse_args()

    # Check if the input is a file or a single URL
    if args.url.endswith('.txt'):
        with open(args.url, 'r') as file:
            urls = file.read().splitlines()
    else:
        urls = [args.url]

    # Analyze each URL
    for url in urls:
        await analyze_url(url, args.output, args.crawl, args.depth)

if __name__ == "__main__":
    asyncio.run(main())
