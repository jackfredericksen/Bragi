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
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = BASE_PATH / "logs" / f"{timestamp}.log"
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Select random background track
bg_music_path = Path("assets") / random.choice(["ambient1.mp3", "ambient2.mp3"])
bg_music = AudioSegment.from_file(bg_music_path)
voice = AudioSegment.from_file(audio_path)

# Loop background to match voice length
bg_music = bg_music - 20  # lower volume
bg_music = bg_music * (len(voice) // len(bg_music) + 1)
bg_music = bg_music[:len(voice)]

# Mix and export
combined = voice.overlay(bg_music)
combined_audio_path = AUDIO_DIR / f"{timestamp}_with_music.mp3"
combined.export(combined_audio_path, format="mp3")

for folder in [SCRIPT_DIR, AUDIO_DIR, VIDEO_DIR, FINAL_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

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

def download_trippy_video(output_path):
    headers = {"Authorization": PEXELS_API_KEY}
    search_term = random.choice(["psychedelic", "space", "cosmic", "fractal", "nature", "trippy"])
    url = f"https://api.pexels.com/videos/search?query={search_term}&orientation=portrait&per_page=1"

    response = requests.get(url, headers=headers)
    data = response.json()
    if not data["videos"]:
        raise Exception("No videos found.")

    video_url = data["videos"][0]["video_files"][0]["link"]
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

        topic = get_random_topic()
        print(f"[+] Topic: {topic}")

        script = generate_script_with_claude(topic)
        script_path = SCRIPT_DIR / f"{timestamp}.txt"
        script_path.write_text(script, encoding="utf-8")

        audio_path = AUDIO_DIR / f"{timestamp}.mp3"
        synthesize_audio(script, audio_path)
        print("[+] Audio generated.")

        video_path = VIDEO_DIR / f"{timestamp}.mp4"
        download_trippy_video(video_path)
        print("[+] Background video downloaded.")

        final_path = FINAL_DIR / f"{timestamp}_final.mp4"
        merge_audio_video(str(audio_path), str(video_path), str(final_path))
        print(f"[+] Final video saved to: {final_path}")

        srt_path = FINAL_DIR / f"{timestamp}.srt"
        captioned_path = FINAL_DIR / f"{timestamp}_captioned.mp4"

        # Transcribe audio to subtitles
        transcribe_audio_to_srt(audio_path, srt_path)
        print("[+] Captions generated.")

        # Burn captions into video
        burn_captions(final_path, srt_path, captioned_path)
        print(f"[+] Final video with captions saved: {captioned_path}")

        caption = f"{topic} #esoteric #alanwatts #consciousness #psychedelic"
        upload_to_tiktok(captioned_path, caption)
        upload_to_youtube(captioned_path, topic)
    except Exception as e:
        logging.error(f"Error in main pipeline: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
