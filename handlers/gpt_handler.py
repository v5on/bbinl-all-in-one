import requests

def register(bot, custom_command_handler, command_prefixes_list):
    @custom_command_handler("gpt")
    def handle_gpt(message):

        command_text = message.text.split(" ", 1)[0].lower()
        actual_command_len = 0
        for prefix in command_prefixes_list: 
            if command_text.startswith(f"{prefix}gpt"):
                actual_command_len = len(f"{prefix}gpt")
                break

        args = message.text[actual_command_len:].strip() 
        if not args:

            bot.reply_to(message, f"অনুগ্রহ করে প্রশ্ন লিখুন। উদাহরণ: `{command_prefixes_list[0]}gpt তোমার প্রশ্ন`, `{command_prefixes_list[1]}gpt তোমার প্রশ্ন`", parse_mode="Markdown")
            return

        try:
            api_list_url = "https://raw.githubusercontent.com/MOHAMMAD-NAYAN-07/Nayan/main/api.json"
            res = requests.get(api_list_url, timeout=10)
            res.raise_for_status()
            api_base = res.json().get("api")
            if not api_base:
                bot.reply_to(message, "API URL পাওয়া যায়নি।")
                return

            gpt_url = f"{api_base}/nayan/gpt3?prompt={requests.utils.quote(args)}"
            gpt_res = requests.get(gpt_url, timeout=15)
            gpt_res.raise_for_status()
            data = gpt_res.json()

            reply_text = data.get("response") or "দুঃখিত, আমি আপনার প্রশ্নটি বুঝতে পারিনি।"
            bot.reply_to(message, reply_text)

        except Exception as e:
            bot.reply_to(message, f"API ত্রুটি: {str(e)}")