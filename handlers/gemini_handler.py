import os
import json
import asyncio
import time
from pathlib import Path
import telebot
import google.generativeai as genai

# 🔐 Gemini API Key
GEMINI_API_KEY = "AIzaSyA-bnKONL8fj-Dwsw8UEec3Ci-UHEHVw4w"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# 📁 Chat histories stored here
HISTORY_DIR = Path("gemini_histories")
HISTORY_DIR.mkdir(exist_ok=True)

# 📁 Auto-reply status stored here
STATUS_FILE = Path("auto_reply_status.json")

# 🧠 In-memory state
auto_reply_status = {}
loaded_histories = {}

MAX_TURNS = 500
HISTORY_RETENTION_TIME = 20 * 60 # 20 minutes in seconds

def load_status():
    """Load auto-reply status from file on bot startup."""
    global auto_reply_status
    if STATUS_FILE.exists():
        with STATUS_FILE.open("r") as f:
            try:
                data = json.load(f)
                auto_reply_status = {int(k): v for k, v in data.items()}
            except (json.JSONDecodeError, ValueError):
                auto_reply_status = {}
                print("Error loading status file, starting fresh.")

def save_status():
    """Save auto-reply status to file."""
    with STATUS_FILE.open("w") as f:
        json.dump(auto_reply_status, f, indent=2)

async def delete_old_histories():
    now = time.time()
    for file_path in HISTORY_DIR.iterdir():
        if file_path.is_file() and file_path.suffix == ".json":
            last_modified_time = file_path.stat().st_mtime
            if (now - last_modified_time) > HISTORY_RETENTION_TIME:
                try:
                    os.remove(file_path)
                    print(f"Deleted old history file: {file_path.name}")
                    chat_id = int(file_path.stem)
                    if chat_id in loaded_histories:
                        del loaded_histories[chat_id]
                except Exception as e:
                    print(f"Error deleting file {file_path.name}: {e}")

async def load_history(chat_id):
    path = HISTORY_DIR / f"{chat_id}.json"
    if path.exists():
        with path.open() as f:
            loaded_histories[chat_id] = json.load(f)
    else:
        loaded_histories[chat_id] = []

async def save_history(chat_id):
    path = HISTORY_DIR / f"{chat_id}.json"
    with path.open("w") as f:
        json.dump(loaded_histories[chat_id], f, indent=2)

async def ask_gemini(prompt, chat_id):
    await delete_old_histories()

    if chat_id not in loaded_histories:
        await load_history(chat_id)

    history = loaded_histories[chat_id]

    if not history:
        persona = "তুমি একজন হট এন্ড সেক্সি মেয়ে, বুদ্ধিমতী, তবে মাঝে মাঝে একটু বোকা। সবসময় বাংলাতে কথা বলে।"
        history.append({"role": "user", "parts": [persona]})
        history.append({"role": "model", "parts": ["হাই! আমি তোমার সেক্সি জেমিনি। কেমন আছো?"]})

    chat_history = [{"role": h["role"], "parts": h["parts"]} for h in history]

    try:
        chat = model.start_chat(history=chat_history)
        response = await asyncio.to_thread(lambda: chat.send_message(prompt).text)
    except Exception as e:
        return f"❌ Gemini error: {e}"

    history.append({"role": "user", "parts": [prompt]})
    history.append({"role": "model", "parts": [response]})

    if len(history) > MAX_TURNS * 2:
        loaded_histories[chat_id] = history[-MAX_TURNS * 2:]

    await save_history(chat_id)
    return response

def register(bot, custom_command_handler, command_prefixes_list):
    load_status() # Load status on startup

    @custom_command_handler("gemini")
    def handle_gemini(message):
        command_text = message.text.split(" ", 1)[0].lower()
        actual_command_len = 0
        for prefix in command_prefixes_list: 
            if command_text.startswith(f"{prefix}gemini"):
                actual_command_len = len(f"{prefix}gemini")
                break

        prompt_raw = message.text[actual_command_len:].strip()

        if not prompt_raw:
            bot.reply_to(message, f"❓ `{command_prefixes_list[0]}gemini [প্রশ্ন]` লিখুন। উদাহরণ: `{command_prefixes_list[0]}gemini তুমি কেমন আছো?`", parse_mode="Markdown")
            return

        prompt = prompt_raw

        thinking_message = bot.reply_to(message, "🤖 জেমিনি ভাবছে...")

        try:
            reply = asyncio.run(ask_gemini(prompt, message.chat.id))
            bot.edit_message_text(
                chat_id=thinking_message.chat.id,
                message_id=thinking_message.message_id,
                text=f"🤖 {reply}"
            )
        except Exception as e:
            bot.edit_message_text(
                chat_id=thinking_message.chat.id,
                message_id=thinking_message.message_id,
                text=f"❌ Error: {e}"
            )

    @custom_command_handler("gmni_on")
    def enable_autoreply(message):
        auto_reply_status[message.chat.id] = True
        save_status() # Save status after change
        bot.reply_to(message, "✅ জেমিনির অটো-রিপ্লাই চালু হয়েছে।")

    @custom_command_handler("gmni_off")
    def disable_autoreply(message):
        auto_reply_status[message.chat.id] = False
        save_status() # Save status after change
        bot.reply_to(message, "❌ জেমিনির অটো-রিপ্লাই বন্ধ করা হয়েছে।")

    @bot.message_handler(func=lambda msg: msg.content_type == 'text' and not any(msg.text.lower().startswith(p) for p in command_prefixes_list)) 
    def auto_reply(message):
        chat_id = message.chat.id
        if not auto_reply_status.get(chat_id, False):
            return

        thinking_message = bot.reply_to(message, "🤖 জেমিনি ভাবছে...")

        try:
            reply = asyncio.run(ask_gemini(message.text, chat_id))
            bot.edit_message_text(
                chat_id=thinking_message.chat.id,
                message_id=thinking_message.message_id,
                text=f"🤖 {reply}"
            )
        except Exception as e:
            bot.edit_message_text(
                chat_id=thinking_message.chat.id,
                message_id=thinking_message.message_id,
                text=f"❌ Error: {e}"
            )
