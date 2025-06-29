import whisper
from pathlib import Path
import subprocess
import os
import shutil
import tempfile

def transcribe_audio_to_srt(audio_path, srt_path):
    """Transcribe audio to SRT subtitle format using Whisper"""
    try:
        model = whisper.load_model("base")
        result = model.transcribe(str(audio_path))
        
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"]):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")
        
        print(f"✅ Captions saved to: {srt_path}")
        
    except Exception as e:
        print(f"❌ Caption generation failed: {e}")
        raise

def format_timestamp(seconds):
    """Format seconds to SRT timestamp format"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

def burn_captions(video_path, srt_path, output_path):
    """Burn captions using the most reliable method possible"""
    
    print("🔥 Burning captions into video...")
    
    # Method 1: Use temporary directory with simple file names
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Copy files to temp directory with simple names
        temp_video = temp_dir_path / "input.mp4"
        temp_srt = temp_dir_path / "captions.srt"
        temp_output = temp_dir_path / "output.mp4"
        
        try:
            # Copy input files
            shutil.copy2(video_path, temp_video)
            shutil.copy2(srt_path, temp_srt)
            
            print(f"📁 Working in temp directory: {temp_dir}")
            
            # Change to temp directory to avoid any path issues
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            # Method A: Simple subtitle burn with basic styling
            cmd = [
                "ffmpeg", "-y",
                "-i", "input.mp4",
                "-vf", "subtitles=captions.srt:force_style='FontSize=24,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,Outline=1,Bold=1,Alignment=2'",
                "-c:a", "copy",
                "output.mp4"
            ]
            
            print("🎬 Method A: Basic subtitle burn...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                # Success! Copy back to original location
                os.chdir(original_cwd)
                shutil.copy2(temp_output, output_path)
                print("✅ Captions burned successfully with Method A!")
                return
            else:
                print(f"⚠️ Method A failed: {result.stderr[:200]}...")
                
        except Exception as e:
            print(f"⚠️ Method A exception: {e}")
        
        # Restore working directory
        os.chdir(original_cwd)
        
        # Method B: Try with ASS filter instead
        try:
            os.chdir(temp_dir)
            
            cmd = [
                "ffmpeg", "-y",
                "-i", "input.mp4",
                "-vf", "ass=captions.srt",
                "-c:a", "copy", 
                "output.mp4"
            ]
            
            print("🎬 Method B: ASS filter...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                os.chdir(original_cwd)
                shutil.copy2(temp_output, output_path)
                print("✅ Captions burned successfully with Method B!")
                return
            else:
                print(f"⚠️ Method B failed: {result.stderr[:200]}...")
                
        except Exception as e:
            print(f"⚠️ Method B exception: {e}")
        
        # Restore working directory
        os.chdir(original_cwd)
        
        # Method C: Convert SRT to simpler format and try again
        try:
            os.chdir(temp_dir)
            
            # Create a simplified SRT with shorter text segments
            simple_srt = temp_dir_path / "simple.srt"
            create_simple_srt(temp_srt, simple_srt)
            
            cmd = [
                "ffmpeg", "-y",
                "-i", "input.mp4",
                "-vf", "subtitles=simple.srt:force_style='FontSize=20,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,Outline=1'",
                "-c:a", "copy",
                "output.mp4"
            ]
            
            print("🎬 Method C: Simplified captions...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                os.chdir(original_cwd)
                shutil.copy2(temp_output, output_path)
                print("✅ Captions burned successfully with Method C!")
                return
            else:
                print(f"⚠️ Method C failed: {result.stderr[:200]}...")
                
        except Exception as e:
            print(f"⚠️ Method C exception: {e}")
        
        # Restore working directory  
        os.chdir(original_cwd)
        
        # Method D: Last resort - hardcode text overlays
        try:
            os.chdir(temp_dir)
            
            # Extract just the first few words for a simple overlay
            with open(temp_srt, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            # Get first subtitle text
            import re
            matches = re.findall(r'\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+\n(.+?)(?=\n\d+|\n\n|\Z)', srt_content, re.DOTALL)
            if matches:
                first_text = matches[0].strip()[:50] + "..."  # First 50 chars
                
                cmd = [
                    "ffmpeg", "-y",
                    "-i", "input.mp4",
                    "-vf", f"drawtext=text='{first_text}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.5",
                    "-c:a", "copy",
                    "output.mp4"
                ]
                
                print("🎬 Method D: Simple text overlay...")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                
                if result.returncode == 0:
                    os.chdir(original_cwd)
                    shutil.copy2(temp_output, output_path)
                    print("✅ Basic text overlay added successfully!")
                    return
                    
        except Exception as e:
            print(f"⚠️ Method D exception: {e}")
        
        # Restore working directory
        os.chdir(original_cwd)
    
    # If all methods failed, copy video without captions
    print("📝 All caption methods failed - using video without captions")
    try:
        shutil.copy2(video_path, output_path)
        print("✅ Video ready (without burned captions)")
        print("💡 TIP: Platforms like TikTok and YouTube will auto-generate captions")
    except Exception as e:
        print(f"❌ Even video copy failed: {e}")
        raise

def create_simple_srt(input_srt, output_srt):
    """Create a simplified SRT file that's more likely to work with FFmpeg"""
    
    try:
        with open(input_srt, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into subtitle blocks
        blocks = content.strip().split('\n\n')
        
        with open(output_srt, 'w', encoding='utf-8') as f:
            for i, block in enumerate(blocks, 1):
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Get timing and text
                    timing = lines[1]
                    text = ' '.join(lines[2:])
                    
                    # Simplify text - remove special characters that might cause issues
                    text = text.replace('"', "'").replace('\n', ' ').replace('\r', '')
                    
                    # Limit text length to avoid issues
                    if len(text) > 80:
                        text = text[:77] + "..."
                    
                    # Write simplified subtitle
                    f.write(f"{i}\n{timing}\n{text}\n\n")
                    
    except Exception as e:
        print(f"⚠️ Failed to simplify SRT: {e}")
        # If simplification fails, just copy the original
        shutil.copy2(input_srt, output_srt)