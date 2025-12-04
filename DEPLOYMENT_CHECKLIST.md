# Friday Voice Assistant - Deployment Checklist

## ✅ Fixes Applied in This Session

### 1. Image Generation API Fix (ImageGeneration.py)
- **Issue**: HuggingFace API returned 410 error (endpoint deprecated)
- **Fix**: Updated `API_URL` from `api-inference.huggingface.co` to `router.huggingface.co`
- **Location**: Line 21 in `Backend/ImageGeneration.py`

### 2. Clarification Behavior Fix (brain.py)
- **Issue**: Assistant wasn't asking for clarification on ambiguous requests
- **Fix**: Added detailed "CRITICAL CLARIFICATION & MULTI-STEP BEHAVIOR" section to system instruction
- **Location**: Lines 163-210 in `Backend/brain.py`

### 3. Connection Stability Fix (main.py)
- **Issue**: Connection drops caused automatic shutdown
- **Fix**: Added auto-reconnection with exponential backoff (up to 10 attempts)
- **Features**:
  - Reconnects automatically on connection loss
  - Exponential backoff (2s, 4s, 8s... up to 60s max)
  - Maximum 10 reconnection attempts
  - Graceful handling of all exception types
- **Location**: `run()` method in `main.py`

### 4. Tool Execution & File Sending
- **Status**: Already working correctly
- **All generators return**: `(response_message, file_path)` tuple
- **Telegram/Email**: Accept file paths and send correctly

---

## 📋 Pre-Deployment Checklist

### 1. Environment Variables (.env file)
Create a `.env` file in the project root with these variables:

```env
# User Settings
Username=Boss
Assistantname=Friday

# Google Gemini API (Main voice AI)
ACTIVE_GOOGLE_API=GOOGLE_API_KEY_1
GOOGLE_API_KEY_1=your_gemini_api_key
GEMINI_API_KEY=your_gemini_api_key

# Groq API (Document generation)
ACTIVE_GROQ_API=GROQ_API_KEY_1
GROQ_API_KEY_1=your_groq_api_key

# HuggingFace (Image generation)
HUGGINGFACE_API_KEY=your_huggingface_api_key

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_default_chat_id

# Tavily Search (Internet search)
TAVILY_API_KEY=your_tavily_api_key

# Mem0 (Long-term memory)
MEM0_API_KEY=your_mem0_api_key

# Power Operations Password
POWER_PASSWORD=your_password

# Optional: Multiple API keys for rotation
# GOOGLE_API_KEY_2=...
# GROQ_API_KEY_2=...
```

### 2. Required Files
- [ ] `credentials.json` - Google OAuth credentials (for Gmail API)
  - Download from Google Cloud Console
  - Place in project root

### 3. Python Dependencies
```bash
pip install -r requirements.txt
```

Key packages:
- `google-generativeai` - Gemini API
- `pyaudio` - Audio processing
- `faster-whisper` - Offline transcription
- `fastapi`, `uvicorn` - WebSocket server
- `python-telegram-bot` - Telegram integration
- `groq` - LLM for documents
- `mem0ai` - Long-term memory
- `tavily-python` - Internet search

### 4. System Requirements
- **OS**: Windows 10/11 (some features Windows-only)
- **Python**: 3.11+ (3.13 for `except*` syntax)
- **Hardware**:
  - Microphone for voice input
  - Speakers/headphones for audio output
- **Network**: Internet connection for all APIs

### 5. Optional Dependencies (Windows)
```bash
pip install pywin32 comtypes screen-brightness-control AppOpener
```
For Office document conversion, Windows theme control, app management.

---

## 🚀 Running the Application

### Start Backend + Voice Assistant
```bash
cd E:\Friday\Friday2
python main.py
```

### Start Frontend UI (separate terminal)
```bash
cd E:\Friday\Friday2\jarvis-ui
pnpm install  # or npm install
pnpm dev      # or npm run dev
```

### Access Points
- **UI**: http://localhost:3000
- **WebSocket**: ws://localhost:8000/ws
- **REST API**: http://localhost:8000/api/*
- **Health Check**: http://localhost:8000/health

---

## 🔍 Troubleshooting

### 1. "Connection lost" messages
- Normal if network is unstable
- Assistant will auto-reconnect (up to 10 times)
- Check your internet connection

### 2. Image generation fails
- Verify `HUGGINGFACE_API_KEY` in `.env`
- Check HuggingFace API status
- The API URL has been updated to the new endpoint

### 3. Telegram messages not sending
- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Ensure the bot has been started by the recipient
- Check contacts.json for saved chat IDs

### 4. Email not working
- Complete Gmail OAuth flow (run once to authorize)
- Ensure `credentials.json` is present
- Check `Database/gmail_token.json` exists after auth

### 5. Audio issues
- Check microphone is connected and working
- Ensure no other app is using the microphone
- Try adjusting `CHUNK_SIZE` in main.py if choppy

### 6. Memory/context issues
- Verify `MEM0_API_KEY` is set
- Check `Database/chatlogs.json` is being updated
- Memory syncs every 5 minutes automatically

---

## 📁 Project Structure

```
Friday2/
├── main.py                 # Main entry point
├── .env                    # Environment variables
├── credentials.json        # Google OAuth
├── requirements.txt        # Python dependencies
├── Backend/
│   ├── brain.py           # AI brain with tools
│   ├── Automation.py      # System control
│   ├── ImageGeneration.py # Image generation
│   ├── telegram_handler.py# Telegram integration
│   ├── email_handler.py   # Gmail integration
│   ├── llm_handler.py     # Groq/Google LLM
│   ├── logger.py          # Logging & transcription
│   ├── memory_handler.py  # Mem0 integration
│   ├── weather.py         # Weather API
│   ├── contacts_manager.py# Contact management
│   └── *Generator.py      # Document generators
├── Database/
│   ├── chatlogs.json      # Conversation history
│   ├── contacts.json      # Saved contacts
│   ├── gmail_token.json   # Gmail OAuth token
│   └── mute_state.txt     # Mic mute persistence
├── Data/
│   ├── GeneratedDocuments/# Generated files
│   ├── GeneratedImages/   # Generated images
│   └── ConvertedDocuments/# Converted files
└── jarvis-ui/             # Next.js frontend
    ├── app/               # Pages
    ├── components/        # React components
    └── hooks/             # Custom hooks
```

---

## 🎉 Ready for Deployment!

All critical issues have been fixed:
1. ✅ Image generation API updated
2. ✅ Clarification behavior improved
3. ✅ Auto-reconnection added
4. ✅ All tools return proper file paths
5. ✅ Exception handling improved

The project is now production-ready!
