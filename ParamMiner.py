#!/usr/bin/env python3

import time
import re
import requests
import asyncio
import aiohttp
import base64
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver as wired_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import json

def ensure_url_scheme(url):
    """Ensure the URL has a scheme (http:// or https://). If not, add https://."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "https://" + url
    return url

def setup_selenium(url):
    """Set up Selenium with ChromeDriver to fetch JavaScript-rendered content."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Configure Selenium-Wire options
    seleniumwire_options = {
        'connection_timeout': 120,  # Increase connection timeout
        'request_timeout': 120,     # Increase request timeout
        'custom_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MrColonel',
            'X-Researcher-Username': 'mrcolonel'
        }
    }

    # Use selenium-wire to capture network requests
    try:
        driver = wired_webdriver.Chrome(
            service=Service(),
            options=chrome_options,
            seleniumwire_options=seleniumwire_options
        )
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Wait for the page to load
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
                        'response': {
                            'headers': dict(request.response.headers) if request.response else None,
                            'body': None
                        }
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
                            request_data['response']['body'] = json.loads(request.response.body.decode('utf-8'))
                        except:
                            # Handle non-JSON response
                            request_data['response']['body'] = request.response.body.decode('utf-8')

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
                'value': cookie['value'],
                'http_only': cookie.get('httpOnly', False),
                'secure': cookie.get('secure', False),
                'same_site': cookie.get('sameSite', 'None')
            })

        # Extract local storage
        hidden_parameters['local_storage'] = driver.execute_script("return window.localStorage;")

        # Extract session storage
        hidden_parameters['session_storage'] = driver.execute_script("return window.sessionStorage;")
    except Exception as e:
        print(f"Error extracting hidden parameters: {e}")
    return hidden_parameters

async def fetch_js_content(session, url):
    """Fetch JavaScript file content asynchronously."""
    try:
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

async def search_js_files(driver, base_url, base_domain):
    """Search JavaScript files for parameters asynchronously."""
    js_parameters = []
    try:
        # Extract all script tags with src attributes
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        script_tags = soup.find_all('script', src=True)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for script in script_tags:
                js_url = urljoin(base_url, script['src'])
                if urlparse(js_url).netloc == base_domain:  # Filter by domain
                    print(f"Analyzing JavaScript file: {js_url}")
                    tasks.append(fetch_js_content(session, js_url))

            js_contents = await asyncio.gather(*tasks)

            for js_content in js_contents:
                if js_content:
                    # Search for parameters in the JavaScript file
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

def decode_value(value):
    """Decode a value if it is encoded (e.g., Base64, URL encoding)."""
    decoded_value = None
    try:
        # Try Base64 decoding
        decoded_value = base64.b64decode(value).decode('utf-8')
    except:
        try:
            # Try URL decoding
            decoded_value = unquote(value)
        except:
            pass
    return decoded_value

def test_reflected_values(driver, base_domain):
    """Test all parameters for reflected values using 'MrColonel'."""
    reflected_values = []
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Test query parameters
        query_params = urlparse(driver.current_url).query
        if query_params:
            for param in query_params.split('&'):
                key, value = param.split('=')
                # Inject 'MrColonel' into the parameter
                modified_url = driver.current_url.replace(f"{key}={value}", f"{key}=MrColonel")
                driver.get(modified_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                if "MrColonel" in driver.page_source:
                    decoded_value = decode_value(value)
                    reflected_values.append({
                        'url': modified_url,
                        'key': key,
                        'original_value': value,
                        'decoded_value': decoded_value,
                        'reflected': True
                    })

        # Test form inputs
        for input_tag in soup.find_all('input'):
            if input_tag.get('name'):
                # Inject 'MrColonel' into the form input
                input_tag['value'] = 'MrColonel'
                form = input_tag.find_parent('form')
                if form:
                    form_action = form.get('action', driver.current_url)
                    form_method = form.get('method', 'GET').upper()
                    form_data = {input_tag['name']: 'MrColonel'}
                    if form_method == 'GET':
                        response = requests.get(urljoin(driver.current_url, form_action), params=form_data)
                    else:
                        response = requests.post(urljoin(driver.current_url, form_action), data=form_data)
                    if "MrColonel" in response.text:
                        decoded_value = decode_value(input_tag.get('value', ''))
                        reflected_values.append({
                            'url': urljoin(driver.current_url, form_action),
                            'key': input_tag['name'],
                            'original_value': input_tag.get('value', ''),
                            'decoded_value': decoded_value,
                            'reflected': True
                        })

    except Exception as e:
        print(f"Error testing reflected values: {e}")
    return reflected_values

def save_results_to_json(results, domain):
    """Save the results to a JSON file named after the domain."""
    filename = f"{domain}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results to JSON: {e}")

async def main():
    url = input("Enter the URL of the site to analyze: ")

    # Ensure the URL has a scheme
    url = ensure_url_scheme(url)
    print(f"Using URL: {url}")

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
        'js_files': [],
        'reflected_values': []
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

    # Search JavaScript files (filtered by domain)
    print("\nSearching JavaScript files for parameters...")
    results['js_files'] = await search_js_files(driver, url, base_domain)

    # Test for reflected values using 'MrColonel'
    print("\nTesting for reflected values using 'MrColonel'...")
    results['reflected_values'] = test_reflected_values(driver, base_domain)

    # Save results to JSON
    save_results_to_json(results, base_domain)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
