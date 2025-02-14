import os
import json
from urllib.parse import urlparse

def ensure_url_scheme(url):
    """Ensure the URL has a scheme."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "https://" + url
    return url

def save_results_to_json(results, domain, output_dir=None):
    """Save results to a JSON file."""
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{domain}.json")
    else:
        filename = f"{domain}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results to JSON: {e}")
