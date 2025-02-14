from bs4 import BeautifulSoup

def extract_input_fields(driver):
    """Extract input fields from the page."""
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        input_fields = []

        for input_tag in soup.find_all('input'):
            input_fields.append({
                'type': input_tag.get('type', 'text'),
                'name': input_tag.get('name'),
                'id': input_tag.get('id'),
                'placeholder': input_tag.get('placeholder'),
                'value': input_tag.get('value')
            })

        for textarea_tag in soup.find_all('textarea'):
            input_fields.append({
                'type': 'textarea',
                'name': textarea_tag.get('name'),
                'id': textarea_tag.get('id'),
                'placeholder': textarea_tag.get('placeholder')
            })

        for select_tag in soup.find_all('select'):
            input_fields.append({
                'type': 'select',
                'name': select_tag.get('name'),
                'id': select_tag.get('id')
            })

        return input_fields
    except Exception as e:
        print(f"Error extracting input fields: {e}")
        return []
