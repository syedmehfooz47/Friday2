"""
Requirements Verification Script
Checks if all critical packages are installed and working
"""

import sys
from typing import Dict, List, Tuple

def check_package(package_name: str, import_path: str = None) -> Tuple[bool, str]:
    """
    Check if a package is installed and can be imported.
    
    Args:
        package_name: Display name of the package
        import_path: Actual import path (if different from package_name)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    import_path = import_path or package_name.lower().replace('-', '_')
    
    try:
        __import__(import_path)
        return True, f"✅ {package_name}"
    except ImportError as e:
        return False, f"❌ {package_name}: {str(e)}"
    except Exception as e:
        return False, f"⚠️  {package_name}: {str(e)}"

def main():
    print("=" * 70)
    print("FRIDAY ASSISTANT - REQUIREMENTS VERIFICATION")
    print("=" * 70)
    print(f"\nPython Version: {sys.version}")
    print(f"Python Executable: {sys.executable}\n")
    
    # Define packages to check
    packages: Dict[str, List[Tuple[str, str]]] = {
        "🤖 Core AI & LLM": [
            ("Google Generative AI", "google.generativeai"),
            ("Groq", "groq"),
            ("Mem0", "mem0"),
        ],
        
        "🎙️ Audio & Transcription": [
            ("PyAudio", "pyaudio"),
            ("Faster Whisper", "faster_whisper"),
            ("Speech Recognition", "speech_recognition"),
            ("Pydub", "pydub"),
        ],
        
        "📱 Communication": [
            ("Telegram Bot", "telegram"),
            ("Gmail API", "googleapiclient"),
            ("Google Auth", "google.auth"),
        ],
        
        "📄 Document Generation": [
            ("Python DOCX", "docx"),
            ("Python PPTX", "pptx"),
            ("OpenPyXL", "openpyxl"),
            ("ReportLab", "reportlab"),
            ("Pillow", "PIL"),
        ],
        
        "🔄 Document Conversion": [
            ("PDF2DOCX", "pdf2docx"),
            ("PyPDF", "pypdf"),
            ("PDF2Image", "pdf2image"),
            ("IMG2PDF", "img2pdf"),
            ("CairoSVG", "cairosvg"),
        ],
        
        "🌐 Web & API": [
            ("FastAPI", "fastapi"),
            ("Uvicorn", "uvicorn"),
            ("WebSockets", "websockets"),
            ("AioHTTP", "aiohttp"),
            ("Requests", "requests"),
        ],
        
        "🤖 Automation": [
            ("PyAutoGUI", "pyautogui"),
            ("Keyboard", "keyboard"),
            ("PyGetWindow", "pygetwindow"),
            ("PSUtil", "psutil"),
            ("Pyperclip", "pyperclip"),
        ],
        
        "🔧 Windows Specific": [
            ("PyWin32", "win32com.client"),
            ("COMTypes", "comtypes"),
        ],
        
        "🛠️ Utilities": [
            ("Python Dotenv", "dotenv"),
            ("Tavily", "tavily"),
            ("AioFiles", "aiofiles"),
        ]
    }
    
    results = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "warnings": 0
    }
    
    failed_packages = []
    
    # Check each category
    for category, package_list in packages.items():
        print(f"\n{category}")
        print("-" * 70)
        
        for package_name, import_path in package_list:
            results["total"] += 1
            success, message = check_package(package_name, import_path)
            print(f"  {message}")
            
            if "✅" in message:
                results["success"] += 1
            elif "❌" in message:
                results["failed"] += 1
                failed_packages.append(package_name)
            else:
                results["warnings"] += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Packages Checked: {results['total']}")
    print(f"✅ Successfully Installed: {results['success']}")
    print(f"❌ Failed/Missing: {results['failed']}")
    print(f"⚠️  Warnings: {results['warnings']}")
    
    if failed_packages:
        print(f"\n❌ Failed Packages ({len(failed_packages)}):")
        for pkg in failed_packages:
            print(f"   - {pkg}")
        print("\n💡 To install missing packages:")
        print("   pip install -r requirements2.txt")
    else:
        print("\n🎉 All critical packages are installed!")
    
    # Additional checks
    print("\n" + "=" * 70)
    print("ADDITIONAL CHECKS")
    print("=" * 70)
    
    # Check Python version
    version_info = sys.version_info
    if version_info.major == 3 and version_info.minor >= 11:
        print(f"✅ Python version {version_info.major}.{version_info.minor}.{version_info.micro} is compatible")
    else:
        print(f"⚠️  Python version {version_info.major}.{version_info.minor}.{version_info.micro} - Recommended: 3.11+")
    
    # Check for virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment (recommended)")
    
    # Check pip version
    try:
        import pip
        print(f"✅ pip version: {pip.__version__}")
    except:
        print("⚠️  Could not determine pip version")
    
    print("\n" + "=" * 70)
    
    # Return exit code
    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
