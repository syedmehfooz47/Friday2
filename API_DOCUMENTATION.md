# Friday AI Assistant - API Documentation

## 📡 REST API Server

**Base URL:** `http://localhost:8000`  
**Framework:** FastAPI with async/await  
**CORS:** Enabled for `localhost:3000` (Next.js UI)  
**Auto-Start:** Launches with main.py  
**Port:** 8000

## API Endpoints Overview

### **System & Health**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check with voice assistant status, WebSocket connections |
| GET | `/api/status` | Backend status, version, and timestamp |

**Health Check Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-11T14:30:00",
  "voice_assistant": "running",
  "voice_state": {
    "initialized": true,
    "is_muted": false,
    "assistant_speaking": false,
    "has_session": true
  },
  "ui_server": "running",
  "websocket_connections": 2
}
```

**Status Response:**
```json
{
  "status": "healthy",
  "server": "Friday Backend",
  "version": "2.0",
  "websocket_clients": 2,
  "timestamp": "2026-01-11T14:30:00"
}
```

### **Settings & Configuration**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settings` | Get all settings (API keys, contacts, models) |
| POST | `/api/settings/update` | Update environment variables |

**GET /api/settings Response:**
```json
{
  "username": "Boss",
  "assistantname": "Friday",
  "active_assistant": "Friday",
  "llm_provider": "Groq",
  "active_groq_api": "GROQ_API_KEY_1",
  "active_google_api": "GOOGLE_API_KEY_1",
  "api_keys": {
    "groq": [
      {
        "slot": "GROQ_API_KEY_1",
        "label": "Groq API Slot 1",
        "has_key": true,
        "is_active": true
      }
    ],
    "google": [
      {
        "slot": "GOOGLE_API_KEY_1",
        "label": "Google API Slot 1",
        "has_key": true,
        "is_active": true
      }
    ]
  },
  "models": {
    "Groq": "llama-3.3-70b-versatile",
    "Gemini": "gemini-2.0-flash-exp",
    "Ollama": "llama3.2",
    "Cohere": "command-r-plus"
  },
  "contacts": [...]
}
```

**POST /api/settings/update Request:**
```json
{
  "key": "Username",
  "value": "Boss"
}
```

### **Chat Logs**

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/chatlogs` | Get chat history with pagination | `date`, `limit`, `offset` |
| GET | `/api/chatlogs/dates` | Get all dates with chatlogs | - |

**GET /api/chatlogs Response:**
```json
{
  "chatlogs": [
    {
      "role": "user",
      "content": "What's the weather?",
      "timestamp": 1736604600.123,
      "date": "2026-01-11"
    },
    {
      "role": "assistant",
      "content": "The weather is sunny...",
      "timestamp": 1736604601.456,
      "date": "2026-01-11"
    }
  ],
  "total": 150,
  "offset": 0,
  "limit": 100,
  "has_more": true
}
```

**Examples:**
```bash
GET /api/chatlogs?limit=50&offset=0
GET /api/chatlogs?date=2026-01-11&limit=100
```

### **System Control**

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/api/brightness` | Get screen brightness | - |
| POST | `/api/brightness` | Set screen brightness | `{"brightness": 75}` |
| POST | `/api/theme` | Change Windows theme | `{"mode": "dark"}` |

**Brightness Response:**
```json
{
  "brightness": 75
}
```

**Set Brightness Request:**
```json
{
  "brightness": 80
}
```

**Change Theme Request:**
```json
{
  "mode": "dark"  // or "light"
}
```

### **Voice/Mic Control**

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/api/mic-state` | Get current mic state | - |
| POST | `/api/mic-state` | Toggle mic mute/unmute | `{"is_muted": true}` |
| GET | `/api/mic-state/verify` | Verify state sync (file/memory/audio) | - |
| POST | `/api/stop-speaking` | Stop Friday from speaking | - |

**Mic State Response:**
```json
{
  "is_muted": false,
  "timestamp": 1736604600.123
}
```

**Set Mic State Response:**
```json
{
  "success": true,
  "is_muted": true,
  "requested": true,
  "verified": true,
  "timestamp": 1736604600.123
}
```

**Verify Mic State Response:**
```json
{
  "all_synced": true,
  "file_state": false,
  "memory_state": false,
  "audio_loop_state": false,
  "file_path": "E:/Friday/Friday2/Database/mute_state.txt",
  "timestamp": 1736604600.123
}
```

**Stop Speaking Response:**
```json
{
  "success": true,
  "stopped": true,
  "is_muted": false,
  "was_speaking": true,
  "timestamp": 1736604600.123
}
```

### **Assistant State**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assistant-state` | Check if assistant is speaking |

