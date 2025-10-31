# -*- coding: utf-8 -*-
"""
Gemini Brain - Core intelligence system with all features
Handles tool routing and advanced feature integration
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv, set_key
from google import genai

from .Automation import (
    CloseApp, Content, GoogleSearch, OpenApp, PlayYoutube, YouTubeSearch,
    change_windows_theme, click_mouse, create_folder, get_brightness,
    get_clipboard, get_mouse_position, manage_window, move_mouse, open_website,
    set_brightness, set_clipboard, set_system_volume, system_power,
    take_screenshot, type_formatted_text, type_text
)
from .contacts_manager import contacts_manager
from .email_handler import EmailHandler
from .ExcelGenerator import excel_generator
from .FileConverter import file_converter
from .ImageGeneration import image_generation_service
from .llm_handler import llm_handler
from .logger import Logger
from .memory_handler import MemoryHandler
from .PDFGenerator import pdf_generator
from .PPTGenerator import ppt_generator
from .telegram_handler import send_telegram_file, send_telegram_message, telegram_service
from .weather import WeatherTool
from .WordGenerator import word_generator

load_dotenv()

# Import automation functions
try:
    from .Automation import (
        OpenApp, CloseApp, manage_window, set_system_volume, set_brightness,
        get_brightness, change_windows_theme, type_text, move_mouse, click_mouse,
        get_mouse_position, set_clipboard, get_clipboard, take_screenshot,
        system_power, GoogleSearch, YouTubeSearch, PlayYoutube, Content,
        create_folder, send_telegram_message, send_telegram_file
    )
    AUTOMATION_AVAILABLE = True
except ImportError as e:
    AUTOMATION_AVAILABLE = False
    Logger.log(f"Automation features not available: {e}", "WARNING")

# Initialize Gemini client with API key rotation
def get_active_gemini_client():
    """Get Gemini client with active API key"""
    active_key_name = os.getenv("ACTIVE_GOOGLE_API", "GOOGLE_API_KEY_1")
    api_key = os.getenv(active_key_name)
    
    if api_key:
        # --- FIXED: Set environment variable for genai v1.0.0 ---
        os.environ["GEMINI_API_KEY"] = api_key
        Logger.log(f"Gemini client configured with {active_key_name}", "BRAIN")
        # Return the configured module itself for client creation
        return genai
    else:
        Logger.log(f"No API key found for {active_key_name}", "ERROR")
        return None

client_module = get_active_gemini_client()
if not client_module:
    Logger.log("FATAL: Gemini client (genai) could not be configured. Check API keys.", "ERROR")
    client = None
else:
    # This is how the client was created in the original file
    client = client_module.Client(http_options={"api_version": "v1alpha"})


# Get user configuration
username = os.getenv("Username", "Boss")
fullname = "Boss"  # FIXED: Always use Boss
assistantname = os.getenv("Assistantname", "Friday")

# Initialize memory handler at module level
memory_handler = MemoryHandler()

# System instruction with memory and personalization
system_instruction = f"""
You are {assistantname}, a highly advanced AI assistant created to help {fullname}.

PERSONALITY & TONE:
- You are helpful, intelligent, and efficient with a touch of wit.
- **CRITICAL**: You **MUST ALWAYS** address the user as 'Boss' in **EVERY** response.
- You **MUST NOT** call the user by their real name '{fullname}' unless explicitly asked, "What is my name?".
- You are proactive and anticipate needs.
- You have long-term memory. Use it to recall past conversations.

CRITICAL RESPONSE GUIDELINES:
- By default, give SHORT, CONCISE answers (1-2 sentences maximum).
- Only provide detailed explanations when explicitly asked ("explain", "tell me more", "elaborate").
- Get straight to the point.
- ALWAYS use the user's preferred name: 'Boss'.

MEMORY & INTELLIGENCE:
- You have access to past conversations. Use the `recall_chat_history` tool.
- You can access and read **ALL files in the project's 'Data' and 'Database' folders** (including logs). Use `access_file_content` or `search_data_folder`.
- You **MUST** remember files you have generated or converted. When the user says "that file" or "the last file", you must identify it.
- Use `get_last_generated_file` and `get_last_converted_file` to find these files.
- **CRITICAL MEMORY BEHAVIOR**:
  * When the user shares personal information (birthday, preferences, facts about themselves), ALWAYS briefly acknowledge it in your response
  * mem0 will automatically extract and remember important information from our conversations
  * All conversations are automatically saved to long-term memory on session end
  * You don't need to manually save - just have natural conversations and mem0 handles the rest

