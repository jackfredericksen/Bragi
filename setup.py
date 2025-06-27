#!/usr/bin/env python3
"""
Setup script for Esoteric Content Automation System
Handles installation, configuration, and initial setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Ensure Python 3.7+ is being used"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directory structure...")
    
    directories = [
        "esoteric_content_pipeline/scripts",
        "esoteric_content_pipeline/audio", 
        "esoteric_content_pipeline/video_clips",
        "esoteric_content_pipeline/final_videos",
        "esoteric_content_pipeline/logs",
        "assets"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}")

def create_env_template():
    """Create .env template if it doesn't exist"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    print("📝 Creating .env template...")
    
    env_template = """# Esoteric Content Bot Configuration
# Get your API keys from the respective services

# Claude (Anthropic API)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ElevenLabs (Voice Generation)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# Pexels (Stock Videos)
PEXELS_API_KEY=your_pexels_api_key_here

# Optional: Platform cookie paths
TIKTOK_COOKIE_PATH=tiktok_cookies.pkl
YOUTUBE_COOKIE_PATH=youtube_cookies.pkl
"""
    
    env_file.write_text(env_template)
    print("✅ .env template created")

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("🎬 Checking FFmpeg installation...")
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ FFmpeg not found")
    print("   Please install FFmpeg from: https://ffmpeg.org/download.html")
    print("   Make sure it's added to your system PATH")
    return False

def check_chrome():
    """Check if Chrome is installed"""
    print("🌐 Checking Chrome installation...")
    
    chrome_paths = [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome"
    ]
    
    for path in chrome_paths:
        if Path(path).exists():
            print("✅ Chrome browser found")
            return True
    
    print("⚠️  Chrome browser not detected in standard locations")
    print("   Please ensure Chrome is installed for platform automation")
    return False

def display_next_steps():
    """Show user what to do next"""
    print("\n" + "="*50)
    print("🎉 SETUP COMPLETE!")
    print("="*50)
    print("\n📋 NEXT STEPS:")
    print("1. Edit .env file with your API keys:")
    print("   - Anthropic API key (Claude)")
    print("   - ElevenLabs API key + Voice ID")  
    print("   - Pexels API key")
    print("\n2. Add ambient music files to assets/ folder")
    print("   - ambient1.mp3, ambient2.mp3, etc.")
    print("   - See assets/README.md for guidance")
    print("\n3. Test the system:")
    print("   python main.py")
    print("\n4. Set up automation:")
    print("   - Use run_bot.bat with Task Scheduler")
    print("   - Schedule to run 1-2 times daily")
    print("\n💡 TIP: Run expand_topics.py to add more content ideas!")

def main():
    """Main setup function"""
    print("🚀 Esoteric Content Automation Setup")
    print("="*40)
    
    # Check requirements
    check_python_version()
    
    # Install dependencies
    if not install_requirements():
        return
    
    # Create structure
    create_directories()
    create_env_template()
    
    # Check external tools
    ffmpeg_ok = check_ffmpeg()
    chrome_ok = check_chrome()
    
    # Final status
    if ffmpeg_ok and chrome_ok:
        print("\n✅ All requirements satisfied!")
    else:
        print("\n⚠️  Some requirements need attention (see above)")
    
    display_next_steps()

if __name__ == "__main__":
    main()