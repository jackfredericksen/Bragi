#!/usr/bin/env python3
"""
Test script for caption generation and burning
Helps debug caption issues independently
"""

import subprocess
from pathlib import Path

def test_caption_burning():
    """Test caption burning with the latest generated files"""
    
    # Find the most recent files
    final_dir = Path("esoteric_content_pipeline/final_videos")
    
    if not final_dir.exists():
        print("❌ No final_videos directory found")
        return
    
    # Get most recent files
    video_files = list(final_dir.glob("*_final.mp4"))
    srt_files = list(final_dir.glob("*.srt"))
    
    if not video_files:
        print("❌ No video files found")
        return
        
    if not srt_files:
        print("❌ No SRT files found")
        return
    
    # Use most recent files
    video_file = sorted(video_files)[-1]
    srt_file = sorted(srt_files)[-1]
    output_file = final_dir / f"{video_file.stem}_test_captions.mp4"
    
    print(f"🧪 Testing caption burning:")
    print(f"   Video: {video_file}")
    print(f"   SRT: {srt_file}")
    print(f"   Output: {output_file}")
    
    # Check if files exist
    if not video_file.exists():
        print(f"❌ Video file doesn't exist: {video_file}")
        return
        
    if not srt_file.exists():
        print(f"❌ SRT file doesn't exist: {srt_file}")
        return
    
    # Test different FFmpeg subtitle commands
    test_commands = [
        # Method 1: Forward slashes
        [
            "ffmpeg", "-y",
            "-i", str(video_file).replace('\\', '/'),
            "-vf", f"subtitles='{str(srt_file).replace('\\', '/')}':force_style='FontName=Arial,FontSize=40,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=0,Alignment=2'",
            "-c:a", "copy",
            str(output_file).replace('\\', '/')
        ],
        
        # Method 2: Escaped backslashes
        [
            "ffmpeg", "-y", 
            "-i", str(video_file),
            "-vf", f"subtitles={str(srt_file).replace('\\', '\\\\')}:force_style='FontName=Arial,FontSize=40,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=0,Alignment=2'",
            "-c:a", "copy",
            str(output_file)
        ],
        
        # Method 3: No quotes around subtitle path
        [
            "ffmpeg", "-y",
            "-i", str(video_file),
            "-vf", f"subtitles={str(srt_file).replace('\\', '/')}:force_style='FontName=Arial,FontSize=40,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=0,Alignment=2'",
            "-c:a", "copy", 
            str(output_file)
        ]
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n🧪 Testing method {i}...")
        print(f"Command: {' '.join(cmd[:4])} ... [truncated]")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
            print(f"✅ Method {i} SUCCESS!")
            print(f"📁 Output saved: {output_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Method {i} failed with exit code {e.returncode}")
            if e.stderr:
                # Show first few lines of error
                error_lines = e.stderr.split('\n')[:3]
                for line in error_lines:
                    if line.strip():
                        print(f"   Error: {line.strip()}")
        except subprocess.TimeoutExpired:
            print(f"❌ Method {i} timed out")
        except Exception as e:
            print(f"❌ Method {i} failed: {e}")
    
    print("\n❌ All caption methods failed")
    return False

def show_srt_content():
    """Show the content of the most recent SRT file"""
    srt_files = list(Path("esoteric_content_pipeline/final_videos").glob("*.srt"))
    
    if not srt_files:
        print("❌ No SRT files found")
        return
    
    srt_file = sorted(srt_files)[-1]
    print(f"\n📝 Content of {srt_file}:")
    print("-" * 30)
    
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:500])  # Show first 500 characters
            if len(content) > 500:
                print("... [truncated]")
    except Exception as e:
        print(f"❌ Error reading SRT file: {e}")

def main():
    """Main test function"""
    print("🧪 Caption Burning Test")
    print("=" * 30)
    
    # Show SRT content first
    show_srt_content()
    
    # Test caption burning
    if test_caption_burning():
        print("\n🎉 Caption test successful!")
    else:
        print("\n❌ Caption test failed - check FFmpeg installation and file paths")

if __name__ == "__main__":
    main()