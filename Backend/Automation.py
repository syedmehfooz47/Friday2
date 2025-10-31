# -*- coding: utf-8 -*-
"""
System Automation - Advanced control of Windows system with security
Handles apps, windows, system controls, and more
"""

import os
import sys
import time
import subprocess
import psutil
import pyautogui
import pyperclip
import keyboard
from pathlib import Path
from dotenv import load_dotenv
from .logger import Logger
from .llm_handler import llm_handler
from .telegram_handler import telegram_service

load_dotenv()

# Conditional imports
try:
    from AppOpener import close, open as appopen, give_appnames
    APPOPENER_AVAILABLE = True
except ImportError:
    APPOPENER_AVAILABLE = False
    Logger.log("AppOpener not installed", "WARNING")

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False

try:
    import screen_brightness_control as sbc
    BRIGHTNESS_AVAILABLE = True
except ImportError:
    BRIGHTNESS_AVAILABLE = False

try:
    from pywhatkit import search, playonyt
    import webbrowser
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

if sys.platform == "win32":
    try:
        import win32com.client
        import winreg as reg
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False


# Power operation security
def verify_power_password(password: str) -> bool:
    """Verify power operation password"""
    correct_password = os.getenv("POWER_PASSWORD", "9747")
    return password == correct_password


# --- Enhanced App Management ---

