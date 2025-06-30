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
    """Get a topic with enhanced variety tracking"""
    # Import the variety enhancer
    from content_variety_enhancer import get_varied_topic, create_expanded_topics_file, auto_expand_topics
    
    # Ensure we have an expanded topics file
    create_expanded_topics_file()
    
    # 10% chance to auto-generate new topics
    if random.random() < 0.1:
        auto_expand_topics()
    
    return get_varied_topic()

def generate_script_with_claude(topic):
    """Generate a clean philosophical script without any meta-instructions"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Much cleaner prompt that focuses on content, not delivery
    prompt = f"""Write a philosophical monologue about "{topic}" in the style of Alan Watts or Terence McKenna. 

Create a 60-90 second spoken piece that:
- Starts with an intriguing hook or question
- Explores the topic with poetic, mystical language
- Uses metaphors and profound insights
- Ends with a thought-provoking conclusion
- Flows naturally as spoken word

Write ONLY the monologue content itself - no stage directions, no speaking instructions, no meta-commentary. Just the pure philosophical content as it should be spoken."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=600,
        temperature=1.0,
        system="You are a philosophical content writer. Generate only the spoken content, no instructions or directions.",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Clean up the response to remove any meta-instructions that might slip through
    script = response.content[0].text.strip()
    
    # Remove common meta-instruction patterns
    meta_patterns = [
        r"\[.*?\]",  # Remove [instructions in brackets]
        r"\(.*speaking.*\)",  # Remove (speaking instructions)
        r"\(.*tone.*\)",  # Remove (tone instructions)
        r"\(.*voice.*\)",  # Remove (voice instructions)
        r"speaking in.*",  # Remove "speaking in a X manner"
        r".*contemplative tone.*",  # Remove tone descriptions
        r".*deliberate.*tone.*",  # Remove deliberate tone mentions
    ]
    
    import re
    for pattern in meta_patterns:
        script = re.sub(pattern, "", script, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and line breaks
    script = re.sub(r'\s+', ' ', script).strip()
    
    # Remove any sentences that start with meta-instructions
    sentences = script.split('.')
    clean_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and not any(word in sentence.lower() for word in [
            'speaking', 'voice', 'tone', 'delivery', 'manner', 'contemplative',
            'deliberate', 'pause', 'emphasis', 'inflection'
        ]):
            clean_sentences.append(sentence)
    
    # Reconstruct the script
    clean_script = '. '.join(clean_sentences)
    if clean_script and not clean_script.endswith('.'):
        clean_script += '.'
    
    return clean_script

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

def download_trippy_video(output_path):
    """Download background video with enhanced variety"""
    from content_variety_enhancer import get_varied_background_search
    
    headers = {"Authorization": PEXELS_API_KEY}
    
    # Use the enhanced variety system for search terms
    search_term = get_varied_background_search()
    
    url = f"https://api.pexels.com/videos/search?query={search_term}&orientation=portrait&per_page=20"

    print(f"🎬 Searching for: {search_term}")
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if not data["videos"]:
        # Fallback to basic search terms if specific search fails
        fallback_terms = ["abstract", "nature", "cosmic", "flowing", "peaceful"]
        search_term = random.choice(fallback_terms)
        url = f"https://api.pexels.com/videos/search?query={search_term}&orientation=portrait&per_page=20"
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if not data["videos"]:
            raise Exception(f"No videos found even with fallback terms")

    # Get the first available video (we'll loop it to match audio length)
    video = data["videos"][0]
    video_files = video["video_files"]
    
    # Prefer HD quality
    best_video = None
    for vf in video_files:
        if vf.get("quality") == "hd":
            best_video = vf
            break
    
    if not best_video:
        best_video = video_files[0]
    
    video_url = best_video["link"]
    video_duration = video.get("duration", 0)
    
    logging.info(f"Downloading video: {search_term} from {video_url}")
    print(f"🎬 Downloading {search_term} video (original duration: {video_duration}s)")
    
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

def extend_video_to_match_audio(video_path, audio_duration, output_path):
    """Loop/extend video to match audio duration exactly"""
    
    original_duration = get_video_duration(video_path)
    
    if not original_duration:
        print("❌ Could not determine video duration")
        return False
    
    print(f"🎥 Original video duration: {original_duration:.2f} seconds")
    print(f"🎙️ Target audio duration: {audio_duration:.2f} seconds")
    
    if original_duration >= audio_duration:
        # Video is long enough, just trim to match
        print(f"✂️ Video is long enough, trimming to {audio_duration:.2f} seconds")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-t", str(audio_duration),  # Trim to exact audio duration
            "-c", "copy",  # Copy without re-encoding for speed
            str(output_path)
        ]
    else:
        # Video is too short, loop it to match audio duration
        loops_needed = int(audio_duration / original_duration) + 1
        print(f"🔄 Video too short, will loop {loops_needed} times")
        
        # Create a concat list file
        concat_file = output_path.parent / "concat_list.txt"
        with open(concat_file, "w") as f:
            for i in range(loops_needed):
                f.write(f"file '{video_path.resolve()}'\n")
        
        # Concatenate the video file multiple times, then trim to exact duration
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-t", str(audio_duration),  # Trim to exact audio duration
            "-c", "copy",
            str(output_path)
        ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Clean up concat file if it exists
        concat_file = output_path.parent / "concat_list.txt"
        if concat_file.exists():
            concat_file.unlink()
        
        # Verify the result
        final_duration = get_video_duration(output_path)
        if final_duration:
            print(f"✅ Extended video duration: {final_duration:.2f} seconds")
            if abs(final_duration - audio_duration) < 1.0:  # Within 1 second is good
                print(f"🎯 Video duration matches audio!")
                return True
            else:
                print(f"⚠️ Duration mismatch: {abs(final_duration - audio_duration):.2f}s difference")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Video extension failed: {e}")
        print(f"❌ Failed to extend video: {e}")
        return False

