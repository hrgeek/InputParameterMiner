import base64
from urllib.parse import unquote, urlparse

def ensure_url_scheme(url):
    """Ensure the URL has a scheme (http:// or https://). If not, add https://."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "https://" + url
    return url

def decode_value(value):
    """Decode a value if it is encoded (e.g., Base64, URL encoding)."""
    decoded_value = None
    try:
        decoded_value = base64.b64decode(value).decode('utf-8')
    except:
        try:
            decoded_value = unquote(value)
        except:
            pass
    return decoded_value

def save_results_to_json(results, domain):
    """Save the results to a JSON file named after the domain."""
    filename = f"results/{domain}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results to JSON: {e}")