**Response:**
```json
{
  "is_speaking": true,
  "is_muted": false,
  "audio_loop_ready": true,
  "timestamp": 1736604600.123
}
```

### **Contacts Management**

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/api/contacts` | Add new contact | `{"names": ["John"], "phone": "123", "email": "john@example.com"}` |
| PUT | `/api/contacts/{name}` | Update contact | `{"phone": "456", "email": "new@example.com"}` |
| DELETE | `/api/contacts/{name}` | Delete contact | - |

**Add Contact Request:**
```json
{
  "names": ["John Doe", "Johnny"],
  "phone": "+1234567890",
  "email": "john@example.com",
  "telegram_id": "johndoe123"
}
```

**Add Contact Response:**
```json
{
  "status": "success",
  "message": "Contact added successfully",
  "contacts": [...]
}
```

**Update Contact Request:**
```json
{
  "names": ["John Doe Updated"],
  "phone": "+9876543210",
  "email": "newemail@example.com",
  "telegram_id": "johndoe456"
}
```

### **File Management**

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/api/generated-files` | List all generated/converted files | - |
| POST | `/api/open-file` | Open file with system default app | `{"path": "E:/path/to/file.pdf"}` |

**Generated Files Response:**
```json
{
  "files": [
    {
      "name": "document.pdf",
      "path": "E:/Friday/Friday2/Data/GeneratedDocuments/document.pdf",
      "size": 102400,
      "modified": "2026-01-11T14:25:00"
    },
    {
      "name": "image.png",
      "path": "E:/Friday/Friday2/Data/GeneratedImages/image.png",
      "size": 256000,
      "modified": "2026-01-11T14:20:00"
    }
  ],
  "count": 2
}
```

**Open File Request:**
```json
{
  "path": "E:/Friday/Friday2/Data/GeneratedDocuments/document.pdf"
}
```

**Open File Response:**
```json
{
  "success": true,
  "path": "E:/Friday/Friday2/Data/GeneratedDocuments/document.pdf"
}
```

