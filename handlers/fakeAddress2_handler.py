import requests
import difflib
from telebot.types import Message

ADDRESS_API = "https://web-production-3071b.up.railway.app/api/address/{code}?key=2580"
COUNTRIES_API = "https://web-production-3071b.up.railway.app/api/countries?key=2580"

# Custom alias mapping for flexible name/code input
ALIASES = {
    "united states": "us", "us": "us",
    "nigeria": "ng", "ng": "ng",
    "lebanon": "lb", "lb": "lb",
    "japan": "jp", "jp": "jp",
    "china": "cn", "cn": "cn",
    "romania": "ro", "ro": "ro",
    "ireland": "ie", "ie": "ie",
    "taiwan": "tw", "tw": "tw",
    "guatemala": "gt", "gt": "gt",
    "azerbaijan": "az", "az": "az",
    "afghanistan": "af", "af": "af",
    "czechia": "cz", "cz": "cz",
    "bulgaria": "bg", "bg": "bg",
    "finland": "fi", "fi": "fi",
    "armenia": "am", "am": "am",
    "ghana": "gh", "gh": "gh",
    "india": "in", "in": "in",
    "singapore": "sg", "sg": "sg",
    "canada": "ca", "ca": "ca",
    "bahrain": "bh", "bh": "bh",
    "bermuda": "bm", "bm": "bm",
    "niger": "ne", "ne": "ne",
    "france": "fr", "fr": "fr",
    "netherlands": "nl", "nl": "nl",
    "argentina": "ar", "ar": "ar",
    "greenland": "gl", "gl": "gl",
    "sudan": "sd", "sd": "sd",
    "uganda": "ug", "ug": "ug",
    "united arab emirates": "ae", "ae": "ae",
    "egypt": "eg", "eg": "eg",
    "iraq": "iq", "iq": "iq",
    "united kingdom": "uk", "uk": "uk",
    "mauritania": "mr", "mr": "mr",
    "greece": "gr", "gr": "gr",
    "poland": "pl", "pl": "pl",
    "portugal": "pt", "pt": "pt",
    "myanmar": "mm", "mm": "mm",
    "algeria": "dz", "dz": "dz",
    "maldives": "mv", "mv": "mv",
    "ukraine": "ua", "ua": "ua",
    "peru": "pe", "pe": "pe",
    "kenya": "ke", "ke": "ke",
    "turkiye": "tr", "tr": "tr",
    "nepal": "np", "np": "np",
    "germany": "de", "de": "de",
    "south korea": "kr", "kr": "kr",
    "chile": "cl", "cl": "cl",
    "colombia": "co", "co": "co",
    "brazil": "br", "br": "br",
    "antarctica": "aq", "aq": "aq",
    "bhutan": "bt", "bt": "bt",
    "australia": "au", "au": "au",
    "tanzania": "tz", "tz": "tz",
    "austria": "at", "at": "at",
    "spain": "es", "es": "es",
    "bolivia": "bo", "bo": "bo",
    "vietnam": "vn", "vn": "vn",
    "saudi arabia": "sa", "sa": "sa",
    "switzerland": "ch", "ch": "ch",
    "sri lanka": "lk", "lk": "lk",
    "panama": "pa", "pa": "pa",
    "sweden": "se", "se": "se",
    "venezuela": "ve", "ve": "ve",
    "indonesia": "id", "id": "id",
    "yemen": "ye", "ye": "ye",
    "jordan": "jo", "jo": "jo",
    "oman": "om", "om": "om",
    "kazakhstan": "kz", "kz": "kz",
    "kzt": "kz", "kazakstan": "kz",
    "anguilla": "ai", "ai": "ai",
    "cameroon": "cm", "cm": "cm",
    "israel": "il", "il": "il",
    "denmark": "dk", "dk": "dk",
    "iceland": "is", "is": "is",
    "belgium": "be", "be": "be",
    "palestine": "ps", "ps": "ps",
    "south africa": "za", "za": "za",
    "cambodia": "kh", "kh": "kh",
    "hong kong": "hk", "hk": "hk",
    "italy": "it", "it": "it",
    "qatar": "qa", "qa": "qa",
    "pakistan": "pk", "pk": "pk",
    "georgia": "ge", "ge": "ge",
    "norway": "no", "no": "no",
    "mexico": "mx", "mx": "mx",
    "new zealand": "nz", "nz": "nz",
    "thailand": "th", "th": "th",
    "albania": "al", "al": "al",
    "morocco": "ma", "ma": "ma",
    "philippines": "ph", "ph": "ph",
    "bangladesh": "bd", "bd": "bd",
    "mahir Land": "4k", "mahir": "4k", "4k": "4k"
}

