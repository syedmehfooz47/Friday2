# -*- coding: utf-8 -*-
"""
Advanced Telegram Handler - Send/receive messages, files with contact auto-save
"""

import os
import asyncio
import threading
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from .logger import Logger
# Import contacts manager for auto-saving
try:
    from .contacts_manager import contacts_manager
    CONTACTS_AVAILABLE = True
except ImportError:
    CONTACTS_AVAILABLE = False
    Logger.log("Contacts manager not found. Telegram auto-save disabled.", "WARNING")

load_dotenv()

try:
    from telegram import Bot, Update
    from telegram.ext import Application, MessageHandler, filters, ContextTypes
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    Logger.log("python-telegram-bot not installed", "ERROR")


class TelegramHandler:
    """Advanced Telegram integration"""
    
    def __init__(self):
        self.bot = None
        self.application = None
        self.default_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.received_messages_folder = Path(__file__).parent.parent / "Database" / "TelegramMessages"
        self.received_messages_folder.mkdir(parents=True, exist_ok=True)
        self._event_loop = None
        self._loop_thread = None
        
        if TELEGRAM_AVAILABLE:
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            
            if bot_token:
                try:
                    self.bot = Bot(token=bot_token)
                    # --- ADDED: Application build for receiving messages ---
                    self.application = Application.builder().token(bot_token).build()
                    
                    # --- ADDED: Message Handlers ---
                    self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text_message))
                    self.application.add_handler(MessageHandler(filters.PHOTO, self._handle_photo_message))
                    self.application.add_handler(MessageHandler(filters.Document.ALL, self._handle_document_message))
                    
                    Logger.log("Telegram bot initialized successfully", "TELEGRAM")
                    
                    # --- ADDED: Start polling in a background thread ---
                    self._start_polling_thread()
                    
                except Exception as e:
                    Logger.log(f"Failed to initialize Telegram bot: {e}", "ERROR")
            else:
                Logger.log("TELEGRAM_BOT_TOKEN not set in .env", "WARNING")
        else:
            Logger.log("Telegram features disabled", "WARNING")
    
    # --- ADDED: Thread-safe async loop management ---
    def _run_async_in_thread(self, coro):
        """Run coroutine in the dedicated event loop"""
        if not self._event_loop:
            Logger.log("Telegram event loop not running.", "ERROR")
            return
        
        asyncio.run_coroutine_threadsafe(coro, self._event_loop)

    def _start_polling_thread(self):
        """Starts the asyncio event loop for polling in a separate thread"""
        def loop_in_thread():
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            Logger.log("Telegram polling event loop started.", "TELEGRAM")
            try:
                self._event_loop.run_until_complete(self._start_polling())
            except Exception as e:
                Logger.log(f"Telegram polling loop error: {e}", "ERROR")
            finally:
                self._event_loop.close()
                Logger.log("Telegram polling event loop closed.", "TELEGRAM")

        self._loop_thread = threading.Thread(target=loop_in_thread, daemon=True)
        self._loop_thread.start()

    async def _start_polling(self):
        """Start polling for updates"""
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            Logger.log("Telegram polling started", "TELEGRAM")
            # Keep the loop running
            while True:
                await asyncio.sleep(3600)
        except Exception as e:
            # Suppress Telegram conflict errors (multiple instances running)
            if "Conflict" in str(e) or "terminated by other getUpdates" in str(e):
                Logger.log("Telegram bot conflict detected - another instance may be running", "WARNING")
            else:
                Logger.log(f"Error starting polling: {e}", "ERROR")
            
    async def _handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        try:
            message = update.message
            user = message.from_user
            text = message.text
            chat_id = message.chat_id
            
            Logger.log(f"Received message from {user.first_name} ({chat_id}): {text}", "TELEGRAM")
            
            # Save message
            msg_file = self.received_messages_folder / f"message_{message.message_id}.txt"
            with open(msg_file, "w", encoding="utf-8") as f:
                f.write(f"From: {user.first_name} {user.last_name or ''}\n")
                f.write(f"Chat ID: {chat_id}\n")
                f.write(f"Username: @{user.username}\n")
                f.write(f"Message: {text}\n")
            
            # --- ADDED: Auto-save contact if new ---
            if CONTACTS_AVAILABLE:
                contact_name = user.first_name or user.username or str(chat_id)
                contact = contacts_manager.find_contact(contact_name)
                if not contact:
                    contacts_manager.add_contact(
                        names=[contact_name],
                        telegram_id=str(chat_id)
                    )
                    Logger.log(f"Auto-saved new contact: {contact_name}", "TELEGRAM")
                    # TODO: Implement notification for main.py to inform user
            
        except Exception as e:
            Logger.log(f"Error handling text message: {e}", "ERROR")
            
    async def _handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming photos"""
        try:
            message = update.message
            user = message.from_user
            
            photo = message.photo[-1]  # Get highest resolution
            file = await context.bot.get_file(photo.file_id)
            
            file_path = self.received_messages_folder / f"photo_{message.message_id}.jpg"
            await file.download_to_drive(str(file_path))
            
            Logger.log(f"Received photo from {user.first_name}: {file_path}", "TELEGRAM")
        except Exception as e:
            Logger.log(f"Error handling photo: {e}", "ERROR")
            
    async def _handle_document_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming documents"""
        try:
            message = update.message
            user = message.from_user
            
            document = message.document
            file = await context.bot.get_file(document.file_id)
            
            file_path = self.received_messages_folder / document.file_name
            await file.download_to_drive(str(file_path))
            
            Logger.log(f"Received document from {user.first_name}: {file_path}", "TELEGRAM")
        except Exception as e:
            Logger.log(f"Error handling document: {e}", "ERROR")

    def _get_chat_id(self, recipient_name: Optional[str] = None) -> Optional[str]:
        """Get chat ID from contact or use default"""
        if recipient_name and CONTACTS_AVAILABLE:
            from .contacts_manager import contacts_manager
            contact = contacts_manager.find_contact(recipient_name)
            if contact and contact.get("telegram_id"):
                return contact.get("telegram_id")
        
        return self.default_chat_id
    
    def send_message(self, recipient_name: str, message: str) -> bool:
        """Send a text message"""
        if not self.bot:
            Logger.log("Telegram bot not initialized", "ERROR")
            return False
        
        chat_id = self._get_chat_id(recipient_name)
        
        if not chat_id:
            Logger.log(f"No chat ID found for {recipient_name}", "ERROR")
            return False
        
        try:
            Logger.log(f"Sending Telegram message to {recipient_name} ({chat_id})", "TELEGRAM")
            # --- MODIFIED: Use thread-safe async call ---
            self._run_async_in_thread(self._send_message_async(chat_id, message))
            Logger.log("Telegram message send task scheduled", "TELEGRAM")
            return True
        except Exception as e:
            Logger.log(f"Failed to send Telegram message: {e}", "ERROR")
            return False
    
    async def _send_message_async(self, chat_id: str, message: str):
        """Async send message"""
        await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    
    def send_file(self, recipient_name: str, file_path: str, caption: Optional[str] = None) -> bool:
        """Send a file"""
        if not self.bot:
            Logger.log("Telegram bot not initialized", "ERROR")
            return False
        
        if not os.path.exists(file_path):
            Logger.log(f"File not found: {file_path}", "ERROR")
            return False
        
        chat_id = self._get_chat_id(recipient_name)
        
        if not chat_id:
            Logger.log(f"No chat ID found for {recipient_name}", "ERROR")
            return False
        
        try:
            Logger.log(f"Sending file '{file_path}' to {recipient_name}", "TELEGRAM")
            
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                self._run_async_in_thread(self._send_photo_async(chat_id, file_path, caption))
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                self._run_async_in_thread(self._send_video_async(chat_id, file_path, caption))
            else:
                self._run_async_in_thread(self._send_document_async(chat_id, file_path, caption))
            
            Logger.log("File send task scheduled via Telegram", "TELEGRAM")
            return True
        except Exception as e:
            Logger.log(f"Failed to send file via Telegram: {e}", "ERROR")
            return False
    
    async def _send_photo_async(self, chat_id: str, file_path: str, caption: Optional[str]):
        """Async send photo"""
        with open(file_path, 'rb') as photo:
            await self.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)
    
    async def _send_video_async(self, chat_id: str, file_path: str, caption: Optional[str]):
        """Async send video"""
        with open(file_path, 'rb') as video:
            await self.bot.send_video(chat_id=chat_id, video=video, caption=caption)
    
    async def _send_document_async(self, chat_id: str, file_path: str, caption: Optional[str]):
        """Async send document"""
        with open(file_path, 'rb') as document:
            await self.bot.send_document(chat_id=chat_id, document=document, caption=caption)
    
    def get_updates(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent updates"""
        if not self.bot:
            return {"status": "error", "message": "Bot not initialized"}
        
        try:
            updates = self._run_async(self._get_updates_async(limit))
            
            messages = []
            for update in updates:
                if update.message:
                    messages.append({
                        "message_id": update.message.message_id,
                        "from": update.message.from_user.first_name if update.message.from_user else "Unknown",
                        "text": update.message.text,
                        "date": update.message.date.isoformat() if update.message.date else ""
                    })
            
            Logger.log(f"Retrieved {len(messages)} Telegram updates", "TELEGRAM")
            return {"status": "success", "messages": messages, "count": len(messages)}
        except Exception as e:
            Logger.log(f"Failed to get Telegram updates: {e}", "ERROR")
            return {"status": "error", "message": str(e)}
    
    async def _get_updates_async(self, limit: int):
        """Async get updates"""
        return await self.bot.get_updates(limit=limit)


# Global instance
telegram_service = TelegramHandler()