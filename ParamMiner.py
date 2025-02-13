import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver as wired_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

def setup_selenium(url):
    """Set up Selenium with ChromeDriver to fetch JavaScript-rendered content."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Use selenium-wire to capture network requests
    try:
        driver = wired_webdriver.Chrome(service=Service(), options=chrome_options)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Wait for the page to load
        return driver
    except Exception as e:
        print(f"Error setting up Selenium: {e}")
        return None

def extract_input_fields(driver):
    """Extract input fields from the JavaScript-rendered page."""
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        input_fields = []

        # Find all input tags (including hidden inputs)
        for input_tag in soup.find_all('input'):
            input_fields.append({
                'type': input_tag.get('type', 'text'),
                'name': input_tag.get('name'),
                'id': input_tag.get('id'),
                'placeholder': input_tag.get('placeholder'),
                'value': input_tag.get('value')
            })

        # Find all textarea tags
        for textarea_tag in soup.find_all('textarea'):
            input_fields.append({
                'type': 'textarea',
                'name': textarea_tag.get('name'),
                'id': textarea_tag.get('id'),
                'placeholder': textarea_tag.get('placeholder')
            })

        # Find all select tags
        for select_tag in soup.find_all('select'):
            input_fields.append({
                'type': 'select',
                'name': select_tag.get('name'),
                'id': select_tag.get('id')
            })

        return input_fields
    except Exception as e:
        print(f"Error extracting input fields: {e}")
        return []

def analyze_network_requests(driver, base_domain):
    """Analyze network requests to identify API endpoints and important parameters."""
    network_requests = []
    try:
        for request in driver.requests:
            if request.method in ['POST', 'GET']:
                request_url = request.url
                if urlparse(request_url).netloc == base_domain:  # Filter by domain
                    request_data = {
                        'url': request_url,
                        'method': request.method,
                        'headers': dict(request.headers),
                        'body': None,
                        'response': None
                    }

                    if request.body:
                        try:
                            # Parse JSON body if present
                            request_data['body'] = json.loads(request.body.decode('utf-8'))
                        except:
                            # Handle non-JSON body
                            request_data['body'] = request.body.decode('utf-8')

                    if request.response:
                        try:
                            # Parse JSON response if present
                            request_data['response'] = json.loads(request.response.body.decode('utf-8'))
                        except:
                            # Handle non-JSON response
                            pass

                    network_requests.append(request_data)
    except Exception as e:
        print(f"Error analyzing network requests: {e}")
    return network_requests

def extract_hidden_parameters(driver):
    """Extract hidden parameters from JavaScript, cookies, and local storage."""
    hidden_parameters = {
        'hidden_inputs': [],
        'cookies': [],
        'local_storage': {},
        'session_storage': {}
    }
    try:
        # Extract hidden input fields
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        hidden_inputs = soup.find_all('input', type='hidden')
        for input_tag in hidden_inputs:
            hidden_parameters['hidden_inputs'].append({
                'name': input_tag.get('name'),
                'value': input_tag.get('value')
            })

        # Extract cookies
        cookies = driver.get_cookies()
        for cookie in cookies:
            hidden_parameters['cookies'].append({
                'name': cookie['name'],
                'value': cookie['value']
            })

        # Extract local storage
        hidden_parameters['local_storage'] = driver.execute_script("return window.localStorage;")

        # Extract session storage
        hidden_parameters['session_storage'] = driver.execute_script("return window.sessionStorage;")
    except Exception as e:
        print(f"Error extracting hidden parameters: {e}")
    return hidden_parameters

def crawl_website(driver, base_url, base_domain, max_depth=2, current_depth=0, visited_urls=None):
    """Crawl the website to discover additional pages and JavaScript files."""
    if visited_urls is None:
        visited_urls = set()

    # Stop crawling if max depth is reached
    if current_depth > max_depth:
        return visited_urls

    # Get the current page URL
    current_url = driver.current_url
    if current_url in visited_urls:
        return visited_urls
    visited_urls.add(current_url)

    # Extract all links on the current page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])
        if urlparse(full_url).netloc == base_domain:  # Ensure it's the same domain
            links.add(full_url)

    # Limit the number of links to process (e.g., first 10 links)
    links = list(links)[:10]

    # Visit each link and crawl recursively
    for link in links:
        if link not in visited_urls:
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Wait for the page to load
                visited_urls = crawl_website(driver, base_url, base_domain, max_depth, current_depth + 1, visited_urls)
                time.sleep(0.125)  # Delay to achieve 8 requests per second (1/8 = 0.125 seconds)
            except Exception as e:
                print(f"Error crawling {link}: {e}")

    return visited_urls

def search_js_files(driver, base_url, base_domain):
    """Search JavaScript files for parameters."""
    js_parameters = []
    try:
        # Extract all script tags with src attributes
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        script_tags = soup.find_all('script', src=True)

        for script in script_tags:
            js_url = urljoin(base_url, script['src'])
            if urlparse(js_url).netloc == base_domain:  # Filter by domain
                print(f"Analyzing JavaScript file: {js_url}")

                # Fetch the JavaScript file content
                response = requests.get(js_url)
                if response.status_code == 200:
                    js_content = response.text

                    # Search for parameters in the JavaScript file
                    # Example: Look for API endpoints or hidden parameters
                    api_endpoints = re.findall(r'https?://[^\s\'"]+', js_content)
                    hidden_params = re.findall(r'[\'"]\w+[\'"]\s*:\s*[\'"]\w+[\'"]', js_content)

                    if api_endpoints or hidden_params:
                        js_parameters.append({
                            'url': js_url,
                            'api_endpoints': api_endpoints,
                            'hidden_parameters': hidden_params
                        })
    except Exception as e:
        print(f"Error searching JavaScript files: {e}")
    return js_parameters

def save_results_to_json(results, filename="results.json"):
    """Save the results to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results to JSON: {e}")

def main():
    url = input("Enter the URL of the site to analyze: ")
    base_domain = urlparse(url).netloc  # Extract the base domain (e.g., example.com)

    # Set up Selenium and fetch JavaScript-rendered content
    print("\nSetting up Selenium to fetch JavaScript-rendered content...")
    driver = setup_selenium(url)

    if not driver:
        print("Failed to set up Selenium. Exiting.")
        return

    # Collect all results in a dictionary
    results = {
        'input_fields': [],
        'network_requests': [],
        'hidden_parameters': {},
        'js_files': []
    }

    # Extract input fields
    print("\nExtracting input fields from the page...")
    results['input_fields'] = extract_input_fields(driver)

    # Analyze network requests (filtered by domain)
    print("\nAnalyzing network requests...")
    results['network_requests'] = analyze_network_requests(driver, base_domain)

    # Extract hidden parameters
    print("\nExtracting hidden parameters...")
    results['hidden_parameters'] = extract_hidden_parameters(driver)

    # Crawl the website with a depth limit of 2 (filtered by domain)
    print("\nCrawling the website to discover additional pages and JavaScript files...")
    visited_urls = crawl_website(driver, url, base_domain, max_depth=2)
    print(f"Visited URLs: {visited_urls}")

    # Search JavaScript files (filtered by domain)
    print("\nSearching JavaScript files for parameters...")
    results['js_files'] = search_js_files(driver, url, base_domain)

    # Save results to JSON
    save_results_to_json(results)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
