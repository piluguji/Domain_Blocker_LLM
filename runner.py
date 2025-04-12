from LLM_judge import classify_website_content
from website_scraper import get_website_info

if __name__ == "__main__":
    
    urls = [
    "https://www.khanacademy.org",        # Educational
    "https://ocw.mit.edu",                # Educational
    "https://www.edx.org",                # Educational
    "https://www.coursera.org",           # Educational
    "https://www.wikipedia.org",          # Educational
    "https://www.ign.com",                # Gaming/Entertainment
    "https://www.reddit.com/r/gaming",    # Gaming/Entertainment
    "https://www.espn.com",               # Sports/Entertainment
    "https://www.pornhub.com",            # Adult Content
    "https://www.xvideos.com",            # Adult Content
    "https://www.tmz.com",                # Celebrity Gossip/Entertainment
    "https://www.nytimes.com",            # News (mixed content)
    "https://www.hulu.com",               # Entertainment
    "https://www.netflix.com"             # Entertainment
    ]

    for url in urls:
    
        # Retrieve website information.
        info = get_website_info(url)
        
        # Get the classification result from the LLM.
        classification = classify_website_content(info)

        # Append the classification output to a text file.
        output_filename = "website_classifications.txt"
        with open(output_filename, "a", encoding="utf-8") as outfile:
            outfile.write("Website URL: " + info.get("url", "N/A") + "\n")
            outfile.write("Classification: " + classification + "\n")
            outfile.write("-" * 50 + "\n")