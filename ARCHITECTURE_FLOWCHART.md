# Friday AI Assistant - Complete Architecture Flowchart

## High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        A1[Voice Input - Microphone]
        A2[Web UI - React/Next.js]
        A3[Text Input - Chat]
    end

    subgraph "Main Application - main.py"
        B1[Audio Loop - PyAudio]
        B2[FastAPI Server]
        B3[WebSocket Manager]
        B4[System Metrics Monitor]
    end

    subgraph "Core Intelligence - brain.py"
        C1[Gemini Brain]
        C2[Tool Router]
        C3[Function Executor]
        C4[Memory Context Handler]
    end

    subgraph "AI Models & APIs"
        D1[AI Model - Native Audio]
        D2[Groq API - Fallback LLM]
        D3[Mem0 - Long-term Memory]
        D4[Tavily - Internet Search]
    end

    subgraph "Backend Modules"
        E1[weather.py - Weather Tool]
        E2[email_handler.py - Gmail API]
        E3[calendar_handler.py - Calendar API]
        E4[telegram_handler.py - Telegram Bot]
        E5[contacts_manager.py - Contacts DB]
        E6[ImageGeneration.py - Stable Diffusion]
        E7[PDFGenerator.py - PDF Creation]
        E8[WordGenerator.py - Word Docs]
        E9[PPTGenerator.py - PowerPoint]
        E10[ExcelGenerator.py - Excel Sheets]
        E11[WebsiteGenerator.py - HTML Sites]
        E12[FileConverter.py - Format Conversion]
        E13[SmartCompressor.py - File Compression]
        E14[Automation.py - System Control]
        E15[logger.py - Logging System]
        E16[memory_handler.py - Memory Management]
        E17[llm_handler.py - LLM Management]
    end

    subgraph "Data Storage"
        F1[Database/chatlogs.json]
        F2[Database/contacts.json]
        F3[Database/gmail_token.json]
        F4[Database/credentials.json]
        F5[Data/GeneratedDocuments/]
        F6[Data/GeneratedImages/]
        F7[Data/GeneratedWebsites/]
        F8[Data/ConvertedDocuments/]
        F9[Database/TerminalLogs/]
    end

    subgraph "External Services"
        G1[Google Cloud APIs]
        G2[Telegram API]
        G3[Hugging Face API]
        G4[Tavily Search API]
        G5[OpenWeather API]
    end

    subgraph "Frontend - jarvis-ui/"
        H1[Next.js App Router]
        H2[React Components]
        H3[WebSocket Client]
        H4[Tailwind CSS Styling]
        H5[Dashboard]
        H6[Chat Interface]
        H7[Settings Page]
    end

    %% User to Main App
    A1 --> B1
    A2 --> B3
    A3 --> B3

    %% Main App to Brain
    B1 --> C1
    B2 --> C1
    B3 --> C1

    %% Brain to AI Models
    C1 --> D1
    C1 --> D2
    C1 --> D3
    C1 --> D4

    %% Brain to Tool Router
    C1 --> C2
    C2 --> C3
    C3 --> C4

    %% Tool Router to Backend Modules
    C3 --> E1
    C3 --> E2
    C3 --> E3
    C3 --> E4
    C3 --> E5
    C3 --> E6
    C3 --> E7
    C3 --> E8
    C3 --> E9
    C3 --> E10
    C3 --> E11
    C3 --> E12
    C3 --> E13
    C3 --> E14
    C3 --> E15
    C3 --> E16
    C3 --> E17

    %% Backend to Storage
    E2 --> F3
    E3 --> F3
    E5 --> F2
    E6 --> F6
    E7 --> F5
    E8 --> F5
    E9 --> F5
    E10 --> F5
    E11 --> F7
    E12 --> F8
    E15 --> F1
    E15 --> F9
    E16 --> F1

    %% Backend to External Services
    E1 --> G5
    E2 --> G1
    E3 --> G1
    E4 --> G2
    E6 --> G3
    D4 --> G4

    %% Frontend Components
    H1 --> H2
    H2 --> H3
    H2 --> H5
    H2 --> H6
    H2 --> H7
    H3 --> B3

    style C1 fill:#4CAF50,stroke:#2E7D32,stroke-width:3px
    style D1 fill:#2196F3,stroke:#1565C0,stroke-width:2px
    style B2 fill:#FF9800,stroke:#E65100,stroke-width:2px
    style H1 fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px
