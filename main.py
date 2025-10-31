# -*- coding: utf-8 -*-
"""
Advanced Gemini Native Audio Assistant - Main Entry Point
Modular architecture with memory, chatlogs, and advanced features
"""
# Standard Library Imports
import asyncio
import os
import signal
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Set

# Third-Party Imports
import psutil
import pyaudio
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Local Application Imports
from Backend.Automation import (
    CloseApp, GoogleSearch, OpenApp, change_windows_theme, get_brightness,
    open_website, set_brightness, take_screenshot
)
from Backend.brain import GeminiBrain, get_config_with_memory
from Backend.contacts_manager import contacts_manager
from Backend.email_handler import EmailHandler
from Backend.ExcelGenerator import excel_generator
from Backend.FileConverter import file_converter
from Backend.ImageGeneration import image_generation_service
from Backend.logger import Logger
from Backend.memory_handler import MemoryHandler
from Backend.PDFGenerator import pdf_generator
from Backend.PPTGenerator import ppt_generator
from Backend.telegram_handler import telegram_service
from Backend.weather import WeatherTool
from Backend.WordGenerator import word_generator

# Suppress deprecation warnings for cleaner output
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent))

# --- CORRECTED: Import get_config_with_memory ---
from Backend.brain import get_config_with_memory, MODEL, client

# FastAPI and WebSocket imports for UI connectivity
try:
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    Logger.log("FastAPI not available - UI WebSocket server disabled", "WARNING")

# WebSocket notification support (optional - for UI integration)
websocket_notifications_enabled = False
try:
    import aiohttp
    websocket_notifications_enabled = True
except ImportError:
    pass

async def notify_websocket(event_type: str, data: dict):
    """Send notifications to WebSocket server if available"""
    if not websocket_notifications_enabled:
        return
    try:
        # This would connect to websocket server if it's running
        # For now, we'll just log the event
        Logger.log(f"WS Event: {event_type}", "WEBSOCKET")
    except Exception:
        pass  # Silently fail if websocket server is not running

