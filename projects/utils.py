import requests
from bs4 import BeautifulSoup

def get_link_metadata(url):
    """Fetch metadata using BeautifulSoup instead of Selenium."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Ensure we got a valid response
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else "No Title"
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"] if description_tag else "No Description"

        return {"title": title, "description": description, "url": url}
    
    except Exception as e:
        print(f"❌ Failed to fetch metadata for {url}: {str(e)}")
        return {"title": "Unknown", "description": "Could not fetch metadata", "url": url}
