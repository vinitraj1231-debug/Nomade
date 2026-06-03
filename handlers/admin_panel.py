# ============================================================
# Group Manager Bot - Admin Panel
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery
)
from config import OWNER_ID
import db
import asyncio

async def is_admin(user_id):
    return user_id == OWNER_ID

def register_admin_handlers(app: Client):
    @app.on_message(filters.private & filters.command("admin"))
    async def admin_panel(client, message: Message):
        if not await is_admin(message.from_user.id):
            return

        text = "⚙️ **Advanced Admin Panel**\n\nManage your bot and clones from here."
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            ],
            [
                InlineKeyboardButton("🤖 Manage Clones", callback_data="admin_clones"),
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="admin_close")
            ]
        ])
        await message.reply_text(text, reply_markup=buttons)

    @app.on_callback_query(filters.regex("^admin_"))
    async def admin_callback(client: Client, callback_query: CallbackQuery):
        if not await is_admin(callback_query.from_user.id):
            return await callback_query.answer("❌ Not authorized.", show_alert=True)

        data = callback_query.data.split("_")[1]

        if data == "stats":
            total_users = await db.total_users_count()
            total_clones = await db.total_clones_count()
            text = f"📊 **Bot Statistics**\n\n👤 Total Users: {total_users}\n🤖 Total Clones: {total_clones}"
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]])
            await callback_query.message.edit_text(text, reply_markup=buttons)

        elif data == "broadcast":
            text = "📢 **Advanced Broadcast**\n\nTo broadcast a message to all users:\n1. Reply to the message you want to broadcast.\n2. Use the command `/advbroadcast`.\n\nThis will send the message to every user in the database with progress updates."
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]])
            await callback_query.message.edit_text(text, reply_markup=buttons)

        elif data == "clones":
            clones = await db.get_clones()
            text = f"🤖 **Total Clones: {len(clones)}**\n\n"
            for clone in clones[:20]: # Limit to 20 for display
                text += f"• @{clone['bot_username']} (Owner: {clone['user_id']})\n"

            buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]])
            await callback_query.message.edit_text(text, reply_markup=buttons)

        elif data == "back":
            text = "⚙️ **Advanced Admin Panel**\n\nManage your bot and clones from here."
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
                    InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                ],
                [
                    InlineKeyboardButton("🤖 Manage Clones", callback_data="admin_clones"),
                ],
                [
                    InlineKeyboardButton("❌ Close", callback_data="admin_close")
                ]
            ])
            await callback_query.message.edit_text(text, reply_markup=buttons)

        elif data == "close":
            await callback_query.message.delete()

        await callback_query.answer()

    # Enhanced Broadcast
    @app.on_message(filters.private & filters.command("advbroadcast"))
    async def advanced_broadcast(client: Client, message: Message):
        if not await is_admin(message.from_user.id):
            return

        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message to broadcast.")

        users = await db.get_all_users()
        msg = await message.reply_text(f"🚀 Starting broadcast to {len(users)} users...")

        count = 0
        for user_id in users:
            try:
                await message.reply_to_message.copy(user_id)
                count += 1
                if count % 20 == 0:
                    await msg.edit_text(f"🚀 Broadcasting... {count}/{len(users)}")
                await asyncio.sleep(0.05) # Rate limit
            except Exception:
                pass

        await msg.edit_text(f"✅ Broadcast complete!\n\nSent to {count} users.")