def register(bot, custom_command_handler, command_prefixes_list): 
    @custom_command_handler("fake")
    def handle_fake(message: Message):

        command_text = message.text.split(" ", 1)[0].lower()
        actual_command_len = 0
        for prefix in command_prefixes_list: 
            if command_text.startswith(f"{prefix}fake"):
                actual_command_len = len(f"{prefix}fake")
                break

        user_input_raw = message.text[actual_command_len:].strip()
        args = user_input_raw.split(" ", 1) 

        if not user_input_raw:
            bot.reply_to(message, f"❌ Country name or code missing.\n\n উদাহরণ:\n`{command_prefixes_list[0]}fake US`\n`{command_prefixes_list[1]}fake bangladesh`\n`{command_prefixes_list[2]}fake kzt`", parse_mode="HTML") 
            return

        user_input = args[0].strip() 
        normalized_input = user_input.lower() if not user_input.isdigit() else user_input

        try:
            # Fetch countries
            response = requests.get(COUNTRIES_API)
            response.raise_for_status()
            countries_data = response.json()["countries"]

            # Create base code map
            code_map = {
                c['country'].lower(): c['country_code'].lower()
                for c in countries_data
            }
            code_map.update({
                c['country_code'].lower(): c['country_code'].lower()
                for c in countries_data
            })

            # Include aliases (lowercased keys, except numbers)
            alias_map = {
                k.lower() if not isinstance(k, int) and not k.isdigit() else k: v.lower()
                for k, v in ALIASES.items()
            }
            code_map.update(alias_map)

            # Try direct match
            country_code = code_map.get(normalized_input)

            if not country_code:
                possible_keys = list(code_map.keys())

                if len(normalized_input) == 2:

                    matches = [
                        (c['country'], c['country_code'])
                        for c in countries_data
                        if c['country_code'].lower().startswith(normalized_input[0]) or c['country_code'].lower().startswith(normalized_input)
                    ]

                    if matches:
                        suggestion_lines = "\n".join([
                            f"• {name} (<code>{code}</code>)" for name, code in matches[:5]
                        ])
                        bot.reply_to(message,
                            f"❌ Country code '<code>{normalized_input}</code>' not found.\n"
                            f"🔍 Did you mean one of these?\n{suggestion_lines}", parse_mode="HTML")
                    else:
                        bot.reply_to(message, f"❌ Invalid country code '<code>{normalized_input}</code>'.", parse_mode="HTML")
                else:

                    suggestion = difflib.get_close_matches(normalized_input, possible_keys, n=1)
                    if suggestion:
                        matched = suggestion[0]
                        suggested_code = code_map[matched]
                        matched_country = next((c['country'] for c in countries_data if c['country_code'].lower() == suggested_code), matched)
                        bot.reply_to(message,
                            f"❌ Country not found.\n"
                            f"🔎 আপনি কি <code>{matched_country}</code> বলতে চেয়েছিলেন? "
                            f"(Code: <code>{suggested_code.upper()}</code>)", parse_mode="HTML")
                    else:
                        bot.reply_to(message, "❌ Country not found or unsupported.", parse_mode="HTML")
                return


            # Fetch address
            address_response = requests.get(ADDRESS_API.format(code=country_code))
            if address_response.status_code != 200:
                bot.send_message(message.chat.id, "❌ Failed to fetch address.")
                return

            address = address_response.json()
            username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

            msg = (
                f"<b>📦 Address for {address.get('country', 'Unknown')}</b> (<code>{address.get('country_code', '').upper()}</code>)\n"
                f"•{'━'*10}•\n"
                f"𝗦𝘁𝗿𝗲𝗲𝘁 𝗔𝗱𝗱𝗿𝗲𝘀𝘀: <code>{address.get('street_address', 'N/A')}</code>\n"
                f"𝗖𝗶𝘁𝘆: <code>{address.get('city', 'N/A')}</code>\n"
                f"𝗦𝘁𝗮𝘁𝗲: <code>{address.get('state', 'N/A')}</code>\n"
                f"𝗣𝗼𝘀𝘁𝗮𝗹 𝗖𝗼𝗱𝗲: <code>{address.get('postal_code', 'N/A')}</code>\n"
                f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: <code>{address.get('country', 'N/A')}</code> (<code>{address.get('country_code', '').upper()}</code>)\n"
                f"𝗖𝘂𝗿𝗿𝗲𝗻𝗰𝘆: <code>{address.get('currency', 'N/A')}</code>\n"
                f"•{'━'*10}•\n"
                f"👤 𝗥𝗲𝗤𝘂𝗲𝘀𝘁 𝗯𝘆: {username}  |  𝗝𝗼𝗶𝗻: @bro_bin_lagbe"
            )
            bot.send_message(message.chat.id, msg, parse_mode="HTML")

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error occurred: {str(e)}")

    # /country কমান্ডের জন্য কাস্টম ডেকোরেটর
    @custom_command_handler("country")
    def handle_countries(message: Message):
        try:
            response = requests.get(COUNTRIES_API)
            response.raise_for_status()
            countries_data = response.json()["countries"]

            if not countries_data:
                bot.send_message(message.chat.id, "⚠️ No countries available at the moment.")
                return

            # Sort alphabetically
            countries_sorted = sorted(countries_data, key=lambda x: x["country"])

            country_lines = [
                f"• {c['country']} (<code>{c['country_code']}</code>)"
                for c in countries_sorted
            ]

            msg = (
                f"<b>🌐 Supported Countries (Total: {len(countries_sorted)})</b>\n"
                f"{'━'*34}\n"
                f"{chr(10).join(country_lines)}\n"
                f"{'━'*34}\n"
                "⚠️ Use the country name or code exactly.\n"
                f"উদাহরণ: <code>{command_prefixes_list[0]}fake BD</code> বা <code>{command_prefixes_list[1]}fake bangladesh</code>" 
            )

            bot.send_message(message.chat.id, msg, parse_mode="HTML")

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Failed to load country list.\nError: {str(e)}")
