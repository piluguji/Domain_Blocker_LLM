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

def read_rules():
    if not os.path.exists(RULES_FILE):
        return []

    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_rules(rules):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)

def normalize_url(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return 'https://' + url
    return url

@app.route("/get_rules")
def get_rules():
    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            rules = json.load(f)
        return jsonify(rules)
    except Exception as e:
        return jsonify({"error": f"Failed to read rules: {str(e)}"}), 500

@app.route("/check_and_classify")
def check_and_classify():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    url = normalize_url(url)
    classifications = read_classifications()
    rules = read_rules()

    # Check if already classified
    if url in classifications:
        if classifications[url].lower() == "restricted":
            return jsonify({"block": True})
        else:
            return jsonify({"block": False})

    try:
        info = get_website_info(url)
        raw_response = classify_website_content(info)
        classification_data = json.loads(raw_response)

        classification = classification_data.get("classification", "Restricted")
        reason = classification_data.get("reason", "Unknown")

    except Exception as e:
        return jsonify({"error": f"Error classifying site: {str(e)}"}), 500

    # Log result
    with open(CLASSIFICATION_FILE, "a", encoding="utf-8") as log:
        log.write(f"Website URL: {url}\n")
        log.write(f"Classification: {classification}\n")
        log.write(f"Reason: {reason}\n")
        log.write("-" * 50 + "\n")

    if classification == "Restricted":
        if not any(rule['condition']['urlFilter'] == url for rule in rules):
            new_rule = {
                "id": len(rules) + 1,  # Must be an integer
                "priority": 1,
                "action": {"type": "block"},
                "condition": {"urlFilter": url, "resourceTypes": ["main_frame"]}
            }
            rules.append(new_rule)
            save_rules(rules)

        return jsonify({"block": True})

    return jsonify({"block": False})

if __name__ == "__main__":
    app.run(port=5000)
