import requests
from bs4 import BeautifulSoup
import pandas as pd

def detect_user_input_forms(url):
    try:

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        detected_forms = []

        forms = soup.find_all('form')
        for form in forms:
            form_details = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'fields': []
            }
            inputs = form.find_all(['input', 'textarea', 'select'])
            for inp in inputs:
                field_type = inp.get('type', 'text') 
                field_name = inp.get('name', '')
                placeholder = inp.get('placeholder', '')
                form_details['fields'].append({
                    'type': field_type,
                    'name': field_name,
                    'placeholder': placeholder
                })

            detected_forms.append(form_details)

        has_user_input = len(detected_forms) > 0

        return {
            'Has User Input': has_user_input,
            'Detected Forms': detected_forms
        }

    except requests.exceptions.RequestException as e:
        return {"Error": f"Failed to access URL: {e}"}

if __name__ == "__main__":
    input_path = ''
    df = pd.read_csv(input_path)
    df['result'] = df['Redirect URL'].apply(detect_user_input_forms)

    output_path = ''
    df.to_csv(output_path, index=False)
