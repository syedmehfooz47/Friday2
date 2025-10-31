# -*- coding: utf-8 -*-
"""
Memory Handler - Long-term memory using Mem0
Stores and retrieves conversation context across sessions with enhanced 
intelligence
"""

import os
import json
import asyncio
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv
from .logger import Logger

load_dotenv()

try:
    from mem0 import AsyncMemoryClient
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    Logger.log("Mem0 not installed. Memory features will be limited.", "WARNING")


class MemoryHandler:
    """Manages long-term memory using Mem0 with enhanced intelligence"""
    
    def __init__(self):
        self.user_name = "Boss"  # FIXED: Always use Boss as username for mem0
        self.mem0_client = None
        self.project_root = Path(__file__).parent.parent
        self.data_folder = self.project_root / "Data"
        self.database_folder = self.project_root / "Database"
        self.cached_memory_str = ""  # Store initial memory string to filter it out later
        
        if MEM0_AVAILABLE:
            try:
                # AsyncMemoryClient reads MEM0_API_KEY from environment automatically
                self.mem0_client = AsyncMemoryClient()
                Logger.log("Mem0 AsyncMemoryClient initialized successfully", "MEMORY")
            except Exception as e:
                Logger.log(f"Failed to initialize Mem0: {e}. Make sure MEM0_API_KEY is set in .env", "ERROR")
                self.mem0_client = None
        else:
            Logger.log("Install mem0ai package for memory features: pip install mem0ai", "INFO")
    
    async def add_conversation_batch(self, messages_list: List[Dict[str, str]]):
        """
        Add batch of conversations to memory on shutdown (like sample agent)
        Filters out the initial memory context to avoid duplication
        """
        if not self.mem0_client:
            Logger.log("Mem0 client not initialized - cannot save memories", "WARNING")
            return
        
        if not messages_list:
            Logger.log("No messages to save to memory", "MEMORY")
            return
        
        try:
            Logger.log(f"Raw messages list has {len(messages_list)} items", "MEMORY")
            
            # Filter out any messages that contain the cached memory string
            # This prevents re-saving the initial context
            filtered_messages = []
            for msg in messages_list:
                content_str = msg.get("content", "")
                
                # Skip if this message contains the initial memory context
                if self.cached_memory_str and self.cached_memory_str in content_str:
                    Logger.log("Skipping memory context message from being re-saved", "MEMORY")
                    continue
                
                # Only save user and assistant messages
                if msg.get("role") in ['user', 'assistant']:
                    filtered_messages.append({
                        "role": msg["role"],
                        "content": content_str.strip()
                    })
            
            if filtered_messages:
                Logger.log(f"Formatted messages to add to memory: {filtered_messages}", "MEMORY")
                Logger.log(f"Saving {len(filtered_messages)} messages to memory for user: Boss", "MEMORY")
                
                # Save to mem0 with user_id="Boss" using latest API (v2, output_format v1.1)
                await self.mem0_client.add(
                    filtered_messages, 
                    user_id="Boss",
                    version="v2",
                    output_format="v1.1"
                )
                Logger.log("Conversation batch saved to memory successfully", "MEMORY")
            else:
                Logger.log("No new messages to save to memory after filtering", "MEMORY")
                
        except Exception as e:
            Logger.log(f"Error adding conversation batch to memory: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
    
    async def sync_chatlogs_to_memory(self, limit: int = 100):
        """
        Sync recent conversations from chatlogs.json to mem0
        This allows transcribed conversations to be saved to long-term memory
        """
        if not self.mem0_client:
            Logger.log("Mem0 client not initialized - cannot sync", "WARNING")
            return
        
        try:
            # Load recent chatlogs
            chatlogs_file = self.database_folder / "chatlogs.json"
            if not chatlogs_file.exists():
                Logger.log("No chatlogs.json found - nothing to sync", "MEMORY")
                return
            
            with open(chatlogs_file, 'r', encoding='utf-8') as f:
                chatlogs = json.load(f)
            
            if not chatlogs:
                Logger.log("Chatlogs.json is empty - nothing to sync", "MEMORY")
                return
            
            # Filter to only get NEW format entries (with direct role/content/timestamp fields)
            # Skip old format entries with session_timestamp
            valid_chatlogs = [
                log for log in chatlogs
                if "role" in log and "content" in log and "timestamp" in log
            ]
            
            Logger.log(f"Found {len(valid_chatlogs)} valid chatlog entries (filtered from {len(chatlogs)} total)", "MEMORY")
            
            # Get recent messages (last N entries)
            recent_logs = valid_chatlogs[-limit:] if len(valid_chatlogs) > limit else valid_chatlogs
            
            # Convert to mem0 format
            messages = []
            for log in recent_logs:
                role = log.get("role", "").lower()
                content = log.get("content", "").strip()
                
                if role in ["user", "assistant"] and content:
                    messages.append({
                        "role": role,
                        "content": content
                    })
            
            if messages:
                Logger.log(f"Syncing {len(messages)} messages from chatlogs to memory", "MEMORY")
                Logger.log(f"Sample messages: {messages[:3]}", "MEMORY")  # Debug: show first 3 messages
                await self.mem0_client.add(
                    messages,
                    user_id="Boss",
                    version="v2",
                    output_format="v1.1"
                )
                Logger.log("✅ Chatlogs synced to memory successfully", "MEMORY")
            else:
                Logger.log("No valid messages to sync from chatlogs", "MEMORY")
                
        except Exception as e:
            Logger.log(f"Error syncing chatlogs to memory: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
    
    async def get_initial_memory_context(self) -> str:
        """
        Retrieve all memories at startup (like sample agent)
        Returns formatted JSON string with memories and caches it
        """
        if not self.mem0_client:
            Logger.log("Mem0 client not initialized - cannot retrieve memories", "WARNING")
            return ""
        
        try:
            Logger.log("Fetching all memories for user: Boss", "MEMORY")
            results = await self.mem0_client.get_all(user_id="Boss")
            Logger.log(f"Mem0 returned {len(results) if results else 0} results", "MEMORY")
            
            if results:
                memories = [
                    {
                        "memory": result.get("memory", ""),
                        "updated_at": result.get("updated_at", "")
                    }
                    for result in results
                ]
                memory_str = json.dumps(memories, indent=2)
                self.cached_memory_str = memory_str  # Cache to filter out later
                Logger.log(f"Retrieved {len(memories)} memories for Boss", "MEMORY")
                Logger.log(f"Memory content preview: {memory_str[:200]}...", "MEMORY")
                return memory_str
            else:
                Logger.log("No memories found for Boss", "MEMORY")
                return ""
        except Exception as e:
            Logger.log(f"Error retrieving memory: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
            return ""
    
    async def get_memory_context(self) -> str:
        """
        Retrieve memory context for the user (backward compatibility)
        Just calls get_initial_memory_context
        """
        return await self.get_initial_memory_context()
    
    def get_latest_memory_for_greeting(self, memory_str: str) -> Optional[Dict]:
        """
        Extract the latest memory from memory context for greeting follow-up
        Returns the most recent memory with an open topic (like sample agent)
        """
        if not memory_str:
            return None
        
        try:
            memories = json.loads(memory_str)
            if not memories:
                return None
            
            # Sort by updated_at to get latest
            sorted_memories = sorted(
                memories, 
                key=lambda x: x.get("updated_at", ""),
                reverse=True
            )
            
            # Return the most recent memory
            if sorted_memories:
                return sorted_memories[0]
            
        except Exception as e:
            Logger.log(f"Error parsing memories for greeting: {e}", "ERROR")
        
        return None
    
    def recall_from_chatlogs(self, date: str = None, keyword: str = None) -> List[Dict]:
        """Recall conversations from chatlogs.json"""
        try:
            results = Logger.search_chatlogs(date=date, keyword=keyword)
            Logger.log(f"Found {len(results)} matching chatlogs", "MEMORY")
            return results
        except Exception as e:
            Logger.log(f"Error recalling from chatlogs: {e}", "ERROR")
            return []
    
    def format_recalled_chats(self, chatlogs: List[Dict]) -> str:
        """Format recalled chats for display"""
        if not chatlogs:
            return "No matching conversations found."
        
        formatted = []
        for log in chatlogs[:20]:  # Limit to 20 most recent
            timestamp = log.get("timestamp", "Unknown time")
            role = log.get("role", "Unknown")
            content = log.get("content", "")
            formatted.append(f"[{timestamp}] {role}: {content}")
        
        return "\n".join(formatted)
    
    def get_all_accessible_paths(self) -> Dict[str, List[str]]:
        """Get all accessible files and folders in Friday project"""
        accessible_paths = {
            "data_folder": [],
            "database_folder": [],
            "chatlogs": [],
            "terminal_logs": [],
            "tool_logs": []
        }
        
        try:
            # Data folder
            if self.data_folder.exists():
                for item in self.data_folder.rglob("*"):
                    if item.is_file():
                        accessible_paths["data_folder"].append(str(item.relative_to(self.project_root)))
            
            # Database folder
            if self.database_folder.exists():
                for item in self.database_folder.rglob("*"):
                    if item.is_file():
                        accessible_paths["database_folder"].append(str(item.relative_to(self.project_root)))
            
            # Session chatlogs
            chatlogs_dir = self.database_folder / "Chatlogs"
            if chatlogs_dir.exists():
                accessible_paths["chatlogs"] = [str(f.relative_to(self.project_root)) 
                                                for f in chatlogs_dir.glob("*.txt")]
            
            # Terminal logs
            terminal_logs_dir = self.database_folder / "TerminalLogs"
            if terminal_logs_dir.exists():
                accessible_paths["terminal_logs"] = [str(f.relative_to(self.project_root)) 
                                                     for f in terminal_logs_dir.glob("*.txt")]
            
            # Tool logs
            tool_logs_dir = self.database_folder / "Tool Logs"
            if tool_logs_dir.exists():
                accessible_paths["tool_logs"] = [str(f.relative_to(self.project_root)) 
                                                 for f in tool_logs_dir.glob("*.txt")]
            
            Logger.log(f"Retrieved accessible paths: {len(accessible_paths['data_folder'])} data files, "
                       f"{len(accessible_paths['database_folder'])} database files", "MEMORY")
            
            return accessible_paths
        except Exception as e:
            Logger.log(f"Error getting accessible paths: {e}", "ERROR")
            return accessible_paths
    
    def read_file_content(self, file_path: str) -> str:
        """Read content from a file"""
        try:
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.is_file():
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                Logger.log(f"Read file: {file_path}", "MEMORY")
                return content
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            Logger.log(f"Error reading file {file_path}: {e}", "ERROR")
            return f"Error reading file: {e}"
    
    def search_in_data_folder(self, keyword: str) -> List[str]:
        """Search for files containing keyword in Data folder"""
        results = []
        try:
            if self.data_folder.exists():
                for file_path in self.data_folder.rglob("*"):
                    if file_path.is_file():
                        if keyword.lower() in file_path.name.lower():
                            results.append(str(file_path.relative_to(self.project_root)))
            
            Logger.log(f"Found {len(results)} files matching '{keyword}'", "MEMORY")
            return results
        except Exception as e:
            Logger.log(f"Error searching in data folder: {e}", "ERROR")
            return results