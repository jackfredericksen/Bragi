import os
import random
import requests
import subprocess
import logging
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from elevenlabs import generate, save
import anthropic
from generate_captions import transcribe_audio_to_srt, burn_captions
from upload_tiktok import upload_to_tiktok
from upload_youtube import upload_to_youtube
from pydub import AudioSegment

# Load env
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

BASE_PATH = Path("esoteric_content_pipeline")
SCRIPT_DIR = BASE_PATH / "scripts"
AUDIO_DIR = BASE_PATH / "audio"
VIDEO_DIR = BASE_PATH / "video_clips"
FINAL_DIR = BASE_PATH / "final_videos"
TOPIC_FILE = "topics.txt"

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = BASE_PATH / "logs" / f"{timestamp}.log"

# Create directories
for folder in [SCRIPT_DIR, AUDIO_DIR, VIDEO_DIR, FINAL_DIR, BASE_PATH / "logs"]:
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
        model="claude-3-sonnet-20240229",
        max_tokens=600,
        temperature=1.0,
        system="You are an enlightened spiritual narrator.",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def synthesize_audio(text, output_path):
    audio = generate(
        text=text,
        voice=ELEVENLABS_VOICE_ID,
        model="eleven_multilingual_v2",
        api_key=ELEVENLABS_API_KEY
    )
    save(audio, output_path)

def add_background_music(voice_audio_path, output_path):
    """Mix background music with the voice audio"""
    assets_path = Path("assets")
    
    # Check if assets folder exists and has music files
    music_files = []
    if assets_path.exists():
        music_files = list(assets_path.glob("*.mp3"))
    
    if not music_files:
        # If no background music available, just copy the original
        voice = AudioSegment.from_file(voice_audio_path)
        voice.export(output_path, format="mp3")
        logging.info("No background music found, using voice only")
        return
    
    # Select random background track
    bg_music_path = random.choice(music_files)
    logging.info(f"Using background music: {bg_music_path}")
    
    # Load audio files
    bg_music = AudioSegment.from_file(bg_music_path)
    voice = AudioSegment.from_file(voice_audio_path)
    
    # Loop background to match voice length
    bg_music = bg_music - 20  # lower volume by 20dB
    if len(bg_music) < len(voice):
        # Loop the background music to match voice length
        loops_needed = (len(voice) // len(bg_music)) + 1
        bg_music = bg_music * loops_needed
    
    # Trim to voice length
    bg_music = bg_music[:len(voice)]
    
    # Mix and export
    combined = voice.overlay(bg_music)
    combined.export(output_path, format="mp3")
    logging.info(f"Mixed audio saved to: {output_path}")

def download_trippy_video(output_path):
    headers = {"Authorization": PEXELS_API_KEY}
    search_term = random.choice(["psychedelic", "space", "cosmic", "fractal", "nature", "trippy"])
    url = f"https://api.pexels.com/videos/search?query={search_term}&orientation=portrait&per_page=10"

    response = requests.get(url, headers=headers)
    data = response.json()
    if not data["videos"]:
        raise Exception("No videos found.")

    # Try to get the best quality video file
    video = data["videos"][0]
    video_files = video["video_files"]
    
    # Prefer HD quality files
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
    with open(output_path, "wb") as f:
        f.write(r.content)

def merge_audio_video(audio_path, video_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True)

def main():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logging.info("Starting video generation pipeline")

        # Step 1: Get topic and generate script
        topic = get_random_topic()
        logging.info(f"Topic selected: {topic}")
        print(f"[+] Topic: {topic}")

        script = generate_script_with_claude(topic)
        script_path = SCRIPT_DIR / f"{timestamp}.txt"
        script_path.write_text(script, encoding="utf-8")
        logging.info(f"Script generated and saved to: {script_path}")

        # Step 2: Generate voice audio
        audio_path = AUDIO_DIR / f"{timestamp}.mp3"
        synthesize_audio(script, audio_path)
        logging.info(f"Voice audio generated: {audio_path}")
        print("[+] Audio generated.")

        # Step 3: Add background music
        combined_audio_path = AUDIO_DIR / f"{timestamp}_with_music.mp3"
        add_background_music(audio_path, combined_audio_path)
        print("[+] Background music added.")

        # Step 4: Download background video
        video_path = VIDEO_DIR / f"{timestamp}.mp4"
        download_trippy_video(video_path)
        logging.info(f"Background video downloaded: {video_path}")
        print("[+] Background video downloaded.")

        # Step 5: Merge audio and video
        final_path = FINAL_DIR / f"{timestamp}_final.mp4"
        merge_audio_video(str(combined_audio_path), str(video_path), str(final_path))
        logging.info(f"Audio and video merged: {final_path}")
        print(f"[+] Final video saved to: {final_path}")

        # Step 6: Generate and burn captions
        srt_path = FINAL_DIR / f"{timestamp}.srt"
        captioned_path = FINAL_DIR / f"{timestamp}_captioned.mp4"

        # Transcribe audio to subtitles
        transcribe_audio_to_srt(combined_audio_path, srt_path)
        logging.info(f"Captions generated: {srt_path}")
        print("[+] Captions generated.")

        # Burn captions into video
        burn_captions(final_path, srt_path, captioned_path)
        logging.info(f"Captions burned into video: {captioned_path}")
        print(f"[+] Final video with captions saved: {captioned_path}")

        # Step 7: Upload to platforms
        caption = f"{topic} #esoteric #alanwatts #consciousness #psychedelic"
        
        try:
            upload_to_tiktok(captioned_path, caption)
            logging.info("Successfully uploaded to TikTok")
        except Exception as e:
            logging.error(f"TikTok upload failed: {e}")
            print(f"⚠️ TikTok upload failed: {e}")
        
        try:
            upload_to_youtube(captioned_path, topic)
            logging.info("Successfully uploaded to YouTube")
        except Exception as e:
            logging.error(f"YouTube upload failed: {e}")
            print(f"⚠️ YouTube upload failed: {e}")

        logging.info("Pipeline completed successfully")
        print("✅ Pipeline completed successfully!")

    except Exception as e:
        logging.error(f"Error in main pipeline: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()