def is_app_installed(app_name: str) -> bool:
    """Check if app is installed on system"""
    if APPOPENER_AVAILABLE:
        try:
            installed_apps = give_appnames()
            return any(app_name.lower() in app.lower() for app in installed_apps)
        except Exception:
            pass
    
    # Fallback: check common installation paths
    common_paths = [
        os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
        os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs')
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                if app_name.lower() in root.lower():
                    return True
                for file in files:
                    if app_name.lower() in file.lower() and file.endswith('.exe'):
                        return True
    
    return False


def OpenApp(app_name: str) -> tuple[str, None]:
    """Open an application or website intelligently"""
    username = os.getenv("Username", "Boss")
    
    Logger.log(f"Opening app: {app_name}", "AUTOMATION")
    
    # Check if it's installed
    if is_app_installed(app_name):
        if APPOPENER_AVAILABLE:
            try:
                appopen(app_name, match_closest=True, output=False, throw_error=True)
                return f"Opening {app_name}, Boss.", None
            except Exception as e:
                Logger.log(f"AppOpener failed: {e}", "ERROR")
    
    # If not installed or failed, open website
    try:
        url_name = app_name.lower().replace(" ", "")
        import webbrowser
        webbrowser.open(f"https://{url_name}.com")
        return f"Opened {app_name} website, Boss.", None
    except Exception as e:
        return f"Sorry Boss, I couldn't open {app_name}.", None


def open_website(website_name: str) -> tuple[str, None]:
    """Open website directly without searching"""
    username = os.getenv("Username", "Boss")
    
    Logger.log(f"Opening website: {website_name}", "AUTOMATION")
    
    try:
        import webbrowser
        
        # Clean website name
        website_name = website_name.lower().replace(" ", "")
        
        # Add .com if not present
        if not any(ext in website_name for ext in ['.com', '.org', '.net', '.io', '.ai']):
            website_name = f"{website_name}.com"
        
        # Add https if not present
        if not website_name.startswith('http'):
            website_name = f"https://{website_name}"
        
        webbrowser.open(website_name)
        return f"Opened website, Boss.", None
    except Exception as e:
        Logger.log(f"Error opening website: {e}", "ERROR")
        return f"Failed to open website, Boss.", None


def CloseApp(app_name: str) -> tuple[str, None]:
    """Close an application"""
    username = os.getenv("Username", "Boss")
    
    if not APPOPENER_AVAILABLE:
        return "AppOpener not available", None
    
    Logger.log(f"Closing app: {app_name}", "AUTOMATION")
    
    try:
        close(app_name, match_closest=True, output=False, throw_error=True)
        return f"Closed {app_name}, Boss.", None
    except Exception:
        if kill_process(app_name):
            return f"Forcefully closed {app_name}, Boss.", None
        else:
            return f"Couldn't find {app_name} to close, Boss.", None


def kill_process(process_name: str) -> bool:
    """Forcefully terminate a process"""
    process_name = process_name.lower()
    if not process_name.endswith('.exe'):
        process_name += '.exe'
    
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == process_name:
            try:
                p = psutil.Process(proc.info['pid'])
                p.kill()
                Logger.log(f"Killed process {proc.info['name']}", "AUTOMATION")
                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                Logger.log(f"Error killing process: {e}", "ERROR")
    return False


# --- Window Management ---

def manage_window(app_name: str, action: str) -> tuple[str, None]:
    """Manage window: minimize, maximize, restore, close"""
    username = os.getenv("Username", "Boss")
    
    if not PYGETWINDOW_AVAILABLE:
        return "Window management not available", None
    
    action = action.lower()
    valid_actions = ['minimize', 'maximize', 'restore', 'close']
    
    if action not in valid_actions:
        return f"Invalid action. Use: {', '.join(valid_actions)}", None
    
    try:
        all_windows = gw.getAllTitles()
        matches = [title for title in all_windows if app_name.lower() in title.lower() and title]
        
        if not matches:
            return f"Couldn't find window for {app_name}, Boss.", None
        
        target_win = gw.getWindowsWithTitle(matches[0])[0]
        
        if not target_win.isActive:
            target_win.activate()
            time.sleep(0.2)
        
        if action == 'minimize':
            target_win.minimize()
        elif action == 'maximize':
            target_win.maximize()
        elif action == 'restore':
            target_win.restore()
        elif action == 'close':
            target_win.close()
        
        return f"Window {action}d, Boss.", None
    except Exception as e:
        Logger.log(f"Window management error: {e}", "ERROR")
        return f"Window management failed, Boss.", None


# --- System Controls ---

def set_system_volume(level: int) -> tuple[str, None]:
    """Set system volume (0-100)"""
    username = os.getenv("Username", "Boss")
    
    try:
        level = int(level)
        if not 0 <= level <= 100:
            return "Volume must be 0-100", None
        
        # Reset to 0
        for _ in range(50):
            keyboard.press_and_release('volume_down')
            time.sleep(0.01)
        
        # Set to target
        target_presses = level // 2
        for _ in range(target_presses):
            keyboard.press_and_release('volume_up')
            time.sleep(0.01)
        
        return f"Volume set to {level}%, Boss.", None
    except Exception as e:
        return f"Volume control error: {e}", None


def set_brightness(level: int) -> tuple[str, None]:
    """Set screen brightness (0-100)"""
    username = os.getenv("Username", "Boss")
    
    if not BRIGHTNESS_AVAILABLE:
        return "Brightness control not available", None
    
    try:
        level = int(level)
        if not 0 <= level <= 100:
            return "Brightness must be 0-100", None
        
        sbc.set_brightness(level)
        return f"Brightness set to {level}%, Boss.", None
    except Exception as e:
        return f"Brightness control error: {e}", None


def get_brightness() -> tuple[str, None]:
    """Get current screen brightness"""
    if not BRIGHTNESS_AVAILABLE:
        return "Brightness control not available", None
    
    try:
        brightness = sbc.get_brightness(display=0)[0]
        return f"Current brightness is {brightness}%.", None
    except Exception as e:
        return f"Error getting brightness: {e}", None


def change_windows_theme(mode: str) -> tuple[str, None]:
    """Change Windows theme to dark/light"""
    username = os.getenv("Username", "Boss")
    
    if sys.platform != "win32" or not WIN32_AVAILABLE:
        return "Theme change only available on Windows", None
    
    mode = mode.lower()
    if mode not in ['dark', 'light']:
        return "Mode must be 'dark' or 'light'", None
    
    try:
        apps_key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        value = 0 if mode == 'dark' else 1
        
        with reg.OpenKey(reg.HKEY_CURRENT_USER, apps_key_path, 0, reg.KEY_WRITE) as key:
            reg.SetValueEx(key, 'AppsUseLightTheme', 0, reg.REG_DWORD, value)
            reg.SetValueEx(key, 'SystemUsesLightTheme', 0, reg.REG_DWORD, value)
        
        return f"Switched to {mode} mode, Boss.", None
    except Exception as e:
        return f"Theme change error: {e}", None


# --- Mouse & Keyboard ---

def type_text(text: str, interval: float = 0.01) -> tuple[str, None]:
    """Type text using keyboard"""
    pyautogui.write(text, interval=float(interval))
    return "Text typed.", None


def type_formatted_text(prompt: str) -> tuple[str, None]:
    """Type formatted text based on prompt"""
    username = os.getenv("Username", "Boss")
    
    try:
        Logger.log(f"Generating formatted text for: {prompt}", "AUTOMATION")
        
        # Generate formatted content
        generation_prompt = f"Write a {prompt}. Format it properly with line breaks and spacing. Give only the content, no explanations."
        
        messages = [{"role": "user", "content": generation_prompt}]
        content = llm_handler.get_response(messages, max_tokens=4000, temperature=0.7)
        
        if content.startswith("Error"):
            return f"Failed to generate text: {content}", None
        
        # Type the content
        time.sleep(1)  # Give time to focus on target
        pyautogui.write(content, interval=0.01)
        
        return f"Typed formatted {prompt}, Boss.", None
    except Exception as e:
        Logger.log(f"Error typing formatted text: {e}", "ERROR")
        return f"Failed to type text: {e}", None


def move_mouse(x: int, y: int) -> tuple[str, None]:
    """Move mouse to coordinates"""
    pyautogui.moveTo(int(x), int(y), duration=0.25)
    return f"Mouse moved to ({x}, {y}).", None


def click_mouse(button: str = "left", clicks: int = 1) -> tuple[str, None]:
    """Perform mouse click"""
    pyautogui.click(button=button.lower(), clicks=int(clicks))
    return f"Performed {clicks} {button} click(s).", None


def get_mouse_position() -> tuple[str, None]:
    """Get current mouse position"""
    x, y = pyautogui.position()
    return f"Mouse is at ({x}, {y}).", None


# --- Clipboard ---

def set_clipboard(text: str) -> tuple[str, None]:
    """Copy text to clipboard"""
    pyperclip.copy(text)
    return "Text copied to clipboard.", None


def get_clipboard() -> tuple[str, None]:
    """Get clipboard text"""
    try:
        text = pyperclip.paste()
        return f"Clipboard: {text}" if text else "Clipboard is empty.", None
    except Exception as e:
        return f"Error reading clipboard: {e}", None


# --- Screenshots ---

def take_screenshot(send_to_recipient: str = None) -> tuple[str, str]:
    """Take screenshot and optionally send via Telegram"""
    username = os.getenv("Username", "Boss")
    
    try:
        data_dir = Path(__file__).parent.parent / "Data" / "Screenshots"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        save_path = data_dir / f"screenshot_{int(time.time())}.png"
        pyautogui.screenshot(str(save_path))
        
        # Open screenshot
        if sys.platform == "win32":
            os.startfile(save_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(save_path)])
        else:
            subprocess.run(["xdg-open", str(save_path)])
        
        response = f"Screenshot saved, Boss."
        
        if send_to_recipient:
            Logger.log(f"Sending screenshot to {send_to_recipient}", "AUTOMATION")
            success = telegram_service.send_file(
                recipient_name=send_to_recipient,
                file_path=str(save_path),
                caption="Here's the screenshot you requested."
            )
            if success:
                response = f"Screenshot sent to {send_to_recipient}, Boss."
            else:
                response = f"Screenshot taken but failed to send to {send_to_recipient}, Boss."
        
        return response, str(save_path)
    except Exception as e:
        return f"Screenshot error: {e}", None


