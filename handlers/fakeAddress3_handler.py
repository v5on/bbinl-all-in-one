import requests
import random
from telebot.types import Message

API_URL = "https://api.npoint.io/ad402f70ec811202c7b7"

# register function now accepts command_prefixes_list
def register(bot, custom_command_handler, command_prefixes_list): # <-- MODIFIED LINE (added command_prefixes_list)
    @custom_command_handler("fake3")
    def handle_fake(message: Message):
        # Get the full command text and calculate actual command length
        command_text = message.text.split(" ", 1)[0].lower()
        actual_command_len = 0
        # Use command_prefixes_list here
        for prefix in command_prefixes_list: # <-- MODIFIED LINE (using command_prefixes_list)
            if command_text.startswith(f"{prefix}fake3"):
                actual_command_len = len(f"{prefix}fake3")
                break

        user_input_raw = message.text[actual_command_len:].strip()
        args = user_input_raw.split(" ", 1) # এবার সঠিক আর্গুমেন্ট পার্সিং

        if not user_input_raw: # যদি শুধু কমান্ড থাকে, কোনো আর্গুমেন্ট না থাকে
            # Update example message with dynamic prefixes
            bot.reply_to(message, f"❌ Country name missing. উদাহরণ: <code>{command_prefixes_list[0]}fake3 US</code>, <code>{command_prefixes_list[1]}fake3 algeria</code>, <code>{command_prefixes_list[2]}fake3 kzt</code>", parse_mode="HTML") # <-- MODIFIED LINE (updated example)
            return

        country_input = args[0].strip().lower() # প্রথম আর্গুমেন্ট, যা কান্ট্রি নাম

        try:
            response = requests.get(API_URL)
            if response.status_code != 200:
                bot.send_message(message.chat.id, "❌ Failed to fetch address database.")
                return

            address_data = response.json()

            matched_country = next((c for c in address_data if c.lower() == country_input), None)

            if not matched_country:
                bot.reply_to(message, "❌ Country not found in database.", parse_mode="HTML")
                return

            address = random.choice(address_data[matched_country])

            username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

            msg = (
                f"<b>Address for {matched_country}</b>\n"
                f"•{'━'*10}•\n"
                f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: <code>{address.get('street', 'N/A')}</code>\n"
                f"𝗖𝗶𝘁𝘆: <code>{address.get('city', 'N/A')}</code>\n"
                f"𝗦𝘁𝗮𝘁𝗲: <code>{address.get('state', 'N/A')}</code>\n"
                f"𝗣𝗼𝘀𝘁𝗮𝗹 𝗖𝗼𝗱𝗲: <code>{address.get('postal_code', 'N/A')}</code>\n"
                f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: <code>{address.get('country', matched_country)}</code>\n"
                f"•{'━'*10}•\n"
                f"Requested by: {username}  |  𝗝𝗼𝗶𝗻: @bro_bin_lagbe"
            )

            bot.send_message(message.chat.id, msg, parse_mode="HTML")

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

    # /country3 কমান্ডের জন্য কাস্টম ডেকোরেটর
    @custom_command_handler("country3")
    def handle_country_list(message: Message):
        try:
            response = requests.get(API_URL)
            if response.status_code != 200:
                bot.send_message(message.chat.id, "❌ Failed to fetch country list.")
                return

            data = response.json()
            country_list = sorted(data.keys())

            country_text = "\n".join([f"• {name}" for name in country_list])
            msg = (
                "<b>✅ Available Countries</b>\n"
                f"{'━'*24}\n"
                f"{country_text}\n"
                f"{'━'*24}\n"
                f"⚠️ Use exactly as shown. উদাহরণ: <code>{command_prefixes_list[0]}fake3 US</code>" # <-- MODIFIED LINE (updated example)
            )

            bot.send_message(message.chat.id, msg, parse_mode="HTML")

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {str(e)}")