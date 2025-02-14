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

async def analyze_url(url):
    """Analyze a single URL."""
    url = ensure_url_scheme(url)
    print(f"Using URL: {url}")

    base_domain = urlparse(url).netloc

    print("\nSetting up Selenium to fetch JavaScript-rendered content...")
    driver = setup_selenium(url)

    if not driver:
        print("Failed to set up Selenium. Exiting.")
        return

    results = {
        'input_fields': [],
        'network_requests': [],
        'hidden_parameters': {},
        'js_files': [],
        'reflected_values': []
    }

    print("\nExtracting input fields from the page...")
    results['input_fields'] = extract_input_fields(driver)

    print("\nAnalyzing network requests...")
    results['network_requests'] = analyze_network_requests(driver, base_domain)

    print("\nExtracting hidden parameters...")
    results['hidden_parameters'] = extract_hidden_parameters(driver)

    print("\nSearching JavaScript files for parameters...")
    results['js_files'] = await search_js_files(driver, url, base_domain)

    print("\nTesting for reflected values using 'MrColonel'...")
    results['reflected_values'] = test_reflected_values(driver, base_domain)

    print("\nCrawling the website to discover additional pages...")
    visited_urls = crawl_website(driver, url, base_domain, max_depth=2)
    print(f"Visited URLs: {visited_urls}")

    save_results_to_json(results, base_domain)

    driver.quit()

async def main():
    parser = argparse.ArgumentParser(description="Analyze a website for input fields, network requests, hidden parameters, and reflected values.")
    parser.add_argument('-u', '--url', required=True, help="Input [Filename | URL]")
    args = parser.parse_args()

    if args.url.endswith('.txt'):
        with open(args.url, 'r') as file:
            urls = file.read().splitlines()
    else:
        urls = [args.url]

    for url in urls:
        await analyze_url(url)

if __name__ == "__main__":
    asyncio.run(main())