# --- System Power (Password Protected) ---

def system_power(action: str, password: str = None) -> tuple[str, None]:
    """System power actions with password protection: shutdown, restart, lock, logoff, sleep"""
    username = os.getenv("Username", "Boss")
    action = action.lower()
    
    if sys.platform != "win32":
        return "Power control only available on Windows", None
    
    # Actions that require password
    protected_actions = ["shutdown", "restart", "logoff"]
    
    if action in protected_actions:
        if not password:
            return f"Password required for {action}, Boss. Please provide the power password.", None
        
        if not verify_power_password(password):
            Logger.log(f"Invalid power password attempt for {action}", "SECURITY")
            return f"Invalid password, Boss. {action.capitalize()} cancelled.", None
    
    try:
        if action == "shutdown":
            subprocess.run(["shutdown", "/s", "/t", "5"], check=True)
            Logger.log("Shutdown initiated", "POWER")
            return f"Shutting down in 5 seconds, Boss.", None
        
        elif action == "restart":
            subprocess.run(["shutdown", "/r", "/t", "5"], check=True)
            Logger.log("Restart initiated", "POWER")
            return f"Restarting in 5 seconds, Boss.", None
        
        elif action == "lock":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            Logger.log("System locked", "POWER")
            return f"System locked, Boss.", None
        
        elif action == "logoff":
            subprocess.run(["shutdown", "/l"], check=True)
            Logger.log("Logoff initiated", "POWER")
            return f"Logging off, Boss.", None
        
        elif action == "sleep":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
            Logger.log("System entering sleep mode", "POWER")
            return f"Entering sleep mode, Boss.", None
        
        return f"Invalid power action: {action}", None
    except Exception as e:
        return f"Power control error: {e}", None


