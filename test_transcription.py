"""
Test script to verify transcription system works
"""
import asyncio
from Backend.logger import Logger

async def test():
    Logger.init()
    
    print("\n✅ Logger initialized with transcription")
    print(f"Transcription enabled: {Logger._transcription_enabled}")
    
    if Logger._transcription_enabled:
        if Logger._whisper_model:
            print("✅ Using Faster-Whisper (offline, most accurate)")
        elif Logger._recognizer:
            print("✅ Using Google Speech Recognition (online)")
    else:
        print("❌ Transcription NOT enabled")
    
    Logger.close()

if __name__ == "__main__":
    asyncio.run(test())
