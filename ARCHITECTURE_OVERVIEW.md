# Friday AI Assistant - Architecture Overview

## High-Level System Architecture

```mermaid
flowchart TB
    User[👤 User] -->|Voice/Text| Input[🎤 Input Layer]
    
    Input --> VoiceInput[Voice Input<br/>PyAudio]
    Input --> TextInput[Text Input<br/>WebSocket/REST API]
    
    VoiceInput --> MainPy[main.py<br/>Entry Point]
    TextInput --> FastAPI[FastAPI Server<br/>Port 8000]
    
    FastAPI --> WSHandler[WebSocket Handler]
    FastAPI --> RESTEndpoints[REST Endpoints<br/>21+ APIs]
    
    MainPy --> Brain[🧠 brain.py<br/>Central Intelligence]
    WSHandler --> Brain
    RESTEndpoints --> Brain
    
    Brain --> AIModel[🤖 AI Model<br/>Gemini 2.5 Flash]
    AIModel --> DMM[🎯 Decision Making Model<br/>DMM]
    
    DMM --> Tools[🛠️ Tool Execution Layer]
    
    Tools --> SystemTools[System Tools<br/>- Automation<br/>- Screenshot<br/>- App Control<br/>- Brightness/Theme]
    Tools --> ContentTools[Content Generation<br/>- PDF/Word/PPT/Excel<br/>- Image Generation<br/>- Website Generator<br/>- File Converter]
    Tools --> CommTools[Communication<br/>- Email Handler<br/>- Telegram Handler<br/>- Calendar Handler]
    Tools --> DataTools[Data & Search<br/>- Memory Handler<br/>- Contacts Manager<br/>- Weather API<br/>- Internet Search]
    
    SystemTools --> Output[📤 Output Layer]
    ContentTools --> Files[📁 Data Folder<br/>Generated Files]
    CommTools --> External[🌐 External Services<br/>Gmail/Telegram/Calendar]
    DataTools --> Database[💾 Database Folder<br/>Chatlogs/Contacts/Tokens]
    
    Output --> VoiceOutput[Voice Output<br/>PyAudio TTS]
    Output --> UIResponse[UI Response<br/>WebSocket/REST]
    
    Files --> User
    VoiceOutput --> User
    UIResponse --> UI[🖥️ Next.js Frontend<br/>jarvis-ui]
    UI --> User
    
    Database -.->|Long-term Memory| Brain
    External -.->|OAuth/API| Tools
    
    style Brain fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style AIModel fill:#4dabf7,stroke:#1971c2,color:#fff
    style DMM fill:#a78bfa,stroke:#7c3aed,color:#fff
    style Tools fill:#51cf66,stroke:#2f9e44,color:#fff
    style FastAPI fill:#ffd43b,stroke:#f08c00,color:#000
    style User fill:#e599f7,stroke:#9c36b5,color:#fff
    style UI fill:#74c0fc,stroke:#1864ab,color:#fff
```

## System Flow Summary

### 1. **Input Layer**
- **Voice:** PyAudio captures audio → Native Audio API
- **Text:** WebSocket/REST API → FastAPI Server

### 2. **Processing Core**
- **main.py:** Entry point, initializes all handlers
- **AI Model:** Gemini 2.5 Flash for natural language processing
- **DMM (Decision Making Model):** Proprietary AI model for tool selection and routingng
- **Tool Selection:** AI decides which tools to execute

### 3. **Tool Execution Layer**
- **System Tools:** Automation, screenshot, app control, system settings
- **Content Generation:** PDF, Word, PPT, Excel, images, websites
- **Communication:** Email, Telegram, Google Calendar
- **Data & Search:** Memory, contacts, weather, internet search

### 4. **Output Layer**
- **Voice Output:** TTS via PyAudio
- **UI Response:** WebSocket/REST to Next.js frontend
- **File Generation:** Saved to Data folder
- **External Services:** Gmail, Telegram, Calendar APIs

### 5. **Storage & State**
- **Database Folder:** Chatlogs, contacts, OAuth tokens
- **Memory System:** Mem0 for long-term context
- **File System:** Generated content in Data folder

## Technology Stack

