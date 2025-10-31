# Friday AI Assistant

A powerful, unified voice and chat AI assistant built with Gemini AI, featuring advanced tools, memory management, and seamless UI integration.

## 🚀 Features

### Core Capabilities
- **🎙️ Natural Voice Conversation** - Real-time voice chat using Gemini Live Audio API
- **💬 Text Chat Interface** - Full-featured web UI with the same Gemini model and tools
- **🧠 Long-term Memory** - Remembers conversations across sessions using Mem0
- **🔄 Multi-Modal Integration** - Voice AND text use the same advanced Gemini model

### Advanced Tools & Integrations
- **🌤️ Weather Information** - Get weather for any city worldwide
- **🔍 Internet Search** - Real-time web search with Tavily
- **📧 Email Management** - Send emails via Gmail integration
- **📱 Telegram Integration** - Send messages and files
- **🖼️ AI Image Generation** - Create images with AI
- **📄 Document Generation** - PDF, Word, PowerPoint, Excel creation
- **🔄 File Conversion** - Convert between various document formats
- **🤖 System Automation** - Control brightness, themes, apps, screenshots
- **🏠 Smart Home Control** - Google Home device integration
- **📞 Smartphone Integration** - Bluetooth-connected phone control
- **👤 Contact Management** - Store and manage contacts with aliases

### Technical Features
- **🔐 Multiple API Support** - 15 Google API slots + 10 Groq API slots
- **💾 Persistent Storage** - JSON-based data storage for contacts and chatlogs
- **🌐 WebSocket Communication** - Real-time UI-backend synchronization
- **⚡ FastAPI Backend** - High-performance async server
- **🎨 Modern React UI** - Next.js with TypeScript and Tailwind CSS
- **🔊 Audio Processing** - PyAudio for microphone input/output
- **🛡️ Secure Operations** - Password-protected power operations

## 🏗️ Architecture

```
Friday AI Assistant
├── Backend (Python/FastAPI)
│   ├── main.py - Core application with voice assistant & WebSocket server
│   ├── brain.py - Gemini AI integration with tool execution
│   ├── memory_handler.py - Conversation memory management
│   ├── contacts_manager.py - Contact storage and retrieval
│   ├── logger.py - Comprehensive logging system
│   └── Various tool modules (weather, email, automation, etc.)
├── Frontend (Next.js/React)
│   ├── Settings page - API key management & contact operations
│   ├── Chat interface - Real-time messaging with streaming
│   ├── Dashboard - System monitoring and controls
│   └── WebSocket client for real-time updates
└── Data Storage
    ├── Database/ - JSON files for persistent data
    ├── Data/ - Generated content and files
    └── Logs - Comprehensive activity logging
```

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **Git**
- **Windows/Linux/Mac** (Windows recommended for full feature support)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd friday-ai-assistant
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd jarvis-ui
pnpm install  # or npm install
```

### 4. Environment Configuration
Create a `.env` file in the root directory:

```env
# User Configuration
Username=Boss
Assistantname=Friday

# API Keys (Choose your active ones)
ACTIVE_GOOGLE_API=GOOGLE_API_KEY_1
ACTIVE_GROQ_API=GROQ_API_KEY_1

# Google API Keys (up to 15 slots)
GOOGLE_API_KEY_1=your_google_api_key_here
GOOGLE_API_KEY_2=your_google_api_key_here
# ... up to GOOGLE_API_KEY_15

# Groq API Keys (up to 10 slots)
GROQ_API_KEY_1=your_groq_api_key_here
GROQ_API_KEY_2=your_groq_api_key_here
# ... up to GROQ_API_KEY_10

# LLM Configuration
LLM_PROVIDER=Google  # or Groq
GEMINI_MODEL=gemini-2.0-flash-exp
GROQ_MODEL=llama-3.3-70b-versatile
OLLAMA_MODEL=llama3.2
COHERE_MODEL=command-r-plus

