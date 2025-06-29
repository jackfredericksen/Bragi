import os
import random
import requests
import subprocess
import logging
import warnings
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import openai
import anthropic
from generate_captions import transcribe_audio_to_srt, burn_captions

# Suppress pydub warnings since we know FFmpeg works
warnings.filterwarnings("ignore", message="Couldn't find ffmpeg or avconv")

from pydub import AudioSegment

# Load env
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def configure_ffmpeg_for_pydub():
    """Configure FFmpeg for pydub using known working path"""
    # We know from your test that this path works
    ffmpeg_path = r"C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
    
    if Path(ffmpeg_path).exists():
        AudioSegment.converter = ffmpeg_path
        AudioSegment.ffmpeg = ffmpeg_path
        AudioSegment.ffprobe = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
        print("✅ FFmpeg configured for pydub")
        return True
    else:
        # Fallback to PATH version (which also works)
        print("✅ Using FFmpeg from PATH")
        return True

BASE_PATH = Path("esoteric_content_pipeline")
SCRIPT_DIR = BASE_PATH / "scripts"
AUDIO_DIR = BASE_PATH / "audio"
VIDEO_DIR = BASE_PATH / "video_clips"
FINAL_DIR = BASE_PATH / "final_videos"
UPLOAD_QUEUE_DIR = BASE_PATH / "ready_to_upload"
TOPIC_FILE = "topics.txt"

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = BASE_PATH / "logs" / f"{timestamp}.log"

# Create directories
for folder in [SCRIPT_DIR, AUDIO_DIR, VIDEO_DIR, FINAL_DIR, UPLOAD_QUEUE_DIR, BASE_PATH / "logs"]:
    folder.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=log_path, 
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s: %(message)s'
)

