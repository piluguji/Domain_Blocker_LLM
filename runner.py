from LLM_judge import classify_website_content
from website_scraper import get_website_info
import time 

if __name__ == "__main__":
    
    urls = [
        ("https://www.khanacademy.org", True),
        ("https://ocw.mit.edu", True),
        ("https://www.edx.org", True),
        ("https://www.coursera.org", True),
        ("https://www.wikipedia.org", True),
        ("https://www.ign.com", False),
        ("https://www.reddit.com/r/gaming", False),
        ("https://www.espn.com", False),
        ("https://www.pornhub.com", False),
        ("https://www.xvideos.com", False),
        ("https://www.tmz.com", False),
        ("https://www.nytimes.com", True),
        ("https://www.hulu.com", False),
        ("https://www.netflix.com", False)
    ]

    incorrect = 0 
    start = time.time()
    for url, is_educational in urls:
    
        # Retrieve website information.
        info = get_website_info(url)
        
        # Get the classification result from the LLM.
        llm_result = classify_website_content(info)
        llm_is_educational = llm_result.lower().startswith("educational")

        if llm_is_educational != is_educational:
            # print(f"Mismatch for {url}: Expected {is_educational}, got {llm_is_educational}")
            # print(llm_result)
            incorrect += 1

    print(f"Time: {time.time() - start:.2f} s")
    print(f"Accuracy: {100*(1.0 - incorrect/len(urls)):.2f}%")