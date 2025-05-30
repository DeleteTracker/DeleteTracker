import pandas as pd
import requests
from bs4 import BeautifulSoup

df = pd.read_csv('')  
df['Data Deletion Info'] = ''  

count = 1

for index, row in df.iterrows():
    app_id = row['Apk Name']  
    print(count, ": ", app_id)
    url = f"https://play.google.com/store/apps/details?id={app_id}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()

            if "You can request that data be deleted" in page_text:
                df.at[index, 'Data Deletion Info'] = 'can'
            else:
                df.at[index, 'Data Deletion Info'] = 'cannot'
        else:
            df.at[index, 'Data Deletion Info'] = 'Cannot access'
    except Exception as e:
        df.at[index, 'Data Deletion Info'] = 'Exception occurred'
    # print(row['B'])
    count += 1

df.to_csv('', index=False)
print("Finished")
