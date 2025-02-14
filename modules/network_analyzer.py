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
                        'body': None,
                        'response': {
                            'headers': dict(request.response.headers) if request.response else None,
                            'body': None
                        }
                    }

                    # Handle request body
                    if request.body:
                        try:
                            # Try to decode as UTF-8 (for text data)
                            request_data['body'] = request.body.decode('utf-8')
                        except UnicodeDecodeError:
                            # If decoding fails, treat as binary data (e.g., images, files)
                            request_data['body'] = "Binary data (not decodable as UTF-8)"

                    # Handle response body
                    if request.response:
                        try:
                            # Try to decode as UTF-8 (for text data)
                            request_data['response']['body'] = request.response.body.decode('utf-8')
                        except UnicodeDecodeError:
                            # If decoding fails, treat as binary data (e.g., images, files)
                            request_data['response']['body'] = "Binary data (not decodable as UTF-8)"

                    network_requests.append(request_data)
    except Exception as e:
        print(f"Error analyzing network requests: {e}")
    return network_requests
