import time
import csv
import pandas as pd
import requests
from tqdm import tqdm


df = pd.read_csv("/content/website_classification.csv")
df['url_exists'] = False

# Function to check if URL is reachable
def check_url(url):
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code < 400
    except requests.RequestException:
        return False

tqdm.pandas(desc="Checking URLs")
df['url_exists'] = df['website_url'].progress_apply(check_url)
df.to_csv("checked_urls.csv", index=False)


df['is_education'] = df['Category'].str.lower() == 'education'
df.to_csv("checked_with_education_flag.csv", index=False)

checked_df2 = pd.read_csv("checked_with_education_flag.csv")  

edu_df = checked_df2[checked_df2['is_education'] == True]
non_edu_df = checked_df2[checked_df2['is_education'] == False]

# Randomly sample 50% of the non-education rows
non_edu_sampled = non_edu_df.sample(frac=0.75, random_state=42)
reduced_df = pd.concat([edu_df, non_edu_sampled], ignore_index=True)
reduced_df = reduced_df.sample(frac=1, random_state=42).reset_index(drop=True)
reduced_df.to_csv("reduced_dataset.csv", index=False)


checked_df = pd.read_csv("checked_urls.csv")
checked_df = checked_df[checked_df['url_exists'] == True].reset_index(drop=True)

category_col = 'Category'

num_unique_categories = checked_df[category_col].nunique()
print(f"Number of unique categories: {num_unique_categories}")

category_counts = checked_df[category_col].value_counts()
print("\nEntries per category:")
print(category_counts)

print(checked_df.info())


def csv_to_list(file_path):
    data_list = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data_list.append(row)
    return data_list

edu_domains = csv_to_list('/content/edu_domains.csv')
edu_domains = [phrase[1].lower() for phrase in edu_domains]
restricted_domains = csv_to_list('/content/restricted_domains.csv')
restricted_domains = [phrase[1].lower() for phrase in restricted_domains]

start_time = time.time()

# Classification function
def classify(row):
    url = row['website_url'].lower()
    is_edu = row['is_education']
    contains_edu = any(phrase in url for phrase in edu_domains)
    contains_restricted = any(phrase in url for phrase in restricted_domains)
    
    if contains_edu and is_edu:
        return "Correct Assumption Educational"
    elif contains_restricted and not is_edu:
      return "Correct Assumption Restricted"
    elif contains_edu and not is_edu:
        return "False Positive"
    elif not contains_edu and is_edu:
        return "Missed Educational"
    elif contains_restricted and is_edu:
      return "False Negative"
    else:
        return "Correct Non-Educational"

df['assumption_result'] = df.apply(classify, axis=1)

correct = df['assumption_result'].isin(["Correct Assumption Educational", "Correct Assumption Restricted"]).sum()
overall_correct = df['assumption_result'].isin(["Correct Assumption Educational", "Correct Assumption Restricted", "Correct Non-Educational"]).sum()
accuracy = correct / len(df)
overall_accuracy = overall_correct / len(df)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Accuracy: {accuracy:.2%}")
print(f"Overall Accuracy: {overall_accuracy:.2%}")
print(f"Execution Time: {elapsed_time:.2f} seconds")

df.to_csv("assumption_evaluation.csv", index=False)

category_counts = df['assumption_result'].value_counts()
print("\nEntries per category:")
print(category_counts)


