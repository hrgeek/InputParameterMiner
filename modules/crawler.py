import time
import re
import concurrent.futures
import urllib.robotparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_links(soup, base_url):
    """Extract all types of links from the page."""
    links = set()

    # Extract <a> tags
    for link in soup.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])
        links.add(full_url)

    # Extract <form> actions
    for form in soup.find_all('form', action=True):
        full_url = urljoin(base_url, form['action'])
        links.add(full_url)

    # Extract <iframe> sources
    for iframe in soup.find_all('iframe', src=True):
        full_url = urljoin(base_url, iframe['src'])
        links.add(full_url)

    # Extract <link> tags (e.g., stylesheets, favicons)
    for link_tag in soup.find_all('link', href=True):
        full_url = urljoin(base_url, link_tag['href'])
        links.add(full_url)

    # Extract JavaScript and CSS files
    for script in soup.find_all('script', src=True):
        full_url = urljoin(base_url, script['src'])
        links.add(full_url)
    for style in soup.find_all('style'):
        # Parse CSS for @import rules
        imports = re.findall(r'@import\s+["\'](.*?)["\']', style.string)
        for imp in imports:
            full_url = urljoin(base_url, imp)
            links.add(full_url)

    return links

def extract_js_links(driver):
    """Extract links generated by JavaScript."""
    js_links = set()

    # Execute JavaScript to find dynamically generated links
    scripts = driver.find_elements(By.TAG_NAME, "script")
    for script in scripts:
        try:
            # Example: Extract links from JavaScript variables
            js_code = script.get_attribute("innerHTML")
            links = re.findall(r'https?://[^\s\'"]+', js_code)
            for link in links:
                js_links.add(link)
        except Exception as e:
            print(f"Error extracting JS links: {e}")

    return js_links

def check_robots_txt(base_url):
    """Check the website's robots.txt file."""
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urljoin(base_url, "/robots.txt"))
    rp.read()
    return rp

def is_allowed(rp, url, user_agent="*"):
    """Check if crawling the URL is allowed."""
    return rp.can_fetch(user_agent, url)

def maintain_session(driver):
    """Maintain session cookies."""
    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session

def crawl_page(driver, url, base_url, base_domain, max_depth, visited_urls):
    """Crawl a single page."""
    if url in visited_urls:
        return visited_urls
    visited_urls.add(url)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract links
        links = extract_links(soup, base_url)
        js_links = extract_js_links(driver)
        links.update(js_links)

        # Filter links by domain
        links = [link for link in links if urlparse(link).netloc == base_domain]

        # Limit the number of links to process (e.g., first 10 links)
        links = list(links)[:10]

        # Recursively crawl links
        if max_depth > 0:
            for link in links:
                if link not in visited_urls:
                    visited_urls = crawl_page(driver, link, base_url, base_domain, max_depth - 1, visited_urls)
                    time.sleep(0.125)  # Delay to achieve 8 requests per second (1/8 = 0.125 seconds)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

    return visited_urls

def crawl_website(driver, base_url, base_domain, max_depth=2):
    """Crawl the website to discover additional pages and resources."""
    visited_urls = set()
    rp = check_robots_txt(base_url)

    # Start crawling from the base URL
    if is_allowed(rp, base_url):
        visited_urls = crawl_page(driver, base_url, base_url, base_domain, max_depth, visited_urls)

    # Generate a sitemap
    generate_sitemap(visited_urls)

    return visited_urls

def generate_sitemap(visited_urls):
    """Generate a sitemap of the crawled URLs."""
    with open("sitemap.txt", "w") as f:
        for url in visited_urls:
            f.write(f"{url}\n")