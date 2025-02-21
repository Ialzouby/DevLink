from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_link_metadata(url):
    """Fetch metadata using a headless browser."""
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Start headless Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load
        soup = BeautifulSoup(driver.page_source, "html.parser")

        title = soup.find("title").text if soup.find("title") else "No Title"
        description = soup.find("meta", attrs={"name": "description"})
        description = description["content"] if description else "No Description"

        driver.quit()  # Close browser

        return {
            "title": title,
            "description": description,
            "image": None,
            "url": url
        }

    except Exception as e:
        driver.quit()
        print(f"❌ Failed to fetch metadata for {url}: {e}")
        return None