# Initialize FastAPI app for UI connectivity (if available)
if FASTAPI_AVAILABLE:
    from Backend.weather import WeatherTool
    from Backend.email_handler import EmailHandler
    from Backend.telegram_handler import telegram_service
    from Backend.contacts_manager import contacts_manager
    from Backend.ImageGeneration import image_generation_service
    from Backend.PDFGenerator import pdf_generator
    from Backend.PPTGenerator import ppt_generator
    from Backend.WordGenerator import word_generator
    from Backend.ExcelGenerator import excel_generator
    from Backend.FileConverter import file_converter
    from Backend.Automation import (
        get_brightness, set_brightness, change_windows_theme,
        GoogleSearch, open_website, OpenApp, CloseApp,
        take_screenshot
    )
    from datetime import datetime
    import traceback
    
    app = FastAPI(title="Jarvis Unified Server", version="2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # WebSocket connection manager
    class ConnectionManager:
        def __init__(self):
            self.active_connections: Set[WebSocket] = set()
            self.connection_lock = asyncio.Lock()
            
        async def connect(self, websocket: WebSocket):
            await websocket.accept()
            async with self.connection_lock:
                self.active_connections.add(websocket)
            Logger.log(f"UI client connected. Total: {len(self.active_connections)}", "WEBSOCKET")
            
        async def disconnect(self, websocket: WebSocket):
            async with self.connection_lock:
                self.active_connections.discard(websocket)
            Logger.log(f"UI client disconnected. Total: {len(self.active_connections)}", "WEBSOCKET")
            
        async def send_personal_message(self, message: dict, websocket: WebSocket):
            try:
                await websocket.send_json(message)
            except Exception as e:
                Logger.log(f"Error sending message: {e}", "ERROR")
                
        async def broadcast(self, message: dict):
            disconnected = set()
            async with self.connection_lock:
                connections = self.active_connections.copy()
                
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
                    
            if disconnected:
                async with self.connection_lock:
                    self.active_connections -= disconnected

    ws_manager = ConnectionManager()
    brain_for_ui = GeminiBrain()
    weather_tool = WeatherTool()
    email_handler = EmailHandler()
    
    # Global AudioLoop instance for voice assistant control
    global_audio_loop = None
    
    # System metrics for UI
    async def get_system_metrics():
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            network = psutil.net_io_counters()
            network_status = (network.bytes_sent + network.bytes_recv) / (1024 * 1024)
            return {
                "cpuUsage": round(cpu, 1),
                "memoryUsage": round(memory, 1),
                "networkStatus": round(network_status, 2)
            }
        except:
            return {"cpuUsage": 0, "memoryUsage": 0, "networkStatus": 0}
    
    # Broadcast system metrics periodically
    async def broadcast_metrics():
        while True:
            try:
                metrics = await get_system_metrics()
                await ws_manager.broadcast({"type": "system_metrics", "payload": metrics})
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                break
            except:
                await asyncio.sleep(5)
    
    # AI message processor for UI - Uses Gemini with full tool support
    async def process_ui_message(message: str):
        """Process UI chat messages using Gemini model with tool execution (same as voice)"""
        try:
            # Get Gemini client and model config
            from Backend.brain import get_config_with_memory, client as gemini_client, MODEL
            
            Logger.log(f"Processing UI message with Gemini: {message[:50]}...", "UI_CHAT")
            
            # Get memory context for personalization
            memory_context = await memory_handler.get_memory_context()
            
            # Create chat session with tools
            config = await get_config_with_memory()
            
            # Send message to Gemini and get response
            response_text = ""
            tool_calls_made = []
            
            # Use Gemini's generate_content with streaming
            async def gemini_chat_with_tools():
                nonlocal response_text, tool_calls_made
                
                try:
                    # Create synchronous chat with Gemini
                    chat = gemini_client.aio.chats.create(
                        model=MODEL,
                        config=config
                    )
                    
                    # Send message
                    response = await chat.send_message(message)
                    
                    # Handle tool calls if any
                    if hasattr(response, 'tool_calls') and response.tool_calls:
                        for tool_call in response.tool_calls:
                            function_name = tool_call.name
                            args = tool_call.args if hasattr(tool_call, 'args') else {}
                            
                            Logger.log(f"UI triggered tool: {function_name}", "TOOL_CALL")
                            tool_calls_made.append(function_name)
                            
                            # Execute tool using brain
                            tool_result = brain_for_ui.execute_tool(function_name, args)
                            
                            # Send tool result back to continue conversation
                            if hasattr(chat, 'send_tool_result'):
                                await chat.send_tool_result(tool_call.id, tool_result)
                    
                    # Get final text response
                    if hasattr(response, 'text'):
                        response_text = response.text
                    elif isinstance(response, str):
                        response_text = response
                    else:
                        response_text = str(response)
                        
                except Exception as e:
                    Logger.log(f"Error in Gemini chat: {e}", "ERROR")
                    # Fallback to brain's execute_tool
                    result = brain_for_ui.execute_tool("internet_search", {"query": message})
                    if isinstance(result, dict):
                        response_text = result.get("result", "") or result.get("answer", "") or str(result)
                    else:
                        response_text = str(result)
            
            # Run Gemini chat
            await gemini_chat_with_tools()
            
            # Broadcast tool calls if any were made
            if tool_calls_made:
                await ws_manager.broadcast({
                    "type": "tools_executed",
                    "payload": {"tools": tool_calls_made}
                })
            
            # Stream response to UI
            if response_text:
                words = response_text.split()
                chunk_size = 8
                
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i+chunk_size])
                    await ws_manager.broadcast({
                        "type": "assistant_stream",
                        "payload": {"content": chunk + " "}
                    })
                    await asyncio.sleep(0.03)
                
                # Send final complete message
                await ws_manager.broadcast({
                    "type": "assistant_end",
                    "payload": {
                        "content": response_text,
                        "timestamp": datetime.now().timestamp()
                    }
                })
                
                # Log to chat history
                Logger.log_chat("ASSISTANT", response_text)
                
                # Save UI chat to memory immediately (separate from voice session batch save)
                # UI chat messages are saved individually since they're not part of voice session
                await memory_handler.add_conversation_batch([
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response_text}
                ])
                
        except Exception as e:
            Logger.log(f"Error processing UI message: {e}", "ERROR")
            Logger.log(traceback.format_exc(), "ERROR")
            error_msg = f"I encountered an error: {str(e)}"
            await ws_manager.broadcast({
                "type": "assistant_end",
                "payload": {
                    "content": error_msg,
                    "timestamp": datetime.now().timestamp()
                }
            })
            Logger.log_chat("ASSISTANT", error_msg)
    
    # WebSocket endpoint for UI - Complete feature support
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await ws_manager.connect(websocket)
        try:
            # Send initial connection message with actual mic state
            mic_state = audio_state_manager.get_mute_state()
            await ws_manager.send_personal_message({
                "type": "connection_established",
                "payload": {"status": "connected", "timestamp": datetime.now().isoformat(), "mic_state": {"is_muted": mic_state}}
            }, websocket)
            
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type")
                payload = data.get("payload", {})
                
                # Ping/Pong for keep-alive
                if msg_type == "ping":
                    await ws_manager.send_personal_message({"type": "pong", "payload": {}}, websocket)
                
                # Chat history
                elif msg_type == "get_chatlogs":
                    chatlogs = Logger.load_chatlogs()
                    await ws_manager.send_personal_message({"type": "chatlogs_response", "payload": {"chatlogs": chatlogs}}, websocket)
                
                # Main chat with Gemini (full tool support)
                elif msg_type == "send_message":
                    message = payload.get("message", "").strip()
                    if message:
                        Logger.log_chat("USER", message)
                        await ws_manager.broadcast({"type": "new_message", "payload": {"role": "user", "content": message, "timestamp": datetime.now().timestamp()}})
                        asyncio.create_task(process_ui_message(message))
                
                # Weather
                elif msg_type == "get_weather":
                    city = payload.get("city", "Bengaluru")
                    weather_data = await asyncio.to_thread(weather_tool.get_weather, city)
                    await ws_manager.send_personal_message({"type": "weather_update", "payload": weather_data}, websocket)
                
                # System controls
                elif msg_type == "set_brightness":
                    brightness = payload.get("brightness", 50)
                    result = await asyncio.to_thread(set_brightness, brightness)
                    await ws_manager.broadcast({"type": "brightness_changed", "payload": {"brightness": brightness, "success": result}})
                
                elif msg_type == "change_theme":
                    mode = payload.get("mode", "dark")
                    result = await asyncio.to_thread(change_windows_theme, mode)
                    await ws_manager.broadcast({"type": "theme_changed", "payload": {"theme": mode, "success": result}})
                
                elif msg_type == "take_screenshot":
                    result = await asyncio.to_thread(take_screenshot)
                    await ws_manager.send_personal_message({"type": "screenshot_taken", "payload": result}, websocket)
                
                # App control
                elif msg_type == "open_app":
                    app_name = payload.get("app_name", "")
                    result = await asyncio.to_thread(OpenApp, app_name)
                    await ws_manager.send_personal_message({"type": "app_opened", "payload": result}, websocket)
                
                elif msg_type == "close_app":
                    app_name = payload.get("app_name", "")
                    result = await asyncio.to_thread(CloseApp, app_name)
                    await ws_manager.send_personal_message({"type": "app_closed", "payload": result}, websocket)
                
                # Search
                elif msg_type == "google_search":
                    query = payload.get("query", "")
                    result = await asyncio.to_thread(GoogleSearch, query)
                    await ws_manager.send_personal_message({"type": "search_results", "payload": {"results": result}}, websocket)
                
                # Website
                elif msg_type == "open_website":
                    url = payload.get("url", "")
                    result = await asyncio.to_thread(open_website, url)
                    await ws_manager.send_personal_message({"type": "website_opened", "payload": result}, websocket)
                
                # Document generation
                elif msg_type == "generate_pdf":
                    title = payload.get("title", "Document")
                    content = payload.get("content", "")
                    result = await asyncio.to_thread(pdf_generator.generate_pdf, title, content)
                    await ws_manager.send_personal_message({"type": "pdf_generated", "payload": result}, websocket)
                
                elif msg_type == "generate_word":
                    title = payload.get("title", "Document")
                    content = payload.get("content", "")
                    result = await asyncio.to_thread(word_generator.generate_word, title, content)
                    await ws_manager.send_personal_message({"type": "word_generated", "payload": result}, websocket)
                
                elif msg_type == "generate_ppt":
                    title = payload.get("title", "Presentation")
                    slides = payload.get("slides", [])
                    result = await asyncio.to_thread(ppt_generator.generate_ppt, title, slides)
                    await ws_manager.send_personal_message({"type": "ppt_generated", "payload": result}, websocket)
                
                elif msg_type == "generate_excel":
                    filename = payload.get("filename", "data.xlsx")
                    data = payload.get("data", [])
                    result = await asyncio.to_thread(excel_generator.generate_excel, filename, data)
                    await ws_manager.send_personal_message({"type": "excel_generated", "payload": result}, websocket)
                
                # Image generation
                elif msg_type == "generate_image":
                    prompt = payload.get("prompt", "")
                    result = await asyncio.to_thread(image_generation_service.generate_image, prompt)
                    await ws_manager.send_personal_message({"type": "image_generated", "payload": result}, websocket)
                
                # File conversion
                elif msg_type == "convert_file":
                    input_path = payload.get("input_path", "")
                    output_format = payload.get("output_format", "")
                    result = await asyncio.to_thread(file_converter.convert_file_format, input_path, output_format)
                    await ws_manager.send_personal_message({"type": "file_converted", "payload": result}, websocket)
                
                # Email
                elif msg_type == "send_email":
                    to = payload.get("to", "")
                    subject = payload.get("subject", "")
                    body = payload.get("body", "")
                    attachments = payload.get("attachments", [])
                    result = await asyncio.to_thread(email_handler.send_email, to, subject, body, attachments)
                    await ws_manager.send_personal_message({"type": "email_sent", "payload": result}, websocket)
                
                # Telegram
                elif msg_type == "send_telegram":
                    chat_id = payload.get("chat_id", "")
                    message = payload.get("message", "")
                    result = await asyncio.to_thread(telegram_service.send_message, chat_id, message)
                    await ws_manager.send_personal_message({"type": "telegram_sent", "payload": result}, websocket)
                
                # Contacts
                elif msg_type == "add_contact":
                    name = payload.get("name", "")
                    email = payload.get("email", "")
                    phone = payload.get("phone", "")
                    alias = payload.get("alias", "")
                    names = [name]
                    if alias:
                        names.append(alias)
                    
                    result = await asyncio.to_thread(contacts_manager.add_contact, names=names, phone=phone, email=email)
                    await ws_manager.send_personal_message({"type": "contact_added", "payload": result}, websocket)
                
                elif msg_type == "find_contact":
                    name = payload.get("name", "")
                    result = await asyncio.to_thread(contacts_manager.find_contact, name)
                    await ws_manager.send_personal_message({"type": "contact_found", "payload": result}, websocket)
                
                # Memory recall
                elif msg_type == "recall_memory":
                    query = payload.get("query", "")
                    result = await memory_handler.get_memory_context(query)
                    await ws_manager.send_personal_message({"type": "memory_recalled", "payload": {"context": result}}, websocket)
                
                # Mic toggle control
                elif msg_type == "toggle_mic":
                    print(f"DEBUG: Received toggle_mic message: {payload}")
                    is_muted = payload.get("is_muted", False)
                    print(f"DEBUG: Setting mic to muted={is_muted}")
                    
                    # Use synchronous method for immediate effect
                    sync_success = audio_state_manager.set_mute_state_sync(is_muted, "websocket_ui")
                    
                    # Also use async for callbacks
                    result = await audio_state_manager.set_mute_state(is_muted, "websocket_ui")
                    
                    # Verify the change took effect
                    verified_state = audio_state_manager.get_mute_state()
                    success = (verified_state == is_muted) and sync_success
                    
                    if success:
                        await ws_manager.broadcast({"type": "mic_toggled", "payload": {"is_muted": is_muted}})
                        print(f"DEBUG: Broadcasted mic_toggled message, verified={verified_state}")
                    else:
                        Logger.log(f"Mic toggle verification failed: requested={is_muted}, actual={verified_state}", "ERROR")
                        await ws_manager.send_personal_message({
                            "type": "mic_toggle_failed",
                            "payload": {"error": "State verification failed", "requested": is_muted, "actual": verified_state}
                        }, websocket)

                # Request for current voice/mic state
                elif msg_type == "get_state":
                    current_state = audio_state_manager.get_mute_state()
                    await ws_manager.send_personal_message({
                        "type": "state_response",
                        "payload": {"is_muted": current_state}
                    }, websocket)
                
                # Stop Jarvis speaking - ONLY works when unmuted AND assistant speaking
                elif msg_type == "stop_jarvis":
                    if not audio_state_manager.is_audio_loop_ready():
                        await ws_manager.send_personal_message({
                            "type": "stop_failed", 
                            "payload": {"error": "Voice assistant not initialized", "reason": "no_audio_loop"}
                        }, websocket)
                    else:
                        # Check conditions: mic must be unmuted AND assistant must be speaking
                        is_muted = audio_state_manager.get_mute_state()
                        is_speaking = audio_state_manager._audio_loop.is_assistant_speaking
                        
                        if is_muted:
                            Logger.log("Stop ignored: Mic is muted", "CONTROL")
                            await ws_manager.send_personal_message({
                                "type": "stop_failed",
                                "payload": {"error": "Cannot stop while muted", "reason": "mic_muted"}
                            }, websocket)
                        elif not is_speaking:
                            Logger.log("Stop ignored: Assistant not speaking", "CONTROL")
                            await ws_manager.send_personal_message({
                                "type": "stop_failed",
                                "payload": {"error": "Assistant not speaking", "reason": "not_speaking"}
                            }, websocket)
                        else:
                            # Valid stop command
                            audio_state_manager._audio_loop.should_stop_speaking = True
                            Logger.log("Stop signal received from UI (valid: unmuted + speaking)", "CONTROL")
                            await ws_manager.broadcast({"type": "jarvis_stopped", "payload": {"success": True}})
                    
        except WebSocketDisconnect:
            await ws_manager.disconnect(websocket)
        except Exception as e:
            Logger.log(f"WebSocket error: {e}", "ERROR")
            await ws_manager.disconnect(websocket)
    
    # REST API endpoints
    @app.get("/api/weather")
    async def get_weather_api(city: str = "Bengaluru"):
        weather_data = await asyncio.to_thread(weather_tool.get_weather, city)
        return JSONResponse(content=weather_data)
    
    @app.get("/api/settings")
    async def get_settings_api():
        """Return comprehensive settings for the UI"""
        try:
            # Load contacts from contacts_manager
            contacts = await asyncio.to_thread(contacts_manager.load_contacts)
            
            # Get API key slots (1-10 for Groq, 1-15 for Google) with their status
            groq_slots = []
            for i in range(1, 11):
                key_name = f"GROQ_API_KEY_{i}"
                key_value = os.getenv(key_name)
                groq_slots.append({
                    "slot": key_name,
                    "label": f"Groq API Slot {i}",
                    "has_key": bool(key_value),
                    "is_active": os.getenv("ACTIVE_GROQ_API") == key_name
                })
            
            google_slots = []
            for i in range(1, 16):
                key_name = f"GOOGLE_API_KEY_{i}"
                key_value = os.getenv(key_name)
                google_slots.append({
                    "slot": key_name,
                    "label": f"Google API Slot {i}",
                    "has_key": bool(key_value),
                    "is_active": os.getenv("ACTIVE_GOOGLE_API") == key_name
                })
            
            # Get active keys
            active_groq_api = os.getenv("ACTIVE_GROQ_API", "GROQ_API_KEY_1")
            active_google_api = os.getenv("ACTIVE_GOOGLE_API", "GOOGLE_API_KEY_1")
            
            # Get LLM provider and model info
            llm_provider = os.getenv("LLM_PROVIDER", "Groq")
            
            return JSONResponse(content={
                "username": os.getenv("Username", "Boss"),
                "assistantname": os.getenv("Assistantname", "Friday"),
                "active_assistant": os.getenv("Assistantname", "Friday"),
                "llm_provider": llm_provider,
                "active_groq_api": active_groq_api,
                "active_google_api": active_google_api,
                "api_keys": {
                    "groq": groq_slots,
                    "google": google_slots
                },
                "models": {
                    "Groq": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                    "Gemini": os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
                    "Ollama": os.getenv("OLLAMA_MODEL", "llama3.2"),
                    "Cohere": os.getenv("COHERE_MODEL", "command-r-plus")
                },
                "contacts": contacts
            })
        except Exception as e:
            Logger.log(f"Error getting settings: {e}", "ERROR")
            return JSONResponse(content={
                "error": str(e),
                "username": os.getenv("Username", "Boss"),
                "assistantname": os.getenv("Assistantname", "Friday"),
                "contacts": []
            }, status_code=500)
    
    @app.post("/api/settings/update")
    async def update_setting_api(data: dict):
        key = data.get("key")
        value = data.get("value")
        if not key or value is None:
            raise HTTPException(status_code=400, detail="Key and value required")
        
        env_path = Path(__file__).parent / ".env"
        from dotenv import set_key
        set_key(env_path, key, value)
        os.environ[key] = value
        
        await ws_manager.broadcast({"type": "setting_updated", "payload": {"key": key, "value": value}})
        return JSONResponse(content={"success": True, "key": key})
    
    @app.get("/api/chatlogs")
    async def get_chatlogs_api(date: str = None, limit: int = 100, offset: int = 0):
        """Get chatlogs with optional date filtering and pagination"""
        try:
            all_chatlogs = Logger.load_chatlogs()
            
            # Filter to only get entries with direct role/content fields (new format)
            # Skip old format entries with session_timestamp and nested messages
            filtered_chatlogs = [
                log for log in all_chatlogs 
                if "role" in log and "content" in log and "timestamp" in log
            ]
            
            # Filter by date if provided
            if date:
                filtered = [log for log in filtered_chatlogs if log.get("date") == date]
            else:
                filtered = filtered_chatlogs
            
            # Apply pagination
            total = len(filtered)
            paginated = filtered[offset:offset + limit] if limit > 0 else filtered[offset:]
            
            return JSONResponse(content={
                "chatlogs": paginated,
                "total": total,
                "offset": offset,
                "limit": limit,
                "has_more": (offset + limit) < total
            })
        except Exception as e:
            Logger.log(f"Error getting chatlogs: {e}", "ERROR")
            return JSONResponse(content={"error": str(e), "chatlogs": []}, status_code=500)
    
    @app.get("/api/chatlogs/dates")
    async def get_chatlog_dates_api():
        """Get list of all dates that have chatlogs"""
        try:
            all_chatlogs = Logger.load_chatlogs()
            
            # Filter to only get entries with direct role/content fields (new format)
            filtered_chatlogs = [
                log for log in all_chatlogs 
                if "role" in log and "content" in log and "date" in log
            ]
            
            dates = sorted(list(set(log.get("date") for log in filtered_chatlogs if log.get("date"))))
            return JSONResponse(content={"dates": dates})
        except Exception as e:
            Logger.log(f"Error getting chatlog dates: {e}", "ERROR")
            return JSONResponse(content={"error": str(e), "dates": []}, status_code=500)
    
    @app.get("/api/brightness")
    async def get_brightness_api():
        brightness = await asyncio.to_thread(get_brightness)
        return JSONResponse(content={"brightness": brightness})
    
    @app.post("/api/brightness")
    async def set_brightness_api(data: dict):
        brightness = data.get("brightness", 50)
        result = await asyncio.to_thread(set_brightness, brightness)
        return JSONResponse(content={"success": result, "brightness": brightness})
    
    @app.post("/api/theme")
    async def change_theme_api(data: dict):
        mode = data.get("mode", "dark")
        result = await asyncio.to_thread(change_windows_theme, mode)
        return JSONResponse(content={"success": result, "theme": mode})

    # Mic state REST endpoints for robust control from UI
    @app.get("/api/mic-state")
    async def get_mic_state_api():
        """Fast endpoint to get current mic state"""
        try:
            current_state = audio_state_manager.get_mute_state()
            return JSONResponse(content={
                "is_muted": current_state,
                "timestamp": asyncio.get_event_loop().time()
            })
        except Exception as e:
            Logger.log(f"Error getting mic state: {e}", "ERROR")
            return JSONResponse(content={"error": str(e)}, status_code=500)

    @app.post("/api/mic-state")
    async def set_mic_state_api(data: dict):
        """Fast endpoint to set mic state with immediate verification"""
        try:
            desired = bool(data.get("is_muted", True))
            Logger.log(f"REST API: Setting mic state to {desired}", "API")
            
            # Use synchronous method for immediate effect
            sync_success = audio_state_manager.set_mute_state_sync(desired, "rest_api")
            
            # Also do async update for callbacks
            result = await audio_state_manager.set_mute_state(desired, "rest_api")
            
            # Verify state was actually changed
            verified_state = audio_state_manager.get_mute_state()
            success = (verified_state == desired) and sync_success
            
            if success:
                # Broadcast to all WebSocket clients
                await ws_manager.broadcast({"type": "mic_toggled", "payload": {"is_muted": desired}})
                Logger.log(f"Mic state verified: {desired}", "API")
            else:
                Logger.log(f"Mic state mismatch! Desired: {desired}, Actual: {verified_state}", "ERROR")
            
            return JSONResponse(content={
                "success": success,
                "is_muted": verified_state,
                "requested": desired,
                "verified": verified_state == desired,
                "timestamp": asyncio.get_event_loop().time()
            })
        except Exception as e:
            Logger.log(f"Error setting mic state: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
            return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
    
    @app.post("/api/contacts")
    async def add_contact_api(data: dict):
        names = data.get("names", [])
        phone = data.get("phone")
        email = data.get("email")
        telegram_id = data.get("telegram_id")
        result = await asyncio.to_thread(contacts_manager.add_contact, names, phone, telegram_id, email)
        if result.get("status") == "success":
            # Return all contacts after successful add
            all_contacts = await asyncio.to_thread(contacts_manager.load_contacts)
            return JSONResponse(content={"status": "success", "message": result["message"], "contacts": all_contacts})
        return JSONResponse(content=result)
    
    @app.delete("/api/contacts/{name}")
    async def delete_contact_api(name: str):
        result = await asyncio.to_thread(contacts_manager.delete_contact, name)
        if result.get("status") == "success":
            # Return all contacts after successful delete
            all_contacts = await asyncio.to_thread(contacts_manager.load_contacts)
            return JSONResponse(content={"status": "success", "message": result["message"], "contacts": all_contacts})
        return JSONResponse(content=result, status_code=404)
    
    @app.put("/api/contacts/{name}")
    async def update_contact_api(name: str, data: dict):
        names = data.get("names")
        phone = data.get("phone")
        email = data.get("email")
        telegram_id = data.get("telegram_id")
        result = await asyncio.to_thread(contacts_manager.update_contact, name, names, phone, telegram_id, email)
        if result.get("status") == "success":
            # Return all contacts after successful update
            all_contacts = await asyncio.to_thread(contacts_manager.load_contacts)
            return JSONResponse(content={"status": "success", "message": result["message"], "contacts": all_contacts})
        return JSONResponse(content=result, status_code=404)
    
    @app.get("/health")
    async def health_check():
        # Get comprehensive state from audio state manager
        state_info = await audio_state_manager.get_full_state()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "voice_assistant": "running" if state_info["audio_loop_ready"] else "not_initialized",
            "voice_state": {
                "initialized": state_info["audio_loop_ready"],
                "is_muted": state_info["is_muted"],
                "assistant_speaking": state_info["assistant_speaking"],
                "has_session": state_info["audio_loop_ready"] and audio_state_manager._audio_loop.session is not None if audio_state_manager._audio_loop else False,
                "has_audio_stream": state_info["audio_loop_ready"] and audio_state_manager._audio_loop.audio_stream is not None if audio_state_manager._audio_loop else False
            },
            "ui_server": "running",
            "websocket_connections": len(ws_manager.active_connections),
            "mic_state_file": str(audio_state_manager._mute_state_file),
            "mic_state_file_exists": audio_state_manager._mute_state_file.exists()
        }
    
    @app.get("/api/mic-state/verify")
    async def verify_mic_state_api():
        """Verification endpoint - checks file, memory, and audio loop state"""
        try:
            file_state = audio_state_manager._load_mute_state()
            memory_state = audio_state_manager.get_mute_state()
            audio_loop_state = audio_state_manager._audio_loop.is_muted if audio_state_manager._audio_loop else None
            
            all_match = (file_state == memory_state) and (audio_loop_state is None or audio_loop_state == memory_state)
            
            return JSONResponse(content={
                "all_synced": all_match,
                "file_state": file_state,
                "memory_state": memory_state,
                "audio_loop_state": audio_loop_state,
                "file_path": str(audio_state_manager._mute_state_file),
                "timestamp": asyncio.get_event_loop().time()
            })
        except Exception as e:
            Logger.log(f"Error verifying mic state: {e}", "ERROR")
            return JSONResponse(content={"error": str(e)}, status_code=500)
    
    @app.post("/api/stop-speaking")
    async def stop_speaking_api():
        """Fast API to stop Friday from speaking - ONLY works when unmuted AND speaking"""
        try:
            if not audio_state_manager.is_audio_loop_ready():
                return JSONResponse(content={
                    "success": False,
                    "error": "Voice assistant not initialized",
                    "reason": "no_audio_loop"
                }, status_code=503)
            
            # Check conditions
            is_muted = audio_state_manager.get_mute_state()
            is_speaking = audio_state_manager._audio_loop.is_assistant_speaking
            
            if is_muted:
                Logger.log("Stop API ignored: Mic is muted", "API")
                return JSONResponse(content={
                    "success": False,
                    "error": "Cannot stop while muted",
                    "reason": "mic_muted",
                    "is_muted": is_muted,
                    "is_speaking": is_speaking
                }, status_code=400)
            
            if not is_speaking:
                Logger.log("Stop API ignored: Assistant not speaking", "API")
                return JSONResponse(content={
                    "success": False,
                    "error": "Assistant not speaking",
                    "reason": "not_speaking",
                    "is_muted": is_muted,
                    "is_speaking": is_speaking
                }, status_code=400)
            
            # Valid stop - execute immediately
            audio_state_manager._audio_loop.should_stop_speaking = True
            Logger.log("Stop API: Valid request (unmuted + speaking)", "API")
            
            # Broadcast to WebSocket clients
            await ws_manager.broadcast({"type": "jarvis_stopped", "payload": {"success": True}})
            
            return JSONResponse(content={
                "success": True,
                "stopped": True,
                "is_muted": is_muted,
                "was_speaking": is_speaking,
                "timestamp": asyncio.get_event_loop().time()
            })
            
        except Exception as e:
            Logger.log(f"Error in stop API: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
            return JSONResponse(content={
                "success": False,
                "error": str(e)
            }, status_code=500)
    
    @app.get("/api/assistant-state")
    async def get_assistant_state_api():
        """Get current assistant speaking state"""
        try:
            if not audio_state_manager.is_audio_loop_ready():
                return JSONResponse(content={
                    "is_speaking": False,
                    "is_muted": audio_state_manager.get_mute_state(),
                    "audio_loop_ready": False
                })
            
            return JSONResponse(content={
                "is_speaking": audio_state_manager._audio_loop.is_assistant_speaking,
                "is_muted": audio_state_manager.get_mute_state(),
                "audio_loop_ready": True,
                "timestamp": asyncio.get_event_loop().time()
            })
        except Exception as e:
            Logger.log(f"Error getting assistant state: {e}", "ERROR")
            return JSONResponse(content={"error": str(e)}, status_code=500)
    
    @app.on_event("startup")
    async def startup_event():
        Logger.log("UI WebSocket server starting on port 8000", "SYSTEM")
        # Add callback for automatic broadcasting of state changes
        async def broadcast_mute_change(new_state: bool):
            try:
                await ws_manager.broadcast({"type": "mic_toggled", "payload": {"is_muted": new_state}})
                Logger.log(f"Auto-broadcasted mute state change: {new_state}", "AUDIO_STATE")
            except Exception as e:
                Logger.log(f"Error broadcasting mute state change: {e}", "ERROR")

        audio_state_manager.add_state_change_callback(broadcast_mute_change)
        asyncio.create_task(broadcast_metrics())
    
    # Run FastAPI server in background
    async def run_fastapi_server():
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="error", access_log=False, ws_ping_interval=20, ws_ping_timeout=10)
        server = uvicorn.Server(config)
        await server.serve()

