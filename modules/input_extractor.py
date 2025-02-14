from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def extract_interactive_elements(soup):
    """Extract all interactive elements from the page."""
    interactive_elements = []

    # Extract <input> tags
    for input_tag in soup.find_all('input'):
        interactive_elements.append({
            'type': input_tag.get('type', 'text'),
            'name': input_tag.get('name'),
            'id': input_tag.get('id'),
            'placeholder': input_tag.get('placeholder'),
            'value': input_tag.get('value'),
            'autocomplete': input_tag.get('autocomplete'),
            'required': input_tag.get('required'),
            'pattern': input_tag.get('pattern')
        })

    # Extract <textarea> tags
    for textarea_tag in soup.find_all('textarea'):
        interactive_elements.append({
            'type': 'textarea',
            'name': textarea_tag.get('name'),
            'id': textarea_tag.get('id'),
            'placeholder': textarea_tag.get('placeholder'),
            'autocomplete': textarea_tag.get('autocomplete'),
            'required': textarea_tag.get('required')
        })

    # Extract <select> tags
    for select_tag in soup.find_all('select'):
        interactive_elements.append({
            'type': 'select',
            'name': select_tag.get('name'),
            'id': select_tag.get('id'),
            'options': [option.get('value') for option in select_tag.find_all('option')]
        })

    # Extract <button> tags
    for button_tag in soup.find_all('button'):
        interactive_elements.append({
            'type': 'button',
            'name': button_tag.get('name'),
            'id': button_tag.get('id'),
            'value': button_tag.get('value')
        })

    # Extract <datalist> tags
    for datalist_tag in soup.find_all('datalist'):
        interactive_elements.append({
            'type': 'datalist',
            'id': datalist_tag.get('id'),
            'options': [option.get('value') for option in datalist_tag.find_all('option')]
        })

    # Extract custom elements (e.g., <div contenteditable>)
    for custom_tag in soup.find_all(attrs={"contenteditable": True}):
        interactive_elements.append({
            'type': 'custom',
            'id': custom_tag.get('id'),
            'content': custom_tag.text
        })

    return interactive_elements

def extract_dynamic_inputs(driver):
    """Extract dynamically generated input fields."""
    dynamic_inputs = []
    try:
        # Execute JavaScript to find dynamically generated inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for input_tag in inputs:
            dynamic_inputs.append({
                'type': input_tag.get_attribute('type'),
                'name': input_tag.get_attribute('name'),
                'id': input_tag.get_attribute('id'),
                'placeholder': input_tag.get_attribute('placeholder'),
                'value': input_tag.get_attribute('value')
            })
    except Exception as e:
        print(f"Error extracting dynamic inputs: {e}")
    return dynamic_inputs

def extract_form_inputs(soup):
    """Extract input fields within forms."""
    form_inputs = []
    for form in soup.find_all('form'):
        inputs = form.find_all(['input', 'textarea', 'select'])
        for input_tag in inputs:
            form_inputs.append({
                'form_id': form.get('id'),
                'type': input_tag.name,
                'name': input_tag.get('name'),
                'id': input_tag.get('id'),
                'placeholder': input_tag.get('placeholder'),
                'value': input_tag.get('value')
            })
    return form_inputs

def extract_input_fields(driver):
    """Extract all input fields from the page."""
    input_fields = []
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract interactive elements
        interactive_elements = extract_interactive_elements(soup)
        input_fields.extend(interactive_elements)

        # Extract dynamic inputs
        dynamic_inputs = extract_dynamic_inputs(driver)
        input_fields.extend(dynamic_inputs)

        # Extract form inputs
        form_inputs = extract_form_inputs(soup)
        input_fields.extend(form_inputs)
    except Exception as e:
        print(f"Error extracting input fields: {e}")
    return input_fields