import requests
from bs4 import BeautifulSoup
from django.core.cache import cache

def get_link_metadata(url):
    """
    Fetches and caches metadata (title, description, and image) from a given URL.
    """

    cache_key = f"link_metadata_{url}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data  # ✅ Return cached metadata if available

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = soup.title.string if soup.title else None
        if not title:
            og_title = soup.find("meta", property="og:title")
            title = og_title["content"] if og_title else "No Title"

        # Extract description
        description = None
        meta_description = soup.find("meta", attrs={"name": "description"})
        og_description = soup.find("meta", property="og:description")

        if meta_description:
            description = meta_description["content"]
        elif og_description:
            description = og_description["content"]
        else:
            description = "No Description"

        # Extract image
        image = None
        og_image = soup.find("meta", property="og:image")
        if og_image:
            image = og_image["content"]

        metadata = {
            "title": title.strip() if title else "No Title",
            "description": description.strip() if description else "No Description",
            "image": image.strip() if image else None,
            "url": url
        }

        # ✅ Store in cache for 1 hour (3600 seconds)
        cache.set(cache_key, metadata, timeout=3600)
        return metadata

    except requests.exceptions.RequestException as e:
        print(f"⚠ Error fetching metadata for {url}: {e}")
        return {"title": "No Title", "description": "No Description", "image": None, "url": url}
