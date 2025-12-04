# 🚀 Quick Fix Guide for Friday Assistant

## ✅ Requirements Status: GOOD
**All critical packages are installed!**

---

## 🔴 CRITICAL ISSUE: Telegram Bot Conflict

### The Problem
```
telegram.error.Conflict: terminated by other getUpdates request; 
make sure that only one bot instance is running
```

### The Solution (Choose One)

#### Option 1: Kill All Python Processes (Recommended)
```powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Wait 2 seconds, then start
python main.py
```

#### Option 2: Use PowerShell to Stop Gracefully
```powershell
# Stop all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start fresh
python main.py
```

#### Option 3: Check for Specific Process
```powershell
# List all Python processes with details
Get-Process python | Select-Object Id, ProcessName, StartTime

# Kill specific process by ID
Stop-Process -Id <PROCESS_ID> -Force
```

---

## ⚠️ Warnings Found (Non-Critical)

### 1. CairoSVG - Missing Cairo Library
**Status:** Non-critical (SVG conversion won't work)  
**Impact:** Cannot convert SVG files  
**Fix Options:**

#### Option A: Install GTK+ Runtime (Windows)
1. Download: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Run installer
3. Restart terminal

#### Option B: Remove CairoSVG (if not needed)
```powershell
pip uninstall CairoSVG cairocffi cssselect2 tinycss2 -y
```

### 2. Pydub - FFmpeg Not Found
**Status:** Minor warning  
**Impact:** Some audio format conversions may fail  
**Fix:**
```powershell
# Install FFmpeg via Chocolatey
choco install ffmpeg

# Or download manually from: https://ffmpeg.org/download.html
```

### 3. Not Using Virtual Environment
**Status:** Recommendation  
**Impact:** Potential package conflicts  
**Fix:**
```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\activate

# Install requirements
pip install -r requirements2.txt
```

### 4. SpeechRecognition Deprecation Warnings
**Status:** Future compatibility issue  
**Impact:** None currently (Python 3.13 will remove aifc/audioop)  
**Action:** Already using faster-whisper as primary, this is just fallback

---

## 🎯 Before Running main.py - CHECKLIST

```powershell
# 1. Kill any existing Python processes
taskkill /F /IM python.exe

# 2. Check Python version (should be 3.11+)
python --version

# 3. Verify critical packages (optional)
python verify_requirements.py

# 4. Start Friday Assistant
python main.py
```

---

## 📋 Fixed in requirements2.txt

✅ Removed `pypiwin32` (conflicts with pywin32)  
✅ Removed `WMI` (not used)  
✅ All critical packages verified and working

---

## 🔧 Maintenance Commands

### Update All Packages
```powershell
pip install --upgrade -r requirements2.txt
```

### Check for Outdated Packages
```powershell
pip list --outdated
```

### Reinstall Specific Package
```powershell
pip uninstall <package> -y
pip install <package>
```

### Clear Pip Cache (if issues)
```powershell
pip cache purge
```

---

## 📊 Current Environment Status

| Component | Status | Notes |
|-----------|--------|-------|
| Python Version | ✅ 3.11.9 | Compatible |
| Pip Version | ✅ 25.0.1 | Latest |
| Virtual Env | ⚠️ Not Active | Recommended but optional |
| Core Packages | ✅ 34/35 | Only CairoSVG has warning |
| Telegram Bot | 🔴 Conflict | Multiple instances running |

---

## 🚀 Recommended Workflow

```powershell
# 1. Stop any running instances
taskkill /F /IM python.exe

# 2. Start Friday (clean)
python main.py

# When done, press Ctrl+C to stop gracefully
```

---

## 💡 Pro Tips

1. **Always stop previous instance before starting new one**
2. **Use Ctrl+C to stop gracefully** (saves chat logs properly)
3. **Check logs** in `Database/` folders for debugging
4. **Virtual environment recommended** for isolation
5. **Keep requirements2.txt updated** when adding packages

---

## 🆘 If Still Having Issues

### Complete Fresh Start
```powershell
# 1. Kill all Python
taskkill /F /IM python.exe

# 2. Clear Python cache
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force Backend/__pycache__

# 3. Restart terminal (close and reopen)

# 4. Start fresh
python main.py
```

### Check for Port Conflicts
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process using port 8000
taskkill /F /PID <PID>
```

---

**Last Updated:** November 12, 2025  
**Status:** ✅ All packages installed and working  
**Action Required:** Stop multiple bot instances before running
