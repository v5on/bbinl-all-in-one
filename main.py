import telebot
import os
from flask import Flask
from threading import Thread
import cleanup
import string
import time
import json

# Handlers import
from handlers import (
    start_handler,
    bgremove_handler,
    gen_handler,
    chk_handler,
    bin_handler,
    reveal_handler,
    gemini_handler,
    gart_handler,
    imagine_handler,
    say_handler,
    translate_handler,
    download_handler,
    gpt_handler,
    fakeAddress_handler,
    fakeAddress2_handler,
    fakeAddress3_handler,
    userinfo_handler,
    yt_handler,
    spam_handler,
    iban_handler,
    b3_handler as b3_register
)

BOT_TOKEN = "8288718215:AAF1h-5sSQKpQpHwsWJbLPuLeq2lc4XaEtQ"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

def get_admin_ids():
    # Assuming users.txt is in the checker directory
    with open('checker/users.txt', 'r') as f:
        return [int(line.strip()) for line in f if line.strip()]

ADMIN_IDS = get_admin_ids()

def get_authorized_group_ids():
    try:
        with open('checker/groups.txt', 'r') as f:
            return [int(line.strip()) for line in f if line.strip() and not line.strip().startswith('#')]
    except FileNotFoundError:
        return []

AUTHORIZED_GROUP_IDS = get_authorized_group_ids()

AUTHORIZED_USERS = {}

