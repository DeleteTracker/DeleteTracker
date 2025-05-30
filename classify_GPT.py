import pandas as pd
import os
import openai

input_path = ''
output_path = ''
folder_path = ""

def chatgpt_classify(content):
    openai.api_key = ''

    messages = [{"role": "system", "content": "You are an expert of Google Data Safety Section."}]
    message = f"You are tasked with reviewing the content of the following URL and classifying the method(s) it describes for account deletion. There are four possible categories: \
                1. In-App Path: The webpage describes the specific steps or navigation paths users can follow within an app (on Android, iOS, or other platforms) to delete their account.\
                2. Web-Based Method: The webpage provides a direct URL or interface where users can input their information and delete their account online.\
                3. Email Request: The webpage specifies that users must send an email to the developer or company to request account deletion.\
                4. No Account Deletion Information: The webpage does not include any content related to account deletion.\
                Task: \
                1. Review the following content. \
                2. Determine which of the above categories apply (it can be one or more).\
                3. Output the classification as follows (must follow this format, do not include any other explanation): [In-App Path], [Web-Based Method], [Email Request], [No Account Deletion Information], or a combination if multiple methods are mentioned.\
                Example Output: [Web-Based Method, Email Request]\
                Content: {content}"
    
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            if message:
                messages.append(
                    {"role": "user", "content": message},
                )
                chat = openai.ChatCompletion.create(
                    model="gpt-4o", messages=messages, timeout=30
                )
            reply = chat.choices[0].message['content']
            print("ChatGPT: " + reply)
            return reply
        except openai.error.APIError as e:
            print(f"API Error occurred: {e}. Retrying...")
            retry_count += 1
        except requests.exceptions.Timeout as e:
            print(f"Timeout occurred: {e}. Retrying...")
            retry_count += 1
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Retrying...")
            retry_count += 1

    return "Error: Max retries exceeded"

def process_txt_files_in_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        return []
    
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    if not files:
        print(f"No .txt files found in {folder_path}.")
        return []

    results = []
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                result = chatgpt_classify(content)
                apk_name = os.path.splitext(file_name)[0]  
                results.append({"Apk Name": apk_name, "GPT Classification": result})
                print(f"File: {file_name} -> {result}")
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
            results.append({"Apk Name": os.path.splitext(file_name)[0], "GPT Classification": f"Error: {e}"})
    
    return results

classification_results = process_txt_files_in_folder(folder_path)

classification_df = pd.DataFrame(classification_results)

df = pd.read_csv(input_path)

df = df.merge(classification_df, on='Apk Name', how='left')

df.to_csv(output_path, index=False)

print("Processing complete. Results saved to:", output_path)
