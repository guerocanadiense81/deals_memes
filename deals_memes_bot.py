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
POST_INTERVAL_HOURS = 0.01  # Post every ~36 seconds

# Real affiliate links with product images
AFFILIATE_LINKS = [
    ("Creepy Cute Bunny Plush", "https://s.click.aliexpress.com/e/_mrbhqxz", "https://i.imgur.com/1qv7F1Z.jpg"),
    ("Funny Cat Massager Toy", "https://s.click.aliexpress.com/e/_mPi5MI7", "https://i.imgur.com/N0u2DbR.jpg"),
    ("LED Star Projector", "https://s.click.aliexpress.com/e/_mrtzk9Z", "https://i.imgur.com/fL2a4fw.jpg"),
    ("Mini Bag Sealer", "https://s.click.aliexpress.com/e/_mPS9JpH", "https://i.imgur.com/yP1IQs0.jpg"),
    ("USB Finger Massager", "https://s.click.aliexpress.com/e/_mq868sn", "https://i.imgur.com/S94Ix0Y.jpg"),
    ("Cute Bear Humidifier", "https://s.click.aliexpress.com/e/_mOkX37p", "https://i.imgur.com/t7eGeqA.jpg"),
    ("Mini Hand Warmer", "https://s.click.aliexpress.com/e/_mLq4Qkn", "https://i.imgur.com/5iSFSU4.jpg"),
    ("Portable Juicer Cup", "https://s.click.aliexpress.com/e/_mtBaB8x", "https://i.imgur.com/kMORXRr.jpg"),
    ("Pet Brush Glove", "https://s.click.aliexpress.com/e/_mscBtzl", "https://i.imgur.com/bU8U3w5.jpg")
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
        "caption": caption
    }
    requests.post(url, data=payload)

# === Posting Loop ===
def post_daily():
    while True:
        if random.random() > 0.2:
            # Meme mode (80% of the time)
            title, meme_url = get_meme()
            caption = f"{title}\n\n#memes #funny"
            post_to_telegram(caption, meme_url)
        else:
            # Product mode (20% of the time)
            product, link, image = random.choice(AFFILIATE_LINKS)
            caption = f"\U0001F525 {product}\nOnly on AliExpress → {link}\n#deals #shopping"
            post_to_telegram(caption, image)

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
