from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver as wired_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_selenium(url):
    """Set up Selenium with ChromeDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    seleniumwire_options = {
        'connection_timeout': 120,
        'request_timeout': 120,
        'custom_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MrColonel',
            'X-Researcher-Username': 'mrcolonel'
        }
    }

    try:
        driver = wired_webdriver.Chrome(
            service=Service(),
            options=chrome_options,
            seleniumwire_options=seleniumwire_options
        )
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return driver
    except Exception as e:
        print(f"Error setting up Selenium: {e}")
        return None