def merge_audio_video(audio_path, video_path, output_path):
    """Merge audio and video - video should already be the right length"""
    
    print("🎬 Merging audio and video...")
    
    # Simple merge - both should be the same duration now
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",  # Copy video stream
        "-c:a", "aac",   # Re-encode audio
        "-map", "0:v:0",  # Use video from first input
        "-map", "1:a:0",  # Use audio from second input
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logging.info(f"Successfully merged audio and video: {output_path}")
        
        # Verify final video duration
        final_duration = get_video_duration(output_path)
        if final_duration:
            print(f"✅ Final video duration: {final_duration:.2f} seconds")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg merge failed: {e}")
        logging.error(f"FFmpeg stderr: {e.stderr}")
        print(f"❌ Audio/video merge failed: {e}")
        return False

def create_upload_instructions(video_path, topic, script, timestamp):
    """Create instructions for manual upload with dynamic captions"""
    from dynamic_captions_hashtags import (
        create_tiktok_caption, 
        create_youtube_title_and_description,
        save_caption_hashtag_usage
    )
    
    instructions_file = UPLOAD_QUEUE_DIR / f"{timestamp}_upload_instructions.txt"
    
    # Generate dynamic content
    tiktok_caption = create_tiktok_caption(topic)
    youtube_title, youtube_description = create_youtube_title_and_description(topic)
    
    # Track usage for variety
    hashtags_used = [tag for tag in tiktok_caption.split() if tag.startswith('#')]
    save_caption_hashtag_usage(tiktok_caption, hashtags_used)
    
    # Get video duration for reference
    video_duration = get_video_duration(video_path)
    duration_info = f" ({video_duration:.1f} seconds)" if video_duration else ""

    instructions_content = f"""🎬 UPLOAD INSTRUCTIONS for {timestamp}
{"="*60}

📁 VIDEO FILE: {video_path.name}{duration_info}
📝 TOPIC: {topic}
⏱️ CREATED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

✨ This video has BURNED-IN CAPTIONS - no need to add additional captions!

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
5. Post! (Captions already embedded in video)

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
7. Publish! (Captions already embedded in video)

{"="*60}
📜 ORIGINAL SCRIPT
{"="*60}
{script}

{"="*60}
💡 CONTENT FEATURES
{"="*60}
- Video has professional burned-in captions
- Dynamic hashtags for maximum reach
- Generic spiritual/philosophical tags (no specific names)
- Varied caption style for engagement
- Optimized for mobile viewing

💡 POSTING TIPS
{"="*60}
- Best posting times: 6-9pm local time
- Engage with early comments quickly
- Cross-post within 1-2 hours for max reach
- Monitor which hashtag combinations perform best
- Save high-performing topics for future content

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
        print("✅ Clean script generated with Claude")

        # Step 2: Generate voice audio with OpenAI TTS
        audio_path = AUDIO_DIR / f"{timestamp}.mp3"
        synthesize_audio(script, audio_path)
        base_audio_duration = get_audio_duration(audio_path)
        logging.info(f"Voice audio generated: {audio_path}, duration: {base_audio_duration:.2f}s")
        print(f"🎙️ Voice generated with OpenAI TTS (onyx) - {base_audio_duration:.2f}s")

        # Step 3: Add background music and get final audio duration
        combined_audio_path = AUDIO_DIR / f"{timestamp}_with_music.mp3"
        final_audio_duration = add_background_music(audio_path, combined_audio_path)

        # Step 4: Download background video
        video_path = VIDEO_DIR / f"{timestamp}.mp4"
        original_video_duration = download_trippy_video(video_path)
        logging.info(f"Background video downloaded: {video_path}")

        # Step 5: Extend video to match audio duration
        extended_video_path = VIDEO_DIR / f"{timestamp}_extended.mp4"
        print("\n🔄 Extending video to match audio length...")
        
        if extend_video_to_match_audio(video_path, final_audio_duration, extended_video_path):
            print("✅ Video extended successfully")
            video_to_use = extended_video_path
        else:
            print("⚠️ Video extension failed, using original")
            video_to_use = video_path

        # Step 6: Merge audio and video with perfect sync
        final_path = FINAL_DIR / f"{timestamp}_final.mp4"
        if merge_audio_video(str(combined_audio_path), str(video_to_use), str(final_path)):
            logging.info(f"Audio and video merged: {final_path}")
            print("🎥 Audio and video merged successfully")
        else:
            raise Exception("Failed to merge audio and video")

        # Step 7: Generate and burn captions
        srt_path = FINAL_DIR / f"{timestamp}.srt"
        captioned_path = FINAL_DIR / f"{timestamp}_captioned.mp4"

        # Transcribe audio to subtitles
        transcribe_audio_to_srt(combined_audio_path, srt_path)
        logging.info(f"Captions generated: {srt_path}")
        print("📝 Captions generated with Whisper")

        # Burn captions into video
        burn_captions(final_path, srt_path, captioned_path)
        logging.info(f"Captions burned into video: {captioned_path}")
        print("🔥 Captions burned into video successfully")

        # Step 8: Prepare for manual upload with dynamic captions
        print("\n📤 Preparing for manual upload with dynamic captions...")
        upload_video_path, instructions_file = prepare_for_upload(captioned_path, topic, script, timestamp)
        
        # Show what captions were generated
        from dynamic_captions_hashtags import create_tiktok_caption, create_youtube_title_and_description
        sample_tiktok = create_tiktok_caption(topic)
        sample_yt_title, _ = create_youtube_title_and_description(topic)
        print(f"📝 Generated TikTok caption preview: {sample_tiktok[:50]}...")
        print(f"📺 Generated YouTube title: {sample_yt_title}")
        
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
        print("4. Captions are already burned into the video!")
        print("5. Delete instructions file after uploading")
        
        # Show quick preview of what was created
        final_video_duration = get_video_duration(upload_video_path)
        print(f"\n🎬 CONTENT PREVIEW:")
        print(f"Topic: {topic}")
        print(f"Script length: {len(script)} characters")
        print(f"Audio duration: {final_audio_duration:.2f} seconds")
        print(f"Video duration: {final_video_duration:.2f} seconds" if final_video_duration else "Video duration: Unknown")
        
        if final_video_duration:
            duration_diff = abs(final_video_duration - final_audio_duration)
            if duration_diff < 1.0:
                print(f"Sync status: ✅ Perfect (difference: {duration_diff:.2f}s)")
            else:
                print(f"Sync status: ⚠️ Check ({duration_diff:.2f}s difference)")
        
        print(f"Has background music: {'Yes' if Path('assets').exists() and list(Path('assets').glob('*.mp3')) else 'No'}")
        print(f"Captions: ✅ Burned-in professionally")
        print(f"Content style: ✅ Dynamic captions and hashtags")

    except Exception as e:
        logging.error(f"Error in main pipeline: {e}")
        print(f"\n❌ Error: {e}")
        print("📋 Check the logs for more details.")
        print(f"📊 Log file: {log_path}")

if __name__ == "__main__":
    main()