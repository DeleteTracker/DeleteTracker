import os
import re
import spacy
import pandas as pd

plaintext_path = ''
csv_path = ''
output_csv = ''

df_apps = pd.read_csv(csv_path)
df_apps['Processed App Name'] = df_apps['App Name'].str.split(':').str[0].str.strip().str.lower()
app_names = df_apps['Processed App Name'].tolist()  

# 加载 spaCy 
nlp = spacy.load("en_core_web_sm")

def detect_in_app_path(page_text):
    keywords = [
        "in-app account deletion"
    ]
    phrase_patterns = [
        r"open\s+\w+\s+app",       # "open Netflix app"
        r"opening\s+\w+\s+app",       # "open Netflix app"
        r"tap\s+\w+\s+profile",    # "tap user profile"
        r"tapping\s+\w+\s+profile",    # "tap user profile"
        r"tap\s+\w+\s+settings"    # "tap account settings"
        r"tapping\s+\w+\s+settings"    # "tap account settings"
    ]

    results = {
        # "Detected Keywords": [],
        "Matched Phrases": [],
        "Dependency Analysis Results": []
    }
    # for kw in keywords:
    #     if kw.lower() in page_text.lower():
    #         results["Detected Keywords"].append(kw)


    for pattern in phrase_patterns:
        found = re.findall(pattern, page_text, re.IGNORECASE)
        results["Matched Phrases"].extend(found)

    doc = nlp(page_text)
    for token in doc:
        #  "open ... app"
        if token.lemma_ in ["open", "opening"] and token.pos_ == "VERB":
            for child in token.children:
                if child.dep_ == "dobj" and any(app_name in child.text.lower() for app_name in app_names):
                    results["Dependency Analysis Results"].append(
                        f"Detected: 'open {child.text}' in '{token.sent.text}'"
                    )
                elif child.dep_ == "dobj":
                    subtree = " ".join([t.text.lower() for t in child.subtree])
                    if any(app_name in subtree for app_name in app_names):
                        results["Dependency Analysis Results"].append(
                            f"Detected: 'open {subtree}' in '{token.sent.text}'"
                        )

        # "tap ... settings" 或 "tap ... profile"
        elif token.lemma_ in ["tap", "tapping"] and token.pos_ == "VERB":
            for child in token.children:
                if child.dep_ == "dobj" and child.text.lower() in ["settings", "profile", "avatar"]:
                    results["Dependency Analysis Results"].append(
                        f"Detected: 'tap ... {child.text}' in '{token.sent.text}'"
                    )
        # "delete ... account ... in-app"
        elif token.lemma_ in ["delete", "deleting"] and token.pos_ == "VERB":
            has_account = False
            has_in_app = False
            for child in token.children:
                if child.dep_ == "dobj" and "account" in child.text.lower():
                    has_account = True
                if child.dep_ in ["prep", "pobj", "advmod"] and any(
                    phrase in child.text.lower() for phrase in ["application", "app", "in-app", "within the app", "via the app", "inside the app", "inside the application"]
                ):
                    has_in_app = True
            if has_account and has_in_app:
                results["Dependency Analysis Results"].append(
                    f"Detected: 'delete ... account ... in-app' in '{token.sent.text}'"
                )

    return any(results.values()), results  



df = pd.read_csv(csv_path)

results = []
for filename in os.listdir(plaintext_path):
    apk_name = filename.replace('.txt', '')

    with open(os.path.join(plaintext_path, filename), "r", encoding="utf-8") as f:
        page_text = f.read()
        is_in_app_path, detection_results = detect_in_app_path(page_text)

        if apk_name in df['Apk Name'].values:
            results.append({
                "Apk Name": apk_name,
                "In-App Path": "Yes" if is_in_app_path else "No",
                # "Detected Keywords": ", ".join(detection_results["Detected Keywords"]),
                "Matched Phrases": ", ".join(detection_results["Matched Phrases"]),
                "Dependency Analysis Results": ", ".join(detection_results["Dependency Analysis Results"])
            })

new_df = pd.DataFrame(results)

merged_df = pd.merge(df, new_df, on="Apk Name", how="left")
merged_df.to_csv(output_csv, index=False)

print(f"Processed results saved to: {output_csv}")
