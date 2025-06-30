import whisper
from pathlib import Path
import subprocess
import os
import shutil
import tempfile
import re

def transcribe_audio_to_srt(audio_path, srt_path):
    """Transcribe audio to SRT with short, punchy captions that sync perfectly"""
    try:
        # Use word-level timestamps for precise control
        model = whisper.load_model("base")
        result = model.transcribe(str(audio_path), word_timestamps=True)
        
        with open(srt_path, "w", encoding="utf-8") as f:
            subtitle_index = 1
            
            for segment in result["segments"]:
                # Get word-level timing if available
                words = segment.get("words", [])
                
                if words:
                    # Create short, punchy caption chunks
                    caption_chunks = create_punchy_chunks(words)
                    
                    for chunk in caption_chunks:
                        start = format_timestamp(chunk["start"])
                        end = format_timestamp(chunk["end"])
                        text = chunk["text"]
                        
                        f.write(f"{subtitle_index}\n{start} --> {end}\n{text}\n\n")
                        subtitle_index += 1
                else:
                    # Fallback: break long segments into short chunks
                    start_time = segment["start"]
                    end_time = segment["end"]
                    text = segment["text"].strip()
                    
                    # Create punchy chunks from the text
                    chunks = create_short_text_chunks(text, start_time, end_time)
                    
                    for chunk in chunks:
                        start = format_timestamp(chunk["start"])
                        end = format_timestamp(chunk["end"])
                        f.write(f"{subtitle_index}\n{start} --> {end}\n{chunk['text']}\n\n")
                        subtitle_index += 1
        
        print(f"✅ Punchy captions saved to: {srt_path}")
        
    except Exception as e:
        print(f"❌ Caption generation failed: {e}")
        raise

def create_punchy_chunks(words, max_words=3, max_chars=20):
    """Create short, impactful caption chunks from word timestamps"""
    chunks = []
    current_chunk = []
    current_text = ""
    
    for word in words:
        word_text = word.get("word", "").strip()
        word_start = word.get("start", 0)
        word_end = word.get("end", 0)
        
        # Clean up word text
        word_text = word_text.strip(".,!?;:")
        if not word_text:
            continue
        
        # Test if adding this word would be too long
        test_text = current_text + (" " if current_text else "") + word_text
        
        if (len(current_chunk) < max_words and len(test_text) <= max_chars):
            # Add to current chunk
            current_chunk.append(word)
            current_text = test_text
        else:
            # Finish current chunk
            if current_chunk:
                chunks.append({
                    "start": current_chunk[0]["start"],
                    "end": current_chunk[-1]["end"],
                    "text": " ".join([w.get("word", "").strip(".,!?;:") for w in current_chunk]).strip()
                })
            
            # Start new chunk
            current_chunk = [word]
            current_text = word_text
    
    # Add the last chunk
    if current_chunk:
        chunks.append({
            "start": current_chunk[0]["start"],
            "end": current_chunk[-1]["end"],
            "text": " ".join([w.get("word", "").strip(".,!?;:") for w in current_chunk]).strip()
        })
    
    return chunks

def create_short_text_chunks(text, start_time, end_time):
    """Break long text into short chunks with proportional timing"""
    
    # Clean and split text
    text = re.sub(r'\s+', ' ', text.strip())
    words = text.split()
    
    chunks = []
    chunk_size = 3  # 3 words per chunk max
    total_duration = end_time - start_time
    
    # Calculate how many chunks we'll have
    num_chunks = (len(words) + chunk_size - 1) // chunk_size
    chunk_duration = total_duration / num_chunks if num_chunks > 0 else total_duration
    
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        # Calculate timing for this chunk
        chunk_index = i // chunk_size
        chunk_start = start_time + (chunk_index * chunk_duration)
        chunk_end = min(start_time + ((chunk_index + 1) * chunk_duration), end_time)
        
        chunks.append({
            "start": chunk_start,
            "end": chunk_end,
            "text": chunk_text
        })
    
    return chunks

