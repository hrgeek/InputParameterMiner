from bs4 import BeautifulSoup

def extract_hidden_parameters(driver):
    """Extract hidden parameters."""
    hidden_parameters = {
        'hidden_inputs': [],
        'cookies': driver.get_cookies(),
        'local_storage': driver.execute_script("return window.localStorage;"),
        'session_storage': driver.execute_script("return window.sessionStorage;")
    }

    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        hidden_inputs = soup.find_all('input', type='hidden')
        for input_tag in hidden_inputs:
            hidden_parameters['hidden_inputs'].append({
                'name': input_tag.get('name'),
                'value': input_tag.get('value')
            })
    except Exception as e:
        print(f"Error extracting hidden parameters: {e}")

    return hidden_parameters
