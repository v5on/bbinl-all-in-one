
# 🤖 Multi-Feature Telegram Bot

A powerful Telegram bot with multiple utilities including card generation, translation, AI chat, image processing, and more!

## 🌟 Features Overview

### 💳 Card Generation & Checking
- **Generate Cards**: Create test cards from BIN numbers
- **Single Card Check**: Validate individual cards
- **Mass Check**: Bulk validation of card lists
- **BIN Information**: Get detailed bank and country info

### 🤖 AI & Chat Features
- **Gemini AI**: Chat with Google's Gemini AI
- **GPT Integration**: Alternative AI chat option
- **Auto-Reply**: Enable/disable AI auto-responses

### 🌐 Translation & Communication
- **Multi-Language Translation**: Translate text to any language
- **Text-to-Speech**: Convert text to audio
- **Say Command**: Generate speech from text

### 🎨 Image & Media Processing
- **Background Removal**: Remove backgrounds from images
- **Image Generation**: Create AI-generated images
- **Format Conversion**: Convert between different file formats
- **Media Download**: Download content from various platforms

### 🛠️ Utility Features
- **Fake Address Generator**: Generate test addresses
- **Anti-Spam Protection**: Automatic spam detection
- **File Management**: Download and process files

---

## 📋 Command Reference

### 🔹 Card Generation Commands

#### `/gen` or `.gen` - Generate Cards
**Syntax:**
```
/gen <BIN> .cnt <amount>
/gen <BIN>|<MM>|<YY>|<CVV> .cnt <amount>
```

**Examples:**
```
/gen 526732 .cnt 5
/gen 526732xxxxxx|12|28|000 .cnt 10
/gen 515462xxxxxx .cnt 15
```

**Parameters:**
- `BIN`: 6-16 digit BIN number (Visa: 4xxx, MasterCard: 5xxx)
- `.cnt`: Number of cards to generate (max 30)
- `MM`: Expiry month (optional)
- `YY`: Expiry year (optional)
- `CVV`: Card verification value (optional)

#### `/chk` or `.chk` - Check Single Card
**Syntax:**
```
/chk <card>|<mm>|<yy>|<cvv>
```

**Example:**
```
/chk 5267321234567890|05|28|123
```

#### `/mas` - Mass Check Cards
**Usage:**
1. Generate cards using `/gen`
2. Reply to the generated card list with `/mas`

#### `/bin` - BIN Information
**Syntax:**
```
/bin <6-digit-bin>
```

**Example:**
```
/bin 526732
```

### 🔹 AI Chat Commands

#### `/gemini` - Chat with Gemini AI
**Syntax:**
```
/gemini <your question>
```

**Example:**
```
/gemini What is artificial intelligence?
```

#### `/gemini_on` - Enable Auto-Reply
Enables automatic AI responses to all messages in the chat.

#### `/gemini_off` - Disable Auto-Reply
Disables automatic AI responses.

#### `/gpt` - Chat with GPT
**Syntax:**
```
/gpt <your question>
```

### 🔹 Translation Commands

#### `/translate` - Translate Text
**Syntax:**
```
/translate <language_code> <text>
```

**Examples:**
```
/translate fr Hello World
/translate es How are you?
/translate bn I love programming
```

**Reply Method:**
Reply to any message with `/translate <language_code>` to translate that message.

### 🔹 Media & Image Commands

#### `/say` - Text to Speech
**Syntax:**
```
/say <text>
```

**Example:**
```
/say Hello, this is a test message
```

#### `/bgremove` - Remove Background
Send an image with the caption `/bgremove` to remove its background.

#### `/imagine` - Generate Images
**Syntax:**
```
/imagine <description>
```

**Example:**
```
/imagine A beautiful sunset over mountains
```

#### `/converter` - Convert Files
Upload a file with `/converter` to convert between formats.

#### `/download` - Download Media
**Syntax:**
```
/download <URL>
```

### 🔹 Utility Commands

#### `/fkaddress` - Generate Fake Address
Generates a random fake address for testing purposes.

#### `/start` or `/arise` - Welcome Message
Shows welcome message and basic command overview.

#### `/reveal` - Show All Commands
Displays comprehensive command list.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from @BotFather)
- Required API keys for various services

### Installation on Replit

1. **Fork this Repl** or create a new Python Repl
2. **Install Dependencies**: Dependencies will be automatically installed from `requirements.txt`
3. **Set Environment Variables**: Use Replit Secrets to configure:
   - `BOT_TOKEN`: Your Telegram bot token
   - `GEMINI_API_KEY`: Google Gemini API key (optional)
   - `OPENAI_API_KEY`: OpenAI API key (optional)
4. **Run the Bot**: Click the Run button or use `python main.py`

### Configuration

Add these secrets in your Replit environment:

```
BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 📁 Project Structure

```
├── handlers/                 # Command handlers
│   ├── gen_handler.py        # Card generation
│   ├── chk_handler.py        # Card checking
│   ├── translate_handler.py  # Translation
│   ├── gemini_handler.py     # AI chat
│   ├── say_handler.py        # Text-to-speech
│   ├── bgremove_handler.py   # Background removal
│   ├── imagine_handler.py    # Image generation
│   └── ...                   # Other handlers
├── main.py                   # Main bot file
├── cleanup.py                # Cleanup utilities
├── flag_data.py             # Country flags data
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

---

## ⚠️ Important Notes

### Card Generation Limits
- ✅ Only **Visa (4xxx)** and **MasterCard (5xxx)** BINs supported
- ⛔ American Express, Discover not supported
- 🔢 Maximum 30 cards per request
- ⚠️ Cards are for **testing purposes only**

### API Rate Limits
- Some features may have rate limits depending on external APIs
- The bot includes fallback mechanisms for reliability

### Privacy & Security
- Chat histories are stored locally for AI continuity
- No sensitive data is permanently stored
- Use responsibly and follow Telegram's ToS

---

## 🛠️ Development

### Adding New Features

1. Create a new handler file in `handlers/`
2. Import and register in `handlers/__init__.py`
3. Add registration call in `main.py`

### Contributing

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📞 Support & Links

- **Telegram Channel**: [https://t.me/bro_bin_lagbe](https://t.me/bro_bin_lagbe)
- **Issues**: Report bugs and request features
- **Documentation**: This README file

---

## 📄 License

This project is for educational purposes only. Use responsibly and in accordance with all applicable laws and terms of service.

---

## 🔄 Recent Updates

- ✅ Enhanced card generation with multiple fallback APIs
- ✅ Improved BIN information accuracy
- ✅ Added translation capabilities
- ✅ Integrated AI chat features
- ✅ Background removal functionality
- ✅ File conversion utilities
- ✅ Anti-spam protection

---

**Happy Botting! 🤖**

*Built with ❤️ for the Telegram community*
