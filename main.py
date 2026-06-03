# ============================================================
#Group Manager Bot
# Author: LearningBotsOfficial (https://github.com/LearningBotsOfficial) 
# Support: https://t.me/LearningBotsCommunity
# Channel: https://t.me/learning_bots
# YouTube: https://youtube.com/@learning_bots
# License: Open-source (keep credits, no resale)
# ============================================================

from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
import logging
from handlers import register_all_handlers
from handlers.clone import start_clone_bot
import db
import asyncio

logging.basicConfig(level=logging.INFO)

app = Client(
    "group_manger_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

async def start_bot():
    print("Bot is starting... ")
    await app.start()
    register_all_handlers(app)

    # Start clones
    clones = await db.get_clones()
    print(f"Starting {len(clones)} clones...")
    for clone in clones:
        try:
            token = clone['token']
            await start_clone_bot(token)
            print(f"✅ Started clone: @{clone['bot_username']}")
            await asyncio.sleep(1) # Staggered start
        except Exception as e:
            print(f"❌ Failed to start clone @{clone.get('bot_username')}: {e}")

    print("✅ Main bot and clones are running!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())