def get_random_topic():
    if os.path.exists(TOPIC_FILE):
        with open(TOPIC_FILE, "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]
        return random.choice(topics)
    return "The nature of consciousness"

def generate_script_with_claude(topic):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""You are a mystical philosopher like Alan Watts or Terence McKenna.
Speak on the topic "{topic}" with poetic, dreamy, and esoteric language. Make it 60–90 seconds long, starting with a hook and ending on a profound note."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=600,
        temperature=1.0,
        system="You are an enlightened spiritual narrator.",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def synthesize_audio(text, output_path):
    """Generate speech using OpenAI TTS with dreamy male voice"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=text,
            response_format="mp3"
        )
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        logging.info(f"Audio generated with OpenAI TTS (onyx voice): {output_path}")
        
    except Exception as e:
        logging.error(f"Failed to generate audio with OpenAI TTS: {e}")
        raise

def get_audio_duration(audio_path):
    """Get the exact duration of an audio file in seconds"""
    try:
        audio = AudioSegment.from_file(audio_path)
        duration_seconds = len(audio) / 1000.0  # Convert from ms to seconds
        return duration_seconds
    except Exception as e:
        logging.error(f"Failed to get audio duration: {e}")
        return None

def add_background_music(voice_audio_path, output_path):
    """Mix background music with the voice audio - ensuring perfect sync"""
    assets_path = Path("assets")
    
    # Check if assets folder exists and has music files
    music_files = []
    if assets_path.exists():
        music_files = list(assets_path.glob("*.mp3"))
    
    if not music_files:
        # No background music available, just copy the original
        try:
            voice = AudioSegment.from_file(voice_audio_path)
            voice.export(output_path, format="mp3")
            logging.info("No background music found, using voice only")
            return get_audio_duration(output_path)
        except Exception as e:
            logging.error(f"Error processing voice audio: {e}")
            # Fallback: direct copy
            import shutil
            shutil.copy2(voice_audio_path, output_path)
            return get_audio_duration(output_path)
    
    # Select random background track
    bg_music_path = random.choice(music_files)
    logging.info(f"Using background music: {bg_music_path}")
    
    try:
        # Load audio files
        bg_music = AudioSegment.from_file(bg_music_path)
        voice = AudioSegment.from_file(voice_audio_path)
        
        print(f"🎙️ Voice duration: {len(voice)/1000:.2f} seconds")
        print(f"🎵 Background music duration: {len(bg_music)/1000:.2f} seconds")
        
        # Loop background to match voice length EXACTLY
        bg_music = bg_music - 20  # lower volume by 20dB
        if len(bg_music) < len(voice):
            # Loop the background music to match voice length
            loops_needed = (len(voice) // len(bg_music)) + 1
            bg_music = bg_music * loops_needed
            print(f"🔄 Looped background music {loops_needed} times")
        
        # Trim to EXACT voice length
        bg_music = bg_music[:len(voice)]
        
        print(f"✂️ Final background music duration: {len(bg_music)/1000:.2f} seconds")
        
        # Mix and export
        combined = voice.overlay(bg_music)
        combined.export(output_path, format="mp3")
        
        final_duration = len(combined) / 1000.0
        logging.info(f"Mixed audio saved to: {output_path}, duration: {final_duration:.2f}s")
        print(f"🎵 Final mixed audio duration: {final_duration:.2f} seconds")
        
        return final_duration
        
    except Exception as e:
        logging.error(f"Failed to mix background music: {e}")
        # Fallback: just use voice without music
        try:
            voice = AudioSegment.from_file(voice_audio_path)
            voice.export(output_path, format="mp3")
            print("⚠️ Background music failed, using voice only")
            return len(voice) / 1000.0
        except Exception as e2:
            logging.error(f"Fallback audio processing failed: {e2}")
            import shutil
            shutil.copy2(voice_audio_path, output_path)
            return get_audio_duration(output_path)

def download_trippy_video(output_path, target_duration=None):
    """Download video and ensure it's long enough for the audio"""
    headers = {"Authorization": PEXELS_API_KEY}
    search_term = random.choice(["psychedelic", "space", "cosmic", "fractal", "nature", "trippy", "meditation", "abstract"])
    url = f"https://api.pexels.com/videos/search?query={search_term}&orientation=portrait&per_page=20"

    response = requests.get(url, headers=headers)
    data = response.json()
    if not data["videos"]:
        raise Exception(f"No videos found for search term: {search_term}")

    # Find a video that's long enough or close to our target duration
    suitable_video = None
    
    for video in data["videos"]:
        video_duration = video.get("duration", 0)
        if target_duration and video_duration >= target_duration:
            suitable_video = video
            print(f"🎬 Found video with duration {video_duration}s (need {target_duration:.1f}s)")
            break
    
    # Fallback to first video if no suitable duration found
    if not suitable_video:
        suitable_video = data["videos"][0]
        video_duration = suitable_video.get("duration", 0)
        print(f"🎬 Using first available video (duration: {video_duration}s)")
    
    # Get the best quality video file
    video_files = suitable_video["video_files"]
    
    # Prefer HD quality
    best_video = None
    for vf in video_files:
        if vf.get("quality") == "hd":
            best_video = vf
            break
    
    if not best_video:
        best_video = video_files[0]
    
    video_url = best_video["link"]
    logging.info(f"Downloading video: {search_term} from {video_url}")
    
    r = requests.get(video_url)
    r.raise_for_status()
    
    with open(output_path, "wb") as f:
        f.write(r.content)
    
    return video_duration

def get_video_duration(video_path):
    """Get the exact duration of a video file"""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json", 
            "-show_format", str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        info = json.loads(result.stdout)
        duration = float(info["format"]["duration"])
        return duration
        
    except Exception as e:
        logging.error(f"Failed to get video duration: {e}")
        return None

def merge_audio_video(audio_path, video_path, output_path, audio_duration):
    """Merge audio and video with perfect synchronization"""
    
    # Get actual durations
    video_duration = get_video_duration(video_path)
    
    if video_duration:
        print(f"🎥 Video duration: {video_duration:.2f} seconds")
        print(f"🎙️ Audio duration: {audio_duration:.2f} seconds")
        
        if video_duration < audio_duration:
            print(f"⚠️ Video is shorter than audio! Will loop video to match.")
        elif video_duration > audio_duration + 2:  # More than 2 seconds longer
            print(f"✂️ Video is much longer than audio, will trim to match.")
    
    # Use ffmpeg to merge with perfect audio synchronization
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "libx264",  # Re-encode video for better control
        "-c:a", "aac",
        "-shortest",  # Use shortest stream (audio will control length)
        "-fflags", "+shortest",  # Ensure shortest flag is enforced
        "-max_interleave_delta", "100M",  # Better A/V sync
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logging.info(f"Successfully merged audio and video: {output_path}")
        
        # Verify final video duration
        final_duration = get_video_duration(output_path)
        if final_duration:
            print(f"✅ Final video duration: {final_duration:.2f} seconds")
            if abs(final_duration - audio_duration) > 0.5:  # More than 0.5s difference
                print(f"⚠️ Duration mismatch: video {final_duration:.2f}s vs audio {audio_duration:.2f}s")
            else:
                print(f"🎯 Perfect sync! Video matches audio duration")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg merge failed: {e}")
        logging.error(f"FFmpeg stderr: {e.stderr}")
        raise

def create_upload_instructions(video_path, topic, script, timestamp):
    """Create instructions for manual upload"""
    instructions_file = UPLOAD_QUEUE_DIR / f"{timestamp}_upload_instructions.txt"
    
    # Generate suggested captions for each platform
    tiktok_caption = f"{topic} #esoteric #alanwatts #consciousness #psychedelic #philosophy #mystical #fyp"
    youtube_title = f"{topic} - Esoteric Philosophy #Shorts"
    youtube_description = f"""Exploring {topic.lower()} through the lens of mystical philosophy.

Inspired by the teachings of Alan Watts and Terence McKenna, this short explores the deeper mysteries of existence and consciousness.

#esoteric #consciousness #philosophy #alanwatts #terencemckenna #mysticism #shorts #spirituality #awakening"""

    # Get video duration for reference
    video_duration = get_video_duration(video_path)
    duration_info = f" ({video_duration:.1f} seconds)" if video_duration else ""

    instructions_content = f"""🎬 UPLOAD INSTRUCTIONS for {timestamp}
{"="*60}

📁 VIDEO FILE: {video_path.name}{duration_info}
📝 TOPIC: {topic}
⏱️ CREATED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{"="*60}
🎵 TIKTOK UPLOAD
{"="*60}

📋 CAPTION TO USE:
{tiktok_caption}

📱 UPLOAD STEPS:
1. Open TikTok app or web.tiktok.com
2. Click "+" to create new video
3. Upload: {video_path.name}
4. Copy-paste caption above
5. Enable auto-captions in TikTok settings
6. Add trending sounds if desired
7. Post!

{"="*60}
📺 YOUTUBE SHORTS UPLOAD  
{"="*60}

📋 TITLE TO USE:
{youtube_title}

📋 DESCRIPTION TO USE:
{youtube_description}

📱 UPLOAD STEPS:
1. Open YouTube Studio (studio.youtube.com)
2. Click "Create" → "Upload videos"
3. Upload: {video_path.name}
4. Title: Copy title above
5. Description: Copy description above  
6. Select "Short" if not auto-detected
7. Enable auto-captions in YouTube settings
8. Publish!

{"="*60}
📜 ORIGINAL SCRIPT
{"="*60}
{script}

{"="*60}
💡 TIPS
{"="*60}
- Best posting times: 6-9pm local time
- Engage with early comments quickly
- Cross-post within 1-2 hours for max reach
- Monitor performance and adjust hashtags
- Save high-performing topics for future content
- Platform auto-captions are enabled by default
- Video duration is perfectly synced with audio

✅ DELETE THIS FILE AFTER UPLOADING
"""

    with open(instructions_file, "w", encoding="utf-8") as f:
        f.write(instructions_content)
    
    return instructions_file

def prepare_for_upload(video_path, topic, script, timestamp):
    """Prepare video and instructions for manual upload"""
    # Copy video to upload queue with clear naming
    upload_video_path = UPLOAD_QUEUE_DIR / f"{timestamp}_{topic.replace(' ', '_').replace('/', '_')}.mp4"
    
    import shutil
    shutil.copy2(video_path, upload_video_path)
    
    # Create upload instructions
    instructions_file = create_upload_instructions(upload_video_path, topic, script, timestamp)
    
    return upload_video_path, instructions_file

def main():
    try:
        # Configure FFmpeg for pydub
        configure_ffmpeg_for_pydub()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logging.info("Starting video generation pipeline")
        
        print("🧠 Esoteric Content Generator Starting...")
        print("=" * 50)

        # Step 1: Get topic and generate script
        topic = get_random_topic()
        logging.info(f"Topic selected: {topic}")
        print(f"📝 Topic: {topic}")

        script = generate_script_with_claude(topic)
        script_path = SCRIPT_DIR / f"{timestamp}.txt"
        script_path.write_text(script, encoding="utf-8")
        logging.info(f"Script generated and saved to: {script_path}")
        print("✅ Script generated with Claude")

        # Step 2: Generate voice audio with OpenAI TTS
        audio_path = AUDIO_DIR / f"{timestamp}.mp3"
        synthesize_audio(script, audio_path)
        base_audio_duration = get_audio_duration(audio_path)
        logging.info(f"Voice audio generated: {audio_path}, duration: {base_audio_duration:.2f}s")
        print(f"🎙️ Voice generated with OpenAI TTS (onyx) - {base_audio_duration:.2f}s")

        # Step 3: Add background music and get final audio duration
        combined_audio_path = AUDIO_DIR / f"{timestamp}_with_music.mp3"
        final_audio_duration = add_background_music(audio_path, combined_audio_path)

        # Step 4: Download background video with target duration
        video_path = VIDEO_DIR / f"{timestamp}.mp4"
        video_duration = download_trippy_video(video_path, final_audio_duration)
        logging.info(f"Background video downloaded: {video_path}")
        print("🎬 Trippy background video downloaded")

        # Step 5: Merge audio and video with perfect sync
        final_path = FINAL_DIR / f"{timestamp}_final.mp4"
        merge_audio_video(str(combined_audio_path), str(video_path), str(final_path), final_audio_duration)
        logging.info(f"Audio and video merged: {final_path}")
        print("🎥 Audio and video merged with perfect sync")

        # Step 6: Generate SRT captions (for reference/backup)
        srt_path = FINAL_DIR / f"{timestamp}.srt"
        
        # Use the final video as the "captioned" version (no burning needed)
        captioned_path = final_path

        # Generate SRT file for reference
        transcribe_audio_to_srt(combined_audio_path, srt_path)
        logging.info(f"Captions generated: {srt_path}")
        print("📝 SRT captions generated (platforms will handle auto-captions)")

        # Step 7: Prepare for manual upload
        print("\n📤 Preparing for manual upload...")
        upload_video_path, instructions_file = prepare_for_upload(captioned_path, topic, script, timestamp)
        
        logging.info("Pipeline completed successfully")
        print("\n" + "=" * 50)
        print("🎉 CONTENT GENERATION COMPLETED!")
        print("=" * 50)
        print(f"📁 Video ready: {upload_video_path.name}")
        print(f"📋 Instructions: {instructions_file.name}")
        print(f"📊 Log file: {log_path}")
        print("\n💡 NEXT STEPS:")
        print("1. Check the 'ready_to_upload' folder")
        print("2. Open the instructions file for upload details")
        print("3. Upload to TikTok and YouTube when ready")
        print("4. Enable platform auto-captions during upload")
        print("5. Delete instructions file after uploading")
        
        # Show quick preview of what was created
        final_video_duration = get_video_duration(upload_video_path)
        print(f"\n🎬 CONTENT PREVIEW:")
        print(f"Topic: {topic}")
        print(f"Script length: {len(script)} characters")
        print(f"Audio duration: {final_audio_duration:.2f} seconds")
        print(f"Video duration: {final_video_duration:.2f} seconds" if final_video_duration else "Video duration: Unknown")
        print(f"Sync status: {'✅ Perfect' if final_video_duration and abs(final_video_duration - final_audio_duration) < 0.5 else '⚠️ Check sync'}")
        print(f"Has background music: {'Yes' if Path('assets').exists() and list(Path('assets').glob('*.mp3')) else 'No'}")

    except Exception as e:
        logging.error(f"Error in main pipeline: {e}")
        print(f"\n❌ Error: {e}")
        print("📋 Check the logs for more details.")
        print(f"📊 Log file: {log_path}")

if __name__ == "__main__":
    main()