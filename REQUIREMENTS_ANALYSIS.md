# Requirements Analysis & Issues Report
**Date:** November 12, 2025  
**Project:** Friday Assistant  
**Python Version:** 3.11.9

---

## ✅ Fixed Issues

### 1. **Removed Conflicting Package: `pypiwin32`**
- **Issue:** `pypiwin32` is deprecated and conflicts with `pywin32`
- **Fix:** Removed from `requirements2.txt` (line 72)
- **Impact:** Prevents installation conflicts on Windows

### 2. **Removed Unnecessary Package: `WMI`**
- **Issue:** WMI package not actively used and can cause import issues
- **Fix:** Removed from `requirements2.txt` (line 91)
- **Impact:** Cleaner installation, no functionality loss

---

## ⚠️ Critical Runtime Issues

### 1. **Telegram Bot Conflict** (HIGH PRIORITY)
**Error:**
```
telegram.error.Conflict: Conflict: terminated by other getUpdates request; 
make sure that only one bot instance is running
```

**Root Cause:**
- Multiple instances of `main.py` running simultaneously
- Telegram API allows only ONE bot instance per token

**Solutions:**
1. **Kill all Python processes** before starting:
   ```powershell
   taskkill /F /IM python.exe
   python main.py
   ```

2. **Check for background processes:**
   ```powershell
   Get-Process python | Stop-Process -Force
   ```

3. **Use process lock** (recommended - code change needed):
   ```python
   import fcntl  # Linux/Mac
   # or use portalocker for cross-platform
   ```

---

## ⚠️ Deprecation Warnings

### 1. **FastAPI `on_event` Deprecated**
**File:** `main.py` line 876  
**Current:**
```python
@app.on_event("startup")
async def startup_event():
    ...
```

**Recommended Fix:**
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    yield
    # Shutdown code

app = FastAPI(lifespan=lifespan)
```

### 2. **websockets.legacy Deprecated**
**Issue:** Using deprecated `websockets.legacy` module  
**Recommendation:** Upgrade to websockets 14.0+ API (code changes needed)

### 3. **oauth2client file_cache Warning**
**Warning:** `file_cache is only supported with oauth2client<4.0.0`  
**Impact:** Non-breaking, just informational  
**Fix:** Consider migrating to `google-auth` completely

---

## 🔧 Missing System Dependencies

### 1. **CairoSVG - GTK+ Runtime Missing**
**Error:**
```
[ERROR] CairoSVG library found, but its C library dependency (Cairo/GTK) 
is missing or not configured.
```

**Fix for Windows:**
1. Download GTK+ Runtime installer:
   - https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Install and add to PATH
3. Or disable SVG conversion in code

**Alternative:** Remove CairoSVG if not needed:
```powershell
pip uninstall CairoSVG cairocffi cssselect2 tinycss2
```

### 2. **Poppler (for pdf2image)**
**Recommendation:** Install Poppler binaries for PDF to Image conversion

**Windows Installation:**
1. Download: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\Program Files\poppler`
3. Add `C:\Program Files\poppler\Library\bin` to PATH

---

## 📦 Package Installation Commands

### Fresh Installation
```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
.\.venv\Scripts\activate

# 3. Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# 4. Install requirements (use requirements2.txt - it's more complete)
pip install -r requirements2.txt

# 5. Verify installation
pip list
```

### Update Existing Packages
```powershell
pip install --upgrade -r requirements2.txt
```

### Fix Specific Package Issues
```powershell
# Reinstall PyAudio if having issues
pip uninstall pyaudio
pip install pipwin
pipwin install pyaudio

# Or download wheel manually:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

---

## 🔍 Verification Commands

### Check Installed Packages
```powershell
# List all installed packages
pip list

# Check for outdated packages
pip list --outdated

# Show package details
pip show google-generativeai
pip show python-telegram-bot
pip show faster-whisper
```

### Verify Critical Imports
```python
# Test script to verify installations
import sys
print(f"Python: {sys.version}")

try:
    import google.generativeai as genai
    print("✅ Google Generative AI")
except: print("❌ Google Generative AI")

try:
    import telegram
    print("✅ Python Telegram Bot")
except: print("❌ Python Telegram Bot")

try:
    from faster_whisper import WhisperModel
    print("✅ Faster Whisper")
except: print("❌ Faster Whisper")

try:
    import fastapi
    print("✅ FastAPI")
except: print("❌ FastAPI")

try:
    import mem0
    print("✅ Mem0")
except: print("❌ Mem0")

try:
    import pyaudio
    print("✅ PyAudio")
except: print("❌ PyAudio")
```

---

## 🎯 Recommended Actions (Priority Order)

### **IMMEDIATE (Do Now)**
1. ✅ **Fixed:** Remove `pypiwin32` from requirements2.txt
2. ✅ **Fixed:** Remove `WMI` from requirements2.txt
3. ⚠️ **TODO:** Kill all Python processes before running
   ```powershell
   taskkill /F /IM python.exe
   ```

### **HIGH PRIORITY (This Week)**
4. Update FastAPI event handlers to use `lifespan` context manager
5. Add process locking to prevent multiple bot instances
6. Install GTK+ runtime for CairoSVG or remove SVG support

### **MEDIUM PRIORITY (This Month)**
7. Upgrade websockets implementation to non-legacy API
8. Migrate from oauth2client to google-auth completely
9. Install Poppler for PDF to Image conversion

### **LOW PRIORITY (When Convenient)**
10. Pin package versions for reproducible builds
11. Create separate requirements files for dev/prod
12. Add automated testing for dependencies

---

## 📝 Notes

### About `requirements.txt` vs `requirements2.txt`
- **requirements.txt**: Minimal, basic dependencies
- **requirements2.txt**: Complete, includes all optional features
- **Recommendation:** Use `requirements2.txt` for full functionality

### Platform-Specific Packages
Some packages are Windows-only:
- `pywin32` - Windows COM automation
- `comtypes` - Windows COM interfaces
- `docx2pdf` - Office document conversion

These use conditional installation: `; sys_platform == 'win32'`

### Virtual Environment Best Practices
- Always use virtual environment
- Don't commit `.venv` to git (already in .gitignore)
- Document Python version used
- Consider using `requirements-dev.txt` for development tools

---

## 🐛 Known Issues

### 1. Multiple Bot Instances
- **Status:** Active issue
- **Impact:** Telegram bot fails to receive updates
- **Workaround:** Kill all Python processes before starting

### 2. CairoSVG GTK+ Dependency
- **Status:** Non-critical
- **Impact:** SVG conversion not available
- **Workaround:** Remove package or install GTK+ runtime

### 3. FastAPI Deprecation Warnings
- **Status:** Non-breaking
- **Impact:** Future compatibility concerns
- **Workaround:** Update to lifespan events (code change needed)

---

## 📚 Additional Resources

- **FastAPI Lifespan Events:** https://fastapi.tiangolo.com/advanced/events/
- **Websockets Upgrade Guide:** https://websockets.readthedocs.io/en/stable/howto/upgrade.html
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Poppler Windows:** https://github.com/oschwartz10612/poppler-windows
- **GTK+ Runtime:** https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

---

**Last Updated:** November 12, 2025  
**Status:** ✅ Critical package conflicts resolved  
**Next Review:** When adding new dependencies
