import pandas as pd
import requests
import random
import time

input_path = ''
output_path = ''

df = pd.read_csv(input_path)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
]

def check_url(url):
    if not url.startswith(('http://', 'https://')):
        url_https = 'https://' + url
        try:
            response = requests.get(
                url_https, 
                timeout=10, 
                headers={"User-Agent": random.choice(user_agents)}
            )
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        
        url_http = 'http://' + url
        try:
            response = requests.get(
                url_http, 
                timeout=10, 
                headers={"User-Agent": random.choice(user_agents)}
            )
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass

    else:
        try:
            response = requests.get(
                url, 
                timeout=10, 
                headers={"User-Agent": random.choice(user_agents)}
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    return False

df['Delete App Account URL Available'] = df['Delete App Account URL'].apply(check_url)
# df['Manage App Data URL Available'] = df['Manage App Data URL'].apply(check_url)

df.to_csv(output_path, index=False)

print(f"{output_path}")
