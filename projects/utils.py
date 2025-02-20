import requests
from bs4 import BeautifulSoup

def get_link_metadata(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract Open Graph metadata
        title = soup.find("meta", property="og:title") or soup.find("title")
        title = title["content"] if title and title.has_attr("content") else title.text if title else "No Title"

        description = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        description = description["content"] if description and description.has_attr("content") else "No Description"

        image = soup.find("meta", property="og:image")
        image = image["content"] if image and image.has_attr("content") else None

        return {"title": title, "description": description, "image": image, "url": url}
    except Exception as e:
        print("Error fetching metadata:", e)
        return None
