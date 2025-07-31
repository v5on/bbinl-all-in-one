import os
import asyncio
import aiohttp
import aiofiles
import telebot
import re

async def generate_image(prompt, style="", amount=1):
    image_paths = []

    for i in range(min(amount, 4)):  # Max 4 images
        # Ensure prompt and style are properly URL-encoded
        encoded_prompt = aiohttp.helpers.quote(prompt)
        encoded_style = aiohttp.helpers.quote(style)
        url = f"https://imggen-delta.vercel.app/?prompt={encoded_prompt}&style={encoded_style}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                res.raise_for_status() # Raise an exception for bad status codes
                data = await res.json()
                image_url = data.get("url")

                if not image_url:
                    break

                async with session.get(image_url) as img_res:
                    img_res.raise_for_status() # Raise an exception for bad status codes
                    img_bytes = await img_res.read()

                img_path = f"gart_result_{i+1}.png"
                async with aiofiles.open(img_path, mode='wb') as f:
                    await f.write(img_bytes)

                image_paths.append(img_path)

    return image_paths

# register function now accepts command_prefixes_list
def register(bot, custom_command_handler, command_prefixes_list): # <-- MODIFIED LINE (added command_prefixes_list)
    @custom_command_handler("gart")
    def gart_command(message):
        # Get the full command text and calculate actual command length
        command_text = message.text.split(" ", 1)[0].lower()
        actual_command_len = 0
        # Use command_prefixes_list here
        for prefix in command_prefixes_list: # <-- MODIFIED LINE (using command_prefixes_list)
            if command_text.startswith(f"{prefix}gart"):
                actual_command_len = len(f"{prefix}gart")
                break

        arg_string = message.text[actual_command_len:].strip() # কমান্ডের অংশ বাদ দিয়ে বাকি টেক্সট

        if not arg_string:
            # Update example message with dynamic prefixes
            bot.reply_to(message, f"অনুগ্রহ করে একটি প্রম্পট দিন। ব্যবহারের নিয়ম: `{command_prefixes_list[0]}gart a cat .stl anime .cnt 2`", parse_mode="Markdown") # <-- MODIFIED LINE (updated example)
            return

        # Regular expression to extract prompt, style, and amount
        # It handles cases where .stl or .cnt might be missing
        match = re.match(r"^(.*?)(?:\s*\.stl\s*(.*?))?(?:\s*\.cnt\s*(\d+))?$", arg_string, re.IGNORECASE | re.DOTALL)

        prompt = match.group(1).strip() if match and match.group(1) else ""
        style = match.group(2).strip() if match and match.group(2) else ""
        amount = int(match.group(3)) if match and match.group(3) else 1

        if not prompt:
            bot.reply_to(message, "অনুগ্রহ করে একটি সঠিক প্রম্পট দিন।", parse_mode="Markdown")
            return

        if amount > 4:
            amount = 4
            bot.reply_to(message, "আপনি সর্বোচ্চ ৪টি ছবি তৈরি করতে পারবেন। ৪টি ছবি তৈরি করা হচ্ছে...")

        generating_msg = bot.reply_to(message, "আপনার ছবি/ছবিগুলো তৈরি করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")

        try:
            image_paths = asyncio.run(generate_image(prompt, style, amount))

            if not image_paths:
                bot.edit_message_text(
                    "ছবি তৈরি করতে ব্যর্থ হয়েছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।",
                    chat_id=generating_msg.chat.id,
                    message_id=generating_msg.message_id
                )
                return

            # Send images one by one
            for path in image_paths:
                with open(path, 'rb') as f:
                    bot.send_photo(message.chat.id, f)

            # Edit the generating message with final result
            result_text = (
                f"🔍ইমেজ জেনারেশন রেজাল্ট🔍\n\n📝প্রম্পট: {prompt}\n" +
                (f"🎨স্টাইল: {style}\n" if style else "") +
                f"#️⃣ছবির সংখ্যা: {len(image_paths)}"
            )
            bot.edit_message_text(
                result_text,
                chat_id=generating_msg.chat.id,
                message_id=generating_msg.message_id
            )

        except Exception as e:
            bot.reply_to(message, f"❌ ছবি তৈরি করতে সমস্যা হয়েছে: {str(e)}")
        finally:
            # Clean up generated files
            for path in image_paths:
                if os.path.exists(path):
                    os.remove(path)