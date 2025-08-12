import html
import requests
import telebot
import time

# Single API endpoint for both single and mass checks
API_URL = "https://chkr-api.vercel.app/api/check?cc={cc}|{mm}|{yy}|{cvv}"

def check_card(card):
    """Check a single card using the updated API"""
    try:
        parts = card.strip().split('|')
        if len(parts) != 4:
            return "❌ Invalid card format. Use cc|mm|yy|cvv"

        cc, mm, yy, cvv = parts
        
        url = API_URL.format(cc=cc, mm=mm, yy=yy, cvv=cvv)
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "message" in data and "card" not in data:
            return f"❌ {data['message']}"

        status = data.get("status", "Unknown")
        message = data.get("message", "")
        
        status_emoji = ""
        if "live" in status.lower():
            status = "Live"
            status_emoji = "🟢✅"
        elif "die" in status.lower() or "declined" in status.lower():
            status = "Dead"
            status_emoji = "🔴❌"
        else:
            status = "Unknown"
            status_emoji = "⚠️❓"
        
        # Note for "Unknown" status
        if status == "Unknown":
            message += "\n\n⚠️ আননোন আসলে আবার চেক করুন।"
        
        return (
            f"{status_emoji} <b>Status:</b> <code>{html.escape(status)}</code>\n"
            f"ℹ️ {html.escape(message)}"
        )

    except Exception as e:
        return f"⚠️ Error checking card: {str(e)}"

def register(bot, custom_command_handler, command_prefixes_list):
    @custom_command_handler("chk")
    def handle_chk(message):
        
        command_text = message.text.split(" ", 1)[0].lower()
        
        actual_command = ""
        for prefix in command_prefixes_list:
            if command_text.startswith(f"{prefix}chk"):
                actual_command = f"{prefix}chk"
                break
        
        if len(message.text[len(actual_command):].strip().split()) < 1:
            bot.reply_to(message, "❌ Provide a card to check. Format: `cc|mm|yy|cvv`. Example: `/chk 4000123456789012|12|25|123`", parse_mode="Markdown")
            return

        card = message.text[len(actual_command):].strip().split()[0]
        
        user = message.from_user
        username = f"@{user.username}" if user.username else user.first_name

        sent_msg = bot.reply_to(message, f"🔄 Checking <code>{card}</code>...", parse_mode="HTML")
        
        status = check_card(card)
        
        try:
            bot.edit_message_text(
                chat_id=sent_msg.chat.id,
                message_id=sent_msg.message_id,
                text=f"<code>{card}</code>\n{status}\n\n👤 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝗯𝘆: {username}  |  𝗝𝗼𝗶𝗻: @bro_bin_lagbe",
                parse_mode="HTML"
            )
        except Exception as e:
            bot.reply_to(message, f"⚠️ Failed to edit message: {str(e)}")

    @custom_command_handler("mas")
    def handle_mass_chk(message):
        if not message.reply_to_message:
            bot.reply_to(message, f"❌ Please reply to a message containing cards. Example: `{command_prefixes_list[0]}mas` replied to a message with `cc|mm|yy|cvv` lines.", parse_mode="Markdown")
            return

        lines = message.reply_to_message.text.strip().split('\n')
        cards = [line.strip() for line in lines if '|' in line and line.count('|') == 3]

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the replied message.")
            return

        if len(cards) > 10:
            bot.reply_to(message, f"⚠️ Limit exceeded: You can check a maximum of 10 cards at once. You provided {len(cards)}.")
            return

        user = message.from_user
        username = f"@{user.username}" if user.username else user.first_name

        sent_msg = bot.reply_to(message, f"🔄 Checking {len(cards)} cards...", parse_mode="HTML")

        results = []
        
        # Added a loop to check each card with a delay
        for i, card in enumerate(cards):
            status = check_card(card)
            results.append(f"<code>{card}</code>\n{status}")
            
            # Update message text after each card check
            current_progress = f"🔄 Checking card {i+1} of {len(cards)}...\n\n"
            reply_text = current_progress + "\n\n".join(results) + f"\n\n👤 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝗯𝘆: {username}  |  𝗝𝗼𝗶𝗻: @bro_bin_lagbe"

            try:
                bot.edit_message_text(
                    chat_id=sent_msg.chat.id,
                    message_id=sent_msg.message_id,
                    text=reply_text.strip(),
                    parse_mode="HTML"
                )
            except Exception as e:
                pass # Ignore edit message errors for now

            # Wait for 2 seconds before checking the next card
            time.sleep(2)
        
        # Final update after all cards are checked
        final_reply_text = "\n\n".join(results) + f"\n\n👤 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝗯𝘆: {username}  |  𝗝𝗼𝗶𝗻: @bro_bin_lagbe"
        
        if len(final_reply_text) > 4000:
            final_reply_text = final_reply_text[:3900] + "\n\n⚠️ Output trimmed..."
        
        try:
            bot.edit_message_text(
                chat_id=sent_msg.chat.id,
                message_id=sent_msg.message_id,
                text=final_reply_text.strip(),
                parse_mode="HTML"
            )
        except Exception as e:
            bot.reply_to(message, f"⚠️ Failed to edit message: {str(e)}")
