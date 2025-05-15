import os
import requests
from bs4 import BeautifulSoup
from app.utils import load_scraped_ids, save_scraped_ids

def fetch_latest_items():
    url = os.getenv("HDHUB4U_URL", "https://hdhub4u.wiki/")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to fetch HDHUB4U: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    scraped_ids = load_scraped_ids()
    new_items = []

    for post in soup.select(".post-title a"):
        title = post.get_text(strip=True)
        link = post.get("href")
        if link and link not in scraped_ids:
            new_items.append({"title": title, "link": link})

    save_scraped_ids(new_items)
    return new_items
