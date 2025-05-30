# deals_memes_bot.py

import os
import random
import threading
import time
import requests
from flask import Flask
from bs4 import BeautifulSoup

# === CONFIG ===
TG_BOT_TOKEN = os.getenv("TG_TOKEN")
# Comma-separated list of chat IDs or channel usernames
TG_CHAT_IDS = os.getenv("TG_CHAT_IDS", "@DealsAndMemes").split(',')
POST_INTERVAL_HOURS = 0.01  # Post every ~36 seconds
ENABLE_MEMES = False  # Set to False to pause memes, True to enable memes

# Initial affiliate URLs (replace or add more)
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
        tag = soup.find("meta", property="og:title")
        title = tag["content"] if tag and tag.has_attr("content") else "AliExpress Deal"
        imgtag = soup.find("meta", property="og:image")
        image = imgtag["content"] if imgtag and imgtag.has_attr("content") else None
        words = [w.strip('#,.!') for w in title.lower().split()][:5]
        hashtags = " ".join(f"#{w}" for w in words if len(w) > 2)
        return title, image, hashtags
    except Exception as e:
        print(f"Error scraping {url}", e)
        return "AliExpress Deal", None, "#deals"

# Pre-fetch affiliate product data once at startup
PRODUCTS = []
for link in AFFILIATE_LINK_URLS:
    name, image, tags = fetch_aliexpress_data(link)
    PRODUCTS.append({"name": name, "link": link, "image": image, "hashtags": tags})

# === Telegram Poster ===
def post_to_telegram(caption, image_url):
    if not image_url:
        return
    chat_id = random.choice(TG_CHAT_IDS).strip()
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": image_url, "caption": caption}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"Error posting to Telegram ({chat_id})", e)

# === Posting Loop ===
def post_daily():
    while True:
        # Always post affiliate products
        item = random.choice(PRODUCTS)
        caption = (
            f"🎁 {item['name']}\n"
            f"Only on AliExpress → {item['link']}\n\n"
            f"{item['hashtags']}"
        )
        post_to_telegram(caption, item['image'])

        # If memes are enabled, optionally post a meme after product
        if ENABLE_MEMES:
            # Meme Fetch
            try:
                res = requests.get("https://meme-api.com/gimme", timeout=5).json()
                title, meme_url = res.get('title'), res.get('url')
            except:
                title, meme_url = "When memes fail to load...", "https://i.imgur.com/4M34hi2.jpg"
            meme_caption = f"😂 {title}\n\n#memes #relatable #funny"
            post_to_telegram(meme_caption, meme_url)

        time.sleep(POST_INTERVAL_HOURS * 3600)

# === Flask App ===
app = Flask(__name__)

@app.route("/")
def home():
    return "Deals & Memes Bot with memes paused is running."

# Start bot in a separate thread
threading.Thread(target=post_daily, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