def load_auth():
    try:
        # Assuming authorized.json is in the checker directory
        with open("checker/authorized.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_auth(data):
    # Assuming authorized.json is in the checker directory
    with open("checker/authorized.json", "w") as f:
        json.dump(data, f)

def is_authorized(chat_id):
    if chat_id in ADMIN_IDS:
        return True
    if chat_id in AUTHORIZED_GROUP_IDS:
        return True
    if str(chat_id) in AUTHORIZED_USERS:
        expiry = AUTHORIZED_USERS[str(chat_id)]
        if expiry == "forever":
            return True
        if time.time() < expiry:
            return True
        else:
            del AUTHORIZED_USERS[str(chat_id)]
            save_auth(AUTHORIZED_USERS)
    return False

AUTHORIZED_USERS = load_auth()

COMMAND_PREFIXES = list(string.punctuation)

def custom_command_handler(command_name):
    def decorator(handler_func):
        @bot.message_handler(func=lambda message: message.text and any(
            message.text.lower().startswith(f"{prefix}{command_name}") for prefix in COMMAND_PREFIXES
        ))
        def wrapper(message):
            return handler_func(message)
        return wrapper
    return decorator

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# ---------------- Bot Commands ---------------- #

@bot.message_handler(commands=['auth'])
def authorize_user(msg):
    if msg.from_user.id not in ADMIN_IDS:
        return
    try:
        parts = msg.text.split()
        if len(parts) < 2:
            return bot.reply_to(msg, "❌ Usage: /auth <user_id> [days]")
        user = parts[1]
        days = int(parts[2]) if len(parts) > 2 else None

        if user.startswith('@'):
            return bot.reply_to(msg, "❌ Use numeric Telegram ID, not @username.")

        uid = int(user)
        expiry = "forever" if not days else time.time() + (days * 86400)
        AUTHORIZED_USERS[str(uid)] = expiry
        save_auth(AUTHORIZED_USERS)

        msg_text = f"✅ Authorized {uid} for {days} days." if days else f"✅ Authorized {uid} forever."
        bot.reply_to(msg, msg_text)
    except Exception as e:
        bot.reply_to(msg, f"❌ Error: {e}")

@bot.message_handler(commands=['rm'])
def remove_auth(msg):
    if msg.from_user.id not in ADMIN_IDS:
        return
    try:
        parts = msg.text.split()
        if len(parts) < 2:
            return bot.reply_to(msg, "❌ Usage: /rm <user_id>")
        uid = int(parts[1])
        if str(uid) in AUTHORIZED_USERS:
            del AUTHORIZED_USERS[str(uid)]
            save_auth(AUTHORIZED_USERS)
            bot.reply_to(msg, f"✅ Removed {uid} from authorized users.")
        else:
            bot.reply_to(msg, "❌ User is not authorized.")
    except Exception as e:
        bot.reply_to(msg, f"❌ Error: {e}")

@bot.message_handler(commands=['authgroup'])
def authorize_group(msg):
    if msg.from_user.id not in ADMIN_IDS:
        return
    try:
        parts = msg.text.split()
        if len(parts) < 2:
            return bot.reply_to(msg, "❌ Usage: /authgroup <group_id>")
        group_id = int(parts[1])

        global AUTHORIZED_GROUP_IDS
        if group_id not in AUTHORIZED_GROUP_IDS:
            AUTHORIZED_GROUP_IDS.append(group_id)
            with open('checker/groups.txt', 'a') as f:
                f.write(f"\n{group_id}")
            bot.reply_to(msg, f"✅ Authorized group {group_id}.")
        else:
            bot.reply_to(msg, f"❌ Group {group_id} is already authorized.")
    except Exception as e:
        bot.reply_to(msg, f"❌ Error: {e}")

@bot.message_handler(commands=['rmgroup'])
def remove_group_auth(msg):
    if msg.from_user.id not in ADMIN_IDS:
        return
    try:
        parts = msg.text.split()
        if len(parts) < 2:
            return bot.reply_to(msg, "❌ Usage: /rmgroup <group_id>")
        group_id = int(parts[1])

        global AUTHORIZED_GROUP_IDS
        if group_id in AUTHORIZED_GROUP_IDS:
            AUTHORIZED_GROUP_IDS.remove(group_id)
            # Rewrite the groups.txt file to reflect the removal
            with open('checker/groups.txt', 'w') as f:
                for gid in AUTHORIZED_GROUP_IDS:
                    f.write(f"{gid}\n")
            bot.reply_to(msg, f"✅ Removed group {group_id} from authorized groups.")
        else:
            bot.reply_to(msg, "❌ Group is not authorized.")
    except Exception as e:
        bot.reply_to(msg, f"❌ Error: {e}")

def register_handler(handler_module, handler_name, is_authorized_func=None, admin_ids_list=None):
    try:
        if handler_name == "B3": # Special case for b3_handler
            handler_module.register(bot, custom_command_handler, COMMAND_PREFIXES, is_authorized_func, admin_ids_list)
        else:
            handler_module.register(bot, custom_command_handler, COMMAND_PREFIXES)
        print(f"✅ {handler_name} handler loaded successfully")
    except Exception as e:
        print(f"❌ {handler_name} handler failed to load: {str(e)}")

print("\n🔄 Loading command handlers...")
print("-" * 40)

# Register all handlers
register_handler(start_handler, "Start") # Register the start_handler module
register_handler(gen_handler, "Gen")
register_handler(chk_handler, "Check")
register_handler(bin_handler, "BIN")
register_handler(reveal_handler, "Reveal")
register_handler(gemini_handler, "Gemini")
register_handler(gart_handler, "Gart")
register_handler(imagine_handler, "Imagine")
register_handler(say_handler, "Say")
register_handler(translate_handler, "Translate")
register_handler(download_handler, "Download")
register_handler(bgremove_handler, "BG Remove")
register_handler(gpt_handler, "GPT")
register_handler(fakeAddress_handler, "Fake Address")
register_handler(fakeAddress2_handler, "Fake Address2")
register_handler(fakeAddress3_handler, "Fake Address3")
register_handler(userinfo_handler, "User Info")
register_handler(yt_handler, "yt")
register_handler(spam_handler, "spam")
register_handler(iban_handler, "iban")
register_handler(b3_register, "B3", is_authorized, ADMIN_IDS)


print("-" * 40)
print("✨ Handler registration completed!\n")

cleanup.cleanup_project()

if __name__ == '__main__':
    print("🤖 Bot is running...")
    bot.infinity_polling()
