import json
import re
import time
import threading
import subprocess
import requests
from urllib.parse import urlparse
from sklearn.ensemble import IsolationForest
import pandas as pd

def analyze_payload(payload):
    """Analyze payload for sensitive data or patterns."""
    sensitive_data = []
    patterns = {
        "api_key": r'API_KEY\s*=\s*["\'](.*?)["\']',
        "jwt_token": r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',  # JWT token pattern
        "credit_card": r'\b(?:\d[ -]*?){13,16}\b',  # Credit card number pattern
        "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'  # Email pattern
    }
    for key, pattern in patterns.items():
        matches = re.findall(pattern, str(payload))
        if matches:
            sensitive_data.append({key: matches})
    return sensitive_data

def detect_anomalies(network_requests):
    """Detect anomalies in network requests using machine learning."""
    # Example training data
    data = {
        'url_length': [len(request['url']) for request in network_requests],
        'payload_size': [len(str(request['body'])) if request['body'] else 0 for request in network_requests],
        'status_code': [int(request['response']['headers'].get('status', 0)) for request in network_requests]
    }
    df = pd.DataFrame(data)

    # Train an Isolation Forest model
    model = IsolationForest(contamination=0.1)  # Adjust contamination based on expected anomaly rate
    model.fit(df)

    # Predict anomalies
    df['anomaly'] = model.predict(df)
    anomalies = [network_requests[i] for i, row in df.iterrows() if row['anomaly'] == -1]
    return anomalies

def analyze_behavior(network_requests):
    """Analyze the behavior of network requests."""
    behavior = {
        'request_rate': len(network_requests),  # Total number of requests
        'unique_endpoints': len(set(request['url'] for request in network_requests)),  # Unique endpoints
        'suspicious_sequences': []  # Suspicious sequences of requests
    }

    # Example: Detect login followed by sensitive data access
    for i in range(len(network_requests) - 1):
        if "login" in network_requests[i]['url'] and "sensitive" in network_requests[i + 1]['url']:
            behavior['suspicious_sequences'].append({
                'sequence': [network_requests[i]['url'], network_requests[i + 1]['url']],
                'description': "Login followed by sensitive data access"
            })

    return behavior

def test_waf(url):
    """Test for web application firewalls using WAFW00F."""
    result = subprocess.run(["wafw00f", url], capture_output=True, text=True)
    return result.stdout

def query_threat_intelligence(url):
    """Query threat intelligence databases for known malicious URLs."""
    # Example: Use VirusTotal API
    api_key = "your_virustotal_api_key"
    response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url}", headers={"x-apikey": api_key})
    return response.json()

def monitor_network_requests(driver, base_domain, callback):
    """Monitor network requests in real-time."""
    def monitor():
        while True:
            for request in driver.requests:
                if request.method and urlparse(request.url).netloc == base_domain:
                    callback(request)
            time.sleep(1)  # Adjust sleep interval as needed

    threading.Thread(target=monitor, daemon=True).start()

def analyze_network_requests(driver, base_domain, rate_limit=1):
    """Analyze network requests to identify API endpoints and important parameters."""
    network_requests = []
    try:
        for request in driver.requests:
            if request.method:  # Capture all HTTP methods
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

                    # Analyze payload for sensitive data
                    request_data['sensitive_data'] = analyze_payload(request_data['body'])

                    network_requests.append(request_data)
                    time.sleep(rate_limit)  # Respect rate limit
    except Exception as e:
        print(f"Error analyzing network requests: {e}")
    return network_requests