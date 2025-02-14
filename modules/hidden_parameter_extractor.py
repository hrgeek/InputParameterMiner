from bs4 import BeautifulSoup

def extract_hidden_parameters(driver):
    """Extract hidden parameters from JavaScript, cookies, and local storage."""
    hidden_parameters = {
        'hidden_inputs': [],
        'cookies': [],
        'local_storage': {},
        'session_storage': {}
    }
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        hidden_inputs = soup.find_all('input', type='hidden')
        for input_tag in hidden_inputs:
            hidden_parameters['hidden_inputs'].append({
                'name': input_tag.get('name'),
                'value': input_tag.get('value')
            })

        cookies = driver.get_cookies()
        for cookie in cookies:
            hidden_parameters['cookies'].append({
                'name': cookie['name'],
                'value': cookie['value'],
                'http_only': cookie.get('httpOnly', False),
                'secure': cookie.get('secure', False),
                'same_site': cookie.get('sameSite', 'None')
            })

        hidden_parameters['local_storage'] = driver.execute_script("return window.localStorage;")
        hidden_parameters['session_storage'] = driver.execute_script("return window.sessionStorage;")
    except Exception as e:
        print(f"Error extracting hidden parameters: {e}")
    return hidden_parameters
