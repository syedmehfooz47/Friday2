# Friday Assistant - Critical Fixes Applied

## Date: November 12, 2025

## Issues Identified and Fixed:

### 1. ✅ Image Generation API Endpoint Fixed
**Problem:** Hugging Face API endpoint changed, causing 410 errors
```
Error: "https://api-inference.huggingface.co is no longer supported"
```

**Fix Applied:** Updated `Backend/ImageGeneration.py`
- Changed API_URL from: `https://api-inference.huggingface.co/models/...`
- To: `https://router.huggingface.co/hf-inference/models/...`

**Status:** ✅ FIXED - Image generation should now work

---

### 2. ⚠️ Assistant Not Asking for Clarification
**Problem:** Friday doesn't ask for missing information (recipient names, file paths, etc.)

**Root Cause:** System instruction doesn't explicitly tell the model to ask for clarification

**Fix Needed:** Update system instruction in `Backend/brain.py` to include:
```python
CLARIFICATION BEHAVIOR:
- When user requests an action but provides incomplete information, ALWAYS ask for what's missing
- Examples:
  * "Send file to John" → Ask: "Which file would you like me to send to John, Boss?"
  * "Generate image and send to MK" → If image fails, say: "I couldn't generate the image, Boss."
  * "Send to telegram" → Ask: "Who would you like me to send this to, Boss?"
- NEVER attempt partial execution without required information
- Be conversational but always get the information you need
```

**Status:** ⚠️ NEEDS MANUAL UPDATE (see below for exact code)

---

### 3. ⚠️ Automatic Shutdown/Connection Loss
**Problem:** Session ends unexpectedly with:
```
ConnectionClosedError: no close frame received or sent
```

**Root Causes:**
1. Network instability with Gemini Live API
2. No automatic reconnection logic
3. Session timeout without warning

**Fix Needed:** Add reconnection logic to `main.py`:
- Implement exponential backoff retry
- Add connection health check
- Auto-reconnect on disconnection

**Status:** ⚠️ NEEDS IMPLEMENTATION

---

### 4. ⚠️ Email/Telegram Operations Not Working
**Problem:** Files not being sent after generation

**Root Cause:** Multi-step operations not completing:
1. User says "generate PDF and send to MK"
2. PDF generates successfully
3. But send operation doesn't execute

**Issues:**
- Model doesn't chain operations automatically
- No automatic file path resolution after generation
- Missing context about "that file" references

**Fix Needed:** Enhance system instruction with chaining logic (see code below)

**Status:** ⚠️ NEEDS MANUAL UPDATE

---

## Code Changes Required:

### A. Update System Instruction in `Backend/brain.py`

Add this section to the system_instruction (around line 50, after the existing instructions):

```python
CRITICAL CLARIFICATION & CHAINING BEHAVIOR:

1. ALWAYS ASK FOR MISSING INFORMATION:
   - If user says "send file to X" without specifying which file, ask: "Which file should I send to X, Boss?"
   - If user says "generate image and send" but generation fails, inform them: "I couldn't generate the image, Boss."
   - If user says "send that to X", use get_last_generated_file or get_last_converted_file
   - NEVER silently skip steps

2. MULTI-STEP OPERATION CHAINING:
   When user requests multiple operations (e.g., "generate PDF on colleges and send to MK on Telegram"):
   
   Step 1: Execute generate_pdf(topic='colleges', pages=10)
   Step 2: Wait for result, extract file_path from response
   Step 3: Call find_contact('MK') to get Telegram ID
   Step 4: Call telegram_send_file(recipient_name='MK', file_path=<path_from_step2>)
   Step 5: Respond: "I've generated the PDF on colleges and sent it to MK on Telegram, Boss."
   
   CRITICAL: You MUST chain these operations yourself. Execute all steps in sequence.

3. FILE PATH AWARENESS:
   - After generating any file (PDF, Word, PPT, Excel, Image), REMEMBER its path
   - When user says "send that to X", use the path from the last generation
   - When user says "convert that PDF", use get_last_generated_file(file_type='pdf')
   - Store context: "I just generated X at path Y"

4. ERROR HANDLING:
   - If any step fails, inform user immediately
   - Don't attempt next step if previous failed
   - Example: "I generated the PDF but couldn't send it to MK because I don't have their Telegram ID, Boss."

5. CONFIRMATION RESPONSES:
   - After completing multi-step operations, confirm ALL steps
   - Example: "I've generated the PDF, converted it to Word, and sent it to John via email, Boss."
```

### B. Add Reconnection Logic to `main.py`

Add this class after the AudioStateManager class (around line 1200):

```python
class ReconnectionManager:
    """Manage Gemini API reconnection with exponential backoff"""
    
    def __init__(self, max_retries=5):
        self.max_retries = max_retries
        self.retry_count = 0
        self.base_delay = 2  # seconds
    
    async def attempt_reconnect(self, audio_loop_instance):
        """Attempt to reconnect with exponential backoff"""
        while self.retry_count < self.max_retries:
            self.retry_count += 1
            delay = self.base_delay * (2 ** (self.retry_count - 1))
            
            Logger.log(f"Reconnection attempt {self.retry_count}/{self.max_retries} in {delay}s...", "RECONNECT")
            await asyncio.sleep(delay)
            
            try:
                # Attempt to reconnect
                await audio_loop_instance.connect_to_gemini()
                Logger.log("Reconnection successful!", "RECONNECT")
                self.retry_count = 0
                return True
            except Exception as e:
                Logger.log(f"Reconnection failed: {e}", "ERROR")
        
        Logger.log("Max reconnection attempts reached. Please restart Friday.", "ERROR")
        return False
```

Then modify the AudioLoop class to use it (search for `ConnectionClosedError` handling and add):

```python
except ConnectionClosedError as e:
    Logger.log(f"Connection closed: {e}", "ERROR")
    
    # Attempt automatic reconnection
    reconnect_mgr = ReconnectionManager()
    success = await reconnect_mgr.attempt_reconnect(self)
    
    if not success:
        Logger.log("Failed to reconnect after multiple attempts", "ERROR")
        raise
```

---

## Testing Checklist:

After applying fixes, test these scenarios:

- [ ] Generate image of a car → Should work with new API
- [ ] Generate PDF on colleges and send to MK on Telegram → Should chain operations
- [ ] "Send that file to John" → Should ask which file or use last generated
- [ ] "Convert that PDF to Word" → Should find last PDF automatically
- [ ] Connection loss → Should attempt reconnection
- [ ] "Send image to telegram" without specifying recipient → Should ask for name

---

## Manual Steps Required:

1. **Update system instruction in Backend/brain.py:**
   - Add the CLARIFICATION & CHAINING section shown above
   - Place it after line ~120 (after the existing system_instruction text)

2. **Add reconnection logic to main.py:**
   - Add ReconnectionManager class
   - Update ConnectionClosedError handling

3. **Test thoroughly:**
   - Run `python main.py`
   - Try each test scenario above
   - Check logs for errors

---

## Notes:

- Image generation API fix is already applied ✅
- Other fixes require manual code updates
- System instruction changes are critical for proper behavior
- Reconnection logic will improve reliability significantly

---

## Additional Improvements Recommended:

1. Add connection health check every 5 minutes
2. Implement file path context memory (store last 5 generated files)
3. Add better error messages for users
4. Create a "task confirmation" mode where Friday asks before executing multi-step operations
5. Add logging for all file generations to help with "that file" references

