# 🎤 Advanced Transcription & Memory System

## Overview
Friday now includes a **real-time audio transcription system** that automatically converts voice conversations to text and stores them in `chatlogs.json`. This enables the **mem0 memory integration** to work properly by providing text-based conversation history.

## Architecture

### Transcription Engine
- **Primary**: `faster-whisper` (offline, most accurate)
  - Model: `base` (balance of speed/accuracy)
  - VAD filtering: Removes silence automatically
  - Language: English
  
- **Fallback**: `SpeechRecognition` (online, Google API)
  - Requires internet connection
  - Good accuracy for clear speech

### How It Works

1. **Audio Capture** (`main.py`)
   - User audio captured from microphone (16kHz, mono)
   - Assistant audio captured from playback stream (24kHz, mono)
   - Audio buffered in 0.5-second chunks

2. **Transcription Processing** (`logger.py`)
   - Audio chunks queued to background worker thread
   - Whisper model transcribes each chunk
   - Chunks accumulated in buffers (USER and ASSISTANT separate)

3. **Smart Saving**
   - Waits 2 seconds after last chunk before saving
   - Combines multiple chunks into complete sentences
   - Prevents incomplete/cut-off transcriptions
   - Saves to `chatlogs.json` with timestamp

4. **Memory Integration** (`memory_handler.py`)
   - On shutdown: `sync_chatlogs_to_memory()` called
   - Reads recent conversations from `chatlogs.json`
   - Sends to mem0 API for long-term memory storage
   - mem0 auto-extracts important facts (birthday, preferences, etc.)

## File Structure

```
Database/
  chatlogs.json          # All transcribed conversations with timestamps
  
Backend/
  logger.py              # Transcription system + chat logging
  memory_handler.py      # mem0 integration + chatlog sync
  
main.py                  # Audio capture + transcription triggers
```

## Configuration

### Transcription Settings (adjustable in `main.py`)
```python
TRANSCRIPTION_CHUNK_THRESHOLD = 25  # Transcribe every 0.5 seconds
```

### Buffer Settings (adjustable in `logger.py`)
```python
_TRANSCRIPTION_SAVE_DELAY = 2.0  # Wait 2 seconds before saving complete sentence
```

## Testing

### Verify Installation
```bash
python test_transcription.py
```

Expected output:
```
✅ Logger initialized with transcription
Transcription enabled: True
✅ Using Faster-Whisper (offline, most accurate)
```

### Test Conversation
1. Run Friday: `python main.py`
2. Say something: "Remember my birthday is June 8th"
3. Exit Friday: Press Ctrl+C
4. Check: `Database/chatlogs.json` for transcribed text
5. Verify memory: `python check_memories.py`

## Logs

- **Chat Log**: `Database/Chatlogs/chat_log_TIMESTAMP.txt`
- **Terminal Log**: `Database/TerminalLogs/terminal_log_TIMESTAMP.txt`
- **Transcription Debug**: Look for `[TRANSCRIPTION]` tags in terminal

## Performance

- **Latency**: ~0.5-1 second per transcription
- **Accuracy**: 85-95% for clear speech
- **CPU Usage**: Moderate (Whisper base model)
- **Disk Usage**: Minimal (~1KB per minute of conversation)

## Troubleshooting

### No transcriptions appearing
- Check: `[TRANSCRIPTION] 🎤 Transcription system ready` in startup logs
- Ensure microphone is working
- Speak clearly and at normal volume

### Incomplete sentences
- Increase `_TRANSCRIPTION_SAVE_DELAY` to 3-4 seconds
- Or decrease `TRANSCRIPTION_CHUNK_THRESHOLD` for more frequent checks

### VAD removing too much audio
```
[INFO] VAD filter removed 00:03.200 of audio
```
- This is normal - VAD removes silence/noise
- Speak immediately after Friday finishes responding

## Future Enhancements

- [ ] Multiple language support
- [ ] Speaker diarization (distinguish multiple voices)
- [ ] Emotion detection from voice
- [ ] Real-time UI display of transcriptions
- [ ] Custom wake word detection
- [ ] Voice activity detection tuning

## Credits

- **faster-whisper**: OpenAI Whisper optimized with CTranslate2
- **mem0ai**: Long-term memory for AI assistants
- **Google Gemini**: Live Audio API for voice conversation