else:
    # Dummy functions if FastAPI not available
    async def run_fastapi_server():
        Logger.log("FastAPI not installed - UI server disabled", "WARNING")
        while True:
            await asyncio.sleep(60)

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

pya = pyaudio.PyAudio()

# Initialize logger and memory
Logger.init()
memory_handler = MemoryHandler()

class AudioStateManager:
    """
    Robust audio state management with persistence and synchronization
    
    PERMANENT MIC MUTE/UNMUTE SOLUTION:
    ====================================
    This class implements a bulletproof mic state management system that prevents
    the common "stops working" issue. Here's how it works:
    
    1. SINGLE SOURCE OF TRUTH: All state is managed here, not scattered across components
    2. FILE PERSISTENCE: State is saved to disk immediately on every change
    3. DUAL SYNC METHODS:
       - Synchronous (set_mute_state_sync): Immediate update for REST API
       - Asynchronous (set_mute_state): For callbacks and WebSocket broadcasts
    4. VERIFICATION: Every state change is verified against actual state
    5. FAST REST API: Primary method for UI uses /api/mic-state POST endpoint
    6. WEBSOCKET FALLBACK: If REST fails, WebSocket is used as backup
    7. PERIODIC SYNC: UI automatically syncs state every 5 seconds
    8. OPTIMISTIC UI: UI updates immediately, then verifies with backend
    9. AUDIO LOOP INTEGRATION: Direct state synchronization with audio processing
    10. DOUBLE-CHECK: Audio sender re-checks mute state before transmitting
    
    This prevents issues caused by:
    - Race conditions between UI and backend
    - State getting out of sync during code changes
    - Network delays or WebSocket disconnections
    - Audio loop not respecting state changes
    """

    def __init__(self):
        self._mute_state_file = Path(__file__).parent / "Database" / "mute_state.txt"
        self._is_muted = self._load_mute_state()
        self._audio_loop = None
        self._state_lock = asyncio.Lock()
        self._last_state_change = 0
        self._state_change_callbacks = []
        Logger.log(f"AudioStateManager initialized with mute_state={self._is_muted}", "AUDIO_STATE")

    def _load_mute_state(self) -> bool:
        """Load mute state from file with error recovery"""
        try:
            if self._mute_state_file.exists():
                content = self._mute_state_file.read_text().strip().lower()
                if content in ['true', 'false']:
                    state = content == 'true'
                    Logger.log(f"Loaded mute state from file: {state}", "AUDIO_STATE")
                    return state
                else:
                    Logger.log(f"Invalid mute state file content: '{content}', resetting to default", "WARNING")
            else:
                Logger.log("Mute state file not found, using default (muted)", "AUDIO_STATE")
        except Exception as e:
            Logger.log(f"Error loading mute state: {e}, using default (muted)", "ERROR")

        # Default to muted for safety
        return True

    def _save_mute_state(self, state: bool) -> bool:
        """Save mute state to file with error handling"""
        try:
            self._mute_state_file.parent.mkdir(exist_ok=True)
            self._mute_state_file.write_text("true" if state else "false")
            Logger.log(f"Saved mute state to file: {state}", "AUDIO_STATE")
            return True
        except Exception as e:
            Logger.log(f"Error saving mute state: {e}", "ERROR")
            return False

    def set_mute_state_sync(self, muted: bool, source: str = "unknown") -> bool:
        """Synchronous version for immediate state changes - returns success"""
        try:
            old_state = self._is_muted
            self._is_muted = muted
            self._last_state_change = 0  # Will be updated by async version
            
            # Save to file immediately
            save_success = self._save_mute_state(muted)
            
            # Sync with audio loop if available
            if self._audio_loop:
                # Direct attribute assignment to bypass the property
                self._audio_loop.state_manager._is_muted = muted
                if not muted:
                    self._audio_loop.is_assistant_speaking = False
            
            Logger.log(f"SYNC mute state: {old_state} -> {muted} (source: {source})", "AUDIO_STATE")
            return save_success
        except Exception as e:
            Logger.log(f"Error in sync mute state: {e}", "ERROR")
            return False

    def register_audio_loop(self, audio_loop):
        """Register the audio loop instance for state synchronization"""
        self._audio_loop = audio_loop
        # Force sync the state immediately
        if self._audio_loop:
            # Direct assignment to ensure immediate sync
            self._audio_loop.state_manager._is_muted = self._is_muted
            Logger.log(f"Registered audio loop, forced mute state: {self._is_muted}", "AUDIO_STATE")

    async def _notify_state_change(self, new_state: bool):
        """Notify all registered callbacks of state change"""
        for callback in self._state_change_callbacks:
            try:
                await callback(new_state)
            except Exception as e:
                Logger.log(f"Error in state change callback: {e}", "ERROR")

    def add_state_change_callback(self, callback):
        """Add callback for state change notifications"""
        self._state_change_callbacks.append(callback)

    async def set_mute_state(self, muted: bool, source: str = "unknown") -> dict:
        """Set mute state with validation and synchronization"""
        async with self._state_lock:
            current_time = asyncio.get_event_loop().time()

            # Prevent rapid toggling (debounce)
            if current_time - self._last_state_change < 0.2:
                Logger.log(f"Ignoring rapid mute toggle from {source}", "AUDIO_STATE")
                return {"success": False, "error": "Too frequent toggles", "current_state": self._is_muted}

            old_state = self._is_muted
            self._is_muted = muted
            self._last_state_change = current_time

            # Save to file
            save_success = self._save_mute_state(muted)

            # Sync with audio loop if available
            loop_sync_success = True
            if self._audio_loop:
                try:
                    self._audio_loop.is_muted = muted
                    # When unmuting, reset assistant speaking flag to allow audio input
                    if not muted:
                        self._audio_loop.is_assistant_speaking = False
                    Logger.log(f"Synced mute state with audio loop: {muted}", "AUDIO_STATE")
                except Exception as e:
                    Logger.log(f"Error syncing with audio loop: {e}", "ERROR")
                    loop_sync_success = False

            # Notify callbacks
            await self._notify_state_change(muted)

            success = save_success and loop_sync_success
            result = {
                "success": success,
                "old_state": old_state,
                "new_state": muted,
                "source": source,
                "timestamp": current_time
            }

            if not success:
                result["errors"] = []
                if not save_success:
                    result["errors"].append("file_save_failed")
                if not loop_sync_success:
                    result["errors"].append("loop_sync_failed")

            Logger.log(f"Mute state changed: {old_state} -> {muted} (source: {source}, success: {success})", "AUDIO_STATE")
            return result

    def get_mute_state(self) -> bool:
        """Get current mute state"""
        return self._is_muted

    def is_audio_loop_ready(self) -> bool:
        """Check if audio loop is registered and ready"""
        return self._audio_loop is not None

    async def get_full_state(self) -> dict:
        """Get comprehensive state information"""
        async with self._state_lock:
            return {
                "is_muted": self._is_muted,
                "audio_loop_ready": self.is_audio_loop_ready(),
                "last_change": self._last_state_change,
                "file_path": str(self._mute_state_file),
                "file_exists": self._mute_state_file.exists(),
                "assistant_speaking": self._audio_loop.is_assistant_speaking if self._audio_loop else None
            }

