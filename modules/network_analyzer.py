import json
from urllib.parse import urlparse

def analyze_network_requests(driver, base_domain):
    """Analyze network requests."""
    network_requests = []
    try:
        for request in driver.requests:
            if request.method in ['POST', 'GET']:
                request_url = request.url
                if urlparse(request_url).netloc == base_domain:
                    request_data = {
                        'url': request_url,
                        'method': request.method,
                        'headers': dict(request.headers),
                        'body': request.body.decode('utf-8') if request.body else None,
                        'response': {
                            'headers': dict(request.response.headers) if request.response else None,
                            'body': request.response.body.decode('utf-8') if request.response else None
                        }
                    }
                    network_requests.append(request_data)
    except Exception as e:
        print(f"Error analyzing network requests: {e}")
    return network_requests
