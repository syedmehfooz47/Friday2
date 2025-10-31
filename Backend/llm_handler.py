# -*- coding: utf-8 -*-
"""
LLM Handler - Groq and Google API with automatic key rotation
Handles document generation and content creation
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv, set_key
from pathlib import Path
from .logger import Logger

load_dotenv()

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Logger.log("Groq not installed. Install with: pip install groq", "ERROR")

try:
    from google import genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    Logger.log("Google GenAI not installed", "ERROR")


class LLMHandler:
    """Manages Groq and Google API with automatic key rotation"""
    
    def __init__(self):
        self.current_groq_key_index = 1
        self.current_google_key_index = 1
        self.max_groq_keys = 10
        self.max_google_keys = 15
        self.groq_client = None
        self.google_client = None
        self.dotenv_path = Path(__file__).parent.parent / ".env"
        self.current_provider = "groq"  # or "google"
        
        if GROQ_AVAILABLE:
            self._initialize_groq_client()
        
        if GOOGLE_AVAILABLE:
            self._initialize_google_client()
    
    def _initialize_groq_client(self):
        """Initialize Groq client with current active key"""
        active_key_name = os.getenv("ACTIVE_GROQ_API", "GROQ_API_KEY_1")
        api_key = os.getenv(active_key_name)
        
        if api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                self.current_groq_key_index = int(active_key_name.split("_")[-1])
                Logger.log(f"Groq client initialized with {active_key_name}", "LLM")
            except Exception as e:
                Logger.log(f"Failed to initialize Groq client: {e}", "ERROR")
        else:
            Logger.log(f"No API key found for {active_key_name}", "ERROR")
    
    def _initialize_google_client(self):
        """Initialize Google client with current active key"""
        active_key_name = os.getenv("ACTIVE_GOOGLE_API", "GOOGLE_API_KEY_1")
        api_key = os.getenv(active_key_name)
        
        if api_key:
            try:
                os.environ["GEMINI_API_KEY"] = api_key
                self.google_client = genai.Client(http_options={"api_version": "v1alpha"})
                self.current_google_key_index = int(active_key_name.split("_")[-1])
                Logger.log(f"Google client initialized with {active_key_name}", "LLM")
            except Exception as e:
                Logger.log(f"Failed to initialize Google client: {e}", "ERROR")
        else:
            Logger.log(f"No API key found for {active_key_name}", "ERROR")
    
    def _rotate_groq_key(self) -> bool:
        """Rotate to next available Groq API key"""
        for i in range(1, self.max_groq_keys + 1):
            next_index = (self.current_groq_key_index % self.max_groq_keys) + 1
            key_name = f"GROQ_API_KEY_{next_index}"
            api_key = os.getenv(key_name)
            
            if api_key:
                try:
                    test_client = Groq(api_key=api_key)
                    set_key(self.dotenv_path, "ACTIVE_GROQ_API", key_name)
                    
                    self.groq_client = test_client
                    self.current_groq_key_index = next_index
                    Logger.log(f"Rotated to {key_name}", "LLM")
                    return True
                except Exception as e:
                    Logger.log(f"Key {key_name} failed: {e}", "ERROR")
                    self.current_groq_key_index = next_index
                    continue
            else:
                self.current_groq_key_index = next_index
        
        Logger.log("No working Groq API keys available", "ERROR")
        return False
    
    def _rotate_google_key(self) -> bool:
        """Rotate to next available Google API key"""
        for i in range(1, self.max_google_keys + 1):
            next_index = (self.current_google_key_index % self.max_google_keys) + 1
            key_name = f"GOOGLE_API_KEY_{next_index}"
            api_key = os.getenv(key_name)
            
            if api_key:
                try:
                    os.environ["GEMINI_API_KEY"] = api_key
                    test_client = genai.Client(http_options={"api_version": "v1alpha"})
                    set_key(self.dotenv_path, "ACTIVE_GOOGLE_API", key_name)
                    
                    self.google_client = test_client
                    self.current_google_key_index = next_index
                    Logger.log(f"Rotated to {key_name}", "LLM")
                    return True
                except Exception as e:
                    Logger.log(f"Key {key_name} failed: {e}", "ERROR")
                    self.current_google_key_index = next_index
                    continue
            else:
                self.current_google_key_index = next_index
        
        Logger.log("No working Google API keys available", "ERROR")
        return False
    
    def switch_to_groq_key(self, key_number: int) -> bool:
        """Manually switch to a specific Groq key"""
        if not 1 <= key_number <= self.max_groq_keys:
            Logger.log(f"Invalid key number: {key_number}", "ERROR")
            return False
        
        key_name = f"GROQ_API_KEY_{key_number}"
        api_key = os.getenv(key_name)
        
        if api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                set_key(self.dotenv_path, "ACTIVE_GROQ_API", key_name)
                self.current_groq_key_index = key_number
                self.current_provider = "groq"
                Logger.log(f"Switched to {key_name}", "LLM")
                return True
            except Exception as e:
                Logger.log(f"Failed to switch to {key_name}: {e}", "ERROR")
                return False
        else:
            Logger.log(f"{key_name} not set in .env", "ERROR")
            return False
    
    def switch_to_google_key(self, key_number: int) -> bool:
        """Manually switch to a specific Google key"""
        if not 1 <= key_number <= self.max_google_keys:
            Logger.log(f"Invalid key number: {key_number}", "ERROR")
            return False
        
        key_name = f"GOOGLE_API_KEY_{key_number}"
        api_key = os.getenv(key_name)
        
        if api_key:
            try:
                os.environ["GEMINI_API_KEY"] = api_key
                self.google_client = genai.Client(http_options={"api_version": "v1alpha"})
                set_key(self.dotenv_path, "ACTIVE_GOOGLE_API", key_name)
                self.current_google_key_index = key_number
                self.current_provider = "google"
                Logger.log(f"Switched to {key_name}", "LLM")
                return True
            except Exception as e:
                Logger.log(f"Failed to switch to {key_name}: {e}", "ERROR")
                return False
        else:
            Logger.log(f"{key_name} not set in .env", "ERROR")
            return False
    
    def get_response(self, messages: List[Dict], model: str = None, 
                     max_tokens: int = 8000, temperature: float = 0.7) -> str:
        """
        Get response from LLM API with automatic key rotation and provider fallback
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (optional)
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0-2)
            
        Returns:
            Generated text response
        """
        # Try current provider first
        if self.current_provider == "groq" and self.groq_client:
            result = self._get_groq_response(messages, model, max_tokens, temperature)
            if not result.startswith("Error"):
                return result
            
            # Try Google as fallback
            if self.google_client:
                Logger.log("Groq failed, switching to Google", "LLM")
                self.current_provider = "google"
                return self._get_google_response(messages, model, max_tokens, temperature)
        
        elif self.current_provider == "google" and self.google_client:
            result = self._get_google_response(messages, model, max_tokens, temperature)
            if not result.startswith("Error"):
                return result
            
            # Try Groq as fallback
            if self.groq_client:
                Logger.log("Google failed, switching to Groq", "LLM")
                self.current_provider = "groq"
                return self._get_groq_response(messages, model, max_tokens, temperature)
        
        return "Error: No working LLM provider available"
    
    def _get_groq_response(self, messages: List[Dict], model: str = None,
                           max_tokens: int = 8000, temperature: float = 0.7) -> str:
        """Get response from Groq"""
        if not self.groq_client:
            return "Error: Groq client not initialized"
        
        if not model:
            model = "llama-3.3-70b-versatile"
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                Logger.log(f"Requesting Groq response (attempt {attempt + 1}/{max_retries})", "LLM")
                
                chat_completion = self.groq_client.chat.completions.create(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                response = chat_completion.choices[0].message.content
                Logger.log("Groq response received successfully", "LLM")
                return response
            
            except Exception as e:
                error_msg = str(e).lower()
                Logger.log(f"Groq request failed: {e}", "ERROR")
                
                if "rate" in error_msg or "quota" in error_msg or "limit" in error_msg:
                    Logger.log("Rate limit detected, rotating Groq key...", "LLM")
                    if self._rotate_groq_key():
                        continue
                    else:
                        return f"Error: All Groq API keys exhausted"
                else:
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return f"Error generating Groq response: {e}"
        
        return "Error: Failed to generate Groq response after all retries"
    
    def _get_google_response(self, messages: List[Dict], model: str = None,
                             max_tokens: int = 8000, temperature: float = 0.7) -> str:
        """Get response from Google Gemini"""
        if not self.google_client:
            return "Error: Google client not initialized"
        
        if not model:
            model = "gemini-2.0-flash-exp"
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                Logger.log(f"Requesting Google response (attempt {attempt + 1}/{max_retries})", "LLM")
                
                # Convert messages to Google format
                contents = []
                for msg in messages:
                    contents.append({
                        "role": "user" if msg["role"] == "user" else "model",
                        "parts": [{"text": msg["content"]}]
                    })
                
                response = self.google_client.models.generate_content(
                    model=model,
                    contents=contents,
                    config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature
                    }
                )
                
                result = response.text
                Logger.log("Google response received successfully", "LLM")
                return result
            
            except Exception as e:
                error_msg = str(e).lower()
                Logger.log(f"Google request failed: {e}", "ERROR")
                
                if "rate" in error_msg or "quota" in error_msg or "limit" in error_msg:
                    Logger.log("Rate limit detected, rotating Google key...", "LLM")
                    if self._rotate_google_key():
                        continue
                    else:
                        return f"Error: All Google API keys exhausted"
                else:
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return f"Error generating Google response: {e}"
        
        return "Error: Failed to generate Google response after all retries"
    
    def get_current_key_info(self) -> Dict:
        """Get information about current active keys"""
        return {
            "provider": self.current_provider,
            "groq": {
                "active_key": f"GROQ_API_KEY_{self.current_groq_key_index}",
                "key_number": self.current_groq_key_index,
                "total_keys": self.max_groq_keys
            },
            "google": {
                "active_key": f"GOOGLE_API_KEY_{self.current_google_key_index}",
                "key_number": self.current_google_key_index,
                "total_keys": self.max_google_keys
            }
        }


# Global instance
llm_handler = LLMHandler()