# Gmail Integration (for email features)
GMAIL_CREDENTIALS_PATH=Database/gmail_credentials.json

# Telegram Bot (for Telegram features)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

## 🚀 Running the Application

### Start Everything (Recommended)
```bash
python main.py
```

This starts both the voice assistant and the web UI server simultaneously.

### Manual Startup

#### Backend Only (Voice Assistant)
```bash
python main.py
```

#### Frontend Only (Web UI)
```bash
cd jarvis-ui
pnpm dev  # or npm run dev
```

## 🌐 Access Points

- **Web UI**: http://localhost:3000
- **API Server**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws
- **Health Check**: http://localhost:8000/health

## 🎯 Usage

### Voice Commands
- **Normal Conversation**: Just speak naturally
- **Stop Speaking**: Say "Friday stop"
- **Shutdown**: Say "Shutdown Friday" or "Exit Friday"

### Web Interface
- **Chat**: Send text messages in the chat interface
- **Settings**: Configure API keys and manage contacts
- **System Controls**: Adjust brightness, change themes, take screenshots
- **Document Generation**: Create PDFs, Word docs, presentations, spreadsheets
- **File Operations**: Convert documents, send emails, use Telegram

### API Key Management
- Supports up to 15 Google API keys and 10 Groq API keys
- Automatic fallback to available keys if rate limits are hit
- Configure active keys in the settings UI or .env file

## 🔧 Configuration

### Voice Settings
- **Microphone**: Automatically detects default input device
- **Audio Format**: 16-bit PCM, 16kHz sample rate
- **Channels**: Mono

### Memory Settings
- **Provider**: Mem0 for long-term conversation memory
- **Context Window**: Intelligent context retrieval
- **Persistence**: Automatic saving across sessions

### UI Settings
- **Theme**: Light/Dark mode support
- **Real-time Updates**: WebSocket-powered live updates
- **System Monitoring**: CPU, memory, and network usage

## 🛠️ Development

### Project Structure
```
.
├── main.py                 # Main application entry point
├── Backend/               # Python backend modules
├── jarvis-ui/            # Next.js frontend
├── Database/             # Persistent data storage
├── Data/                 # Generated content
├── requirements.txt      # Python dependencies
└── .env                  # Environment configuration
```

### Adding New Tools
1. Create a new module in `Backend/`
2. Implement the tool function
3. Register it in `brain.py`
4. Add WebSocket endpoint in `main.py` if needed
5. Update the frontend UI

### API Key Rotation
The system automatically rotates between available API keys when rate limits are encountered. Add more keys to your `.env` file using the slot system.

## 🔍 Troubleshooting

### Common Issues

**Microphone Not Working**
- Check microphone permissions
- Verify default audio device in system settings
- Use headphones to prevent audio feedback

**API Key Errors**
- Verify API keys in `.env` file
- Check API key validity and quotas
- Ensure correct slot configuration

**WebSocket Connection Issues**
- Verify port 8000 is not blocked
- Check firewall settings
- Ensure FastAPI is running

**Memory Issues**
- Check available RAM (minimum 4GB recommended)
- Clear old chatlogs if storage is full
- Verify Mem0 service connectivity

### Logs
All activities are logged to:
- `Database/TerminalLogs/` - System operations
- `Database/Tool Logs/` - Tool executions
- `Database/Chatlogs/` - Conversations

## 📊 System Requirements

### Minimum
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Network**: Stable internet connection

### Recommended
- **OS**: Windows 11
- **RAM**: 8GB+
- **Storage**: 10GB+ free space
- **Network**: High-speed internet

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For issues and questions:
1. Check the logs in `Database/` directories
2. Verify your `.env` configuration
3. Ensure all dependencies are installed
4. Test with minimal configuration first

## 🔄 Updates

- Keep dependencies updated regularly
- Monitor API key usage and quotas
- Backup your `Database/` folder regularly
- Update environment variables as needed

---

**Built with ❤️ using Gemini AI, FastAPI, Next.js, and modern Python tooling.**