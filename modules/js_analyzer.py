import re
import asyncio
import aiohttp
import ast
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

async def fetch_js_content(session, url):
    """Fetch JavaScript file content asynchronously."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MrColonel',
        'X-Researcher-Username': 'mrcolonel'
    }
    try:
        async with session.get(url, headers=headers, timeout=30) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def search_js_patterns(js_content):
    """Search for advanced patterns in JavaScript files."""
    patterns = {
        "api_key": r'API_KEY\s*=\s*["\'](.*?)["\']',
        "token": r'token\s*=\s*["\'](.*?)["\']',
        "secret": r'secret\s*=\s*["\'](.*?)["\']',
        "password": r'password\s*=\s*["\'](.*?)["\']',
        "endpoint": r'https?://[^\s\'"]+'
    }
    results = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, js_content)
        if matches:
            results[key] = matches
    return results

def analyze_context(js_content):
    """Analyze the context of extracted patterns."""
    context = {
        "authentication": [],
        "configuration": [],
        "sensitive_data": []
    }
    # Example: Look for authentication tokens
    auth_tokens = re.findall(r'authToken\s*=\s*["\'](.*?)["\']', js_content)
    if auth_tokens:
        context["authentication"].extend(auth_tokens)
    # Example: Look for configuration variables
    config_vars = re.findall(r'config\s*=\s*{.*?}', js_content, re.DOTALL)
    if config_vars:
        context["configuration"].extend(config_vars)
    return context

def parse_js_with_ast(js_content):
    """Parse JavaScript content using AST."""
    try:
        # Parse JavaScript content into an AST
        tree = ast.parse(js_content)
        # Example: Extract function definitions
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return functions
    except Exception as e:
        print(f"Error parsing JS with AST: {e}")
        return []

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
                    # Search for patterns
                    patterns = search_js_patterns(js_content)
                    # Analyze context
                    context = analyze_context(js_content)
                    # Parse with AST
                    functions = parse_js_with_ast(js_content)
                    # Combine results
                    js_parameters.append({
                        'url': js_url,
                        'patterns': patterns,
                        'context': context,
                        'functions': functions
                    })
    except Exception as e:
        print(f"Error searching JavaScript files: {e}")
    return js_parameters