# -*- coding: utf-8 -*-
"""
Advanced logging system for Friday Assistant
Supports multiple log files, persistent JSON storage, and real-time audio transcription
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import threading
import queue
import io
import wave

# Audio transcription imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# Alternative: faster-whisper for offline transcription
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

class Logger:
    """Enhanced logger for terminal, file logging, and real-time audio transcription"""
    
    DATABASE_DIR = None
    CHATLOGS_DIR = None
    TERMINALLOGS_DIR = None
    TOOLLOGS_DIR = None
    CHAT_LOG_FILE = None
    TERMINAL_LOG_FILE = None
    TOOL_LOG_FILE = None
    CHATLOGS_JSON_FILE = None
    
    # --- ADDED: File handles to keep files open ---
    _chat_log_handle = None
    _terminal_log_handle = None
    _tool_log_handle = None
    
    # --- NEW: Transcription system ---
    _transcription_enabled = False
    _whisper_model = None
    _recognizer = None
    _transcription_queue = queue.Queue()
    _transcription_thread = None
    _transcription_running = False
    
    # Buffers for accumulating multi-chunk transcriptions
    _user_transcription_buffer = []
    _assistant_transcription_buffer = []
    _last_user_save_time = 0
    _last_assistant_save_time = 0
    _TRANSCRIPTION_SAVE_DELAY = 2.0  # Wait 2 seconds after last chunk to save complete sentence
    
    @classmethod
    def init_transcription(cls):
        """Initialize transcription system with best available engine"""
        if cls._transcription_enabled:
            return
        
        try:
            # Try faster-whisper first (most accurate, works offline)
            if FASTER_WHISPER_AVAILABLE:
                cls.log("Initializing Faster-Whisper transcription (offline)...", "TRANSCRIPTION")
                # Use 'base' model for balance of speed/accuracy
                # Options: tiny, base, small, medium, large
                cls._whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
                cls._transcription_enabled = True
                cls.log("✅ Faster-Whisper initialized successfully", "TRANSCRIPTION")
                
            # Fallback to Google Speech Recognition (requires internet)
            elif SPEECH_RECOGNITION_AVAILABLE:
                cls.log("Initializing Google Speech Recognition (online)...", "TRANSCRIPTION")
                cls._recognizer = sr.Recognizer()
                cls._recognizer.energy_threshold = 300
                cls._recognizer.dynamic_energy_threshold = True
                cls._recognizer.pause_threshold = 0.8
                cls._transcription_enabled = True
                cls.log("✅ Google Speech Recognition initialized", "TRANSCRIPTION")
            else:
                cls.log("⚠️ No transcription engine available. Install: pip install faster-whisper OR pip install SpeechRecognition", "WARNING")
                return
            
            # Start transcription worker thread
            cls._transcription_running = True
            cls._transcription_thread = threading.Thread(target=cls._transcription_worker, daemon=True)
            cls._transcription_thread.start()
            cls.log("🎤 Transcription system ready", "TRANSCRIPTION")
            
        except Exception as e:
            cls.log(f"Failed to initialize transcription: {e}", "ERROR")
            cls._transcription_enabled = False
    
    @classmethod
    def _transcription_worker(cls):
        """Background worker that processes audio chunks for transcription"""
        import time
        
        while cls._transcription_running:
            try:
                # Get audio chunk from queue (timeout to check _transcription_running)
                item = cls._transcription_queue.get(timeout=1)
                if item is None:  # Poison pill
                    break
                
                audio_data, role, sample_rate, channels = item
                
                # Transcribe the audio
                text = cls._transcribe_audio(audio_data, sample_rate, channels)
                
                if text:
                    # Accumulate transcriptions in buffer instead of saving immediately
                    current_time = time.time()
                    
                    if role == "USER":
                        cls._user_transcription_buffer.append(text)
                        cls._last_user_save_time = current_time
                    elif role == "ASSISTANT":
                        cls._assistant_transcription_buffer.append(text)
                        cls._last_assistant_save_time = current_time
                    
                    cls.log(f"[{role}] Transcribed chunk: {text[:50]}...", "TRANSCRIPTION")
                
            except queue.Empty:
                # Check if we need to save accumulated transcriptions
                cls._check_and_save_buffered_transcriptions()
                continue
            except Exception as e:
                cls.log(f"Transcription worker error: {e}", "ERROR")
    
    @classmethod
    def _check_and_save_buffered_transcriptions(cls):
        """Check if enough time has passed to save buffered transcriptions"""
        import time
        current_time = time.time()
        
        # Save user transcription if buffer has content and delay has passed
        if cls._user_transcription_buffer and (current_time - cls._last_user_save_time) >= cls._TRANSCRIPTION_SAVE_DELAY:
            complete_text = " ".join(cls._user_transcription_buffer).strip()
            if complete_text:
                cls.log_chat("USER", complete_text)
                cls.log(f"[USER] Complete transcription saved: {complete_text[:100]}...", "TRANSCRIPTION")
            cls._user_transcription_buffer.clear()
        
        # Save assistant transcription if buffer has content and delay has passed
        if cls._assistant_transcription_buffer and (current_time - cls._last_assistant_save_time) >= cls._TRANSCRIPTION_SAVE_DELAY:
            complete_text = " ".join(cls._assistant_transcription_buffer).strip()
            if complete_text:
                cls.log_chat("ASSISTANT", complete_text)
                cls.log(f"[ASSISTANT] Complete transcription saved: {complete_text[:100]}...", "TRANSCRIPTION")
            cls._assistant_transcription_buffer.clear()
    
    @classmethod
    def _transcribe_audio(cls, audio_data: bytes, sample_rate: int = 16000, channels: int = 1) -> str:
        """Transcribe audio data to text using available engine"""
        try:
            if cls._whisper_model:
                # Use faster-whisper (most accurate)
                # Convert raw audio to WAV format in memory
                wav_io = io.BytesIO()
                with wave.open(wav_io, 'wb') as wav_file:
                    wav_file.setnchannels(channels)
                    wav_file.setsampwidth(2)  # 16-bit audio
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data)
                
                wav_io.seek(0)
                
                # Transcribe with faster-whisper
                segments, info = cls._whisper_model.transcribe(
                    wav_io,
                    language="en",
                    beam_size=5,
                    vad_filter=True,  # Voice activity detection
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
                
                # Combine all segments
                text = " ".join([segment.text.strip() for segment in segments])
                return text.strip()
                
            elif cls._recognizer:
                # Use Google Speech Recognition
                # Convert raw audio to AudioData format
                audio = sr.AudioData(audio_data, sample_rate, 2)
                
                try:
                    text = cls._recognizer.recognize_google(audio, language="en-US")
                    return text.strip()
                except sr.UnknownValueError:
                    return ""  # Speech not understood
                except sr.RequestError as e:
                    cls.log(f"Google Speech API error: {e}", "ERROR")
                    return ""
            
            return ""
            
        except Exception as e:
            cls.log(f"Transcription error: {e}", "ERROR")
            return ""
    
    @classmethod
    def transcribe_audio_chunk(cls, audio_data: bytes, role: str = "USER", sample_rate: int = 16000, channels: int = 1):
        """
        Queue audio chunk for transcription
        
        Args:
            audio_data: Raw audio bytes (PCM format)
            role: "USER" or "ASSISTANT"
            sample_rate: Audio sample rate (default 16000 Hz)
            channels: Number of audio channels (1=mono, 2=stereo)
        """
        if not cls._transcription_enabled:
            return
        
        try:
            cls._transcription_queue.put((audio_data, role, sample_rate, channels))
        except Exception as e:
            cls.log(f"Failed to queue audio for transcription: {e}", "ERROR")
    
    @classmethod
    def stop_transcription(cls):
        """Stop transcription worker thread and save any remaining buffered transcriptions"""
        if cls._transcription_running:
            # Save any remaining buffered transcriptions before stopping
            if cls._user_transcription_buffer:
                complete_text = " ".join(cls._user_transcription_buffer).strip()
                if complete_text:
                    cls.log_chat("USER", complete_text)
                    cls.log(f"[USER] Final transcription saved: {complete_text[:100]}...", "TRANSCRIPTION")
                cls._user_transcription_buffer.clear()
            
            if cls._assistant_transcription_buffer:
                complete_text = " ".join(cls._assistant_transcription_buffer).strip()
                if complete_text:
                    cls.log_chat("ASSISTANT", complete_text)
                    cls.log(f"[ASSISTANT] Final transcription saved: {complete_text[:100]}...", "TRANSCRIPTION")
                cls._assistant_transcription_buffer.clear()
            
            cls._transcription_running = False
            cls._transcription_queue.put(None)  # Poison pill
            if cls._transcription_thread:
                cls._transcription_thread.join(timeout=2)
            cls.log("Transcription system stopped", "TRANSCRIPTION")
    
    @classmethod
    def init(cls):
        """Initialize logger directories and files"""
        # Get the project root directory (parent of Backend)
        project_root = Path(__file__).parent.parent
        
        cls.DATABASE_DIR = project_root / "Database"
        cls.CHATLOGS_DIR = cls.DATABASE_DIR / "Chatlogs"
        cls.TERMINALLOGS_DIR = cls.DATABASE_DIR / "TerminalLogs"
        cls.TOOLLOGS_DIR = cls.DATABASE_DIR / "Tool Logs"
        
        cls.DATABASE_DIR.mkdir(exist_ok=True)
        cls.CHATLOGS_DIR.mkdir(exist_ok=True)
        cls.TERMINALLOGS_DIR.mkdir(exist_ok=True)
        cls.TOOLLOGS_DIR.mkdir(exist_ok=True)
        
        # Create log files with timestamp
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cls.CHAT_LOG_FILE = cls.CHATLOGS_DIR / f"chat_log_{session_timestamp}.txt"
        cls.TERMINAL_LOG_FILE = cls.TERMINALLOGS_DIR / f"terminal_log_{session_timestamp}.txt"
        cls.TOOL_LOG_FILE = cls.TOOLLOGS_DIR / f"tool_log_{session_timestamp}.txt"
        cls.CHATLOGS_JSON_FILE = cls.DATABASE_DIR / "chatlogs.json"
        
        # --- ADDED: Open files and keep handles ---
        # buffering=1 means line-buffered, which flushes on every newline
        cls._chat_log_handle = open(cls.CHAT_LOG_FILE, "a", encoding="utf-8", buffering=1)
        cls._terminal_log_handle = open(cls.TERMINAL_LOG_FILE, "a", encoding="utf-8", buffering=1)
        cls._tool_log_handle = open(cls.TOOL_LOG_FILE, "a", encoding="utf-8", buffering=1)
        
        # Initialize chatlogs.json if it doesn't exist
        if not cls.CHATLOGS_JSON_FILE.exists():
            with open(cls.CHATLOGS_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
        
        print(f"📁 Database directory: {cls.DATABASE_DIR}")
        print(f"💬 Chat log: {cls.CHAT_LOG_FILE.relative_to(project_root)}")
        print(f"📋 Terminal log: {cls.TERMINAL_LOG_FILE.relative_to(project_root)}")
        print(f"🔧 Tool log: {cls.TOOL_LOG_FILE.relative_to(project_root)}")
        print(f"📝 Chatlogs JSON: {cls.CHATLOGS_JSON_FILE.relative_to(project_root)}")
        
        # --- NEW: Initialize transcription system ---
        cls.init_transcription()
    
    # --- ADDED: Close method for graceful shutdown ---
    @classmethod
    def close(cls):
        """Close all open log file handles and stop transcription"""
        # Stop transcription worker
        cls.stop_transcription()
        
        # Close file handles
        if cls._chat_log_handle:
            cls._chat_log_handle.close()
        if cls._terminal_log_handle:
            cls._terminal_log_handle.close()
        if cls._tool_log_handle:
            cls._tool_log_handle.close()
        Logger.log("Logger file handles closed.", "CLEANUP")

    @classmethod
    def load_chatlogs(cls) -> List[Dict]:
        """Load existing chatlogs from JSON file"""
        if cls.CHATLOGS_JSON_FILE and cls.CHATLOGS_JSON_FILE.exists():
            try:
                with open(cls.CHATLOGS_JSON_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading chatlogs.json: {e}")
                return []
        return []
    
    @classmethod
    def save_chat(cls, role: str, content: str):
        """Save a chat message to the persistent JSON log - IMMEDIATE WRITE"""
        if not cls.CHATLOGS_JSON_FILE:
            cls.init()
        
        try:
            # Load existing chatlogs
            chatlogs = cls.load_chatlogs()
            
            # Create new entry with precise timestamp
            now = datetime.now()
            new_entry = {
                "timestamp": now.isoformat(),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "role": role,
                "content": content
            }
            chatlogs.append(new_entry)
            
            # Write immediately to disk (unbuffered) - GUARANTEES persistence
            with open(cls.CHATLOGS_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(chatlogs, f, indent=2, ensure_ascii=False)
                f.flush()  # Force OS to write to disk immediately
                
            # Extra safety: sync to disk (platform-dependent but adds extra reliability)
            try:
                import os
                os.fsync(f.fileno())
            except:
                pass  # Not critical if this fails
            
            # NEW: Notify UI via WebSocket for live updates
            cls._broadcast_new_chatlog(new_entry)
                
        except Exception as e:
            print(f"Error saving to chatlogs.json: {e}")
            # Try to log the error but don't crash
            try:
                import traceback
                print(traceback.format_exc())
            except:
                pass
    
    @classmethod
    def _broadcast_new_chatlog(cls, chatlog_entry: dict):
        """Broadcast new chatlog to UI via WebSocket"""
        try:
            # Import here to avoid circular dependency
            import asyncio
            from main import ws_manager
            
            # Convert to message format for UI
            message = {
                "type": "new_chatlog",
                "payload": {
                    "role": chatlog_entry["role"].lower(),  # user or assistant
                    "content": chatlog_entry["content"],
                    "timestamp": datetime.fromisoformat(chatlog_entry["timestamp"]).timestamp(),
                    "date": chatlog_entry["date"],
                    "time": chatlog_entry["time"]
                }
            }
            
            # Try to broadcast if event loop exists
            try:
                loop = asyncio.get_running_loop()
                # Schedule broadcast in the existing event loop
                asyncio.create_task(ws_manager.broadcast(message))
            except RuntimeError:
                # No running event loop, try to create one
                try:
                    asyncio.run(ws_manager.broadcast(message))
                except:
                    pass  # Silently fail if can't broadcast
                    
        except Exception as e:
            # Don't crash if broadcast fails
            pass
    
    @classmethod
    def search_chatlogs(cls, date: str = None, keyword: str = None, role: str = None) -> List[Dict]:
        """Search chatlogs by date, keyword, or role"""
        chatlogs = cls.load_chatlogs()
        results = []
        
        for log in chatlogs:
            match = True
            
            if date and log.get("date") != date:
                match = False
            
            if keyword and keyword.lower() not in log.get("content", "").lower():
                match = False
            
            if role and log.get("role") != role:
                match = False
            
            if match:
                results.append(log)
        
        return results
    
    @classmethod
    def log(cls, message: str, log_type: str = "INFO"):
        """Log message to terminal and file"""
        if not cls.TERMINAL_LOG_FILE:
            cls.init()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] [{log_type}] {message}"
        
        print(formatted_msg)
        
        try:
            # --- MODIFIED: Use file handle ---
            if cls._terminal_log_handle and not cls._terminal_log_handle.closed:
                cls._terminal_log_handle.write(formatted_msg + "\n")
            # No flush needed due to buffering=1
        except Exception as e:
            print(f"Failed to write to terminal log: {e}")
    
    @classmethod
    def log_chat(cls, role: str, content: str):
        """Log chat messages to chat log file and JSON"""
        if not cls.CHAT_LOG_FILE:
            cls.init()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] {role}: {content}"
        
        # Only save USER and ASSISTANT to chatlogs.json and session chat log
        if role in ["USER", "ASSISTANT"]:
            try:
                # --- MODIFIED: Use file handle ---
                if cls._chat_log_handle and not cls._chat_log_handle.closed:
                    cls._chat_log_handle.write(formatted_msg + "\n")
                # No flush needed
            except Exception as e:
                print(f"Failed to write to chat log: {e}")
            
            cls.save_chat(role, content)
    
    @classmethod
    def log_tool_call(cls, function_name: str, args: Dict[str, Any]):
        """Log tool calls to tool log file"""
        if not cls.TOOL_LOG_FILE:
            cls.init()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] TOOL_CALL: {function_name} | Args: {json.dumps(args, indent=2)}"
        
        try:
            # --- MODIFIED: Use file handle ---
            if cls._tool_log_handle and not cls._tool_log_handle.closed:
                cls._tool_log_handle.write(msg + "\n")
            # No flush needed
        except Exception as e:
            print(f"Failed to write to tool log: {e}")
        
        cls.log(f"Tool Call: {function_name}", "TOOL_CALL")
    
    @classmethod
    def log_tool_result(cls, function_name: str, result: Dict[str, Any]):
        """Log tool results to tool log file"""
        if not cls.TOOL_LOG_FILE:
            cls.init()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] TOOL_RESULT: {function_name} | Result: {json.dumps(result, indent=2)}"
        
        try:
            # --- MODIFIED: Use file handle ---
            if cls._tool_log_handle and not cls._tool_log_handle.closed:
                cls._tool_log_handle.write(msg + "\n")
            # No flush needed
        except Exception as e:
            print(f"Failed to write to tool log: {e}")
        
        cls.log(f"Tool Result: {function_name}", "TOOL_RESULT")
    
    @classmethod
    def log_tool_status(cls, function_name: str, status: str, details: str = ""):
        """Log tool status (working, success, failure, canceled, error)"""
        if not cls.TOOL_LOG_FILE:
            cls.init()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] TOOL_STATUS: {function_name} | Status: {status}"
        if details:
            msg += f" | Details: {details}"
        
        try:
            # --- MODIFIED: Use file handle ---
            if cls._tool_log_handle and not cls._tool_log_handle.closed:
                cls._tool_log_handle.write(msg + "\n")
            # No flush needed
        except Exception as e:
            print(f"Failed to write to tool log: {e}")
        
        cls.log(msg, "TOOL_STATUS")