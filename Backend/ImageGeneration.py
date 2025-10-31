# -*- coding: utf-8 -*-
"""
Image Generation Service - HuggingFace Stable Diffusion
Generates high-quality images from text prompts
"""

import os
import sys
import time
import asyncio
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv
from .logger import Logger

load_dotenv()

API_KEY = os.getenv("HuggingFaceAPIKey")
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}


class ImageGenerationService:
    """Generate images using HuggingFace Stable Diffusion"""
    
    def __init__(self):
        if not API_KEY:
            Logger.log("HuggingFaceAPIKey not found in .env file. Image Generation will fail.", "ERROR")
        
        self.data_folder = Path(__file__).parent.parent / "Data" / "GeneratedImages"
        self.data_folder.mkdir(parents=True, exist_ok=True)
    
    def _open_image(self, image_path: str):
        """Open image in default viewer"""
        try:
            if sys.platform == "win32":
                os.startfile(image_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", image_path])
            else:
                subprocess.run(["xdg-open", image_path])
        except Exception as e:
            Logger.log(f"Unable to open {image_path}: {e}", "ERROR")
    
    async def _query_api(self, payload: dict) -> bytes:
        """Query HuggingFace API"""
        if not headers:
            return None
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    requests.post, API_URL, headers=headers, json=payload, timeout=180
                )
                
                if response.status_code == 200:
                    return response.content
                elif response.status_code >= 500:
                    Logger.log(
                        f"API request failed with server error {response.status_code} on attempt {attempt + 1}/{max_retries}.",
                        "WARNING"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(5 * (attempt + 1))
                    continue
                else:
                    Logger.log(f"API request failed with status {response.status_code}: {response.text}", "ERROR")
                    return None
            except requests.exceptions.RequestException as e:
                Logger.log(f"API request failed on attempt {attempt + 1}/{max_retries}: {e}", "ERROR")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5 * (attempt + 1))
        
        Logger.log("API request failed after all retries.", "ERROR")
        return None
    
    async def _generate_single_image(self, prompt: str, negative_prompt: str) -> str:
        """Generate a single image"""
        payload = {
            "inputs": f"4k photo of {prompt}, professional, rich colors, sharp focus",
            "parameters": {
                "negative_prompt": f"blurry, cartoon, disfigured, deformed, ugly, {negative_prompt}",
                "num_inference_steps": 28
            },
            "options": {
                "use_cache": False,
                "wait_for_model": True
            }
        }
        
        image_bytes = await self._query_api(payload)
        
        if image_bytes:
            safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '_')).rstrip()[:50]
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_path = self.data_folder / f"{safe_prompt.replace(' ', '_')}_{timestamp}.jpg"
            
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            
            return str(file_path)
        else:
            Logger.log(f"Failed to generate image for prompt: {prompt}", "ERROR")
            return None
    
    def generate_images(self, prompt: str, count: int = 1, negative_prompt: str = "bad art", 
                        send_to_recipient: str = None) -> tuple[str, list]:
        """
        Generate one or multiple images based on prompt
        
        Args:
            prompt: Text description of image
            count: Number of images to generate (default: 1)
            negative_prompt: What to avoid in image
            send_to_recipient: Optional Telegram recipient name
            
        Returns:
            Tuple of (response message, list of image paths)
        """
        if not API_KEY:
            return "Image generation failed: The HuggingFaceAPIKey is missing from your .env file.", []
        
        Logger.log(f"Generating {count} image(s) for prompt: '{prompt}'", "IMAGE")
        
        try:
            generated_paths = []
            username = os.getenv("Username", "Boss")
            
            for i in range(count):
                Logger.log(f"Generating image {i+1}/{count}...", "IMAGE")
                image_path = asyncio.run(self._generate_single_image(prompt, negative_prompt))
                
                if image_path:
                    generated_paths.append(image_path)
                    self._open_image(image_path)
                else:
                    Logger.log(f"Failed to generate image {i+1}", "ERROR")
            
            if not generated_paths:
                return f"I'm sorry, Boss. I was unable to generate any images for that prompt.", []
            
            response_message = f"I've generated {len(generated_paths)} image(s) for '{prompt}' and opened them, Boss."
            
            # Send to Telegram if requested
            if send_to_recipient and generated_paths:
                from .telegram_handler import telegram_service
                Logger.log(f"Sending generated images to {send_to_recipient} via Telegram...", "IMAGE")
                
                for img_path in generated_paths:
                    success = telegram_service.send_file(
                        recipient_name=send_to_recipient,
                        file_path=img_path,
                        caption=f"Here is the image of '{prompt}' you requested."
                    )
                    if not success:
                        response_message += f" However, I failed to send the images to {send_to_recipient}."
                        break
                else:
                    response_message = f"I've generated {len(generated_paths)} image(s) of '{prompt}' and sent them to {send_to_recipient}, Boss."
            
            return response_message, generated_paths
        
        except Exception as e:
            Logger.log(f"Critical error during image generation: {e}", "ERROR")
            return f"I'm sorry, Boss. I encountered a critical error while trying to generate the image: {e}", []


# Global instance
image_generation_service = ImageGenerationService()