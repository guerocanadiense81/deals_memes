# deals_memes_bot.py

import os
import threading
import time
import requests
from flask import Flask
from bs4 import BeautifulSoup

# === CONFIG ===
TG_BOT_TOKEN = os.getenv("TG_TOKEN")
# Comma-separated list of chat IDs or channel usernames
TG_CHAT_IDS = os.getenv("TG_CHAT_IDS", "@DealsAndMemes").split(',')
POST_INTERVAL_HOURS = float(os.getenv("POST_INTERVAL_HOURS", 0.01))  # Hours between posts

# Initial affiliate URLs (add or replace as needed)
AFFILIATE_LINK_URLS = [
    "https://s.click.aliexpress.com/e/_mrbhqxz",
    "https://s.click.aliexpress.com/e/_mPi5MI7",
    "https://s.click.aliexpress.com/e/_mrtzk9Z",
    "https://s.click.aliexpress.com/e/_mPS9JpH",
    "https://s.click.aliexpress.com/e/_mq868sn",
    "https://s.click.aliexpress.com/e/_mOkX37p",
    "https://s.click.aliexpress.com/e/_mLq4Qkn",
    "https://s.click.aliexpress.com/e/_mtBaB8x",
    "https://s.click.aliexpress.com/e/_mscBtzl"
]

# === Scraper: Fetch title, image, and generate hashtags ===
def fetch_aliexpress_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag and title_tag.has_attr("content") else "AliExpress Deal"
        img_tag = soup.find("meta", property="og:image")
        image = img_tag["content"] if img_tag and img_tag.has_attr("content") else None
        words = [w.strip('#,.!') for w in title.lower().split()][:5]
        hashtags = " ".join(f"#{w}" for w in words if len(w) > 2)
        return title, image, hashtags
    except:
        return "AliExpress Deal", None, "#deals"

# Pre-fetch affiliate product data once at startup
PRODUCTS = []
for link in AFFILIATE_LINK_URLS:
    name, image, tags = fetch_aliexpress_data(link)
    if image:
        PRODUCTS.append({"name": name, "link": link, "image": image, "hashtags": tags})

# Index to track sequential posting
item_index = 0

# === Telegram Poster ===
def post_to_telegram(caption, image_url):
    chat_id = random.choice(TG_CHAT_IDS).strip()
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": image_url, "caption": caption}
    try:
        requests.post(url, data=payload, timeout=5)
    except:
        pass

# === Posting Loop ===
def post_daily():
    global item_index
    while True:
        if not PRODUCTS:
            time.sleep(POST_INTERVAL_HOURS * 3600)
            continue

        # Sequential product posting
        item = PRODUCTS[item_index]
        caption = (
            f"🎁 {item['name']}\n"
            f"Only on AliExpress → {item['link']}\n\n"
            f"{item['hashtags']}"
        )
        post_to_telegram(caption, item['image'])

        # Update index and wrap around
        item_index = (item_index + 1) % len(PRODUCTS)

        time.sleep(POST_INTERVAL_HOURS * 3600)

# === Flask App ===
app = Flask(__name__)

@app.route("/")
def home():
    return "Deals & Memes Bot (sequential products) is running."

# Start bot in a separate thread
threading.Thread(target=post_daily, daemon=True).start()

if __name__ == "__main__":
    import random
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