```

## Detailed Component Flow

```mermaid
flowchart TD
    START[User Input] --> INPUT_TYPE{Input Type?}
    
    INPUT_TYPE -->|Voice| VOICE[Voice Input via PyAudio]
    INPUT_TYPE -->|Text/UI| WEBSOCKET[WebSocket Connection]
    INPUT_TYPE -->|Chat| UI_CHAT[Web UI Chat Interface]
    
    VOICE --> AUDIO_LOOP[Audio Loop Processing]
    WEBSOCKET --> FASTAPI[FastAPI Server]
    UI_CHAT --> FASTAPI
    
    AUDIO_LOOP --> GEMINI_STREAM[Gemini Native Audio Stream]
    FASTAPI --> GEMINI_CHAT[Gemini Chat API]
    
    GEMINI_STREAM --> BRAIN{Gemini Brain<br/>Tool Router}
    GEMINI_CHAT --> BRAIN
    
    BRAIN --> MEMORY[Memory Handler<br/>Load Context]
    MEMORY --> CHECK_TOOL{Tool Call<br/>Required?}
    
    CHECK_TOOL -->|No| DIRECT_RESPONSE[Direct AI Response]
    CHECK_TOOL -->|Yes| ROUTE_TOOL[Route to Tool]
    
    ROUTE_TOOL --> TOOL_CATEGORY{Tool Category}
    
    TOOL_CATEGORY -->|Communication| COMM_TOOLS[Email/Telegram/Calendar]
    TOOL_CATEGORY -->|Information| INFO_TOOLS[Weather/Search/Memory]
    TOOL_CATEGORY -->|Generation| GEN_TOOLS[PDF/Word/PPT/Excel/Image/Website]
    TOOL_CATEGORY -->|File Operations| FILE_TOOLS[Convert/Compress/Open]
    TOOL_CATEGORY -->|System| SYS_TOOLS[Automation/Screenshot/Power]
    TOOL_CATEGORY -->|Data| DATA_TOOLS[Contacts/Memory/File Access]
    
    COMM_TOOLS --> EXECUTE[Execute Tool Function]
    INFO_TOOLS --> EXECUTE
    GEN_TOOLS --> EXECUTE
    FILE_TOOLS --> EXECUTE
    SYS_TOOLS --> EXECUTE
    DATA_TOOLS --> EXECUTE
    
    EXECUTE --> STORE{Store Result?}
    STORE -->|Yes| DATABASE[(Database/Data<br/>Storage)]
    STORE -->|No| LOG[Log Action]
    DATABASE --> LOG
    
    LOG --> RESULT[Tool Result]
    RESULT --> BRAIN
    
    DIRECT_RESPONSE --> OUTPUT[Format Output]
    
    OUTPUT --> OUTPUT_TYPE{Output Type?}
    OUTPUT_TYPE -->|Voice| AUDIO_OUT[Audio Response via PyAudio]
    OUTPUT_TYPE -->|UI| WS_BROADCAST[WebSocket Broadcast]
    OUTPUT_TYPE -->|Both| BOTH_OUT[Audio + UI Sync]
    
    AUDIO_OUT --> END[User Receives Response]
    WS_BROADCAST --> END
    BOTH_OUT --> END
    
    style BRAIN fill:#4CAF50,stroke:#2E7D32,stroke-width:4px
    style GEMINI_STREAM fill:#2196F3,stroke:#1565C0,stroke-width:3px
    style EXECUTE fill:#FF9800,stroke:#E65100,stroke-width:3px
    style DATABASE fill:#795548,stroke:#4E342E,stroke-width:3px
