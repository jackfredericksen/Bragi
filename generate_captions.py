import whisper
from pathlib import Path
import subprocess
import os
import shutil

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
    """Burn captions into video using FFmpeg with Windows path workaround"""
    
    # Convert paths to Path objects
    video_path = Path(video_path)
    srt_path = Path(srt_path)
    output_path = Path(output_path)
    
    # Verify files exist
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not srt_path.exists():
        raise FileNotFoundError(f"SRT file not found: {srt_path}")
    
    print(f"🔥 Burning captions into video...")
    
    # Method 1: Try with short path names (8.3 format) to avoid spaces
    try:
        # Get short path names on Windows to avoid issues with spaces
        if os.name == 'nt':  # Windows
            import subprocess
            
            def get_short_path(path):
                try:
                    result = subprocess.run(['cmd', '/c', 'for', '%i', 'in', f'("{path}")', 'do', '@echo', '%~si'], 
                                          capture_output=True, text=True)
                    short_path = result.stdout.strip()
                    return short_path if short_path else str(path)
                except:
                    return str(path)
            
            short_video = get_short_path(video_path)
            short_srt = get_short_path(srt_path)
            short_output = get_short_path(output_path)
        else:
            short_video = str(video_path)
            short_srt = str(srt_path)
            short_output = str(output_path)
        
        # FFmpeg command with short paths
        style = "FontName=Arial,FontSize=40,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=0,Alignment=2"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", short_video,
            "-vf", f"subtitles={short_srt}:force_style='{style}'",
            "-c:a", "copy",
            short_output
        ]
        
        print(f"   Attempting with short paths...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        print("✅ Captions burned successfully!")
        return
        
    except Exception as e:
        print(f"⚠️ Short path method failed: {e}")
    
    # Method 2: Copy files to temp location with simple names
    try:
        print("🔄 Trying with temporary files...")
        
        # Create temp directory
        temp_dir = Path("temp_caption_work")
        temp_dir.mkdir(exist_ok=True)
        
        # Copy files with simple names
        temp_video = temp_dir / "video.mp4"
        temp_srt = temp_dir / "subtitles.srt"
        temp_output = temp_dir / "output.mp4"
        
        shutil.copy2(video_path, temp_video)
        shutil.copy2(srt_path, temp_srt)
        
        # FFmpeg command with simple paths
        cmd = [
            "ffmpeg", "-y",
            "-i", str(temp_video),
            "-vf", f"subtitles={str(temp_srt)}:force_style='{style}'",
            "-c:a", "copy",
            str(temp_output)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        
        # Copy result back
        shutil.copy2(temp_output, output_path)
        
        # Cleanup temp files
        shutil.rmtree(temp_dir)
        
        print("✅ Captions burned successfully with temp files!")
        return
        
    except Exception as e:
        print(f"⚠️ Temp file method failed: {e}")
    
    # Method 3: Create video without captions
    try:
        print("📝 Creating video without burned-in captions as fallback...")
        shutil.copy2(video_path, output_path)
        print("⚠️ Video copied without captions - you can add them manually later")
        
    except Exception as e:
        print(f"❌ Even fallback copy failed: {e}")
        raise