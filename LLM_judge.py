import ollama
from website_scraper import get_website_info

# Define the system prompt to instruct the LLM on its classification task.
system_prompt = """
You are an expert website content analyst specializing in evaluating educational material. 
Given the website details, your task is to determine whether the website is appropriate for educational use. 
A website is considered "Educational" if it primarily offers academic or instructional content, research, or learning resources.
If the website primarily contains non-educational topics (such as gaming, pornographic material, etc.), classify it as "Not Educational."
Answer in one sentence: first provide your classification ("Educational" or "Not Educational") followed by a brief explanation.
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
        "Ensure that content related to gaming, pornography, or other non-educational topics results in a 'Not Educational' classification."
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