```

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph "Input Layer"
        I1[Microphone]
        I2[Web Browser]
        I3[Terminal]
    end
    
    subgraph "Processing Layer"
        P1[main.py<br/>Entry Point]
        P2[Audio Loop<br/>Voice Processing]
        P3[FastAPI<br/>Web Server]
        P4[WebSocket<br/>Real-time Comm]
    end
    
    subgraph "Intelligence Layer"
        AI1[brain.py<br/>Gemini Integration]
        AI2[Tool Router<br/>Function Dispatcher]
        AI3[Memory Handler<br/>Context Manager]
    end
    
    subgraph "Tool Execution Layer"
        T1[Communication<br/>Tools]
        T2[Document<br/>Generation]
        T3[System<br/>Automation]
        T4[Information<br/>Retrieval]
    end
    
    subgraph "Storage Layer"
        S1[JSON Databases]
        S2[Generated Files]
        S3[Logs & History]
        S4[OAuth Tokens]
    end
    
    subgraph "External APIs"
        E1[Google Cloud]
        E2[Telegram]
        E3[AI Services]
        E4[Search APIs]
    end
    
    I1 --> P1
    I2 --> P1
    I3 --> P1
    
    P1 --> P2
    P1 --> P3
    P3 --> P4
    
    P2 --> AI1
    P4 --> AI1
    
    AI1 --> AI2
    AI1 --> AI3
    AI2 --> AI3
    
    AI2 --> T1
    AI2 --> T2
    AI2 --> T3
    AI2 --> T4
    
    T1 --> S1
    T2 --> S2
    T3 --> S3
    T1 --> S4
    
    T1 --> E1
    T1 --> E2
    T2 --> E3
    T4 --> E4
    
    style AI1 fill:#4CAF50,stroke:#2E7D32,stroke-width:4px
    style P1 fill:#FF9800,stroke:#E65100,stroke-width:3px
    style T1 fill:#2196F3,stroke:#1565C0,stroke-width:2px
    style T2 fill:#2196F3,stroke:#1565C0,stroke-width:2px
    style T3 fill:#2196F3,stroke:#1565C0,stroke-width:2px
    style T4 fill:#2196F3,stroke:#1565C0,stroke-width:2px
```

## Authentication & Security Flow

```mermaid
sequenceDiagram
    participant User
    participant Friday
    participant OAuth
    participant Google
    participant Services
    
    User->>Friday: Start Application
    Friday->>OAuth: Check Token (gmail_token.json)
    
    alt Token Exists & Valid
        OAuth->>Friday: Load Credentials
        Friday->>Services: Initialize Services
    else Token Missing/Expired
        OAuth->>User: Open Browser for Auth
        User->>Google: Authorize Permissions
        Google->>OAuth: Return Access Token
        OAuth->>Friday: Save Token
        Friday->>Services: Initialize Services
    end
    
    Services->>User: Ready for Commands
    
    User->>Friday: Request Calendar/Email Action
    Friday->>Google: API Call with Token
    Google->>Friday: Return Data
    Friday->>User: Display Result
```

## Tool Execution Flow

```mermaid
stateDiagram-v2
    [*] --> Idle: Application Running
    
    Idle --> UserInput: User Makes Request
    
    UserInput --> GeminiProcessing: Send to Gemini AI
    
    GeminiProcessing --> ToolDetection: Analyze Intent
    
    ToolDetection --> DirectResponse: No Tool Needed
    ToolDetection --> ToolSelection: Tool Required
    
    ToolSelection --> WeatherTool: Weather Query
    ToolSelection --> EmailTool: Email Operation
    ToolSelection --> CalendarTool: Calendar Operation
    ToolSelection --> TelegramTool: Telegram Message
    ToolSelection --> DocumentTool: Generate Document
    ToolSelection --> ImageTool: Generate Image
    ToolSelection --> SearchTool: Internet Search
    ToolSelection --> AutomationTool: System Control
    ToolSelection --> FileTool: File Operation
    
    WeatherTool --> ToolExecution
    EmailTool --> ToolExecution
    CalendarTool --> ToolExecution
    TelegramTool --> ToolExecution
    DocumentTool --> ToolExecution
    ImageTool --> ToolExecution
    SearchTool --> ToolExecution
    AutomationTool --> ToolExecution
    FileTool --> ToolExecution
    
    ToolExecution --> Success: Operation Complete
    ToolExecution --> Error: Operation Failed
    
    Success --> Logging: Log Result
    Error --> Logging: Log Error
    
    Logging --> ResponseGeneration: Create Response
    DirectResponse --> ResponseGeneration
    
    ResponseGeneration --> OutputType: Format Output
    
    OutputType --> VoiceOutput: Audio Response
    OutputType --> UIOutput: WebSocket/UI Update
    OutputType --> BothOutput: Audio + UI
    
    VoiceOutput --> UserReceives
    UIOutput --> UserReceives
    BothOutput --> UserReceives
    
    UserReceives --> MemoryUpdate: Save to Memory
    MemoryUpdate --> Idle: Ready for Next Command
    
    Idle --> [*]: Application Closed
```

## Module Dependency Graph

