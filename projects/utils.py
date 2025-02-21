import requests
from bs4 import BeautifulSoup

def get_link_metadata(url):
    """
    Fetches metadata (title, description, and image) from a given URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else None
        og_title = soup.find("meta", property="og:title")
        title = og_title["content"] if og_title else title or "No Title"

        description = None
        meta_description = soup.find("meta", attrs={"name": "description"})
        og_description = soup.find("meta", property="og:description")

        if meta_description:
            description = meta_description["content"]
        elif og_description:
            description = og_description["content"]
        else:
            description = "No Description"

        og_image = soup.find("meta", property="og:image")
        image = og_image["content"] if og_image else None

        return {
            "title": title.strip() if title else "No Title",
            "description": description.strip() if description else "No Description",
            "image": image.strip() if image else None,
            "url": url
        }

    except requests.exceptions.RequestException as e:
        print(f"⚠ Error fetching metadata for {url}: {e}")
        return {"title": "No Title", "description": "No Description", "image": None, "url": url}