FILE & DOCUMENT AWARENESS:
- You have FULL awareness of all files in the `Data/GeneratedDocuments`, `Data/ConvertedDocuments`, `Data/GeneratedImages`, and `Data/Screenshots` folders.
- When a user asks to "convert that PDF" after you just generated one, you **MUST** use `get_last_generated_file(file_type='pdf')` to get the path, then use `convert_file_format`.
- When a user asks to "send that file to John", you **MUST** use `get_last_converted_file()` or `get_last_generated_file()` to identify the path, then use `telegram_send_file` or `email_send`.
- Use `search_data_folder` to find files if the user is vague.

CONTACT MANAGEMENT:
- Use `add_contact`, `update_contact`, `find_contact`, `list_contacts`, `delete_contact`.

MULTI-TASKING & SMART TASK EXECUTION:
- Break down complex requests logically (e.g., "Generate X and send to Y" -> generate_X -> get file path -> `find_contact('Y')` -> `telegram_send_file` (or `email_send`).
- "Convert the last PDF to Word" -> `get_last_generated_file(file_type='pdf')` -> `convert_file_format(input_path=..., output_format='docx')`.
- "Send the file I just converted to John via email" -> `get_last_converted_file()` -> `find_contact('John')` -> `email_send(to=johns_email, subject='File', body='Here is the file.', attachments=[file_path])`.

POWER OPERATIONS SECURITY:
- Shutdown, restart, logoff require password via `system_power_secure`. Ask for password if missing.
- Lock, sleep via `system_power_secure` do not require password.

APP & WEBSITE MANAGEMENT:
- "Open X": Use `open_app`. It smartly checks for apps first, then websites.
- "Open X website": Use `open_website_direct`.
- "Search X on Google": Use `Google Search`.
- DO NOT confuse `open_app` with `Google Search`.

TOOL USAGE - CRITICAL:
You MUST use the available tools when appropriate.
- **Weather**: `get_weather`.
- **Current Info/News/Prices/Dates**: **ALWAYS** use `internet_search`. Never use training data for these.
- **Email**: `email_send` (can include attachments), `email_read`, `email_delete`, `email_reply`.
- **Telegram**: `telegram_send_message`, `telegram_send_file`, `telegram_get_updates`.
- **Images**: `generate_image`.
- **Docs**: `generate_pdf`, `generate_word`, `generate_ppt`, `generate_excel`.
- **File Conversion**: `convert_file_format` (the advanced one), `convert_document` (the basic one).
- **File Compression**: `compress_file`.
- **System Automation**: `open_app`, `close_app`, `type_text`, etc.
- **Memory**: `recall_chat_history`.
- **File System**: `access_file_content`, `search_data_folder`.
- **Contacts**: Contact tools.
- **API Keys**: `switch_groq_key`, `switch_google_key`.

INTERNET SEARCH PRIORITY:
- For ANY real-time information (news, weather, prices, dates, current events), ALWAYS use `internet_search`.
- When user says "use internet tool" or "search online", you MUST use `internet_search`.

NOTIFICATION AWARENESS:
- You monitor incoming emails and telegram messages.
- When notified, inform the user proactively and ask for action.

Keep responses conversational but brief unless asked otherwise.
"""

MODEL = "gemini-2.5-flash-native-audio-preview-09-2025" # Updated to a stable, recent model


# Enhanced CONFIG with memory context (like sample agent)
async def get_config_with_memory():
    """
    Get configuration with loaded memory context
    This is called at startup to inject memories into initial system instruction
    """
    memory_context = await memory_handler.get_initial_memory_context()
    
    system_instruction_with_memory = system_instruction
    
    if memory_context:
        # Inject memory context into system instruction (like sample agent)
        system_instruction_with_memory += f"""

MEMORY CONTEXT FROM PREVIOUS SESSIONS:
The user's name is Boss, and here is relevant context about them from previous conversations:
{memory_context}

IMPORTANT - MEMORY & GREETING BEHAVIOR:
- Use this context to provide personalized responses and remember important details about Boss.
- When greeting Boss at the START of a session, if there's an open topic from previous conversations 
  (check 'updated_at' field for latest info), you MAY follow up on it briefly, but:
  * Only if it's truly unresolved or has an expected outcome
  * Don't ask about it again if you already discussed the outcome in a previous session
  * Look at the 'updated_at' timestamps to see what's most recent
  * Keep it natural - if no obvious follow-up, just say "Good evening Boss, how can I assist you today?"
- Always address the user as 'Boss', never use their real name unless asked "What is my name?".
"""
        Logger.log("Memory context injected into system instruction", "MEMORY")
    
    # --- FIXED: Return dictionary in the format expected by config=... ---
    return {
        "system_instruction": system_instruction_with_memory,
        "response_modalities": ["AUDIO"],
        "tools": tools,
    }

# Complete tool definitions
tools = [
    {
        "function_declarations": [
            # Weather
            {
                "name": "get_weather",
                "description": "Get current weather information for a city. MUST be used for weather questions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name (e.g., 'London', 'New York')"}
                    },
                    "required": ["city"]
                }
            },
            # Internet Search
            {
                "name": "internet_search",
                "description": "Search the internet for current information, news, or facts. MUST be used for recent events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },
            # Email Tools
            {
                "name": "email_send",
                "description": "Send an email. Can include attachments.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email(s), comma-separated"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body text"},
                        "cc": {"type": "string", "description": "CC email(s), optional"},
                        "bcc": {"type": "string", "description": "BCC email(s), optional"},
                        "attachments": {"type": "array", "items": {"type": "string"}, "description": "Optional list of file paths to attach."}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "email_read",
                "description": "Read emails from mailbox. Can filter by sender, subject, or date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder": {"type": "string", "description": "Folder (INBOX, SENT, DRAFTS, TRASH)", "default": "INBOX"},
                        "limit": {"type": "integer", "description": "Max emails to retrieve", "default": 10},
                        "unread_only": {"type": "boolean", "description": "Only unread emails", "default": False},
                        "sender": {"type": "string", "description": "Filter by sender, optional"},
                        "subject_filter": {"type": "string", "description": "Filter by subject keyword, optional"}
                    },
                    "required": []
                }
            },
            {
                "name": "email_delete",
                "description": "Delete emails from mailbox.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_id": {"type": "string", "description": "Email ID to delete, optional"},
                        "folder": {"type": "string", "description": "Folder to delete from, optional"},
                        "confirm": {"type": "boolean", "description": "Confirmation flag", "default": False}
                    },
                    "required": ["confirm"]
                }
            },
            {
                "name": "email_reply",
                "description": "Reply to an email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_id": {"type": "string", "description": "Email ID to reply to"},
                        "body": {"type": "string", "description": "Reply message body"},
                        "reply_all": {"type": "boolean", "description": "Reply to all recipients", "default": False}
                    },
                    "required": ["email_id", "body"]
                }
            },
            # Telegram Tools
            {
                "name": "telegram_send_message",
                "description": "Send a message via Telegram. Can compose intelligent messages from prompts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient_name": {"type": "string", "description": "Recipient name"},
                        "message_prompt": {"type": "string", "description": "Message text or concept (e.g., 'birthday wish')"}
                    },
                    "required": ["recipient_name", "message_prompt"]
                }
            },
            {
                "name": "telegram_send_file",
                "description": "Send a file (document, image, video) via Telegram.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient_name": {"type": "string", "description": "Recipient name"},
                        "file_path": {"type": "string", "description": "Full path to file"}
                    },
                    "required": ["recipient_name", "file_path"]
                }
            },
            {
                "name": "telegram_get_updates",
                "description": "Check for new Telegram messages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max messages to check", "default": 10}
                    },
                    "required": []
                }
            },
            # Image Generation
            {
                "name": "generate_image",
                "description": "Generate AI images from text prompts using Stable Diffusion. Default: 1 image. Specify count for multiple.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Description of image to generate"},
                        "count": {"type": "integer", "description": "Number of images (default: 1)", "default": 1},
                        "negative_prompt": {"type": "string", "description": "What to avoid", "default": "bad art"},
                        "send_to_recipient": {"type": "string", "description": "Optional Telegram recipient name"}
                    },
                    "required": ["prompt"]
                }
            },
            # Document Generation
            {
                "name": "generate_pdf",
                "description": "Generate a professional PDF document on any topic. Default: 10 pages. Specify custom page count if needed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Document topic/subject"},
                        "pages": {"type": "integer", "description": "Number of pages (default: 10)", "default": 10}
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "generate_word",
                "description": "Generate a professional Word document (.docx). Default: 10 pages. Specify custom page count if needed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Document topic/subject"},
                        "pages": {"type": "integer", "description": "Number of pages (default: 10)", "default": 10}
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "generate_ppt",
                "description": "Generate a professional PowerPoint presentation (.pptx). Default: 7 slides. Specify custom slide count if needed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Presentation topic/subject"},
                        "slides": {"type": "integer", "description": "Number of slides (default: 7)", "default": 7}
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "generate_excel",
                "description": "Generate a professional Excel spreadsheet (.xlsx) with structured data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Spreadsheet topic/purpose"},
                        "rows": {"type": "integer", "description": "Approximate data rows (default: 20)", "default": 20}
                    },
                    "required": ["topic"]
                }
            },
            # Document Conversion
            {
                "name": "convert_document",
                "description": "Convert documents between formats (PDF, DOCX, PPTX). Windows only.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_path": {"type": "string", "description": "Full path to input file"},
                        "output_format": {"type": "string", "description": "Output format: pdf, docx, or pptx"}
                    },
                    "required": ["input_path", "output_format"]
                }
            },
            {
                "name": "convert_active_doc",
                "description": "Convert the currently active Word or PowerPoint document to another format. Windows only.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "output_format": {"type": "string", "description": "Output format: pdf, docx, or pptx"}
                    },
                    "required": ["output_format"]
                }
            },
            # System Automation
            {
                "name": "open_app",
                "description": "Open a desktop application or website.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "Application name"}
                    },
                    "required": ["app_name"]
                }
            },
            {
                "name": "close_app",
                "description": "Close a running application.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "Application name"}
                    },
                    "required": ["app_name"]
                }
            },
            {
                "name": "manage_window",
                "description": "Control application windows: minimize, maximize, restore, close.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "Application name"},
                        "action": {"type": "string", "description": "Action: minimize, maximize, restore, close"}
                    },
                    "required": ["app_name", "action"]
                }
            },
            {
                "name": "set_volume",
                "description": "Set system volume level (0-100).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "integer", "description": "Volume level 0-100"}
                    },
                    "required": ["level"]
                }
            },
            {
                "name": "set_brightness",
                "description": "Set screen brightness level (0-100).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "integer", "description": "Brightness level 0-100"}
                    },
                    "required": ["level"]
                }
            },
            {
                "name": "get_brightness",
                "description": "Get current screen brightness level.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "change_theme",
                "description": "Change Windows theme to dark or light mode.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mode": {"type": "string", "description": "Theme mode: dark or light"}
                    },
                    "required": ["mode"]
                }
            },
            {
                "name": "type_text",
                "description": "Type text using keyboard automation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to type"},
                        "interval": {"type": "number", "description": "Delay between characters (seconds)", "default": 0.01}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "move_mouse",
                "description": "Move mouse cursor to screen coordinates.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate"},
                        "y": {"type": "integer", "description": "Y coordinate"}
                    },
                    "required": ["x", "y"]
                }
            },
            {
                "name": "click_mouse",
                "description": "Perform mouse click.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "button": {"type": "string", "description": "Button: left, right, middle", "default": "left"},
                        "clicks": {"type": "integer", "description": "Number of clicks", "default": 1}
                    },
                    "required": []
                }
            },
            {
                "name": "get_mouse_position",
                "description": "Get current mouse cursor position.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "set_clipboard",
                "description": "Copy text to system clipboard.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to copy"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "get_clipboard",
                "description": "Get text from system clipboard.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "take_screenshot",
                "description": "Take a screenshot. Can optionally send to Telegram recipient.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "send_to_recipient": {"type": "string", "description": "Optional Telegram recipient name"}
                    },
                    "required": []
                }
            },
            {
                "name": "system_power",
                "description": "System power actions: shutdown, restart, lock, logoff. Windows only.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action: shutdown, restart, lock, logoff"}
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "google_search",
                "description": "Search Google for a query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "youtube_search",
                "description": "Search YouTube for videos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "play_youtube",
                "description": "Play a YouTube video by search query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Video search query"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "generate_content",
                "description": "Generate written content and open in notepad.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Content topic/prompt"}
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "create_folder",
                "description": "Create a new folder. Relative paths created on Desktop.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Folder path (absolute or relative)"}
                    },
                    "required": ["path"]
                }
            },
            # Contacts Management
            {
                "name": "add_contact",
                "description": "Add a new contact with multiple names, phone, telegram ID, and email",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "names": {"type": "array", "items": {"type": "string"}, "description": "List of names/aliases"},
                        "phone": {"type": "string", "description": "Phone number, optional"},
                        "telegram_id": {"type": "string", "description": "Telegram ID, optional"},
                        "email": {"type": "string", "description": "Email address, optional"}
                    },
                    "required": ["names"]
                }
            },
            {
                "name": "update_contact",
                "description": "Update an existing contact",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Current contact name"},
                        "names": {"type": "array", "items": {"type": "string"}, "description": "New names, optional"},
                        "phone": {"type": "string", "description": "New phone, optional"},
                        "telegram_id": {"type": "string", "description": "New telegram ID, optional"},
                        "email": {"type": "string", "description": "New email, optional"}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "find_contact",
                "description": "Find contact information by name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Contact name to search"}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "list_contacts",
                "description": "List all saved contacts",
                "parameters": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "delete_contact",
                "description": "Delete a contact",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Contact name to delete"}
                    },
                    "required": ["name"]
                }
            },
            # Enhanced File Conversion
            {
                "name": "convert_file_format",
                "description": "Convert file between formats (PDF, DOCX, PPTX, XLSX, JPG, PNG, SVG)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_path": {"type": "string", "description": "Input file path"},
                        "output_format": {"type": "string", "description": "Output format"},
                        "compress": {"type": "boolean", "description": "Compress output", "default": False},
                        "quality": {"type": "integer", "description": "Quality 10-100", "default": 85}
                    },
                    "required": ["input_path", "output_format"]
                }
            },
            {
                "name": "compress_file",
                "description": "Compress PDF, JPG, PNG, or SVG file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_path": {"type": "string", "description": "File path to compress"},
                        "compression_percent": {"type": "integer", "description": "Target size 10-100%", "default": 50}
                    },
                    "required": ["input_path"]
                }
            },
            # Enhanced Automation
            {
                "name": "open_website_direct",
                "description": "Open a website directly without search (use when user says 'open X website')",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "website_name": {"type": "string", "description": "Website name or URL"}
                    },
                    "required": ["website_name"]
                }
            },
            {
                "name": "type_formatted_text",
                "description": "Type formatted text like letters, applications at cursor position",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "What to type (e.g. 'formal leave letter')"}
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "system_power_secure",
                "description": "Power operations with password (shutdown, restart, logoff, lock, sleep)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action: shutdown, restart, logoff, lock, sleep"},
                        "password": {"type": "string", "description": "Power password (required for shutdown/restart/logoff)"}
                    },
                    "required": ["action"]
                }
            },
            # Memory and File Access
            {
                "name": "access_file_content",
                "description": "Read content from any file in Friday project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Relative file path from project root"}
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "search_data_folder",
                "description": "Search for files in Data folder by keyword",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "Search keyword"}
                    },
                    "required": ["keyword"]
                }
            },
            {
                "name": "get_accessible_paths",
                "description": "Get all accessible files and folders in Friday project",
                "parameters": {"type": "object", "properties": {}, "required": []}
            },
            # Memory & Chat Recall
            {
                "name": "recall_chat_history",
                "description": "Recall previous conversations by date or keyword. Use this to remember past interactions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Date in YYYY-MM-DD format, optional"},
                        "keyword": {"type": "string", "description": "Keyword to search for in conversations, optional"}
                    },
                    "required": []
                }
            },
             # ADDED FILE TRACKING TOOLS
            {
                "name": "get_last_generated_file",
                "description": "Get the file path of the most recently generated file (PDF, DOCX, PPTX, XLSX, TXT, or Image).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_type": {"type": "string", "description": "Optional: 'pdf', 'word', 'ppt', 'excel', 'image', 'content'. Default is all.", "default": "all"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_last_converted_file",
                "description": "Get the file path of the most recently converted file from the ConvertedDocuments folder.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            },
            # API Key Management
            {
                "name": "switch_groq_key",
                "description": "Switch to a different Groq API key (1-10) for document generation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_number": {"type": "integer", "description": "Key number (1-10)"}
                    },
                    "required": ["key_number"]
                }
            },
            {
                "name": "switch_google_key",
                "description": "Switch to a different Google API key (1-15) for Gemini Live.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_number": {"type": "integer", "description": "Key number (1-15)"}
                    },
                    "required": ["key_number"]
                }
            }
        ]
    }
]

# Initial CONFIG (will be updated by get_config_with_memory)
# --- FIXED: This is now just a placeholder, get_config_with_memory is the source of truth ---
CONFIG = {
    "system_instruction": system_instruction,
    "response_modalities": ["AUDIO"],
    "tools": tools,
}


class GeminiBrain:
    """Core intelligence system that handles tool routing and execution"""

    def __init__(self):
        self.weather_tool = WeatherTool()
        self.email_handler = EmailHandler()
        self.memory_handler = memory_handler # Use the global instance
        self.project_root = Path(__file__).parent.parent
        Logger.log("GeminiBrain initialized with all advanced features", "BRAIN")

    def _get_last_file_from_folders(self, folders: List[Path], file_type: str) -> Optional[str]:
        """Helper to find the most recent file in a list of folders, with optional type filter."""
        all_files = []
        # Define extensions for file types
        ext_map = {
            "pdf": [".pdf"],
            "word": [".docx"],
            "ppt": [".pptx"],
            "excel": [".xlsx"],
            "image": [".jpg", ".jpeg", ".png"],
            "content": [".txt"]
        }
        allowed_extensions = ext_map.get(file_type.lower())

        for folder in folders:
            if folder.exists():
                all_files.extend(folder.glob("*.*")) # Get all files
        
        if not all_files:
            Logger.log("No files found in specified folders.", "BRAIN_HELPER")
            return None

        # Filter by extension if specified
        if file_type.lower() != 'all' and allowed_extensions: # Check if filter needed
            all_files = [f for f in all_files if f.suffix.lower() in allowed_extensions]
            Logger.log(f"Found {len(all_files)} files matching type '{file_type}'.", "BRAIN_HELPER")
        
        if not all_files:
            Logger.log(f"No files found matching type '{file_type}'.", "BRAIN_HELPER")
            return None
            
        # Sort by modification time, newest first
        all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        last_file_path = str(all_files[0].resolve())
        Logger.log(f"Last file found: {last_file_path}", "BRAIN_HELPER")
        return last_file_path # Return absolute path


    def execute_tool(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route tool execution to appropriate handler
        """
        Logger.log(f"Brain executing tool: {function_name}", "BRAIN")
        Logger.log_tool_call(function_name, args)
        
        result: Dict[str, Any] = {"status": "error", "message": f"Tool '{function_name}' is not implemented."} # Default error

        try:
            # Weather
            if function_name == "get_weather":
                result = self.weather_tool.get_weather(args.get("city", ""))
            
            # Internet Search
            elif function_name == "internet_search":
                result = self._internet_search(args.get("query", ""))
            
            # Email Tools
            elif function_name == "email_send":
                result = self.email_handler.send_email(
                    to=args.get("to"),
                    subject=args.get("subject"),
                    body=args.get("body"),
                    cc=args.get("cc"),
                    bcc=args.get("bcc"),
                    attachments=args.get("attachments") # Pass attachments
                )
            elif function_name == "email_read":
                result = self.email_handler.read_emails(
                    folder=args.get("folder", "INBOX"),
                    limit=args.get("limit", 10),
                    unread_only=args.get("unread_only", False),
                    sender=args.get("sender"),
                    subject_filter=args.get("subject_filter")
                )
            elif function_name == "email_delete":
                result = self.email_handler.delete_email(
                    email_id=args.get("email_id"),
                    folder=args.get("folder"),
                    confirm=args.get("confirm", False)
                )
            elif function_name == "email_reply":
                result = self.email_handler.reply_email(
                    email_id=args.get("email_id"),
                    body=args.get("body"),
                    reply_all=args.get("reply_all", False)
                )
            
            # Telegram Tools
            elif function_name == "telegram_send_message":
                try:
                    result_msg, _ = send_telegram_message(
                        args.get("recipient_name"),
                        args.get("message_prompt")
                    )
                    success = "Failed" not in result_msg and "Error" not in result_msg
                    result = {"status": "success" if success else "error", "message": result_msg}
                except Exception as e:
                    result = {"status": "error", "message": f"Telegram send failed: {str(e)}"}

            elif function_name == "telegram_send_file":
                try:
                    result_msg, _ = send_telegram_file(
                        args.get("recipient_name"),
                        args.get("file_path")
                    )
                    success = "Failed" not in result_msg and "Error" not in result_msg
                    result = {"status": "success" if success else "error", "message": result_msg}
                except Exception as e:
                    result = {"status": "error", "message": f"Telegram file send failed: {str(e)}"}

            elif function_name == "telegram_get_updates":
                result = telegram_service.get_updates(args.get("limit", 10))
            
            # Image Generation
            elif function_name == "generate_image":
                result_msg, paths = image_generation_service.generate_images(
                    prompt=args.get("prompt"),
                    count=args.get("count", 1),
                    negative_prompt=args.get("negative_prompt", "bad art"),
                    send_to_recipient=args.get("send_to_recipient")
                )
                result = {"status": "success" if paths else "error", "message": result_msg, "image_paths": paths}
            
            # Document Generation
            elif function_name == "generate_pdf":
                result_msg, file_path = pdf_generator.generate_pdf(
                    topic=args.get("topic"),
                    pages=args.get("pages", 10)
                )
                result = {"status": "success" if file_path else "error", "message": result_msg, "file_path": file_path}
            elif function_name == "generate_word":
                result_msg, file_path = word_generator.generate_word(
                    topic=args.get("topic"),
                    pages=args.get("pages", 10)
                )
                result = {"status": "success" if file_path else "error", "message": result_msg, "file_path": file_path}
            elif function_name == "generate_ppt":
                result_msg, file_path = ppt_generator.generate_ppt(
                    topic=args.get("topic"),
                    slides=args.get("slides", 7)
                )
                result = {"status": "success" if file_path else "error", "message": result_msg, "file_path": file_path}
            elif function_name == "generate_excel":
                result_msg, file_path = excel_generator.generate_excel(
                    topic=args.get("topic"),
                    rows=args.get("rows", 20)
                )
                result = {"status": "success" if file_path else "error", "message": result_msg, "file_path": file_path}
            
            # --- FIXED: Use file_converter instance for this call ---
            elif function_name == "convert_document":
                result_msg, file_path = file_converter.convert_file(
                    input_path=args.get("input_path"),
                    output_format=args.get("output_format")
                )
                result = {"status": "success" if file_path else "error", "message": result_msg, "file_path": file_path}
            
            # --- FIXED: Use file_converter instance for this call ---
            elif function_name == "convert_active_doc":
                result_msg, file_path = file_converter.convert_active_document(
                    output_format=args.get("output_format")
                )
                result = {"status": "success" if file_path else "error", "message": result_msg, "file_path": file_path}
            
            # System Automation Tools
            elif function_name == "open_app":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    try:
                        result_msg, _ = OpenApp(args.get("app_name"))
                        result = {"status": "success", "message": result_msg}
                    except Exception as e:
                        result = {"status": "error", "message": f"Failed to open app: {str(e)}"}
            elif function_name == "close_app":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = CloseApp(args.get("app_name"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "manage_window":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = manage_window(args.get("app_name"), args.get("action"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "set_volume":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = set_system_volume(args.get("level"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "set_brightness":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = set_brightness(args.get("level"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "get_brightness":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = get_brightness()
                    result = {"status": "success", "message": result_msg}
            elif function_name == "change_theme":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = change_windows_theme(args.get("mode"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "type_text":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = type_text(args.get("text"), args.get("interval", 0.01))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "move_mouse":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = move_mouse(args.get("x"), args.get("y"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "click_mouse":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = click_mouse(args.get("button", "left"), args.get("clicks", 1))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "get_mouse_position":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = get_mouse_position()
                    result = {"status": "success", "message": result_msg}
            elif function_name == "set_clipboard":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = set_clipboard(args.get("text"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "get_clipboard":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = get_clipboard()
                    result = {"status": "success", "message": result_msg}
            elif function_name == "take_screenshot":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, file_path = take_screenshot(args.get("send_to_recipient"))
                    result = {"status": "success", "message": result_msg, "file_path": file_path}
            
            # --- This tool is redundant, as system_power_secure handles it. ---
            # --- But keeping it and pointing to the correct function as requested ---
            elif function_name == "system_power":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    # Call the secure function, it will ask for a password if needed
                    result_msg, _ = system_power(args.get("action"), None) 
                    result = {"status": "success", "message": result_msg}
            
            elif function_name == "google_search":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = GoogleSearch(args.get("query"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "youtube_search":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = YouTubeSearch(args.get("query"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "play_youtube":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = PlayYoutube(args.get("query"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "generate_content":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, file_path = Content(args.get("prompt"))
                    result = {"status": "success", "message": result_msg, "file_path": file_path}
            elif function_name == "create_folder":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, folder_path = create_folder(args.get("path"))
                    result = {"status": "success", "message": result_msg, "folder_path": folder_path}
            # Contacts Management
            elif function_name == "add_contact":
                result = contacts_manager.add_contact(**args)
            elif function_name == "update_contact":
                result = contacts_manager.update_contact(**args)
            elif function_name == "find_contact":
                contact = contacts_manager.find_contact(args.get("name"))
                result = {"status": "success" if contact else "error", "contact": contact or "Contact not found."}
            elif function_name == "list_contacts":
                result = contacts_manager.list_all_contacts()
            elif function_name == "delete_contact":
                result = contacts_manager.delete_contact(args.get("name"))
            
            # --- FIXED: Use file_converter instance ---
            elif function_name == "convert_file_format":
                result_msg, file_path = file_converter.convert_file(**args)
                result = {"status": "success" if file_path else "error", "message": result_msg, "file_path": file_path}
            # --- FIXED: Use file_converter instance ---
            elif function_name == "compress_file":
                result_msg, file_path = file_converter.compress_file(**args)
                result = {"status": "success" if file_path else "error", "message": result_msg, "file_path": file_path}
            
            # Enhanced Automation
            elif function_name == "open_website_direct":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = open_website(args.get("website_name"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "type_formatted_text":
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = type_formatted_text(args.get("prompt"))
                    result = {"status": "success", "message": result_msg}
            elif function_name == "system_power_secure": # Secure tool
                if not AUTOMATION_AVAILABLE:
                    result = {"status": "error", "message": "Automation not available"}
                else:
                    result_msg, _ = system_power(args.get("action"), args.get("password"))
                    result = {"status": "success", "message": result_msg}
            # Memory and File Access
            elif function_name == "access_file_content":
                content = self.memory_handler.read_file_content(args.get("file_path"))
                result = {"status": "success" if content and "File not found" not in content else "error", "content": content}
            elif function_name == "search_data_folder":
                files = self.memory_handler.search_in_data_folder(args.get("keyword"))
                result = {"status": "success", "files": files, "count": len(files)}
            elif function_name == "get_accessible_paths":
                paths = self.memory_handler.get_all_accessible_paths()
                result = {"status": "success", "paths": paths}
            
            # --- ADDED FILE TRACKING LOGIC ---
            elif function_name == "get_last_generated_file":
                file_type = args.get("file_type", "all")
                path = self._get_last_file_from_folders(
                    [
                        self.project_root / "Data" / "GeneratedDocuments",
                        self.project_root / "Data" / "GeneratedImages",
                        self.project_root / "Data" / "GeneratedContent"
                    ],
                    file_type
                )
                result = {"status": "success", "file_path": path or "No files found."}
            elif function_name == "get_last_converted_file":
                path = self._get_last_file_from_folders(
                    [self.project_root / "Data" / "ConvertedDocuments"],
                    "all" # Converted folder doesn't need type filter
                )
                result = {"status": "success", "file_path": path or "No files found."}

            # Memory & Chat Recall
            elif function_name == "recall_chat_history":
                chatlogs = self.memory_handler.recall_from_chatlogs(
                    date=args.get("date"),
                    keyword=args.get("keyword")
                )
                formatted_chats = self.memory_handler.format_recalled_chats(chatlogs)
                result = {"status": "success", "message": formatted_chats, "count": len(chatlogs)}
            
            # API Key Management
            elif function_name == "switch_groq_key":
                key_number = args.get("key_number")
                success = llm_handler.switch_to_groq_key(key_number) # Corrected function call
                result = {"status": "success" if success else "error", "message": f"Switched to GROQ key {key_number}." if success else "Failed to switch."}
            elif function_name == "switch_google_key":
                key_number = args.get("key_number")
                if not 1 <= key_number <= 15:
                    result = {"status": "error", "message": "Key number must be 1-15"}
                else:
                    key_name = f"GOOGLE_API_KEY_{key_number}"
                    api_key = os.getenv(key_name)
                    if api_key:
                        dotenv_path = Path(__file__).parent.parent / ".env"
                        set_key(dotenv_path, "ACTIVE_GOOGLE_API", key_name)
                        result = {"status": "success", "message": f"Switched to {key_name}. Restart required."}
                    else:
                        result = {"status": "error", "message": f"{key_name} not set in .env"}
            
            # Default else
            else:
                error_msg = f"Unknown function: {function_name}"
                Logger.log(error_msg, "ERROR")
                result = {"status": "error", "message": error_msg}

        except Exception as e:
            error_msg = f"Error executing {function_name}: {str(e)}"
            Logger.log(error_msg, "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR") # Log full traceback
            result = {"status": "error", "message": error_msg}

        Logger.log_tool_result(function_name, result)
        return result

    def _internet_search(self, query: str) -> Dict[str, Any]:
        """Execute internet search using Tavily API"""
        try:
            from tavily import TavilyClient
        except ImportError:
            Logger.log("Tavily library not installed. pip install tavily-python", "ERROR")
            return {"status": "error", "message": "Tavily library not installed."}

        TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        if not TAVILY_API_KEY:
            return {"status": "error", "message": "TAVILY_API_KEY not configured"}

        try:
            tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
            response = tavily_client.search(
                query=query,
                include_answer=True,
                max_results=5
            )

            results = {
                "status": "success",
                "query": query,
                "answer": response.get('answer', 'No direct answer available'),
                "results": []
            }

            for res in response.get('results', [])[:5]:
                results["results"].append({
                    "title": res.get('title', 'No title'),
                    "url": res.get('url', ''),
                    "content": res.get('content', '')
                })

            return results

        except Exception as e:
            Logger.log(f"Tavily search failed: {str(e)}", "ERROR")
            return {"status": "error", "message": f"Search failed: {str(e)}"}


# Global brain instance
brain = GeminiBrain()