# deals_memes_bot.py

import os
import random
import threading
import time
import requests
from flask import Flask

# === CONFIG ===
TG_BOT_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
POST_INTERVAL_HOURS = 24  # Post once per day

# === REAL AFFILIATE LINKS ===
AFFILIATE_LINKS = [
    ("Creepy Cute Bunny Plush", "https://s.click.aliexpress.com/e/_mrbhqxz"),
    ("Funny Cat Massager Toy", "https://s.click.aliexpress.com/e/_mPi5MI7"),
    ("LED Star Projector", "https://s.click.aliexpress.com/e/_mrtzk9Z"),
    ("Mini Bag Sealer", "https://s.click.aliexpress.com/e/_mPS9JpH")
]

# === Meme Fetcher ===
def get_meme():
    url = "https://meme-api.com/gimme"
    try:
        res = requests.get(url)
        data = res.json()
        return data['title'], data['url']  # title, image URL
    except:
        return "When memes fail to load...", "https://i.imgur.com/4M34hi2.jpg"

# === Telegram Poster ===
def post_to_telegram(caption, image_url):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TG_CHAT_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=payload)
        print("✅ Posted to Telegram!" if r.status_code == 200 else r.text)
    except Exception as e:
        print(f"❌ Error posting to Telegram: {e}")

# === Posting Loop ===
def post_daily():
    while True:
        title, meme_url = get_meme()
        product, link = random.choice(AFFILIATE_LINKS)
        caption = f"{title}\n\n**Today’s meme deal:**\n[{product}]({link})"
        post_to_telegram(caption, meme_url)
        time.sleep(POST_INTERVAL_HOURS * 3600)

# === Flask App ===
app = Flask(__name__)

@app.route("/")
def home():
    return "Deals & Memes Bot is running."

# === Start bot in a separate thread ===
threading.Thread(target=post_daily, daemon=True).start()

# === Run Flask app ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