### **Weather**

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/weather` | Get weather for city | `city` (default: Bengaluru) |

**Example:**
```bash
GET /api/weather?city=London
```

**Response:**
```json
{
  "status": "success",
  "city": "London",
  "temperature": 15,
  "description": "Partly cloudy",
  "humidity": 65,
  "wind_speed": 12
}
```

## 🔌 WebSocket API

**Endpoint:** `ws://localhost:8000/ws`

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to Friday');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from Friday');
};
```

### WebSocket Message Types

#### **Client → Server Messages**

| Type | Payload | Description |
|------|---------|-------------|
| `ping` | `{}` | Keep-alive heartbeat |
| `get_chatlogs` | `{}` | Request chat history |
| `send_message` | `{message: string}` | Send chat message to AI |
| `get_weather` | `{city: string}` | Get weather data |
| `set_brightness` | `{brightness: number}` | Set screen brightness (0-100) |
| `change_theme` | `{mode: "dark"\|"light"}` | Change Windows theme |
| `take_screenshot` | `{}` | Take screenshot |
| `open_app` | `{app_name: string}` | Open application |
| `close_app` | `{app_name: string}` | Close application |
| `google_search` | `{query: string}` | Perform Google search |
| `open_website` | `{url: string}` | Open website in browser |
| `generate_pdf` | `{title: string, content: string}` | Generate PDF document |
| `generate_word` | `{title: string, content: string}` | Generate Word document |
| `generate_ppt` | `{title: string, slides: array}` | Generate PowerPoint |
| `generate_excel` | `{filename: string, data: array}` | Generate Excel spreadsheet |
| `generate_image` | `{prompt: string}` | Generate AI image |
| `convert_file` | `{input_path: string, output_format: string}` | Convert file format |
| `send_email` | `{to: string, subject: string, body: string, attachments?: array}` | Send email |
| `send_telegram` | `{chat_id: string, message: string}` | Send Telegram message |
| `add_contact` | `{name: string, phone?: string, email?: string, alias?: string}` | Add contact |
| `find_contact` | `{name: string}` | Find contact by name |
| `recall_memory` | `{query: string}` | Query long-term memory |
| `toggle_mic` | `{is_muted: boolean}` | Toggle mic mute state |
| `get_state` | `{}` | Get voice assistant state |
| `stop_jarvis` | `{}` | Stop assistant from speaking |

#### **Server → Client Messages**

| Type | Payload | Description |
|------|---------|-------------|
| `pong` | `{}` | Heartbeat response |
| `chatlogs_response` | `{chatlogs: array}` | Chat history data |
| `new_message` | `{role: string, content: string, timestamp: number}` | New chat message |
| `weather_update` | `{...weatherData}` | Weather information |
| `brightness_changed` | `{brightness: number, success: boolean}` | Brightness updated |
| `theme_changed` | `{theme: string, success: boolean}` | Theme changed |
| `screenshot_taken` | `{file_path: string, status: string}` | Screenshot saved |
| `app_opened` | `{message: string, status: string}` | Application opened |
| `app_closed` | `{message: string, status: string}` | Application closed |
| `search_results` | `{results: array}` | Search results |
| `website_opened` | `{url: string, status: string}` | Website opened |
| `pdf_generated` | `{file_path: string, status: string}` | PDF created |
| `word_generated` | `{file_path: string, status: string}` | Word document created |
| `ppt_generated` | `{file_path: string, status: string}` | PowerPoint created |
| `excel_generated` | `{file_path: string, status: string}` | Excel created |
| `image_generated` | `{image_paths: array, status: string}` | Images created |
| `file_converted` | `{file_path: string, status: string}` | File converted |
| `email_sent` | `{status: string, message: string}` | Email sent |
| `telegram_sent` | `{status: string, message: string}` | Telegram sent |
| `contact_added` | `{status: string, contact: object}` | Contact added |
| `contact_found` | `{status: string, contact: object}` | Contact found |
| `memory_recalled` | `{context: string}` | Memory context |
| `mic_toggled` | `{is_muted: boolean}` | Mic state changed |
| `mic_toggle_failed` | `{error: string, requested: boolean, actual: boolean}` | Mic toggle failed |
| `state_response` | `{is_muted: boolean}` | Voice state response |
| `jarvis_stopped` | `{success: boolean}` | Assistant stopped |
| `stop_failed` | `{error: string, reason: string}` | Stop failed |
| `system_metrics` | `{cpuUsage: number, memoryUsage: number, networkStatus: number}` | System metrics (broadcast every 2s) |
| `setting_updated` | `{key: string, value: string}` | Setting updated |

### WebSocket Examples

#### Send Chat Message

```javascript
ws.send(JSON.stringify({
  type: 'send_message',
  payload: {
    message: 'What is the weather in Paris?'
  }
}));
```

#### Generate PDF

```javascript
ws.send(JSON.stringify({
  type: 'generate_pdf',
  payload: {
    title: 'My Report',
    content: 'This is the content of my report...'
  }
}));
```

#### Toggle Mic

```javascript
ws.send(JSON.stringify({
  type: 'toggle_mic',
  payload: {
    is_muted: true
  }
}));
```

#### Listen for Responses

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'new_message':
      console.log('AI:', data.payload.content);
      break;
      
    case 'pdf_generated':
      console.log('PDF created at:', data.payload.file_path);
      break;
      
    case 'mic_toggled':
      console.log('Mic muted:', data.payload.is_muted);
      break;
      
    case 'system_metrics':
      console.log('CPU:', data.payload.cpuUsage);
      console.log('Memory:', data.payload.memoryUsage);
      break;
  }
};
```

## 📊 Usage Examples

### cURL Examples

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Get Settings
```bash
curl http://localhost:8000/api/settings
```

#### Toggle Mic
```bash
curl -X POST http://localhost:8000/api/mic-state \
  -H "Content-Type: application/json" \
  -d '{"is_muted": true}'
```

#### Get Weather
```bash
curl "http://localhost:8000/api/weather?city=London"
```

#### Get Generated Files
```bash
curl http://localhost:8000/api/generated-files
```

#### Add Contact
```bash
curl -X POST http://localhost:8000/api/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "names": ["Alice Johnson", "Ali"],
    "phone": "+1234567890",
    "email": "alice@example.com",
    "telegram_id": "alicejohnson"
  }'
```

#### Update Contact
```bash
curl -X PUT http://localhost:8000/api/contacts/Alice \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+9876543210",
    "email": "newalice@example.com"
  }'
```

#### Delete Contact
```bash
curl -X DELETE http://localhost:8000/api/contacts/Alice
```

#### Get Chat Logs
```bash
curl "http://localhost:8000/api/chatlogs?limit=50&offset=0"
```

