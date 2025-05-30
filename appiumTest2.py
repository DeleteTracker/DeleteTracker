import csv
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Set up UiAutomator2Options for Google Play
options = UiAutomator2Options()
options.platformName = 'Android'
options.deviceName = 'emulator-5554'
options.platformVersion = '15.0'
options.appPackage = 'com.android.vending'
options.appActivity = 'com.google.android.finsky.activities.MainActivity'
options.automationName = 'UiAutomator2'
options.sessionOverride = True 

# Connect to the Appium server and launch Google Play
driver = webdriver.Remote('http://localhost:4723', options=options)

# Wait for Google Play to load
sleep(0.5)

# # Initialize the CSV file with headers
# with open('developer_sites.csv', mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(["App Name", "Delete App Account URL", "Manage App Data URL"])


input_file_path = ''
output_file_path = ''

existing_apps = set()
try:
    with open(output_file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            existing_apps.add(row[0])
except FileNotFoundError:
    # If the file doesn't exist, initialize it with headers
    with open(output_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["App Name", "Delete App Account URL", "Manage App Data URL"])

app_names_set = set()

with open(input_file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        app_name = row['App Name']
        if app_name != 'Not Found':
            app_names_set.add(app_name)

app_names = sorted(list(app_names_set))

# print(app_names)

# app_names = ["101 Okey Plus Rummy Board Game"]

for app_name in app_names:
    print(app_name)

    if app_name in existing_apps:
        print(f"App '{app_name}' already exists in the CSV. Skipping.")
        continue  # Skip this app as it's already in the CSV

    start_time = time.time()

    # Find and click the search box in Google Play
    search_box = WebDriverWait(driver, 0.5).until(
        EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, 'Search Google Play'))
    )
    search_box.click()

    # Enter the app name to search for (e.g., "Snapchat")
    search_input = driver.find_element(AppiumBy.XPATH, '//android.widget.EditText')
    search_input.send_keys(app_name)

    # Simulate pressing the "Enter" key on the keyboard to search
    driver.press_keycode(66)

    # Wait for search results to load
    sleep(0.5)

    # Click on the first app in the search results
    try:
    # Try to locate the app by its name
        first_result = WebDriverWait(driver, 0.5).until(
            EC.presence_of_element_located((AppiumBy.XPATH, f'//android.view.View[contains(@content-desc, "{app_name}")]'))
        )
        first_result.click()  # Click the app if found
    except Exception as e:
        print(f"App '{app_name}' not found or doesn't match exactly. Skipping this app.")
        with open(output_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([app_name, 'Skipping this app', 'Skipping this app'])
        sleep(2)
        continue

    # Wait for the app details page to load
    sleep(0.5)

    # Use a loop to scroll multiple times to find the "Data safety" section
    found = False
    for _ in range(4):
        try:
            data_safety_button = WebDriverWait(driver, 0.5).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Data safety"]'))
            )
            data_safety_button.click()
            found = True
            break
        except:
            driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true)).scrollForward()'
            )
            sleep(0.5)

    if found:
        
        delete_account_url = None
        manage_data_url = None

        # Scroll a few times to ensure that the entire section is loaded
        for _ in range(4):
            driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true)).scrollForward()'
            )
            sleep(0.5)

        try:
            # Find all "Go to developer's site" links
            go_to_site_links = driver.find_elements(AppiumBy.XPATH, '//android.widget.TextView[@text="Go to developer\'s site"]')
            print(f"Found {len(go_to_site_links)} 'Go to developer's site' links")
            
            FindDeleteAccount = False
            FindManageData = False

            # Check for the existence of the "Delete app account" section
            try:
                driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Delete app account"]')
                FindDeleteAccount = True
                print("Found 'Delete app account' section.")
            except:
                print("'Delete app account' section not found.")

            # Check for the existence of the "Manage app data" section
            try:
                driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Manage app data"]')
                FindManageData = True
                print("Found 'Manage app data' section.")
            except:
                print("'Manage app data' section not found.")

            if len(go_to_site_links) == 0:
                print("No 'Go to developer's site' links found.")
                with open(output_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([app_name, 'Not found', 'Not found'])
            
            if len(go_to_site_links) == 1:
                go_to_site_links[0].click()
                if FindDeleteAccount:
                    # Get the URL from the Chrome browser
                    try:
                        url_field = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.android.chrome:id/url_bar"]'))
                        )
                        print(f"Delete account URL: {url_field.text}")
                    except Exception as e:
                        print(f"Exception occurred while retrieving 'Delete app account' URL: {e}")
                    with open(output_file_path, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([app_name, url_field.text, 'Not found'])
                    driver.back()
                if FindManageData:
                    # Get the URL from the Chrome browser
                    try:
                        url_field = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.android.chrome:id/url_bar"]'))
                        )
                        print(f"Manage app data URL: {url_field.text}")
                    except Exception as e:
                        print(f"Exception occurred while retrieving 'Manage app data' URL: {e}")
                    with open(output_file_path, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([app_name, "Not found", url_field.text])
                    driver.back()

            if len(go_to_site_links) > 1:
                # Click the first lin
                go_to_site_links[0].click()
                sleep(0.5)

                url_field = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.android.chrome:id/url_bar"]'))
                    )
                delete_account_url = url_field.text
                print(f"Delete account URL: {delete_account_url}")
                
                driver.back()

                go_to_site_links[1].click()
                sleep(0.5)

                url_field = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.android.chrome:id/url_bar"]'))
                    )
                manage_data_url = url_field.text
                print(f"Manage app data URL: {manage_data_url}")
                    
                driver.back()
                    
                with open(output_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([app_name, delete_account_url, manage_data_url])                    
                
        except Exception as e:
            print(f"Exception occurred while retrieving URLs: {e}")

    driver.back()
    sleep(2)

    # Click on the search box to start a new search
    try:
        search_button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Search"]'))
        )
        search_button.click()
        # print("Search button clicked.")
    except Exception as e:
        print(f"Exception occurred while trying to click the search button: {e}")
    
    print(f"Time taken for {app_name}: {time.time() - start_time:.2f} seconds")


# Close the Appium session
driver.quit()
