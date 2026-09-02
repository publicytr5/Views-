import os
import asyncio
import random
from datetime import datetime
from threading import Thread
from flask import Flask
from pyrogram import Client, errors

# Flask ওয়েব সার্ভার (UptimeRobot এর জন্য)
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

# টেলিগ্রাম এপিআই সেটআপ
API_ID = int(os.getenv("API_ID", "34350558"))
API_HASH = os.getenv("API_HASH", "2047c85a14c5af759734811483199e99")
SESSION_STRING = os.getenv("SESSION_STRING", "BQIMJd4AK7rKJHXS_SjW5aaDZYZPAUj9IhaOTY-pho_bMVt-8r4DRW_UNfq5VXmztTTweCbcjG75HvxGaRNq9k0I8SeMbpArOVK0cZ9N3lqZXlX5oRhtICxhwFUJ1BrAZcwc19sYqROHWc-OIOC4pfqa_hKZSl3ZjB1aqK-BENrP3QUN174QBlmzQ11pxq4fhl-i7N8NqKIDIstZYG9pu1O8mthbuhcZ-ueuZc3zFF1mxovt9PF3W7d7sUtEO61lncJjLsGka0G-iSc88ZHBj-62QyPcNFd_pG68qw0bgxtb3khVC8-72dAqzrhvTvJ5_REGYSjP8yajDx_gtlUQJDjIzcMO7QAAAAHGjZFuAA")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL") # যেমন: @yourchannel

EMOJIS = ["👍", "❤️", "🔥", "🥰", "👏", "😍", "🎉", "🤩"]

tg_app = Client("render_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

daily_reactions_count = 0
current_day = datetime.now().day

async def auto_view_and_react():
    global daily_reactions_count, current_day
    
    async with tg_app:
        print("অটোমেশন স্টার্ট হয়েছে...")
        while True:
            # নতুন দিন শুরু হলে কাউন্টার রিসেট
            today = datetime.now().day
            if today != current_day:
                daily_reactions_count = 0
                current_day = today
                print("নতুন দিন শুরু, রিয়েকশন কাউন্টার ০ করা হলো।")

            # দিনে ১৫০ টির বেশি রিয়েকশন দিলে সেদিন আর রিয়েক্ট করবে না
            if daily_reactions_count >= 150:
                print("আজকের দৈনিক ১৫০ রিয়েকশনের সীমা শেষ। এখন শুধু ভিউ দেওয়া হবে।")

            try:
                # পোস্ট ফেচ করা
                messages = []
                async for msg in tg_app.get_chat_history(TARGET_CHANNEL, limit=10):
                    messages.append(msg)

                if messages:
                    # ১. ভিউ দেওয়া
                    msg_ids = [m.id for m in messages]
                    await tg_app.read_conversation_history(TARGET_CHANNEL, max_id=max(msg_ids))
                    print(f"{len(msg_ids)} টি পোস্টে ভিউ মার্ক করা হয়েছে।")

                    # ২. রিয়েকশন দেওয়া (যদি সীমার মধ্যে থাকে)
                    if daily_reactions_count < 150:
                        # প্রতিবারে ১ থেকে ৪টি রেনডম রিয়েকশন
                        react_limit = min(random.randint(1, 4), len(messages))
                        selected_messages = random.sample(messages, react_limit)

                        for msg in selected_messages:
                            if daily_reactions_count >= 150:
                                break
                            emoji = random.choice(EMOJIS)
                            try:
                                await tg_app.send_reaction(TARGET_CHANNEL, msg.id, emoji)
                                daily_reactions_count += 1
                                print(f"Post ID {msg.id} -> {emoji} | আজকের মোট রিয়েকশন: {daily_reactions_count}")
                            except errors.FloodWait as e:
                                await asyncio.sleep(e.value)
                            except Exception as e:
                                print(f"Reaction Error: {e}")
                            
                            # এক পোস্ট থেকে অন্য পোস্টে রিয়েকশনের মাঝে বিরতি (৩০-৬০ সেকেন্ড)
                            await asyncio.sleep(random.randint(30, 60))

            except Exception as e:
                print(f"লুপ এরর: {e}")

            # প্রতি ৩০ থেকে ৪৫ মিনিট পর পর স্ক্রিপ্টটি পুনরায় রান হবে (দৈনিক ৫-১৫০ রিয়েকশনের ব্যালেন্স রাখতে)
            sleep_time = random.randint(1800, 2700)
            print(f"পরবর্তী চেকের জন্য {sleep_time // 60} মিনিট অপেক্ষা করা হচ্ছে...")
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    # ব্যাকগ্রাউন্ডে Flask সার্ভার চালু করা
    Thread(target=run_web, daemon=True).start()
    # প্রধান টেলিগ্রাম বট চালু করা
    asyncio.run(auto_view_and_react())
