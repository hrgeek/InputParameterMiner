from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
import re
import json
from selenium.webdriver.common.by import By

def extract_js_parameters(driver):
    """Extract hidden parameters from JavaScript files."""
    js_parameters = {}
    try:
        # Extract all script tags
        scripts = driver.find_elements(By.TAG_NAME, "script")
        for script in scripts:
            js_code = script.get_attribute("innerHTML")
            # Search for common patterns
            patterns = {
                "api_key": r'API_KEY\s*=\s*["\'](.*?)["\']',
                "token": r'token\s*=\s*["\'](.*?)["\']',
                "secret": r'secret\s*=\s*["\'](.*?)["\']'
            }
            for key, pattern in patterns.items():
                matches = re.findall(pattern, js_code)
                if matches:
                    js_parameters[key] = matches[0]
    except Exception as e:
        print(f"Error extracting JS parameters: {e}")
    return js_parameters

def extract_url_parameters(url):
    """Extract hidden parameters from the URL."""
    url_parameters = {}
    try:
        parsed_url = urlparse(url)
        # Extract query parameters
        query_params = parse_qs(parsed_url.query)
        for key, values in query_params.items():
            url_parameters[key] = values[0]
        # Extract fragment parameters
        fragment_params = parse_qs(parsed_url.fragment)
        for key, values in fragment_params.items():
            url_parameters[key] = values[0]
    except Exception as e:
        print(f"Error extracting URL parameters: {e}")
    return url_parameters

def extract_json_parameters(driver):
    """Extract hidden parameters from JSON payloads in network requests."""
    json_parameters = {}
    try:
        for request in driver.requests:
            if request.method == "POST" and request.headers.get("Content-Type") == "application/json":
                try:
                    payload = json.loads(request.body.decode("utf-8"))
                    for key, value in payload.items():
                        json_parameters[key] = value
                except Exception as e:
                    print(f"Error parsing JSON payload: {e}")
    except Exception as e:
        print(f"Error extracting JSON parameters: {e}")
    return json_parameters

def extract_contextual_parameters(driver):
    """Extract contextual parameters like CSRF tokens."""
    contextual_parameters = {}
    try:
        # Extract CSRF token from meta tags
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        csrf_token = soup.find("meta", attrs={"name": "csrf-token"})
        if csrf_token:
            contextual_parameters["csrf_token"] = csrf_token.get("content")
    except Exception as e:
        print(f"Error extracting contextual parameters: {e}")
    return contextual_parameters

def extract_hidden_parameters(driver):
    """Extract all hidden parameters."""
    hidden_parameters = {
        'hidden_inputs': [],
        'cookies': [],
        'local_storage': {},
        'session_storage': {},
        'js_parameters': {},
        'url_parameters': {},
        'json_parameters': {},
        'contextual_parameters': {}
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

        # Extract JavaScript parameters
        hidden_parameters['js_parameters'] = extract_js_parameters(driver)

        # Extract URL parameters
        hidden_parameters['url_parameters'] = extract_url_parameters(driver.current_url)

        # Extract JSON parameters
        hidden_parameters['json_parameters'] = extract_json_parameters(driver)

        # Extract contextual parameters
        hidden_parameters['contextual_parameters'] = extract_contextual_parameters(driver)
    except Exception as e:
        print(f"Error extracting hidden parameters: {e}")
    return hidden_parameters