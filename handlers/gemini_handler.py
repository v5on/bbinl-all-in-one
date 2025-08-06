import os
import json
import asyncio
from pathlib import Path
import telebot
import google.generativeai as genai

# 🔐 Gemini API Key
GEMINI_API_KEY = "AIzaSyC6gWj3u28Rx5bOS82VkhWslQKC4v3O7cQ"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# 📁 Chat histories stored here
HISTORY_DIR = Path("gemini_histories")
HISTORY_DIR.mkdir(exist_ok=True)

# 🧠 In-memory state
loaded_histories = {}
auto_reply_status = {}

MAX_TURNS = 50

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

        # প্রথমে একটি প্লেসহোল্ডার মেসেজ পাঠাও
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

    # ✅ Turn auto-reply ON
    @custom_command_handler("gemini_on")
    def enable_autoreply(message):
        auto_reply_status[message.chat.id] = True
        bot.reply_to(message, "✅ জেমিনির অটো-রিপ্লাই চালু হয়েছে।")

    # ✅ Turn auto-reply OFF
    @custom_command_handler("gemini_off")
    def disable_autoreply(message):
        auto_reply_status[message.chat.id] = False
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
