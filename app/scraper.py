# app/scraper.py
import os
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException

class Hdhub4uScraper:
    def __init__(self, base_url='https://hdhub4u.football'):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # MongoDB connection
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('MONGODB_DB', 'scraper_db')]
        self.collection = self.db[os.getenv('MONGODB_COLLECTION', 'scraped_items')]
        
        # Create unique index on links
        self.collection.create_index('link', unique=True)

    def _get_existing_links(self):
        return {item['link'] for item in self.collection.find({}, {'link': 1})}

    def _store_new_items(self, items):
        if not items:
            return
        try:
            # Insert only new items
            for item in items:
                self.collection.update_one(
                    {'link': item['link']},
                    {'$setOnInsert': item},
                    upsert=True
                )
        except Exception as e:
            print(f"MongoDB error: {e}")

    def scrape_new_releases(self):
        """
        WARNING: Website structure changes frequently. This selector pattern
        may need adjustment. Scraping may violate HDHUB4U's Terms of Service.
        """
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.movie-list .movie-item')  # Update selector
            
            parsed_items = []
            for item in items:
                try:
                    title = item.select_one('.title').text.strip()
                    link = item.select_one('a')['href']
                    if not link.startswith('http'):
                        link = self.base_url + link
                    parsed_items.append({'title': title, 'link': link})
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue

            existing_links = self._get_existing_links()
            new_items = [item for item in parsed_items if item['link'] not in existing_links]
            
            if new_items:
                self._store_new_items(new_items)
            
            return new_items

        except RequestException as e:
            print(f"Request failed: {e}")
            return []
        except Exception as e:
            print(f"Scraping error: {e}")
            return []
