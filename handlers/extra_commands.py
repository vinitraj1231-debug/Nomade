# ============================================================
# Group Manager Bot - Extra Commands
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message, ChatPrivileges, ChatPermissions
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
import asyncio
import random
import aiohttp
import io
import string
from datetime import datetime

# Global session for aiohttp
session = aiohttp.ClientSession()

def register_extra_commands(app: Client):

    async def is_power(client, chat_id: int, user_id: int) -> bool:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        except:
            return False

    # ==========================================================
    # Pin / Unpin
    # ==========================================================
    @app.on_message(filters.group & filters.command("pin"))
    async def pin_message(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message to pin it.")

        try:
            await message.reply_to_message.pin()
            await message.reply_text("📌 Message pinned successfully!")
        except Exception as e:
            await message.reply_text(f"❌ Failed to pin: {e}")

    @app.on_message(filters.group & filters.command("unpin"))
    async def unpin_message(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        try:
            if message.reply_to_message:
                await message.reply_to_message.unpin()
            else:
                await client.unpin_chat_message(message.chat.id)
            await message.reply_text("📍 Message unpinned successfully!")
        except Exception as e:
            await message.reply_text(f"❌ Failed to unpin: {e}")

    @app.on_message(filters.group & filters.command("unpinall"))
    async def unpin_all_messages(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        try:
            await client.unpin_all_chat_messages(message.chat.id)
            await message.reply_text("📍 All messages unpinned successfully!")
        except Exception as e:
            await message.reply_text(f"❌ Failed to unpin all: {e}")

    # ==========================================================
    # Chat Management
    # ==========================================================
    @app.on_message(filters.group & filters.command("settitle"))
    async def set_chat_title(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/settitle <new title>`")

        new_title = message.text.split(None, 1)[1]
        try:
            await client.set_chat_title(message.chat.id, new_title)
            await message.reply_text(f"✅ Chat title changed to: **{new_title}**")
        except Exception as e:
            await message.reply_text(f"❌ Failed to change title: {e}")

    @app.on_message(filters.group & filters.command("setdesc"))
    async def set_chat_description(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/setdesc <new description>`")

        new_desc = message.text.split(None, 1)[1]
        try:
            await client.set_chat_description(message.chat.id, new_desc)
            await message.reply_text("✅ Chat description updated!")
        except Exception as e:
            await message.reply_text(f"❌ Failed to change description: {e}")

    @app.on_message(filters.group & filters.command("del"))
    async def delete_message(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message to delete it.")

        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception as e:
            await message.reply_text(f"❌ Failed to delete message: {e}")

    # ==========================================================
    # Zombies (Deleted Accounts)
    # ==========================================================
    @app.on_message(filters.group & filters.command(["zombies", "clean"]))
    async def clean_zombies(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        status_msg = await message.reply_text("🔍 Searching for deleted accounts...")
        count = 0
        try:
            async for member in client.get_chat_members(message.chat.id):
                if member.user.is_deleted:
                    try:
                        await client.ban_chat_member(message.chat.id, member.user.id)
                        await client.unban_chat_member(message.chat.id, member.user.id)
                        count += 1
                    except Exception:
                        pass

            if count == 0:
                await status_msg.edit_text("✅ No deleted accounts found.")
            else:
                await status_msg.edit_text(f"✅ Removed {count} deleted accounts (zombies).")
        except Exception as e:
            await status_msg.edit_text(f"❌ Error: {e}")

    # ==========================================================
    # Report
    # ==========================================================
    @app.on_message(filters.group & filters.command("report"))
    async def report_user(client, message: Message):
        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message to report it to admins.")

        reporter = message.from_user
        reported_user = message.reply_to_message.from_user

        admins = []
        async for admin in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            if not admin.user.is_bot:
                admins.append(admin.user.mention)

        admin_mentions = ", ".join(admins[:5]) # Mention first 5 admins

        report_text = f"🚨 **Report Received**\n\n"
        report_text += f"👤 **Reporter:** {reporter.mention} (`{reporter.id}`)\n"
        report_text += f"👤 **Reported:** {reported_user.mention} (`{reported_user.id}`)\n\n"
        report_text += f"📣 **Admins notified:** {admin_mentions}"

        await client.send_message(message.chat.id, report_text, reply_to_message_id=message.reply_to_message.id)

    # ==========================================================
    # Fun Commands
    # ==========================================================
    @app.on_message(filters.command("slap"))
    async def slap_user(client, message: Message):
        if message.reply_to_message:
            target = message.reply_to_message.from_user.mention
        else:
            target = "themselves"

        slaps = [
            "slaps {target} with a large trout!",
            "gives {target} a hard slap on the face!",
            "slaps {target} across the face with a wet noodle!",
            "delivers a powerful slap to {target}!",
        ]
        await message.reply_text(f"👤 {message.from_user.mention} {random.choice(slaps).format(target=target)}")

    @app.on_message(filters.command("hug"))
    async def hug_user(client, message: Message):
        if message.reply_to_message:
            target = message.reply_to_message.from_user.mention
        else:
            target = "themselves"
        await message.reply_text(f"💖 {message.from_user.mention} gives a warm hug to {target}! 🤗")

    @app.on_message(filters.command("kiss"))
    async def kiss_user(client, message: Message):
        if message.reply_to_message:
            target = message.reply_to_message.from_user.mention
        else:
            target = "themselves"
        await message.reply_text(f"💋 {message.from_user.mention} gives a sweet kiss to {target}! 😘")

    @app.on_message(filters.command("pat"))
    async def pat_user(client, message: Message):
        if message.reply_to_message:
            target = message.reply_to_message.from_user.mention
        else:
            target = "themselves"
        await message.reply_text(f"👋 {message.from_user.mention} gently pats {target}! 😊")

    # ==========================================================
    # Utility Commands
    # ==========================================================
    @app.on_message(filters.command("link"))
    async def get_invite_link(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        try:
            link = await client.export_chat_invite_link(message.chat.id)
            await message.reply_text(f"🔗 **Group Invite Link:**\n{link}")
        except Exception as e:
            await message.reply_text(f"❌ Failed to get link: {e}")

    @app.on_message(filters.command("members"))
    async def member_count(client, message: Message):
        count = await client.get_chat_members_count(message.chat.id)
        await message.reply_text(f"👥 **Total Members in {message.chat.title}:** `{count}`")

    @app.on_message(filters.command("admins"))
    async def admins_count(client, message: Message):
        count = 0
        async for _ in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            count += 1
        await message.reply_text(f"👮 **Total Admins in {message.chat.title}:** `{count}`")

    # ==========================================================
    # More Advanced Management
    # ==========================================================
    @app.on_message(filters.group & filters.command("setgpic"))
    async def set_group_pic(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        if not message.reply_to_message or not message.reply_to_message.photo:
            return await message.reply_text("⚠️ Reply to a photo to set it as group profile picture.")

        status = await message.reply_text("🔄 Updating group profile picture...")
        try:
            path = await message.reply_to_message.download()
            await client.set_chat_photo(message.chat.id, photo=path)
            await status.edit_text("✅ Group profile picture updated!")
        except Exception as e:
            await status.edit_text(f"❌ Failed: {e}")

    @app.on_message(filters.group & filters.command("slowmode"))
    async def set_slowmode(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/slowmode <seconds>` (0 to disable)")

        seconds = message.command[1]
        if not seconds.isdigit():
            return await message.reply_text("⚠️ Please provide a valid number of seconds.")

        try:
            await client.set_slow_mode(message.chat.id, int(seconds))
            await message.reply_text(f"✅ Slow mode set to {seconds} seconds.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    @app.on_message(filters.group & filters.command("kickme"))
    async def kick_me(client, message: Message):
        try:
            await message.reply_text("Goodbye! 👋")
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await client.unban_chat_member(message.chat.id, message.from_user.id)
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    # ==========================================================
    # Utility / Tools
    # ==========================================================
    @app.on_message(filters.command("ping"))
    async def ping_pong(client, message: Message):
        start = asyncio.get_event_loop().time()
        msg = await message.reply_text("🏓 Pong!")
        end = asyncio.get_event_loop().time()
        await msg.edit_text(f"🏓 **Pong!**\n⏱ `{round((end - start) * 1000)}ms`")

    @app.on_message(filters.command("google"))
    async def google_search(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/google <query>`")
        query = message.text.split(None, 1)[1]
        link = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        await message.reply_text(f"🔍 **Google Search:**\n[Click Here]({link})", disable_web_page_preview=True)

    @app.on_message(filters.command("wiki"))
    async def wiki_search(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/wiki <query>`")
        query = message.text.split(None, 1)[1]
        link = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
        await message.reply_text(f"📖 **Wikipedia:**\n[Click Here]({link})", disable_web_page_preview=True)

    @app.on_message(filters.command("qr"))
    async def create_qr(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/qr <text/link>`")
        text = message.text.split(None, 1)[1]
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={text}"
        await message.reply_photo(qr_url, caption=f"✅ QR Code for: `{text}`")

    @app.on_message(filters.command("shorten"))
    async def shorten_url(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/shorten <url>`")
        url = message.command[1]
        try:
            async with session.get(f"http://tinyurl.com/api-create.php?url={url}") as res:
                if res.status == 200:
                    short_url = await res.text()
                    await message.reply_text(f"🔗 **Shortened URL:** {short_url}")
                else:
                    await message.reply_text("❌ Failed to shorten URL.")
        except:
            await message.reply_text("❌ An error occurred.")

    # ==========================================================
    # Extra Fun
    # ==========================================================
    @app.on_message(filters.command("joke"))
    async def get_joke(client, message: Message):
        try:
            async with session.get("https://official-joke-api.appspot.com/random_joke") as res:
                joke = await res.json()
                await message.reply_text(f"😂 **{joke['setup']}**\n\n{joke['punchline']}")
        except:
            await message.reply_text("❌ Couldn't find a joke right now.")

    @app.on_message(filters.command("quote"))
    async def get_quote(client, message: Message):
        try:
            async with session.get("https://zenquotes.io/api/random") as res:
                quote = await res.json()
                quote = quote[0]
                await message.reply_text(f"💭 *\"{quote['q']}\"*\n\n— **{quote['a']}**")
        except:
            await message.reply_text("❌ Couldn't find a quote right now.")

    # ==========================================================
    # More Utility Commands
    # ==========================================================
    @app.on_message(filters.command("weather"))
    async def get_weather(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/weather <city>`")
        city = message.text.split(None, 1)[1]
        try:
            async with session.get(f"https://wttr.in/{city}?format=3") as res:
                text = await res.text()
                await message.reply_text(f"🌡 **Weather in {city}:**\n`{text}`")
        except:
            await message.reply_text("❌ Failed to fetch weather.")

    @app.on_message(filters.command("tr"))
    async def translate_text(client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.text:
            return await message.reply_text("⚠️ Reply to a message to translate it to English.")

        text = message.reply_to_message.text
        link = f"https://translate.google.com/?sl=auto&tl=en&text={text.replace(' ', '%20')}"
        await message.reply_text(f"🌐 **Translation:**\n[View Translation]({link})", disable_web_page_preview=True)

    @app.on_message(filters.command("dice"))
    async def throw_dice(client, message: Message):
        await client.send_dice(message.chat.id)

    @app.on_message(filters.command("dart"))
    async def throw_dart(client, message: Message):
        await client.send_dice(message.chat.id, emoji="🎯")

    @app.on_message(filters.command("basket"))
    async def throw_basket(client, message: Message):
        await client.send_dice(message.chat.id, emoji="🏀")

    @app.on_message(filters.command("football"))
    async def throw_football(client, message: Message):
        await client.send_dice(message.chat.id, emoji="⚽")

    @app.on_message(filters.command("slot"))
    async def throw_slot(client, message: Message):
        await client.send_dice(message.chat.id, emoji="🎰")

    # ==========================================================
    # Even More Admin Commands
    # ==========================================================
    @app.on_message(filters.group & filters.command("muteall"))
    async def mute_all(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        try:
            await client.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=False))
            await message.reply_text("🔇 Chat has been muted for everyone except admins.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    @app.on_message(filters.group & filters.command("unmuteall"))
    async def unmute_all(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

        try:
            await client.set_chat_permissions(message.chat.id, ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_invite_users=True,
                can_pin_messages=False,
                can_change_info=False
            ))
            await message.reply_text("🔊 Chat has been unmuted for everyone.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    @app.on_message(filters.group & filters.command("clearchat"))
    async def clear_chat(client, message: Message):
         if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Only admins can use this command.")

         msg = await message.reply_text("🧹 Clearing chat...")
         await msg.edit_text("ㅤ\n" * 100 + "✅ **Chat Cleared!**")

    # ==========================================================
    # Additional Fun Commands
    # ==========================================================
    @app.on_message(filters.command("love"))
    async def love_calculator(client, message: Message):
        if len(message.command) < 2 and not message.reply_to_message:
            return await message.reply_text("⚠️ Usage: `/love @user` or reply to a user.")

        target = await client.get_users(message.command[1]) if len(message.command) > 1 else message.reply_to_message.from_user
        percentage = random.randint(0, 100)
        await message.reply_text(f"❤️ **Love Calculator** ❤️\n\n{message.from_user.mention} + {target.mention} = **{percentage}%**")

    @app.on_message(filters.command("ship"))
    async def ship_users(client, message: Message):
        members = []
        async for member in client.get_chat_members(message.chat.id, limit=50):
            if not member.user.is_bot:
                members.append(member.user)

        if len(members) < 2:
            return await message.reply_text("❌ Not enough members to ship!")

        user1, user2 = random.sample(members, 2)
        await message.reply_text(f"💞 **New Couple Shipped!** 💞\n\n{user1.mention} + {user2.mention} = 💖")

    @app.on_message(filters.command("toss"))
    async def toss_coin(client, message: Message):
        result = random.choice(["Heads", "Tails"])
        await message.reply_text(f"🪙 **Tossing a coin...**\n\nResult: **{result}**")

    @app.on_message(filters.command("roll"))
    async def roll_dice_fun(client, message: Message):
        result = random.randint(1, 6)
        await message.reply_text(f"🎲 **Rolling a dice...**\n\nResult: **{result}**")

    # ==========================================================
    # More Advanced Tools
    # ==========================================================
    @app.on_message(filters.command("github"))
    async def github_user(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/github <username>`")
        username = message.command[1]
        try:
            async with session.get(f"https://api.github.com/users/{username}") as res:
                if res.status == 200:
                    data = await res.json()
                    text = f"🐙 **GitHub User: {data['name'] or username}**\n\n"
                    text += f"• **Bio:** {data['bio'] or 'N/A'}\n"
                    text += f"• **Public Repos:** {data['public_repos']}\n"
                    text += f"• **Followers:** {data['followers']}\n"
                    text += f"• **Following:** {data['following']}\n"
                    text += f"• **Location:** {data['location'] or 'N/A'}\n"
                    await message.reply_photo(data['avatar_url'], caption=text)
                else:
                    await message.reply_text("❌ User not found.")
        except:
            await message.reply_text("❌ Error fetching data.")

    @app.on_message(filters.command("ip"))
    async def ip_info(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/ip <address>`")
        ip = message.command[1]
        try:
            async with session.get(f"http://ip-api.com/json/{ip}") as res:
                data = await res.json()
                if data['status'] == 'success':
                    text = f"🌐 **IP Info: {ip}**\n\n"
                    text += f"• **Country:** {data['country']}\n"
                    text += f"• **Region:** {data['regionName']}\n"
                    text += f"• **City:** {data['city']}\n"
                    text += f"• **ISP:** {data['isp']}\n"
                    text += f"• **Org:** {data['org']}\n"
                    await message.reply_text(text)
                else:
                    await message.reply_text("❌ Invalid IP address.")
        except:
            await message.reply_text("❌ Error fetching data.")

    @app.on_message(filters.command("advice"))
    async def get_advice(client, message: Message):
        try:
            async with session.get("https://api.adviceslip.com/advice") as res:
                data = await res.json()
                advice = data['slip']['advice']
                await message.reply_text(f"💡 **Advice:**\n\n`{advice}`")
        except:
            await message.reply_text("❌ No advice right now.")

    @app.on_message(filters.command("fact"))
    async def get_fact(client, message: Message):
        try:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as res:
                data = await res.json()
                fact = data['text']
                await message.reply_text(f"📚 **Random Fact:**\n\n`{fact}`")
        except:
            await message.reply_text("❌ No facts right now.")

    @app.on_message(filters.command("carbon"))
    async def code_to_image(client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.text:
            return await message.reply_text("⚠️ Reply to some code to generate a carbon image.")

        code = message.reply_to_message.text
        carbon_url = f"https://carbonara.vercel.app/api/cook"
        try:
            status = await message.reply_text("🎨 Generating image...")
            async with session.post(carbon_url, json={"code": code}) as res:
                if res.status == 200:
                    image_data = await res.read()
                    image_io = io.BytesIO(image_data)
                    image_io.name = "carbon.png"
                    await message.reply_photo(image_io, caption="✅ Generated by Carbonara")
                    await status.delete()
                else:
                    await status.edit_text("❌ Failed to generate image.")
        except:
            await status.edit_text("❌ An error occurred.")

    @app.on_message(filters.command("write"))
    async def text_to_handwriting(client, message: Message):
        if len(message.command) < 2 and not message.reply_to_message:
            return await message.reply_text("⚠️ Usage: `/write <text>` or reply to text.")

        text = message.text.split(None, 1)[1] if len(message.command) > 1 else message.reply_to_message.text
        await message.reply_photo(f"https://pyro-api.vercel.app/handwrite?text={text.replace(' ', '%20')}", caption="✍️ Handwritten text")

    @app.on_message(filters.command("urban"))
    async def urban_dictionary(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/urban <word>`")
        word = message.text.split(None, 1)[1]
        try:
            async with session.get(f"https://api.urbandictionary.com/v0/define?term={word}") as res:
                data = await res.json()
                if data['list']:
                    def_ = data['list'][0]
                    text = f"📖 **Urban Dictionary: {word}**\n\n"
                    text += f"**Definition:**\n{def_['definition'][:500]}\n\n"
                    text += f"**Example:**\n{def_['example'][:500]}"
                    await message.reply_text(text)
                else:
                    await message.reply_text("❌ No definition found.")
        except:
            await message.reply_text("❌ Error fetching data.")

    @app.on_message(filters.command("crypto"))
    async def crypto_price(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/crypto <symbol>` (e.g. BTC)")
        symbol = message.command[1].upper()
        try:
            mapping = {"BTC": "bitcoin", "ETH": "ethereum", "DOGE": "dogecoin", "SOL": "solana", "BNB": "binancecoin"}
            coin_id = mapping.get(symbol, symbol.lower())
            async with session.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd") as res:
                data = await res.json()
                if coin_id in data:
                    price = data[coin_id]['usd']
                    await message.reply_text(f"💰 **{symbol} Price:** `${price}`")
                else:
                    await message.reply_text("❌ Coin not found or not supported.")
        except:
            await message.reply_text("❌ Error fetching data.")

    @app.on_message(filters.command("calc"))
    async def calculator(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/calc <expression>` (e.g. 2+2)")
        expr = message.text.split(None, 1)[1]
        try:
            allowed = "0123456789+-*/(). "
            if all(c in allowed for c in expr):
                result = eval(expr)
                await message.reply_text(f"🔢 **Result:** `{result}`")
            else:
                await message.reply_text("❌ Invalid characters in expression.")
        except:
            await message.reply_text("❌ Invalid expression.")

    # ==========================================================
    # Even More Commands to reach 100+
    # ==========================================================
    @app.on_message(filters.command("echo"))
    async def echo_text(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/echo <text>`")
        await message.reply_text(message.text.split(None, 1)[1])

    @app.on_message(filters.command("dog"))
    async def random_dog(client, message: Message):
        try:
            async with session.get("https://dog.ceo/api/breeds/image/random") as res:
                data = await res.json()
                await message.reply_photo(data['message'], caption="🐶 Woof!")
        except:
            await message.reply_text("❌ Error.")

    @app.on_message(filters.command("cat"))
    async def random_cat(client, message: Message):
        try:
            async with session.get("https://api.thecatapi.com/v1/images/search") as res:
                data = await res.json()
                await message.reply_photo(data[0]['url'], caption="🐱 Meow!")
        except:
            await message.reply_text("❌ Error.")

    @app.on_message(filters.command("panda"))
    async def random_panda(client, message: Message):
        try:
            async with session.get("https://some-random-api.com/img/panda") as res:
                data = await res.json()
                await message.reply_photo(data['link'], caption="🐼 Panda!")
        except:
            await message.reply_text("❌ Error.")

    @app.on_message(filters.command("fox"))
    async def random_fox(client, message: Message):
        try:
            async with session.get("https://some-random-api.com/img/fox") as res:
                data = await res.json()
                await message.reply_photo(data['link'], caption="🦊 Fox!")
        except:
            await message.reply_text("❌ Error.")

    @app.on_message(filters.command("lyrics"))
    async def song_lyrics(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/lyrics <song name>`")
        song = message.text.split(None, 1)[1]
        try:
            async with session.get(f"https://some-random-api.com/lyrics?title={song}") as res:
                data = await res.json()
                if 'lyrics' in data:
                    text = f"🎵 **Lyrics: {data['title']}**\n👤 **Artist:** {data['author']}\n\n{data['lyrics'][:4000]}"
                    await message.reply_text(text)
                else:
                    await message.reply_text("❌ Lyrics not found.")
        except:
            await message.reply_text("❌ Error.")

    @app.on_message(filters.command("imdb"))
    async def imdb_search(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/imdb <movie name>`")
        movie = message.text.split(None, 1)[1]
        try:
            async with session.get(f"https://www.omdbapi.com/?t={movie}&apikey=6a03197") as res:
                data = await res.json()
                if data['Response'] == 'True':
                    text = f"🎬 **{data['Title']} ({data['Year']})**\n\n"
                    text += f"⭐ **Rating:** {data['imdbRating']}\n"
                    text += f"🎭 **Genre:** {data['Genre']}\n"
                    text += f"👥 **Actors:** {data['Actors']}\n"
                    text += f"📝 **Plot:** {data['Plot']}"
                    await message.reply_photo(data['Poster'], caption=text)
                else:
                    await message.reply_text("❌ Movie not found.")
        except:
            await message.reply_text("❌ Error.")

    @app.on_message(filters.command("wall"))
    async def wallpaper(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/wall <query>`")
        query = message.text.split(None, 1)[1]
        await message.reply_photo(f"https://source.unsplash.com/1600x900/?{query.replace(' ', ',')}", caption=f"🖼 Wallpaper: {query}")

    @app.on_message(filters.command("alive"))
    async def bot_alive(client, message: Message):
        await message.reply_photo(
            "https://graph.org/file/b39584488b77377261d5d-7af6b93551275c06bb.jpg",
            caption="✅ **I am alive and running!**\n\n💪 Powered by Python & Pyrogram"
        )

    @app.on_message(filters.command("repo"))
    async def bot_repo(client, message: Message):
        await message.reply_text("📦 **Bot Repository:**\n\n[GitHub](https://github.com/LearningBotsOfficial/Group-Manager-Bot)", disable_web_page_preview=True)

    @app.on_message(filters.command("rules"))
    async def chat_rules(client, message: Message):
        await message.reply_text("📜 **Group Rules:**\n\n1. Be respectful.\n2. No spam.\n3. No NSFW.\n4. Follow admin instructions.")

    @app.on_message(filters.command("staff"))
    async def chat_staff(client, message: Message):
        admins = []
        async for m in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            admins.append(m.user.mention)
        await message.reply_text(f"👮 **Chat Staff:**\n\n" + "\n".join(admins))

    @app.on_message(filters.group & filters.command("banme"))
    async def ban_me(client, message: Message):
        await message.reply_text("As you wish! 💨")
        await client.ban_chat_member(message.chat.id, message.from_user.id)

    @app.on_message(filters.command("time"))
    async def get_time(client, message: Message):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await message.reply_text(f"🕒 **Current Time:** `{now}`")

    @app.on_message(filters.command("date"))
    async def get_date(client, message: Message):
        now = datetime.now().strftime("%A, %d %B %Y")
        await message.reply_text(f"📅 **Today's Date:** `{now}`")

    @app.on_message(filters.command("shout"))
    async def shout_text(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/shout <text>`")
        text = message.text.split(None, 1)[1]
        await message.reply_text(f"📣 **{text.upper()}**")

    @app.on_message(filters.command("reverse"))
    async def reverse_text(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/reverse <text>`")
        text = message.text.split(None, 1)[1]
        await message.reply_text(text[::-1])

    @app.on_message(filters.command("caps"))
    async def caps_text(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/caps <text>`")
        text = message.text.split(None, 1)[1]
        await message.reply_text(text.upper())

    @app.on_message(filters.command("small"))
    async def small_text(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("⚠️ Usage: `/small <text>`")
        text = message.text.split(None, 1)[1]
        await message.reply_text(text.lower())

    @app.on_message(filters.command("password"))
    async def gen_password(client, message: Message):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = "".join(random.choice(chars) for _ in range(12))
        await message.reply_text(f"🔐 **Generated Password:** `{pwd}`")

    @app.on_message(filters.command("dice2"))
    async def roll_2_dice(client, message: Message):
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        await message.reply_text(f"🎲 **Rolling two dice...**\n\nResult: `{d1}` and `{d2}` (Total: `{d1+d2}`)")

    @app.on_message(filters.command("head"))
    async def head_info(client, message: Message):
        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message.")
        await message.reply_text(f"📝 **Message Header Info:**\n\n`{message.reply_to_message.id}`")

    @app.on_message(filters.command("json"))
    async def json_info(client, message: Message):
        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message.")
        await message.reply_text(f"📄 **Message JSON:**\n\n`{message.reply_to_message}`")

    @app.on_message(filters.command("id2"))
    async def id_info_extended(client, message: Message):
        text = f"**Chat ID:** `{message.chat.id}`\n"
        text += f"**User ID:** `{message.from_user.id}`\n"
        if message.chat.type:
            text += f"**Chat Type:** `{message.chat.type}`\n"
        await message.reply_text(text)

    @app.on_message(filters.command("avatar"))
    async def get_avatar(client, message: Message):
        user = await client.get_users(message.command[1]) if len(message.command) > 1 else (message.reply_to_message.from_user if message.reply_to_message else message.from_user)
        if user.photo:
            await message.reply_photo(user.photo.big_file_id, caption=f"📸 Avatar of {user.mention}")
        else:
            await message.reply_text("❌ User has no profile photo.")

    @app.on_message(filters.command("bio"))
    async def get_user_bio(client, message: Message):
        user = await client.get_users(message.command[1]) if len(message.command) > 1 else (message.reply_to_message.from_user if message.reply_to_message else message.from_user)
        full_user = await client.get_chat(user.id)
        await message.reply_text(f"📝 **Bio of {user.mention}:**\n\n{full_user.bio or 'N/A'}")

    @app.on_message(filters.command("dc"))
    async def get_user_dc(client, message: Message):
        user = await client.get_users(message.command[1]) if len(message.command) > 1 else (message.reply_to_message.from_user if message.reply_to_message else message.from_user)
        await message.reply_text(f"🏢 **DC of {user.mention}:** `{user.dc_id or 'N/A'}`")

    @app.on_message(filters.command("is_bot"))
    async def check_bot(client, message: Message):
        user = await client.get_users(message.command[1]) if len(message.command) > 1 else (message.reply_to_message.from_user if message.reply_to_message else message.from_user)
        await message.reply_text(f"🤖 **Is {user.mention} a bot?** `{'Yes' if user.is_bot else 'No'}`")

    @app.on_message(filters.command("mention"))
    async def mention_user(client, message: Message):
        user = await client.get_users(message.command[1]) if len(message.command) > 1 else (message.reply_to_message.from_user if message.reply_to_message else message.from_user)
        await message.reply_text(f"🔗 {user.mention}")

    @app.on_message(filters.command("tag"))
    async def tag_user_hidden(client, message: Message):
        user = await client.get_users(message.command[1]) if len(message.command) > 1 else (message.reply_to_message.from_user if message.reply_to_message else message.from_user)
        await message.reply_text(f"[\u200b](tg://user?id={user.id})Tagged!", parse_mode=enums.ParseMode.MARKDOWN)

    @app.on_message(filters.command("unbanall_confirm"))
    async def unban_all_confirm(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
             return await message.reply_text("❌ Only admins.")
        await message.reply_text("⚠️ Use `/unbanall` to unban everyone in this chat.")

    @app.on_message(filters.command("unbanall"))
    async def unban_all_users(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
             return await message.reply_text("❌ Only admins.")

        status = await message.reply_text("🔓 Unbanning everyone...")
        count = 0
        async for member in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.BANNED):
            await client.unban_chat_member(message.chat.id, member.user.id)
            count += 1
        await status.edit_text(f"✅ Unbanned {count} users.")

    @app.on_message(filters.command("unmuteall_confirm"))
    async def unmute_all_confirm(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
             return await message.reply_text("❌ Only admins.")
        await message.reply_text("⚠️ Use `/unmuteall` to unmute everyone.")

    @app.on_message(filters.command("kickall"))
    async def kick_all_confirm(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
             return await message.reply_text("❌ Only admins.")
        await message.reply_text("❌ This command is disabled for safety.")

    @app.on_message(filters.command("promoteall"))
    async def promote_all_confirm(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
             return await message.reply_text("❌ Only admins.")
        await message.reply_text("❌ This command is disabled for safety.")

    @app.on_message(filters.command("msg_id"))
    async def msg_id_info(client, message: Message):
        if message.reply_to_message:
            await message.reply_text(f"🆔 **Message ID:** `{message.reply_to_message.id}`")
        else:
            await message.reply_text(f"🆔 **Message ID:** `{message.id}`")

    @app.on_message(filters.command("chat_id"))
    async def chat_id_info(client, message: Message):
        await message.reply_text(f"🆔 **Chat ID:** `{message.chat.id}`")

    @app.on_message(filters.command("my_id"))
    async def my_id_info(client, message: Message):
        await message.reply_text(f"🆔 **Your ID:** `{message.from_user.id}`")

    @app.on_message(filters.command("is_admin"))
    async def check_admin(client, message: Message):
        user = await client.get_users(message.command[1]) if len(message.command) > 1 else (message.reply_to_message.from_user if message.reply_to_message else message.from_user)
        is_adm = await is_power(client, message.chat.id, user.id)
        await message.reply_text(f"👮 **Is {user.mention} admin?** `{'Yes' if is_adm else 'No'}`")

    @app.on_message(filters.command("is_owner"))
    async def check_owner(client, message: Message):
        user = await client.get_users(message.command[1]) if len(message.command) > 1 else (message.reply_to_message.from_user if message.reply_to_message else message.from_user)
        member = await client.get_chat_member(message.chat.id, user.id)
        is_own = member.status == ChatMemberStatus.OWNER
        await message.reply_text(f"👑 **Is {user.mention} owner?** `{'Yes' if is_own else 'No'}`")
