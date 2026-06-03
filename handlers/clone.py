# ============================================================
# Group Manager Bot - Clone Handler
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import Message
import db
from config import API_ID, API_HASH
import logging

logger = logging.getLogger(__name__)

# To keep track of running clones in the current process
cloned_bots = {}

async def start_clone_bot(token):
    if token in cloned_bots:
        try:
            bot_info = await cloned_bots[token].get_me()
            return bot_info.username
        except Exception:
            del cloned_bots[token]

    try:
        from handlers import register_all_handlers
        client = Client(
            name=f"clone_{token[:10]}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=token
        )
        await client.start()
        register_all_handlers(client)
        bot_info = await client.get_me()
        cloned_bots[token] = client
        return bot_info.username
    except Exception as e:
        logger.error(f"Error starting clone bot: {e}")
        return None

def register_clone_handlers(app: Client):
    @app.on_message(filters.private & filters.command("clone"))
    async def clone_bot(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/clone <BOT_TOKEN>`\n\nGet your bot token from @BotFather")

        token = message.text.split(None, 1)[1]
        msg = await message.reply_text("🤖 Starting your clone bot... Please wait.")

        bot_username = await start_clone_bot(token)
        if bot_username:
            await db.add_clone(message.from_user.id, token, bot_username)
            await msg.edit_text(f"✅ Your bot has been cloned successfully!\n\nBot Username: @{bot_username}\n\nYou can now add it to your groups.")
        else:
            await msg.edit_text("❌ Failed to start the clone bot. Please check if the token is valid.")

    @app.on_message(filters.private & filters.command("clones"))
    async def list_clones(client, message: Message):
        clones = await db.get_user_clones(message.from_user.id)
        if not clones:
            return await message.reply_text("🤖 You don't have any cloned bots yet.")

        text = "🤖 **Your Cloned Bots:**\n\n"
        for clone in clones:
            text += f"• @{clone['bot_username']}\n"

        await message.reply_text(text)

    @app.on_message(filters.private & filters.command("delclone"))
    async def delete_clone(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/delclone <BOT_TOKEN>`")

        token = message.text.split(None, 1)[1]
        clones = await db.get_user_clones(message.from_user.id)

        is_owner = any(c['token'] == token for c in clones)
        if not is_owner:
            return await message.reply_text("❌ You don't own this clone or it doesn't exist.")

        await db.remove_clone(token)
        if token in cloned_bots:
            await cloned_bots[token].stop()
            del cloned_bots[token]

        await message.reply_text("✅ Clone deleted and stopped successfully.")
