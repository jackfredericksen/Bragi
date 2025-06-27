# Bragi, Norse god of poetry, eloquence, and music

Fully automated pipeline for generating and publishing TikTok and YouTube Shorts featuring esoteric philosophical content inspired by Alan Watts and Terence McKenna.

## 🎯 Features

- **AI Script Generation**: Claude creates mystical philosophical monologues  
- **Natural Voiceover**: ElevenLabs dreamy male voice synthesis
- **Dynamic Visuals**: Auto-downloads trippy/psychedelic background videos
- **Professional Production**: Burned-in captions with custom styling
- **Background Music**: Ambient tracks mixed under narration
- **Auto-Publishing**: Direct upload to TikTok and YouTube Shorts
- **Self-Expanding**: AI continuously adds new topics to content bank
- **Fully Automated**: Schedule 1-2 videos per platform daily

## 🚀 Quick Start

### 1. Setup
```bash
# Clone the repository
git clone [your-repo-url]
cd [repo-name]

# Run setup script
python setup.py
```

### 2. Configure API Keys
Edit `.env` file with your credentials:
```env
ANTHROPIC_API_KEY=your_claude_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id
PEXELS_API_KEY=your_pexels_key
```

### 3. Add Background Music
Place ambient MP3 files in `assets/` folder:
- `ambient1.mp3`
- `ambient2.mp3`
- (Add more as desired)

### 4. Test Run
```bash
python main.py
```

### 5. Schedule Automation
Use Windows Task Scheduler with `run_bot.bat` to run daily.

## 📁 Project Structure

```
├── main.py                    # Core automation pipeline
├── generate_captions.py       # Whisper transcription & caption burning  
├── upload_tiktok.py          # TikTok automation
├── upload_youtube.py         # YouTube automation
├── expand_topics.py          # AI topic expansion
├── setup.py                  # Installation script
├── run_bot.bat              # Windows scheduler launcher
├── topics.txt               # Content knowledge bank
├── assets/                  # Background music files
└── esoteric_content_pipeline/
    ├── scripts/             # Generated scripts
    ├── audio/              # Voice files  
    ├── video_clips/        # Background videos
    ├── final_videos/       # Completed content
    └── logs/              # System logs
```

## 🛠 Requirements

### APIs Required
- **Anthropic Claude**: Script generation
- **ElevenLabs**: Voice synthesis  
- **Pexels**: Stock video footage (free tier available)

### System Requirements
- Python 3.7+
- FFmpeg installed and in PATH
- Google Chrome browser
- Windows (for Task Scheduler automation)

### Python Dependencies
```
anthropic
elevenlabs
requests
python-dotenv
selenium
pydub
openai-whisper
undetected-chromedriver
```

## 🎬 How It Works

1. **Topic Selection**: Randomly picks from `topics.txt`
2. **Script Generation**: Claude creates 60-90 second philosophical monologue
3. **Voice Synthesis**: ElevenLabs generates dreamy male narration
4. **Background Music**: Mixes ambient track under voice (20dB lower)
5. **Visual Selection**: Downloads trippy video from Pexels API
6. **Video Assembly**: FFmpeg merges audio and video
7. **Caption Generation**: Whisper transcribes and burns styled subtitles
8. **Auto-Upload**: Selenium publishes to TikTok and YouTube Shorts

## 📈 Content Strategy

### Topics Include:
- The illusion of time
- Ego death and dissolution of self  
- Fractal nature of universe
- Consciousness exploration
- Psychedelic experiences
- Non-duality concepts
- Dreams and reality

### Output Format:
- **TikTok**: 30-60 seconds, portrait orientation
- **YouTube Shorts**: 60-90 seconds, optimized for mobile
- **Captions**: White text, black outline, centered
- **Hashtags**: #esoteric #alanwatts #consciousness #psychedelic

## 🔄 Automation

### Scheduling Options:
- **Windows Task Scheduler**: Use `run_bot.bat`
- **Frequency**: 1-2 videos per platform daily
- **Timing**: Every 12 hours recommended

### Monitoring:
- Detailed logs saved to `esoteric_content_pipeline/logs/`
- Error handling with retry logic
- Session persistence for platform logins

## 🎵 Background Music

Add royalty-free ambient tracks to `assets/` folder:

**Recommended Sources:**
- YouTube Audio Library
- Freesound.org  
- Pixabay Music
- Zapsplat

**Track Requirements:**
- Format: MP3
- Length: 30+ seconds (loops automatically)
- Style: Ambient, ethereal, cosmic

## 🔧 Advanced Usage

### Expand Topic Bank:
```bash
python expand_topics.py
```

### Custom Voice Configuration:
1. Visit ElevenLabs voice library
2. Copy desired voice ID  
3. Update `ELEVENLABS_VOICE_ID` in `.env`

### Platform Login:
- First run will prompt for manual login
- Sessions saved as cookies for future runs
- Supports headless operation after initial setup

## 🚀 Scaling & Extensions

### Potential Enhancements:
- Instagram Reels support
- Multi-account management  
- Analytics dashboard
- Custom background video generation
- Voice cloning for variety
- Sound-reactive visual effects

### Multi-Platform Support:
The modular architecture makes it easy to add new platforms by creating additional upload modules following the existing pattern.

## 🐛 Troubleshooting

### Common Issues:

**FFmpeg not found:**
- Install from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add to system PATH

**Chrome/Selenium errors:**
- Update Chrome browser
- Check ChromeDriver compatibility

**API rate limits:**
- Add delays between requests
- Implement exponential backoff

**Upload failures:**
- Check platform login sessions
- Verify video format compliance
- Review error logs

## 📜 License

This project is for educational and personal use. Ensure compliance with platform terms of service and content policies.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional platform integrations
- Enhanced error handling
- Performance optimizations
- UI/dashboard development

---

**Note**: This system is designed for legitimate content creation. Always follow platform guidelines and respect intellectual property rights.