| Layer | Technology |
|-------|------------|
| **AI Model** | Gemini 2.5 Flash (Native Audio) |
| **Decision Engine** | DMM (Decision Making Model) - Proprietary |
| **Backend** | Python + FastAPI |
| **Frontend** | Next.js + React + TypeScript |
| **UI Framework** | shadcn/ui + Tailwind CSS |
| **Voice** | PyAudio (Input/Output) |
| **Memory** | Mem0 (Long-term) |
| **Database** | JSON files |
| **Communication** | WebSocket + REST API |
| **Authentication** | OAuth 2.0 (Google Services) |

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Next.js UI
    participant B as Brain
    participant AI as AI Model
    participant DMM as DMM
    participant T as Tools
    participant O as Output
    
    U->>I: Voice/Text Request
    U->>UI: UI Interaction
    I->>B: Process Input
    UI->>B: WebSocket Message
    B->>AI: Send to AI Model
    AI->>DMM: Analyze Intent
    DMM->>DMM: Tool Selection
    DMM->>B: Selected Tools
    B->>T: Execute Tool(s)
    T->>T: Perform Action
    T->>B: Return Result
    B->>AI: Send Result to AI
    AI->>B: Generate Response
    B->>O: Format Output
    O->>U: Voice/Text Response
    O->>UI: Update UI
    UI->>U: Visual Feedback
    O->>U: Voice/Text/File Response
```

## Key Features

### 🎯 Core Capabilities
- **Voice Conversation:** Natural voice interaction with native audio processing
- **Tool Orchestration:** 50+ integrated tools for diverse tasks
- **Multi-Modal:** Text, voice, image, document generation
- **Real-time Communication:** WebSocket for instant updates
- **Long-term Memory:** Context retention across sessions

### 🔧 Tool Categories

1. **System Control** (8 tools)
   - Automation, screenshots, app management, system settings

2. **Content Generation** (10 tools)
   - Documents (PDF, Word, PPT, Excel), images, websites

3. **Communication** (6 tools)
   - Email, Telegram, Calendar (view, create, update, delete events)

4. **Data Management** (8 tools)
   - Memory, contacts, weather, internet search

5. **File Operations** (5 tools)
   - File conversion, compression, generation tracking

### 🌐 API Access
- **REST API:** 21+ endpoints for synchronous operations
- **WebSocket:** Real-time bidirectional communication
- **Frontend:** Next.js dashboard with live updates

## Architecture Principles

### ✅ Design Patterns
- **Modular Design:** Each tool is an independent handler
- **Central Router:** brain.py orchestrates all operations
- **Async Processing:** FastAPI with async/await
- **Stateless API:** RESTful design with token-based auth
- **Event-Driven:** WebSocket for real-time updates

### 🔒 Security
- **OAuth 2.0:** Google services authentication
- **Token Storage:** Secure credential management
- **Local-First:** No external data sharing
- **API Isolation:** CORS-protected endpoints

### 📊 Scalability
- **Async I/O:** Non-blocking operations
- **Modular Tools:** Easy to add new capabilities
- **Multiple API Keys:** 15 Google + 10 Groq slots
- **LoadDMM/               # Decision Making Model (AI)
│   │   ├── decision_model.py
│   │   ├── tool_classifier.py
│   │   ├── intent_analyzer.py
│   │   └── models/        # Trained model weights
│   ├── *_handler.py       # Tool handlers (email, calendar, memory, etc.)
│   └── *Generator.py      # Content generators (PDF, Word, PPT, etc.)
├── Database/              # Chatlogs, contacts, OAuth tokens
├── Data/                  # Generated files (PDF, images, websites)
└── jarvis-ui/            # Next.js frontend (shadcn/ui + Tailwind)
Friday2/
├── main.py                 # Entry point + FastAPI server
├── Backend/
│   ├── brain.py           # Central intelligence router
│   ├── *_handler.py       # Tool handlers (email, calendar, memory, etc.)
│   └── *Generator.py      # Content generators (PDF, Word, PPT, etc.)
├── Database/              # Chatlogs, contacts, OAuth tokens
├── Data/                  # Generated files (PDF, images, websites)
└── jarvis-ui/            # Next.js frontend
```

## Quick Links

- **Full Architecture:** [ARCHITECTURE_FLOWCHART.md](ARCHITECTURE_FLOWCHART.md)
- **API Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Calendar Integration:** [CALENDAR_INTEGRATION.md](CALENDAR_INTEGRATION.md)
- **Main Documentation:** [README.md](README.md)

---

**Last Updated:** January 11, 2026  
**Version:** 2.0  
**Status:** Production Ready
