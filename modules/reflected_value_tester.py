import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from modules.utils import decode_value

def test_reflected_values(driver, base_domain):
    """Test all parameters for reflected values using 'MrColonel'."""
    reflected_values = []
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        query_params = urlparse(driver.current_url).query
        if query_params:
            for param in query_params.split('&'):
                key, value = param.split('=')
                modified_url = driver.current_url.replace(f"{key}={value}", f"{key}=MrColonel")
                driver.get(modified_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                if "MrColonel" in driver.page_source:
                    decoded_value = decode_value(value)
                    reflected_values.append({
                        'url': modified_url,
                        'key': key,
                        'original_value': value,
                        'decoded_value': decoded_value,
                        'reflected': True
                    })

        for input_tag in soup.find_all('input'):
            if input_tag.get('name'):
                input_tag['value'] = 'MrColonel'
                form = input_tag.find_parent('form')
                if form:
                    form_action = form.get('action', driver.current_url)
                    form_method = form.get('method', 'GET').upper()
                    form_data = {input_tag['name']: 'MrColonel'}
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MrColonel',
                        'X-Researcher-Username': 'mrcolonel'
                    }
                    if form_method == 'GET':
                        response = requests.get(urljoin(driver.current_url, form_action), params=form_data, headers=headers)
                    else:
                        response = requests.post(urljoin(driver.current_url, form_action), data=form_data, headers=headers)
                    if "MrColonel" in response.text:
                        decoded_value = decode_value(input_tag.get('value', ''))
                        reflected_values.append({
                            'url': urljoin(driver.current_url, form_action),
                            'key': input_tag['name'],
                            'original_value': input_tag.get('value', ''),
                            'decoded_value': decoded_value,
                            'reflected': True
                        })

    except Exception as e:
        print(f"Error testing reflected values: {e}")
    return reflected_values