def elegant_text_wrap(text, max_chars_per_line=25):
    """Create elegant, readable text chunks that fit nicely on mobile"""
    
    # Clean up the text
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split into sentences first
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    
    for sentence in sentences:
        words = sentence.split()
        current_chunk = ""
        
        for word in words:
            test_chunk = current_chunk + (" " if current_chunk else "") + word
            
            if len(test_chunk) <= max_chars_per_line:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk)
    
    return chunks

def format_timestamp(seconds):
    """Format seconds to SRT timestamp format"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

def burn_captions(video_path, srt_path, output_path):
    """Burn elegant, mobile-optimized captions"""
    
    print("🔥 Burning elegant captions into video...")
    
    # Use temporary directory for clean processing
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
            
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            # Method 1: Perfect TikTok/YouTube mobile style
            cmd = [
                "ffmpeg", "-y",
                "-i", "input.mp4",
                "-vf", (
                    "subtitles=captions.srt:force_style='"
                    "FontName=Arial Black,"
                    "FontSize=40,"
                    "Bold=1,"
                    "PrimaryColour=&Hffffff&,"
                    "OutlineColour=&H000000&,"
                    "Outline=4,"
                    "Shadow=2,"
                    "Alignment=2,"
                    "MarginV=160,"
                    "BorderStyle=1"
                    "'"
                ),
                "-c:a", "copy",
                "output.mp4"
            ]
            
            print("🎬 Creating professional captions...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                os.chdir(original_cwd)
                shutil.copy2(temp_output, output_path)
                print("✅ Professional captions created successfully!")
                return
            else:
                print(f"⚠️ Professional style failed, trying simplified...")
                
        except Exception as e:
            print(f"⚠️ Professional style exception: {e}")
        
        # Method 2: Simplified but elegant style
        try:
            os.chdir(temp_dir)
            
            cmd = [
                "ffmpeg", "-y",
                "-i", "input.mp4",
                "-vf", (
                    "subtitles=captions.srt:force_style='"
                    "FontName=Arial,"
                    "FontSize=28,"
                    "Bold=1,"
                    "PrimaryColour=&Hffffff&,"
                    "OutlineColour=&H000000&,"
                    "Outline=2,"
                    "Alignment=2,"
                    "MarginV=100"
                    "'"
                ),
                "-c:a", "copy",
                "output.mp4"
            ]
            
            print("🎬 Creating simplified elegant captions...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                os.chdir(original_cwd)
                shutil.copy2(temp_output, output_path)
                print("✅ Simplified elegant captions created!")
                return
            else:
                print(f"⚠️ Simplified style failed...")
                
        except Exception as e:
            print(f"⚠️ Simplified style exception: {e}")
        
        # Method 3: Ultra-minimal fallback
        try:
            os.chdir(temp_dir)
            
            # Create ultra-simple SRT
            simple_srt = temp_dir_path / "simple.srt"
            create_minimal_srt(temp_srt, simple_srt)
            
            cmd = [
                "ffmpeg", "-y",
                "-i", "input.mp4",
                "-vf", (
                    "subtitles=simple.srt:force_style='"
                    "FontSize=24,"
                    "PrimaryColour=&Hffffff&,"
                    "OutlineColour=&H000000&,"
                    "Outline=1,"
                    "Alignment=2"
                    "'"
                ),
                "-c:a", "copy",
                "output.mp4"
            ]
            
            print("🎬 Creating minimal captions...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                os.chdir(original_cwd)
                shutil.copy2(temp_output, output_path)
                print("✅ Minimal captions created!")
                return
                
        except Exception as e:
            print(f"⚠️ Minimal style exception: {e}")
        
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

def create_minimal_srt(input_srt, output_srt):
    """Create a minimal SRT file with very short, key phrases only"""
    
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
                    
                    # Extract key phrases only (first few words)
                    words = text.split()
                    if len(words) > 3:
                        key_phrase = ' '.join(words[:3]) + "..."
                    else:
                        key_phrase = text
                    
                    # Clean up
                    key_phrase = re.sub(r'[^\w\s\.]', '', key_phrase)
                    
                    f.write(f"{i}\n{timing}\n{key_phrase}\n\n")
                    
    except Exception as e:
        print(f"⚠️ Failed to create minimal SRT: {e}")
        # If failed, just copy the original
        shutil.copy2(input_srt, output_srt)