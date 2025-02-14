import re
import aiohttp
import asyncio
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

async def fetch_js_content(session, url):
    """Fetch JavaScript file content."""
    try:
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

async def search_js_files(driver, base_url, base_domain):
    """Search JavaScript files for parameters."""
    js_parameters = []
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        script_tags = soup.find_all('script', src=True)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for script in script_tags:
                js_url = urljoin(base_url, script['src'])
                if urlparse(js_url).netloc == base_domain:
                    tasks.append(fetch_js_content(session, js_url))

            js_contents = await asyncio.gather(*tasks)

            for js_content in js_contents:
                if js_content:
                    api_endpoints = re.findall(r'https?://[^\s\'"]+', js_content)
                    hidden_params = re.findall(r'[\'"]\w+[\'"]\s*:\s*[\'"]\w+[\'"]', js_content)
                    if api_endpoints or hidden_params:
                        js_parameters.append({
                            'url': js_url,
                            'api_endpoints': api_endpoints,
                            'hidden_parameters': hidden_params
                        })
    except Exception as e:
        print(f"Error searching JavaScript files: {e}")
    return js_parameters
