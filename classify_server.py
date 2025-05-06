
import os
from flask import Flask, request, jsonify
from LLM_judge import classify_website_content
from website_scraper import get_website_info
import json
from flask_cors import CORS

CLASSIFICATION_FILE = "chrome_extension/website_classifications.txt"
RULES_FILE = "chrome_extension/rules.json"

app = Flask(__name__)
CORS(app)

# Read the classification file and return the classifications
def read_classifications():
    if not os.path.exists(CLASSIFICATION_FILE):
        return {}

    classifications = {}
    with open(CLASSIFICATION_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_url = None
    for line in lines:
        if line.startswith("Website URL:"):
            current_url = line.split("Website URL:")[1].strip()
        elif line.startswith("Classification:") and current_url:
            classification = line.split("Classification:")[1].strip()
            classifications[current_url] = classification
            current_url = None
    return classifications

# Read the rules from rules.json
def read_rules():
    if not os.path.exists(RULES_FILE):
        return []

    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Save the updated rules back to rules.json
def save_rules(rules):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)

# Function to normalize and check URL format (adds https if missing)
def normalize_url(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return 'https://' + url
    return url

@app.route("/get_rules")
def get_rules():
    with open("chrome_extension/rules.json", "r", encoding="utf-8") as f:
        rules = json.load(f)
    return jsonify(rules)

@app.route("/check_and_classify")
def check_and_classify():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    # Normalize the URL to ensure it has the proper format
    url = normalize_url(url)

    # Read classifications and rules
    classifications = read_classifications()
    rules = read_rules()

    # If URL is already classified, return the classification
    if url in classifications:
        if "not educational" in classifications[url].lower():
            return jsonify({"block": True})
        else:
            return jsonify({"block": False})

    # If not in classification file, classify the website
    try:
        info = get_website_info(url)
        classification = classify_website_content(info)
    except Exception as e:
        return jsonify({"error": f"Error classifying site: {str(e)}"}), 500

    # Log classification to file
    with open(CLASSIFICATION_FILE, "a", encoding="utf-8") as log:
        log.write(f"Website URL: {url}\n")
        log.write(f"Classification: {classification}\n")
        log.write("-" * 50 + "\n")

    # If it's non-educational, add it to rules.json
    if "not educational" in classification.lower():
        # Check if the rule already exists
        rule_exists = any(rule['condition']['urlFilter'] == url for rule in rules)
        if not rule_exists:
            new_rule = {
                "id": len(rules) + 1,  # Unique ID for the rule
                "priority": 1,
                "action": {"type": "block"},
                "condition": {"urlFilter": url, "resourceTypes": ["main_frame"]}
            }
            rules.append(new_rule)

            # Save the updated rules to rules.json
            save_rules(rules)

        return jsonify({"block": True})

    return jsonify({"block": False})

if __name__ == "__main__":
    app.run(port=5000)
