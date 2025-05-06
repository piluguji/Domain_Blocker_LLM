from LLM_judge import classify_website_content
from website_scraper import get_website_info
import time
import pandas as pd
import json

# --- Keyword Lists ---
EDUCATIONAL_KEYWORDS = {
    "university", "college", "school", "curriculum", "syllabus", "degree", "graduate", "undergraduate",
    "lectures", "learning", "education", "academic", "research", "textbook", "tutorial", "study", "students",
    "professor", "instructor",
    "science", "math", "engineering", "humanities", "class", "seminar", "lesson",
    "scholarly", "study guide", "STEM",
}

RESTRICTED_KEYWORDS = {
    "porn", "xxx", "nsfw", "sex", "nude", "camgirl", "adult", "escort", "strip", "fetish",
    "casino", "betting", "poker", "lottery", "jackpot", "slots", "roulette", "gamble", "wager", "odds",
    "netflix", "hulu", "disney+", "prime video", "streaming", "movies online", "free movies", "watch tv", "live sports", "crunchyroll", "twitch", "anime streaming",
    "gaming", "video game", "ps5", "xbox", "nintendo", "minecraft", "fortnite", "roblox", "steam", "epic games",
    "torrent", "pirate", "crack", "keygen", "warez", "cheat", "hack tool", "dark web",
    "buy weed", "buy cocaine", "buy lsd", "marijuana", "drugstore without prescription", "legal high",
    "celebrity gossip", "fashion blog", "shopping deals", "luxury brands", "astrology", "dating site", "chatroom", "meme site", "influencer", "reality tv"
}


# --- Classification Functions ---
def rules_based_classification(text):
    if not text or not isinstance(text, str):
        return False  # Block if no info available

    text_lower = text.lower()

    if any(keyword in text_lower for keyword in RESTRICTED_KEYWORDS):
        return False

    if any(keyword in text_lower for keyword in EDUCATIONAL_KEYWORDS):
        return True

    return False  # Default to non-educational


def llm_classification(text):
    # call into your LLM wrapper
    raw = classify_website_content(text)

    # try to parse the JSON the model returns
    try:
        obj = json.loads(raw)
        classification = obj.get("classification", "Restricted")
        reason         = obj.get("reason", "")
    except json.JSONDecodeError:
        # fallback if the LLM strays
        classification = "Restricted"
        reason         = "parse error fallback"

    is_blocked = not (classification == "Educational")
    return is_blocked, reason


# --- Evaluation Function ---
def evaluate(df):
    incorrect_llm = 0
    incorrect_rules = 0

    # accumulators for just the classification calls
    time_llm = 0.0
    time_rules = 0.0

    llm_predictions = []

    for _, row in df.iterrows():
        url = row['website_url']
        expected = row['is_blocked']

        # 1) scrape once
        t = time.time()
        info = get_website_info(url)
        elapsed = (time.time() - t)
        time_llm += elapsed
        time_rules += elapsed

        # 2) rules-based
        t0 = time.time()
        pred_rules = rules_based_classification(info)
        time_rules += (time.time() - t0)
        if pred_rules != expected:
            incorrect_rules += 1

        # 3) LLM-based
        t1 = time.time()
        pred_llm, _ = llm_classification(info)
        time_llm += (time.time() - t1)
        llm_predictions.append((url, pred_llm, _ + "\n--------\n"))
        if pred_llm != expected:
            incorrect_llm += 1

    n = len(df)
    acc_rules = 100 * (1 - incorrect_rules / n)
    acc_llm   = 100 * (1 - incorrect_llm   / n)

    print(f"[RULES] Time spent classifying: {time_rules:.2f}s | Accuracy: {acc_rules:.2f}%")
    print(f"[LLM]   Time spent classifying: {time_llm:.2f}s | Accuracy: {acc_llm:.2f}%\n")

    with open("output.txt", "w") as f:
        for item in llm_predictions:
            f.write(f"{item}\n")


# --- Main Runner ---
if __name__ == "__main__":
    df = pd.read_csv('data.csv')

    # Choose one or both
    evaluate(df)
