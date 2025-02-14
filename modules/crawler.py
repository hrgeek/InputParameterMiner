import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def crawl_website(driver, base_url, base_domain, max_depth=2, current_depth=0, visited_urls=None):
    """Crawl the website."""
    if visited_urls is None:
        visited_urls = set()

    if current_depth > max_depth:
        return visited_urls

    current_url = driver.current_url
    if current_url in visited_urls:
        return visited_urls
    visited_urls.add(current_url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])
        if urlparse(full_url).netloc == base_domain:
            links.add(full_url)

    links = list(links)[:10]  # Limit to first 10 links

    for link in links:
        if link not in visited_urls:
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                visited_urls = crawl_website(driver, base_url, base_domain, max_depth, current_depth + 1, visited_urls)
                time.sleep(0.125)  # Delay to avoid overloading the server
            except Exception as e:
                print(f"Error crawling {link}: {e}")

    return visited_urls
