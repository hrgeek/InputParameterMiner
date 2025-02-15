import json
import os
import logging
from urllib.parse import urlparse, urljoin
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("utils.log"), logging.StreamHandler()]
)

def ensure_url_scheme(url):
    """
    Ensure the URL has a scheme (http:// or https://). If not, add https://.
    
    Args:
        url (str): The URL to validate.
    
    Returns:
        str: The URL with a valid scheme.
    
    Raises:
        ValueError: If the URL is invalid (e.g., missing domain).
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "https://" + url
        parsed_url = urlparse(url)  # Re-parse to validate the new URL
    
    # Validate the URL
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {url} - Missing domain or invalid format.")
    
    return url

def save_results_to_json(results, base_domain):
    """
    Save the analysis results to a JSON file in the results/ directory.
    
    Args:
        results (dict): The analysis results to save.
        base_domain (str): The base domain (used for the filename).
    
    Raises:
        Exception: If there is an error saving the file.
    """
    try:
        # Create the results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)

        # Generate the filename
        filename = f"results/{base_domain}.json"

        # Save the results to the JSON file
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)
        
        logging.info(f"Results saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving results to JSON: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_url(url, headers=None):
    """
    Fetch the content of a URL with retries and exponential backoff.
    
    Args:
        url (str): The URL to fetch.
        headers (dict, optional): Custom headers to include in the request.
    
    Returns:
        str: The content of the URL.
    
    Raises:
        Exception: If the request fails after retries.
    """
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        raise

def is_valid_url(url):
    """
    Check if a URL is valid.
    
    Args:
        url (str): The URL to validate.
    
    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    try:
        parsed_url = urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc])
    except Exception:
        return False

def join_url(base_url, path):
    """
    Join a base URL and a path, ensuring the result is a valid URL.
    
    Args:
        base_url (str): The base URL.
        path (str): The path to join.
    
    Returns:
        str: The joined URL.
    """
    return urljoin(base_url, path)

def create_directory(directory):
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory (str): The directory to create.
    """
    try:
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Directory created or already exists: {directory}")
    except Exception as e:
        logging.error(f"Error creating directory {directory}: {e}")
        raise

# Example usage
if __name__ == "__main__":
    # Test ensure_url_scheme
    print(ensure_url_scheme("example.com"))  # Output: https://example.com

    # Test save_results_to_json
    test_results = {
        "input_fields": [{"name": "username", "type": "text"}],
        "network_requests": [{"url": "https://example.com/api", "method": "GET"}],
        "hidden_parameters": {"csrf_token": "abc123"},
        "js_files": ["https://example.com/script.js"],
        "reflected_values": [],
        "errors": []
    }
    save_results_to_json(test_results, "example.com")

    # Test fetch_url
    try:
        content = fetch_url("https://example.com")
        print(content[:100])  # Print the first 100 characters of the content
    except Exception as e:
        print(f"Failed to fetch URL: {e}")

    # Test is_valid_url
    print(is_valid_url("https://example.com"))  # Output: True
    print(is_valid_url("example.com"))         # Output: False

    # Test join_url
    print(join_url("https://example.com", "/path/to/resource"))  # Output: https://example.com/path/to/resource

    # Test create_directory
    create_directory("test_directory")