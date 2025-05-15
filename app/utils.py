import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "hdhub4u")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "scraped_links")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def load_scraped_ids():
    return [doc["link"] for doc in collection.find({}, {"_id": 0, "link": 1})]

def save_scraped_ids(new_items):
    if not new_items:
        return
    to_insert = [{"link": item["link"], "title": item["title"]} for item in new_items]
    collection.insert_many(to_insert)