#### Get Chat Logs by Date
```bash
curl "http://localhost:8000/api/chatlogs?date=2026-01-11"
```

#### Update Brightness
```bash
curl -X POST http://localhost:8000/api/brightness \
  -H "Content-Type: application/json" \
  -d '{"brightness": 80}'
```

#### Change Theme
```bash
curl -X POST http://localhost:8000/api/theme \
  -H "Content-Type: application/json" \
  -d '{"mode": "dark"}'
```

#### Stop Assistant Speaking
```bash
curl -X POST http://localhost:8000/api/stop-speaking
```

### JavaScript/TypeScript Examples

#### Fetch API
```javascript
// Get settings
const settings = await fetch('http://localhost:8000/api/settings')
  .then(res => res.json());
console.log(settings);

// Toggle mic
const micState = await fetch('http://localhost:8000/api/mic-state', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ is_muted: false })
}).then(res => res.json());
console.log(micState);

// Get weather
const weather = await fetch('http://localhost:8000/api/weather?city=Tokyo')
  .then(res => res.json());
console.log(weather);
```

#### WebSocket Client
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to Friday');
  
  // Send chat message
  ws.send(JSON.stringify({
    type: 'send_message',
    payload: { message: 'Hello Friday!' }
  }));
  
  // Keep alive
  setInterval(() => {
    ws.send(JSON.stringify({ type: 'ping', payload: {} }));
  }, 30000);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'new_message') {
    console.log('Friday:', data.payload.content);
  }
  
  if (data.type === 'system_metrics') {
    updateSystemMetrics(data.payload);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
  // Reconnect logic here
};
```

### Python Examples

#### Using requests
```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Get settings
response = requests.get(f"{BASE_URL}/api/settings")
settings = response.json()
print(f"Assistant: {settings['assistantname']}")
print(f"Username: {settings['username']}")

# Toggle mic
response = requests.post(
    f"{BASE_URL}/api/mic-state",
    json={"is_muted": False}
)
mic_state = response.json()
print(f"Mic muted: {mic_state['is_muted']}")

# Get weather
response = requests.get(f"{BASE_URL}/api/weather", params={"city": "Tokyo"})
weather = response.json()
print(f"Weather in Tokyo: {weather}")

# Add contact
response = requests.post(
    f"{BASE_URL}/api/contacts",
    json={
        "names": ["Bob Smith", "Bobby"],
        "phone": "+1234567890",
        "email": "bob@example.com"
    }
)
result = response.json()
print(f"Contact added: {result['status']}")

# Get generated files
response = requests.get(f"{BASE_URL}/api/generated-files")
files = response.json()
print(f"Found {files['count']} generated files")
for file in files['files'][:5]:
    print(f"  - {file['name']} ({file['size']} bytes)")
```

#### Using websockets
```python
import asyncio
import websockets
import json

async def friday_client():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "type": "send_message",
            "payload": {"message": "What's the weather?"}
        }))
        
        # Receive response
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data['type']}")
            
            if data['type'] == 'new_message':
                print(f"Friday: {data['payload']['content']}")

asyncio.run(friday_client())
```

## 🔐 Authentication & Security

- **CORS:** Configured for `localhost:3000` (Next.js frontend)
- **No API Keys Required:** Local access only
- **OAuth Tokens:** Stored securely in `Database/` folder
- **File Access:** Restricted to project directories
- **Logging:** All API calls logged for debugging

## 📝 Response Format

All API responses follow this general format:

**Success Response:**
```json
{
  "status": "success",
  "data": {...},
  "message": "Operation completed"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": "Error description",
  "message": "User-friendly error message"
}
```

## 🚀 Getting Started

### Start the API Server

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run Friday (starts API server automatically)
python main.py
```

The API server will start on `http://localhost:8000`

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get status
curl http://localhost:8000/api/status
```

### Connect Frontend

```javascript
// REST API
const API_URL = 'http://localhost:8000';

// WebSocket
const WS_URL = 'ws://localhost:8000/ws';
```

## 📚 Additional Resources

- **Architecture Flowchart:** See [ARCHITECTURE_FLOWCHART.md](ARCHITECTURE_FLOWCHART.md)
- **Calendar Integration:** See [CALENDAR_INTEGRATION.md](CALENDAR_INTEGRATION.md)
- **Main Documentation:** See [README.md](README.md)

---

**API Version:** 2.0  
**Last Updated:** January 11, 2026  
**Total Endpoints:** 21+ REST + WebSocket  
**Server:** FastAPI (Python)  
**Port:** 8000