# --- Web Search ---

def GoogleSearch(query: str) -> tuple[str, None]:
    """Search Google"""
    username = os.getenv("Username", "Boss")
    if not WEB_AVAILABLE:
        return "Web search not available", None
    
    try:
        search(query)
        return f"Searching Google for {query}, Boss.", None
    except Exception as e:
        return f"Google search error: {e}", None


def YouTubeSearch(query: str) -> tuple[str, None]:
    """Search YouTube"""
    username = os.getenv("Username", "Boss")
    try:
        import webbrowser
        
        webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        return f"Here are YouTube results for {query}, Boss.", None
    except Exception as e:
        return f"YouTube search error: {e}", None


def PlayYoutube(query: str) -> tuple[str, None]:
    """Play YouTube video"""
    username = os.getenv("Username", "Boss")
    if not WEB_AVAILABLE:
        return "YouTube playback not available", None
    
    try:
        playonyt(query)
        return f"Playing {query} on YouTube, Boss.", None
    except Exception as e:
        return f"YouTube playback error: {e}", None


# --- Content Generation ---

def Content(prompt: str) -> tuple[str, str]:
    """Generate written content"""
    username = os.getenv("Username", "Boss")
    try:
        messages = [{"role": "user", "content": f"Write detailed content about: {prompt}"}]
        content = llm_handler.get_response(messages)
        
        data_dir = Path(__file__).parent.parent / "Data" / "GeneratedContent"
        data_dir.mkdir(parents=True, exist_ok=True)
        safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '_')).rstrip()[:50]
        file_path = data_dir / f"{safe_prompt.replace(' ', '_')}.txt"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        if sys.platform == "win32":
            subprocess.Popen(['notepad.exe', str(file_path)])
        
        return f"Content generated and opened, Boss.", str(file_path)
    except Exception as e:
        return f"Content generation error: {e}", None


# --- Folder Management ---

def create_folder(path: str) -> tuple[str, str]:
    """Create a new folder"""
    username = os.getenv("Username", "Boss")
    try:
        if not os.path.isabs(path):
            desktop = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
            path = os.path.join(desktop, path)
        
        os.makedirs(path, exist_ok=True)
        return f"Folder created at {path}, Boss.", path
    except Exception as e:
        return f"Folder creation error: {e}", None


# --- Telegram Integration ---

def send_telegram_message(recipient_name: str, message_prompt: str) -> tuple[str, None]:
    """Send Telegram message with AI composition"""
    username = os.getenv("Username", "Boss")
    Logger.log(f"Composing Telegram message for {recipient_name}", "AUTOMATION")
    
    # Compose message if prompt is short
    if len(message_prompt.split()) < 4:
        composition_prompt = f"Write a short, friendly message for '{recipient_name}' based on: '{message_prompt}'. Just give the message, no introduction."
        try:
            final_message = llm_handler.get_response([{"role": "user", "content": composition_prompt}])
        except Exception:
            final_message = message_prompt
    else:
        final_message = message_prompt
    
    success = telegram_service.send_message(recipient_name, final_message)
    
    if success:
        return f"Message sent to {recipient_name} on Telegram, Boss.", None
    else:
        return f"Failed to send message to {recipient_name}, Boss.", None


def send_telegram_file(recipient_name: str, file_path: str) -> tuple[str, None]:
    """Send file via Telegram"""
    username = os.getenv("Username", "Boss")
    
    if not os.path.exists(file_path):
        return f"File not found: {file_path}", None
    
    Logger.log(f"Sending file to {recipient_name} via Telegram", "AUTOMATION")
    file_name = os.path.basename(file_path)
    caption = f"Here is {file_name}"
    
    success = telegram_service.send_file(recipient_name, file_path, caption)
    
    if success:
        return f"File '{file_name}' sent to {recipient_name}, Boss.", None
    else:
        return f"Failed to send file to {recipient_name}, Boss.", None