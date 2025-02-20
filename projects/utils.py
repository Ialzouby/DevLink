import requests
from bs4 import BeautifulSoup

def get_link_metadata(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 403:
            print(f"❌ Blocked by {url} (403 Forbidden)")
            return None
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text if soup.find("title") else "No Title"
        description = soup.find("meta", attrs={"name": "description"})
        description = description["content"] if description else "No Description"

        return {
            "title": title,
            "description": description,
            "image": None,
            "url": url
        }
    except Exception as e:
        print(f"❌ Failed to fetch metadata for {url}: {e}")
        return None
