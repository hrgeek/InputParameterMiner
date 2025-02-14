import json
from urllib.parse import urlparse

def analyze_network_requests(driver, base_domain):
    """Analyze network requests and handle binary or non-UTF-8 data."""
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
                        'body': None,  # Default to None for non-text or binary data
                        'response': {
                            'headers': None,
                            'body': None
                        }
                    }

                    # Handle request body
                    if request.body:
                        content_type = request.headers.get('content-type', '').lower()
                        if any(text_type in content_type for text_type in ['text', 'json', 'xml', 'html']):
                            try:
                                request_data['body'] = request.body.decode('utf-8')
                            except UnicodeDecodeError:
                                request_data['body'] = "Binary or non-UTF-8 data (not decoded)"
                        else:
                            request_data['body'] = "Binary content (not decoded)"

                    # Handle response
                    if request.response:
                        request_data['response']['headers'] = dict(request.response.headers)

                        # Handle response body
                        if request.response.body:
                            content_type = request.response.headers.get('content-type', '').lower()
                            if any(text_type in content_type for text_type in ['text', 'json', 'xml', 'html']):
                                try:
                                    request_data['response']['body'] = request.response.body.decode('utf-8')
                                except UnicodeDecodeError:
                                    request_data['response']['body'] = "Binary or non-UTF-8 data (not decoded)"
                            else:
                                request_data['response']['body'] = "Binary content (not decoded)"

                    network_requests.append(request_data)

    except Exception as e:
        print(f"Error analyzing network requests: {e}")

    return network_requests