```mermaid
graph TD
    MAIN[main.py<br/>Entry Point] --> BRAIN[brain.py<br/>Core Intelligence]
    MAIN --> LOGGER[logger.py<br/>Logging System]
    MAIN --> MEMORY[memory_handler.py<br/>Memory Management]
    
    BRAIN --> ALL_MODULES{All Backend<br/>Modules}
    
    ALL_MODULES --> WEATHER[weather.py]
    ALL_MODULES --> EMAIL[email_handler.py]
    ALL_MODULES --> CALENDAR[calendar_handler.py]
    ALL_MODULES --> TELEGRAM[telegram_handler.py]
    ALL_MODULES --> CONTACTS[contacts_manager.py]
    ALL_MODULES --> IMAGE[ImageGeneration.py]
    ALL_MODULES --> PDF[PDFGenerator.py]
    ALL_MODULES --> WORD[WordGenerator.py]
    ALL_MODULES --> PPT[PPTGenerator.py]
    ALL_MODULES --> EXCEL[ExcelGenerator.py]
    ALL_MODULES --> WEBSITE[WebsiteGenerator.py]
    ALL_MODULES --> CONVERT[FileConverter.py]
    ALL_MODULES --> COMPRESS[SmartCompressor.py]
    ALL_MODULES --> AUTO[Automation.py]
    ALL_MODULES --> LLM[llm_handler.py]
    
    EMAIL --> LOGGER
    CALENDAR --> LOGGER
    TELEGRAM --> LOGGER
    CONTACTS --> LOGGER
    IMAGE --> LOGGER
    PDF --> LOGGER
    WORD --> LOGGER
    PPT --> LOGGER
    EXCEL --> LOGGER
    WEBSITE --> LOGGER
    CONVERT --> LOGGER
    COMPRESS --> LOGGER
    
    EMAIL --> GOOGLE_API[Google APIs]
    CALENDAR --> GOOGLE_API
    TELEGRAM --> TELEGRAM_API[Telegram API]
    IMAGE --> HF_API[Hugging Face]
    WEATHER --> WEATHER_API[OpenWeather]
    
    PDF --> LLM
    WORD --> LLM
    PPT --> LLM
    EXCEL --> LLM
    WEBSITE --> LLM
    
    LLM --> GROQ[Groq API]
    BRAIN --> GEMINI[Gemini API]
    BRAIN --> MEM0[Mem0 Memory]
    BRAIN --> TAVILY[Tavily Search]
    
    style MAIN fill:#FF9800,stroke:#E65100,stroke-width:4px
    style BRAIN fill:#4CAF50,stroke:#2E7D32,stroke-width:4px
    style LOGGER fill:#9E9E9E,stroke:#616161,stroke-width:2px
```

## WebSocket Communication Flow

```mermaid
sequenceDiagram
    participant Browser as Web Browser
    participant WS as WebSocket Server
    participant Brain as Gemini Brain
    participant Tools as Backend Tools
    participant Storage as Data Storage
    
    Browser->>WS: Connect WebSocket
    WS->>Browser: Connection Accepted
    
    Browser->>WS: ping (keep-alive)
    WS->>Browser: pong
    
    Browser->>WS: send_message: "Schedule meeting"
    WS->>Brain: Process Message
    Brain->>Brain: Analyze with Gemini
    Brain->>Tools: calendar_create_event()
    Tools->>Storage: Save to Database
    Storage->>Tools: Success
    Tools->>Brain: Event Created
    Brain->>WS: Response Ready
    WS->>Browser: new_message: "Event created"
    
    Browser->>WS: get_weather: "London"
    WS->>Brain: Execute Tool
    Brain->>Tools: get_weather("London")
    Tools->>Brain: Weather Data
    Brain->>WS: Weather Response
    WS->>Browser: weather_update: {...}
    
    Browser->>WS: take_screenshot
    WS->>Tools: take_screenshot()
    Tools->>Storage: Save Screenshot
    Tools->>WS: Screenshot Path
    WS->>Browser: screenshot_taken: {...}
    
    loop System Metrics (every 2s)
        WS->>Browser: system_metrics: {cpu, memory, network}
    end
    
    Browser->>WS: Disconnect
    WS->>Browser: Connection Closed
```

## File Generation Pipeline

