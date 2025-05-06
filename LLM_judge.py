import ollama
from website_scraper import get_website_info

# Define the system prompt to instruct the LLM on its classification task.
system_prompt = """
You are a website content classifier tasked with determining whether a site is suitable for children. Your goal is to block access to websites with any potentially harmful, distracting, or inappropriate content. Classify a website as **"Restricted"** if it contains or promotes:

- Gambling or betting (e.g., Stake, FanDuel)
- Adult or explicit content (e.g., Pornhub)
- Streaming services primarily focused on entertainment (e.g., Netflix)
- Streaming services focused on sports (e.g., ESPN)
- Gaming platforms (e.g., Xbox)
- Celebrity gossip or tabloid-style media (e.g., TMZ)
- Social media platforms (e.g., Facebook, Instagram)
- Dating sites (e.g., Tinder)
- Chatrooms or forums (e.g., Reddit)
- Meme sites or influencer content (e.g., TikTok)
- Reality TV or lifestyle blogs (e.g., Buzzfeed)
- Shopping or luxury brands (e.g., Amazon, Gucci)
- Non-educational forums or time-wasting content

Classify a website as **"Educational"** if it is safe, age-appropriate, and primarily intended for learning or informational purposes. Allow edge cases only if the primary purpose is clearly educational, even if the topic (e.g., poker probability) overlaps with restricted themes.

Now reply *only* with JSON in this exact format:
{
  "classification": "Educational" or "Restricted",
  "reason": "<very brief – cite the indicator>"
}

"""



def classify_website_content(info):
    """
    Constructs a prompt using the website info dictionary and queries the Ollama LLM.
    
    Parameters:
        info (dict): A dictionary containing keys such as 'url', 'page_title', 'meta_description', 
                     and 'content_preview' representing the website metadata and preview text.
    
    Returns:
        str: The LLM's classification and explanation.
    """
    # Build the user content prompt using the info dictionary
    user_content = (
        f"Website Information:\n"
        f"URL: {info.get('url', 'N/A')}\n"
        f"Title: {info.get('page_title', 'N/A')}\n"
        f"Meta Description: {info.get('meta_description', 'N/A')}\n"
        f"Content Preview: {info.get('content_preview', 'N/A')}\n\n"
        "Based on the above details, classify if this website can be used for educational purposes. "
        "Ensure that content related to gaming, pornography, or other non-educational topics results in a 'Restricted' classification."
    )
    
    # Send the prompt to the Ollama LLM and collect the response.
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    
    # Process the response to extract a clean answer.
    full_response = response["message"]["content"]
    clean_response = full_response.split("References:")[0].strip()  # Remove any appended references if present.
    
    if clean_response.lower().startswith("response:"):
        clean_response = clean_response[len("Response:"):].strip()
    
    return clean_response