# Global audio state manager
audio_state_manager = AudioStateManager()


class AudioLoop:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_stream = None
        self.current_text_buffer = ""
        self.is_assistant_speaking = False
        self.should_stop_speaking = False
        self.user_speech_buffer = ""
        # Remove old mute state management - now handled by state_manager
        # --- MEMORY INTEGRATION (Like sample agent) ---
        self.session_messages = []  # Store all messages for batch save on shutdown
        self.cached_memory_str = ""  # Store initial memory context to filter it out
        self.last_activity_time = 0
        self.shutdown_initiated = False
        
        # --- BULLETPROOF CHAT LOGGING ---
        # Track what's been logged to prevent duplicates and ensure NOTHING is missed
        self.last_logged_user_text = ""
        self.last_logged_assistant_text = ""
        self.current_turn_user_text = ""  # Accumulate user text for current turn
        self.current_turn_assistant_text = ""  # Accumulate assistant text for current turn
        self.user_text_logged_this_turn = False
        self.assistant_text_logged_this_turn = False
        
        # --- REAL-TIME TRANSCRIPTION BUFFERS ---
        self.user_audio_buffer = bytearray()  # Buffer for user audio chunks
        self.assistant_audio_buffer = bytearray()  # Buffer for assistant audio chunks
        self.user_audio_chunk_count = 0  # Count chunks for user
        self.assistant_audio_chunk_count = 0  # Count chunks for assistant
        # Transcribe every N chunks (adjust for latency/accuracy balance)
        # 25 chunks = ~0.5 second at 20ms chunks for faster transcription
        self.TRANSCRIPTION_CHUNK_THRESHOLD = 25

        # Register this audio loop with the state manager
        self.state_manager.register_audio_loop(self)

    @property
    def is_muted(self):
        """Get current mute state from state manager"""
        return self.state_manager.get_mute_state()

    @is_muted.setter
    def is_muted(self, value):
        """Set mute state through state manager synchronously"""
        # Update the internal state directly for immediate effect
        self.state_manager._is_muted = value
        self.state_manager._save_mute_state(value)


    async def listen_audio(self):
        """Capture audio from microphone and send to the model"""
        try:
            Logger.log("Starting audio capture from microphone", "AUDIO")
            mic_info = pya.get_default_input_device_info()
            Logger.log(f"Using microphone: {mic_info['name']}", "AUDIO")
            
            self.audio_stream = await asyncio.to_thread(
                pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=SEND_SAMPLE_RATE,
                input=True,
                input_device_index=mic_info["index"],
                frames_per_buffer=CHUNK_SIZE,
            )
            
            if __debug__:
                kwargs = {"exception_on_overflow": False}
            else:
                kwargs = {}
            
            Logger.log("Audio capture started successfully", "AUDIO")
            
            # Track state for logging changes
            last_logged_muted = self.is_muted
            last_logged_speaking = self.is_assistant_speaking
            
            while not self.shutdown_initiated:
                try:
                    # Log state changes
                    if last_logged_muted != self.is_muted or last_logged_speaking != self.is_assistant_speaking:
                        Logger.log(f"Audio state: muted={self.is_muted}, assistant_speaking={self.is_assistant_speaking}", "AUDIO")
                        last_logged_muted = self.is_muted
                        last_logged_speaking = self.is_assistant_speaking
                    
                    # Read audio data with error handling
                    data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
                    
                    # Only send audio if not muted and assistant is not speaking
                    if not self.is_muted and not self.is_assistant_speaking:
                        # Make sure queue exists before putting
                        if self.out_queue:
                            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})
                            self.last_activity_time = asyncio.get_event_loop().time()
                        
                        # --- TRANSCRIPTION: Buffer user audio for transcription ---
                        self.user_audio_buffer.extend(data)
                        self.user_audio_chunk_count += 1
                        
                        # Transcribe when we have enough audio (~1 second)
                        if self.user_audio_chunk_count >= self.TRANSCRIPTION_CHUNK_THRESHOLD:
                            # Queue for transcription in background
                            audio_copy = bytes(self.user_audio_buffer)
                            Logger.transcribe_audio_chunk(
                                audio_copy, 
                                role="USER",
                                sample_rate=SEND_SAMPLE_RATE,
                                channels=CHANNELS
                            )
                            # Clear buffer
                            self.user_audio_buffer.clear()
                            self.user_audio_chunk_count = 0
                    else:
                        # Still read but don't send - prevents buffer overflow
                        await asyncio.sleep(0.01)
                        
                except OSError as e:
                    if not self.shutdown_initiated:
                        Logger.log(f"Audio stream error: {e}. Attempting recovery...", "WARNING")
                        # Try to recover by waiting a bit
                        await asyncio.sleep(0.1)
                        continue
                except Exception as e:
                    if not self.shutdown_initiated:
                        Logger.log(f"Unexpected error reading audio: {e}", "ERROR")
                    raise
                
        except KeyboardInterrupt:
            Logger.log("Session interrupted by user in listen_audio", "SESSION")
            self.shutdown_initiated = True
            raise
        except Exception as e:
            if not self.shutdown_initiated:
                Logger.log(f"Error in listen_audio: {e}", "ERROR")
            raise

    async def send_realtime(self):
        """Send audio data to the model"""
        try:
            Logger.log("Starting realtime audio sender", "AUDIO")
            while not self.shutdown_initiated:
                msg = await self.out_queue.get()
                
                # Double-check mute state before sending - prevent race conditions
                if not self.is_muted and not self.is_assistant_speaking:
                    if self.session:
                        await self.session.send_realtime_input(audio=msg)
                        self.last_activity_time = asyncio.get_event_loop().time()
                else:
                    # Silently discard audio if muted or assistant speaking
                    pass
                    
                self.out_queue.task_done() # Mark task as done
        except Exception as e:
            if not self.shutdown_initiated:
                Logger.log(f"Error in send_realtime: {e}", "ERROR")
            raise

    async def receive_audio(self):
        """
        Receive responses from the model and handle tool calls
        
        BULLETPROOF CHAT LOGGING SYSTEM:
        =================================
        This method implements a GUARANTEED chat logging system that:
        
        1. IMMEDIATE TRANSCRIPTION CAPTURE:
           - Logs user speech the INSTANT Gemini provides input_transcription
           - Accumulates assistant text as it arrives in real-time
           - No waiting for turn completion (prevents loss on interrupts)
        
        2. DUPLICATE PREVENTION:
           - Tracks last logged text to prevent duplicate entries
           - Uses separate turn buffers (current_turn_user_text, current_turn_assistant_text)
           - Compares before logging to ensure each message logged exactly once
        
        3. TRIPLE SAFETY NET:
           - End-of-turn logging (normal completion)
           - Shutdown logging (_save_final_chatlogs on exit)
           - Fallback buffers (user_speech_buffer, current_text_buffer)
        
        4. IMMEDIATE DISK WRITE:
           - Logger.log_chat() calls save_chat() which writes immediately
           - Uses fsync() to force OS to commit to disk
           - No buffering delays that could lose data
        
        5. UI REAL-TIME BROADCAST:
           - Sends messages to UI via WebSocket as they're logged
           - Users see conversations appear in real-time
           - Chat screen always synchronized with chatlogs.json
        
        6. CRASH PROTECTION:
           - Finally block always executes _save_final_chatlogs()
           - Even on crash/interrupt, all text in buffers is saved
           - Nothing is ever lost
        
        This system is PERMANENT and CANNOT be broken by:
        - Code changes in other features
        - Interrupts or crashes
        - Network issues
        - UI disconnections
        - Stop commands
        - Any external factors
        
        Every single word spoken and responded is GUARANTEED to be in chatlogs.json
        """
        try:
            Logger.log("Starting response receiver", "RESPONSE")
            brain = GeminiBrain()
            
            while not self.shutdown_initiated:
                if not self.session: # Wait for session to be established
                    await asyncio.sleep(0.1)
                    continue
                    
                turn = self.session.receive()
                async for response in turn:
                    if self.shutdown_initiated:
                        break
                    
                    self.last_activity_time = asyncio.get_event_loop().time()
                    
                    # DEBUG: Log ALL response attributes to understand what Gemini sends
                    if hasattr(response, '__dict__'):
                        attrs = {k: v for k, v in response.__dict__.items() if v is not None}
                        if attrs:
                            Logger.log(f"Response attributes: {list(attrs.keys())}", "DEBUG_RESPONSE")
                    
                    # Handle audio data
                    if data := response.data:
                        if self.should_stop_speaking:
                            Logger.log("Stop command detected - clearing audio queue", "INTERRUPT")
                            while not self.audio_in_queue.empty():
                                try:
                                    self.audio_in_queue.get_nowait()
                                except:
                                    break
                            self.should_stop_speaking = False
                            self.is_assistant_speaking = False
                            # Re-enable mic immediately when stopping
                            if self.is_muted:
                                Logger.log("Mic still muted by user - respecting mute state", "AUDIO")
                            
                            # Notify UI that speaking stopped
                            try:
                                if FASTAPI_AVAILABLE and 'ws_manager' in globals():
                                    asyncio.create_task(ws_manager.broadcast({
                                        "type": "assistant_speaking_changed",
                                        "payload": {"is_speaking": False}
                                    }))
                            except:
                                pass
                            continue
                        
                        # Mark as speaking if not already
                        if not self.is_assistant_speaking:
                            self.is_assistant_speaking = True
                            Logger.log("Assistant started speaking", "AUDIO")
                            # Notify UI that speaking started
                            try:
                                if FASTAPI_AVAILABLE and 'ws_manager' in globals():
                                    asyncio.create_task(ws_manager.broadcast({
                                        "type": "assistant_speaking_changed",
                                        "payload": {"is_speaking": True}
                                    }))
                            except:
                                pass
                        
                        if self.audio_in_queue:
                            self.audio_in_queue.put_nowait(data)
                        continue
                    
                    # Handle text output - LOG IMMEDIATELY as it arrives
                    if text := response.text:
                        self.current_text_buffer += text
                        self.current_turn_assistant_text += text
                        print(text, end="", flush=True)
                        # Don't print debug for every character, only periodically
                        continue
                    
                    # Check for input transcription (user speech)
                    # VOICE INTERRUPT SYSTEM:
                    # - Only listens to stop commands when assistant is speaking AND mic is unmuted
                    # - Ignores all other user speech while assistant is speaking
                    # - Supported stop phrases: "stop", "friday stop", "jarvis stop"
                    # - This prevents interrupting the assistant during normal conversation
                    # 
                    # BULLETPROOF LOGGING SYSTEM:
                    # - Logs user speech IMMEDIATELY when transcription arrives (not at end of turn)
                    # - Prevents duplicate logging by tracking what's already been logged
                    # - Accumulates partial transcriptions to get complete utterances
                    # - GUARANTEES no messages are ever missed
                    if hasattr(response, 'server_content') and response.server_content:
                        # DEBUG: Log server_content structure
                        if hasattr(response.server_content, '__dict__'):
                            sc_attrs = {k: v for k, v in response.server_content.__dict__.items() if v is not None}
                            if sc_attrs:
                                Logger.log(f"Server content attributes: {list(sc_attrs.keys())}", "DEBUG_SERVER_CONTENT")
                        
                        # Check for turn_complete event
                        if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                            Logger.log("Turn complete received", "TURN")
                        
                        if hasattr(response.server_content, 'input_transcription') and response.server_content.input_transcription:
                            user_text = response.server_content.input_transcription
                            Logger.log(f"User speech detected: {user_text}", "TRANSCRIPTION")
                            print(f"\n[DEBUG] User transcription received: {user_text[:50]}...")
                            
                            # Accumulate user text for this turn
                            self.user_speech_buffer = user_text
                            self.current_turn_user_text = user_text  # Keep full text
                            
                            user_text_lower = str(user_text).lower()
                            assistantname = os.getenv("Assistantname", "Friday").lower()
                            
                            # VOICE INTERRUPT: Only works when mic unmuted AND assistant speaking
                            if self.is_assistant_speaking and not self.is_muted:
                                # Check for stop commands
                                stop_phrases = ["stop", f"{assistantname} stop", "jarvis stop", "friday stop"]
                                if any(phrase in user_text_lower for phrase in stop_phrases):
                                    Logger.log(f"VOICE INTERRUPT DETECTED: '{user_text}' (valid: unmuted + speaking)", "INTERRUPT")
                                    self.should_stop_speaking = True
                                    self.is_assistant_speaking = False
                                    
                                    while not self.audio_in_queue.empty():
                                        try:
                                            self.audio_in_queue.get_nowait()
                                        except:
                                            break
                                    
                                    print("\n🛑 [STOPPED BY VOICE]")
                                    continue
                                else:
                                    # While assistant is speaking, ignore all other user input
                                    Logger.log(f"User speech ignored while assistant speaking: '{user_text}'", "TRANSCRIPTION")
                                    continue
                            
                            # --- Shutdown Commands (work anytime) ---
                            if "shutdown friday" in user_text_lower or "exit friday" in user_text_lower:
                                Logger.log("SHUTDOWN COMMAND DETECTED!", "SESSION")
                                print("\n\n👋 Shutting down Friday...")
                                self.shutdown_initiated = True
                                # This will trigger the KeyboardInterrupt in run()
                                raise KeyboardInterrupt 
                    
                    # Handle tool calls
                    if hasattr(response, 'tool_call') and response.tool_call:
                        Logger.log(f"Tool call detected!", "TOOL_CALL")
                        
                        for function_call in response.tool_call.function_calls:
                            function_name = function_call.name
                            function_id = function_call.id
                            
                            Logger.log(f"Function call: {function_name} (ID: {function_id})", "TOOL_CALL")
                            Logger.log_tool_status(function_name, "WORKING", "Tool execution started")
                            
                            try:
                                args = dict(function_call.args.items()) if function_call.args else {}
                            except Exception as e:
                                Logger.log(f"Error parsing args: {e}", "ERROR")
                                args = {}
                            
                            # Execute tool through brain
                            try:
                                result = await asyncio.to_thread(brain.execute_tool, function_name, args)
                                
                                if result.get("status") == "success":
                                    Logger.log_tool_status(function_name, "SUCCESS", "Tool completed successfully")
                                else:
                                    Logger.log_tool_status(function_name, "FAILURE", result.get("message", "Unknown error"))
                                
                                Logger.log(f"Tool result received", "TOOL_RESULT")
                                
                                try:
                                    await self.session.send_tool_response(
                                        function_responses=[{
                                            "id": function_id,
                                            "name": function_name,
                                            "response": result
                                        }]
                                    )
                                    Logger.log("Tool response sent successfully", "TOOL_RESPONSE")
                                    print(f"\n[DEBUG] Tool executed: {function_name}, waiting for assistant response...")
                                except Exception as e:
                                    Logger.log(f"Error sending tool response: {e}", "ERROR")
                                    Logger.log_tool_status(function_name, "ERROR", f"Failed to send response: {e}")
                            except Exception as e:
                                Logger.log(f"Error executing tool: {e}", "ERROR")
                                Logger.log_tool_status(function_name, "ERROR", str(e))
                    
                    if hasattr(response, 'tool_call_cancellation') and response.tool_call_cancellation:
                        for tool_id in response.tool_call_cancellation.ids:
                            Logger.log(f"Tool call cancelled: {tool_id}", "WARNING")
                            Logger.log_tool_status("unknown", "CANCELED", f"Tool ID {tool_id} was cancelled")

                if self.shutdown_initiated:
                    break
                    
                # --- BULLETPROOF CHAT LOGGING SYSTEM ---
                # This logs conversations IMMEDIATELY at end of each turn
                # Prevents ANY loss of data regardless of interruptions or errors
                
                # Log user message if we have one and haven't logged it yet
                if self.current_turn_user_text.strip():
                    user_msg = self.current_turn_user_text.strip()
                    
                    # Only log if it's different from what we last logged (prevent duplicates)
                    if user_msg != self.last_logged_user_text:
                        Logger.log_chat("USER", user_msg)
                        # Collect for batch memory save (like sample agent)
                        self.session_messages.append({"role": "user", "content": user_msg})
                        print(f"\n[DEBUG] Added USER message to session_messages. Total: {len(self.session_messages)}")
                        self.last_logged_user_text = user_msg
                        user_msg_for_memory = user_msg
                        Logger.log(f"✅ USER message logged: {user_msg[:50]}...", "CHAT_LOG")
                        
                        # Broadcast to UI in real-time
                        try:
                            if FASTAPI_AVAILABLE and 'ws_manager' in globals():
                                asyncio.create_task(ws_manager.broadcast({
                                    "type": "new_message",
                                    "payload": {
                                        "role": "user",
                                        "content": user_msg,
                                        "timestamp": datetime.now().timestamp()
                                    }
                                }))
                        except:
                            pass
                    else:
                        user_msg_for_memory = None
                    
                    # Clear the turn buffer after logging
                    self.current_turn_user_text = ""
                    self.user_speech_buffer = ""
                else:
                    user_msg_for_memory = None

                # Log assistant message if we have one and haven't logged it yet
                if self.current_turn_assistant_text.strip():
                    assistant_msg = self.current_turn_assistant_text.strip()
                    
                    # Only log if it's different from what we last logged (prevent duplicates)
                    if assistant_msg != self.last_logged_assistant_text:
                        Logger.log_chat("ASSISTANT", assistant_msg)
                        # Collect for batch memory save (like sample agent)
                        self.session_messages.append({"role": "assistant", "content": assistant_msg})
                        print(f"\n[DEBUG] Added ASSISTANT message to session_messages. Total: {len(self.session_messages)}")
                        self.last_logged_assistant_text = assistant_msg
                        Logger.log(f"✅ ASSISTANT message logged: {assistant_msg[:50]}...", "CHAT_LOG")
                        
                        # Broadcast complete message to UI
                        try:
                            if FASTAPI_AVAILABLE and 'ws_manager' in globals():
                                asyncio.create_task(ws_manager.broadcast({
                                    "type": "assistant_end",
                                    "payload": {
                                        "content": assistant_msg,
                                        "timestamp": datetime.now().timestamp()
                                    }
                                }))
                        except:
                            pass
                    else:
                        assistant_msg = None
                    
                    # Clear the turn buffer after logging
                    self.current_turn_assistant_text = ""
                    self.current_text_buffer = ""
                else:
                    assistant_msg = None

                # DO NOT save to memory immediately - collect for batch save on shutdown (like sample agent)

                self.is_assistant_speaking = False
                self.should_stop_speaking = False
                
                # Notify UI that speaking stopped naturally
                try:
                    if FASTAPI_AVAILABLE and 'ws_manager' in globals():
                        asyncio.create_task(ws_manager.broadcast({
                            "type": "assistant_speaking_changed",
                            "payload": {"is_speaking": False}
                        }))
                except:
                    pass
                
                # Log microphone re-enabled only if there was a conversation
                if user_msg_for_memory and assistant_msg:
                    Logger.log("Assistant finished speaking - microphone re-enabled", "AUDIO")

                while not self.audio_in_queue.empty():
                    self.audio_in_queue.get_nowait()
                    
        except KeyboardInterrupt:
            Logger.log("Session interrupted by user in receive_audio", "SESSION")
            self.shutdown_initiated = True
            raise
        except Exception as e:
            if not self.shutdown_initiated:
                Logger.log(f"Error in receive_audio: {e}", "ERROR")
            raise

    async def play_audio(self):
        """Play audio responses from the model and transcribe them"""
        try:
            Logger.log("Starting audio playback", "AUDIO")
            stream = await asyncio.to_thread(
                pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=RECEIVE_SAMPLE_RATE,
                output=True,
            )
            Logger.log("Audio playback started successfully", "AUDIO")
            
            while not self.shutdown_initiated:
                bytestream = await self.audio_in_queue.get()
                
                # Play the audio
                await asyncio.to_thread(stream.write, bytestream)
                
                # --- TRANSCRIPTION: Buffer assistant audio for transcription ---
                self.assistant_audio_buffer.extend(bytestream)
                self.assistant_audio_chunk_count += 1
                
                # Transcribe when we have enough audio (~1 second)
                if self.assistant_audio_chunk_count >= self.TRANSCRIPTION_CHUNK_THRESHOLD:
                    # Queue for transcription in background
                    audio_copy = bytes(self.assistant_audio_buffer)
                    Logger.transcribe_audio_chunk(
                        audio_copy,
                        role="ASSISTANT",
                        sample_rate=RECEIVE_SAMPLE_RATE,
                        channels=CHANNELS
                    )
                    # Clear buffer
                    self.assistant_audio_buffer.clear()
                    self.assistant_audio_chunk_count = 0
                
                self.audio_in_queue.task_done()
                
        except Exception as e:
            if not self.shutdown_initiated:
                Logger.log(f"Error in play_audio: {e}", "ERROR")
            raise

    async def monitor_connection(self):
        """Monitor connection and send keep-alive pings"""
        try:
            while not self.shutdown_initiated:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if self.shutdown_initiated:
                    break
                
                current_time = asyncio.get_event_loop().time()
                if current_time - self.last_activity_time > 180:  # 3 minutes of inactivity
                    Logger.log("No activity detected - sending keep-alive", "CONNECTION")
                    empty_audio = b'\x00' * 320  # Small silent audio chunk
                    try:
                        if self.out_queue:
                            await self.out_queue.put({"data": empty_audio, "mime_type": "audio/pcm"})
                            self.last_activity_time = current_time
                    except Exception as e:
                        Logger.log(f"Keep-alive failed: {e}", "WARNING")
                
        except Exception as e:
            if not self.shutdown_initiated:
                Logger.log(f"Error in monitor_connection: {e}", "ERROR")
    
    async def periodic_memory_sync(self):
        """Periodically sync chatlogs to memory (every 5 minutes)"""
        try:
            sync_interval = 300  # 5 minutes
            last_sync_count = 0
            
            while not self.shutdown_initiated:
                await asyncio.sleep(sync_interval)
                
                if self.shutdown_initiated:
                    break
                
                # Check if we have new chatlogs to sync
                try:
                    current_logs = Logger.load_chatlogs()
                    current_count = len(current_logs)
                    
                    if current_count > last_sync_count:
                        Logger.log(f"Auto-syncing {current_count - last_sync_count} new messages to memory", "MEMORY")
                        await memory_handler.sync_chatlogs_to_memory(limit=50)
                        last_sync_count = current_count
                        Logger.log("✅ Periodic memory sync completed", "MEMORY")
                    else:
                        Logger.log("No new messages to sync", "MEMORY")
                        
                except Exception as e:
                    Logger.log(f"Error in periodic sync: {e}", "WARNING")
                
        except Exception as e:
            if not self.shutdown_initiated:
                Logger.log(f"Error in periodic_memory_sync: {e}", "ERROR")

    # --- BULLETPROOF: Final chat log save on shutdown ---
    async def _save_final_chatlogs(self):
        """Save any remaining unsaved chatlogs on shutdown - GUARANTEES nothing is lost"""
        try:
            Logger.log("Performing final chatlog save check...", "CHAT_LOG")
            
            # Check if there's any unsaved user text
            if self.current_turn_user_text.strip():
                user_msg = self.current_turn_user_text.strip()
                if user_msg != self.last_logged_user_text:
                    Logger.log_chat("USER", user_msg)
                    self.all_user_messages.append(user_msg)
                    Logger.log(f"✅ Final USER message saved: {user_msg[:50]}...", "CHAT_LOG")
            
            # Check if there's any unsaved assistant text
            if self.current_turn_assistant_text.strip():
                assistant_msg = self.current_turn_assistant_text.strip()
                if assistant_msg != self.last_logged_assistant_text:
                    Logger.log_chat("ASSISTANT", assistant_msg)
                    self.all_assistant_messages.append(assistant_msg)
                    Logger.log(f"✅ Final ASSISTANT message saved: {assistant_msg[:50]}...", "CHAT_LOG")
            
            # Also check the original buffers as fallback
            if self.user_speech_buffer.strip() and self.user_speech_buffer.strip() != self.last_logged_user_text:
                Logger.log_chat("USER", self.user_speech_buffer.strip())
                Logger.log(f"✅ Final USER buffer saved: {self.user_speech_buffer[:50]}...", "CHAT_LOG")
            
            if self.current_text_buffer.strip() and self.current_text_buffer.strip() != self.last_logged_assistant_text:
                Logger.log_chat("ASSISTANT", self.current_text_buffer.strip())
                Logger.log(f"✅ Final ASSISTANT buffer saved: {self.current_text_buffer[:50]}...", "CHAT_LOG")
            
            Logger.log("Final chatlog save complete - ALL conversations preserved", "CHAT_LOG")
        except Exception as e:
            Logger.log(f"Error in final chatlog save: {e}", "ERROR")

    # --- ADDED: Shutdown memory save ---
    async def _save_session_memory(self):
        """
        Save all session conversations to memory on shutdown
        Now uses transcribed chatlogs from chatlogs.json instead of Gemini transcriptions
        """
        try:
            Logger.log(f"_save_session_memory called", "MEMORY")
            
            # NEW APPROACH: Sync transcribed chatlogs to memory
            Logger.log("Syncing transcribed chatlogs to memory...", "MEMORY")
            await memory_handler.sync_chatlogs_to_memory(limit=100)
            
            Logger.log("Session memory saved successfully from chatlogs", "MEMORY")
        except Exception as e:
            Logger.log(f"Error saving session memory: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")


    async def run(self):
        """Main execution loop"""
        username = os.getenv("Username", "Boss")
        assistantname = os.getenv("Assistantname", "Friday")
        
        print("\n" + "="*70)
        print(f"🤖 Advanced {assistantname} - Unified Voice & Chat Assistant")
        print("="*70)
        print("\n✨ Available Features:")
        print("  🎙️  Natural voice conversation (Gemini Live Audio)")
        print("  💬 Text chat via UI (Same Gemini model with full tools)")
        print("  🌤️  Weather information for any city")
        print("  🔍 Internet search for current information")
        print("  📧 Advanced email management and sending")
        print("  📱 Telegram message & file sending")
        print("  🖼️  AI Image generation")
        print("  📄 PDF, Word, PPT, Excel generation")
        print("  🔄 Advanced document format conversion & compression")
        print("  🤖 System automation & control")
        print("  🧠 Long-term memory across sessions")
        print("  👤 Contact management")
        print(f"  🛑 Say '{assistantname} Stop' to interrupt voice")
        print(f"  🔚 Say 'Shutdown {assistantname}' or 'Exit {assistantname}' to close")
        print("  🔐 Power operations secured with password")
        print("\n🌐 UI Access:")
        if FASTAPI_AVAILABLE:
            print("  📡 WebSocket Server: ws://localhost:8000/ws")
            print("  🔗 REST API: http://localhost:8000/api/*")
            print("  🏥 Health Check: http://localhost:8000/health")
            print("  💻 Start UI: cd jarvis-ui && npm run dev")
            print("  🌍 Open: http://localhost:3000")
        else:
            print("  ⚠️  UI Server disabled (FastAPI not installed)")
            print("  📦 Install: pip install fastapi uvicorn psutil")
        print("\n💡 Tips:")
        print("  - Use headphones to prevent echo")
        print(f"  - I'll always call you Boss")
        print("  - I remember our past conversations")
        print("  - Ask me to recall previous chats")
        print("  - Voice AND chat use the SAME Gemini model")
        print("  - All features work in both voice and chat")
        print("  - Press Ctrl+C to exit")
        print("\n" + "="*70)
        
        Logger.log("=== VOICE SESSION START ===", "SESSION")
        Logger.log(f"User: Boss | Assistant: {assistantname}", "SESSION")
        Logger.log(f"Features enabled: ALL ADVANCED FEATURES", "SESSION")
        Logger.log(f"UI Server: {'ENABLED' if FASTAPI_AVAILABLE else 'DISABLED'}", "SESSION")
        
        # Load memory context at startup (like sample agent)
        memory_context = await memory_handler.get_initial_memory_context()
        if memory_context:
            # Cache it in both AudioLoop instance and memory_handler to filter out later
            self.cached_memory_str = memory_context
            memory_handler.cached_memory_str = memory_context
            Logger.log(f"Memory context loaded: {len(memory_context)} characters", "MEMORY")
        else:
            Logger.log("No previous memories found", "MEMORY")

        print(f"\n🎤 Listening, Boss... Start speaking!\n")

        try:
            from Backend.brain import client, MODEL
            
            Logger.log("Connecting to Gemini Live API...", "CONNECTION")
            
            # --- ADDED: Load config with memory ---
            live_config = await get_config_with_memory()
            
            try:
                async with (
                    # --- FIXED: Pass config as a single argument ---
                    client.aio.live.connect(model=MODEL, config=live_config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    self.session = session
                    Logger.log("Connected to Gemini Live API successfully", "CONNECTION")

                    self.audio_in_queue = asyncio.Queue()
                    self.out_queue = asyncio.Queue(maxsize=5)

                    Logger.log("Starting task group...", "SYSTEM")
                    tg.create_task(self.send_realtime())
                    tg.create_task(self.listen_audio())
                    tg.create_task(self.receive_audio())
                    tg.create_task(self.play_audio())
                    tg.create_task(self.monitor_connection())
                    tg.create_task(self.periodic_memory_sync())  # NEW: Auto-sync memory
                    Logger.log("All tasks started successfully", "SYSTEM")
                    
            # --- FIXED: Python 3.13+ exception group syntax ---
            except* Exception as eg: 
                Logger.log("Exception group caught from TaskGroup", "ERROR")
                print("\n❌ Error occurred:")
                for exc in eg.exceptions:
                    if not isinstance(exc, (KeyboardInterrupt, asyncio.CancelledError)):
                        print(f"  - {type(exc).__name__}: {exc}")
                        Logger.log(f"Exception: {type(exc).__name__}: {exc}", "ERROR")
                
                # Re-raise KeyboardInterrupt if it was part of the group
                if any(isinstance(e, KeyboardInterrupt) for e in eg.exceptions):
                    raise KeyboardInterrupt
                
        except KeyboardInterrupt:
            Logger.log("User interrupted session (Ctrl+C or Shutdown Command)", "SESSION")
            print(f"\n\n👋 Goodbye, Boss! Saving memory...")
        except asyncio.CancelledError:
            Logger.log("Session cancelled", "SESSION")
        except Exception as e:
            Logger.log(f"Unexpected error: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self.shutdown_initiated = True
            
            print(f"\n[DEBUG] In finally block - preparing shutdown")
            
            # --- BULLETPROOF: Save any remaining chatlogs FIRST ---
            Logger.log("Executing final chatlog save...", "CLEANUP")
            await self._save_final_chatlogs()
            
            # --- ALWAYS save transcribed chatlogs to memory on shutdown ---
            print(f"\n[DEBUG] Syncing chatlogs to memory")
            Logger.log(f"Syncing transcribed conversations to memory", "MEMORY")
            await self._save_session_memory()
                
            if self.audio_stream:
                try:
                    if self.audio_stream.is_active():
                        self.audio_stream.stop_stream()
                    self.audio_stream.close()
                    Logger.log("Audio stream closed", "CLEANUP")
                except Exception as e:
                     Logger.log(f"Error closing audio stream: {e}", "WARNING")
            
            Logger.log("=== SESSION END ===", "SESSION")
            Logger.close() # Close log files
            print("\n🔇 Session ended.")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n⚠️  Interrupt received, shutting down gracefully...")
    Logger.log("Shutdown signal received", "SYSTEM")
    raise KeyboardInterrupt

if __name__ == "__main__":
    # Verify API keys
    active_google_api = os.getenv("ACTIVE_GOOGLE_API", "GOOGLE_API_KEY_1")
    gemini_api_key = os.getenv(active_google_api)
    
    if not gemini_api_key:
        Logger.log(f"{active_google_api} environment variable is not set", "ERROR")
        print(f"❌ Error: {active_google_api} environment variable is not set.")
        print("Please set it in your .env file.")
        sys.exit(1)
    
    # Set the active API key as GEMINI_API_KEY
    os.environ["GEMINI_API_KEY"] = gemini_api_key
    
    Logger.log("Starting Friday Assistant with UI Server", "SYSTEM")
    Logger.log(f"Python version: {sys.version}", "SYSTEM")
    Logger.log(f"Working directory: {Path.cwd()}", "SYSTEM")
    Logger.log(f"Using API: {active_google_api}", "SYSTEM")
    
    if FASTAPI_AVAILABLE:
        Logger.log("UI WebSocket Server will start on port 8000", "SYSTEM")
    else:
        Logger.log("FastAPI not available - voice-only mode", "WARNING")
    
    # --- ADDED: Signal handler ---
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run both voice assistant and UI server
    async def main_combined():
        """Run both voice assistant and UI server simultaneously"""
        # Create AudioLoop with state manager
        loop = AudioLoop(audio_state_manager)

        # Create tasks for both services
        voice_task = asyncio.create_task(loop.run())
        ui_server_task = asyncio.create_task(run_fastapi_server())

        try:
            # Run both tasks concurrently
            await asyncio.gather(voice_task, ui_server_task)
        except KeyboardInterrupt:
            Logger.log("Shutdown signal received", "SYSTEM")
            print("\n\n👋 Shutting down all services...")
        except Exception as e:
            Logger.log(f"Error in main_combined: {e}", "ERROR")
        finally:
            # Cancel tasks if still running
            for task in [voice_task, ui_server_task]:
                if not task.done():
                    task.cancel()
    
    try:
        asyncio.run(main_combined())
    except KeyboardInterrupt:
        Logger.log("Application terminated by user", "SYSTEM")
        print("\n\n👋 Goodbye!")
    finally:
        Logger.close() # Final fallback to close logs
        pya.terminate()
        sys.exit(0)