```mermaid
flowchart TD
    START[User Request:<br/>"Generate X document on Y"] --> BRAIN[Gemini Brain<br/>Parse Request]
    
    BRAIN --> DETERMINE{Document<br/>Type?}
    
    DETERMINE -->|PDF| PDF_GEN[PDFGenerator.py]
    DETERMINE -->|Word| WORD_GEN[WordGenerator.py]
    DETERMINE -->|PowerPoint| PPT_GEN[PPTGenerator.py]
    DETERMINE -->|Excel| EXCEL_GEN[ExcelGenerator.py]
    DETERMINE -->|Website| WEB_GEN[WebsiteGenerator.py]
    DETERMINE -->|Image| IMG_GEN[ImageGeneration.py]
    
    PDF_GEN --> RESEARCH{Research<br/>Content?}
    WORD_GEN --> RESEARCH
    PPT_GEN --> RESEARCH
    EXCEL_GEN --> RESEARCH
    WEB_GEN --> RESEARCH
    
    RESEARCH -->|Yes| INTERNET[Internet Search<br/>via Tavily]
    RESEARCH -->|No| LLM[LLM Generation<br/>via Groq/Gemini]
    
    INTERNET --> LLM
    
    LLM --> FORMAT[Format Content<br/>for Document Type]
    
    FORMAT --> CREATE[Create Document<br/>with Libraries]
    
    CREATE --> LIBS{Library Used}
    
    LIBS -->|PDF| REPORTLAB[ReportLab]
    LIBS -->|Word| PYTHON_DOCX[python-docx]
    LIBS -->|PPT| PYTHON_PPTX[python-pptx]
    LIBS -->|Excel| OPENPYXL[openpyxl]
    LIBS -->|Website| HTML_GEN[HTML/CSS/JS]
    LIBS -->|Image| STABLE_DIFF[Stable Diffusion<br/>via Hugging Face]
    
    REPORTLAB --> SAVE[Save to Data/<br/>GeneratedDocuments/]
    PYTHON_DOCX --> SAVE
    PYTHON_PPTX --> SAVE
    OPENPYXL --> SAVE
    HTML_GEN --> SAVE_WEB[Save to Data/<br/>GeneratedWebsites/]
    STABLE_DIFF --> SAVE_IMG[Save to Data/<br/>GeneratedImages/]
    
    IMG_GEN --> STABLE_DIFF
    
    SAVE --> LOG[Log Generation]
    SAVE_WEB --> LOG
    SAVE_IMG --> LOG
    
    LOG --> RESPONSE[Return File Path<br/>to Brain]
    
    RESPONSE --> USER_ACTION{User<br/>Action?}
    
    USER_ACTION -->|Open| OPEN[Open with<br/>Default App]
    USER_ACTION -->|Send| SEND[Send via<br/>Email/Telegram]
    USER_ACTION -->|Convert| CONVERT[Convert Format]
    USER_ACTION -->|Compress| COMPRESS[Smart Compress]
    USER_ACTION -->|Done| COMPLETE[Complete]
    
    OPEN --> COMPLETE
    SEND --> COMPLETE
    CONVERT --> COMPLETE
    COMPRESS --> COMPLETE
    
    style BRAIN fill:#4CAF50,stroke:#2E7D32,stroke-width:3px
    style LLM fill:#2196F3,stroke:#1565C0,stroke-width:2px
    style SAVE fill:#795548,stroke:#4E342E,stroke-width:2px
```

---

## API Documentation

For comprehensive API documentation including all REST endpoints, WebSocket messages, and usage examples, see:

👉 **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

Quick summary:
- **21+ REST API endpoints** for system control, file management, contacts, etc.
- **WebSocket API** for real-time bidirectional communication
- **Base URL:** `http://localhost:8000`
- **Framework:** FastAPI with async/await

## Key Architecture Principles

### 1. **Modular Design**
- Each backend module is self-contained
- Clear separation of concerns
- Easy to add new tools/features

### 2. **Unified Intelligence**
- Single Gemini Brain handles all routing
- Consistent tool calling interface
- Memory context shared across all operations

### 3. **Multi-Modal Input**
- Voice (PyAudio + Gemini Native Audio)
- Text (WebSocket + FastAPI)
- UI (React + Next.js)

### 4. **Shared Authentication**
- OAuth2 tokens shared across Google services
- Single authentication flow for Gmail + Calendar
- Secure token storage in Database/

### 5. **Real-Time Communication**
- WebSocket for instant UI updates
- Bi-directional data flow
- System metrics broadcasting

### 6. **Persistent Memory**
- Mem0 for long-term context
- JSON databases for contacts/chatlogs
- File system for generated content

### 7. **Error Resilience**
- Comprehensive logging
- API key rotation (15 Google + 10 Groq keys)
- Graceful degradation

### 8. **Extensibility**
- Easy to add new tools
- Plugin-like architecture
- Standardized tool interface

### 9. **RESTful & Real-time APIs**
- FastAPI for REST endpoints
- WebSocket for bidirectional communication
- CORS-enabled for frontend integration
- Comprehensive API documentation

---

**Generated:** January 11, 2026  
**Project:** Friday AI Assistant  
**Architecture Version:** 2.0  
**API Endpoints:** 21+ REST + WebSocket  
**Server:** FastAPI (port 8000)
