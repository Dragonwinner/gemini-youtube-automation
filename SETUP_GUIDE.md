# Complete Setup Guide for 24/7 YouTube News Anchor System

## Overview

This system provides a fully automated 24/7 YouTube news anchor platform with AI-generated content, live streaming, and comprehensive analytics.

## System Requirements

### Software
- Python 3.11 or higher
- FFmpeg (for video encoding and streaming)
- ImageMagick (for graphics processing)
- Git

### Hardware (Recommended)
- CPU: 4+ cores
- RAM: 8GB minimum, 16GB recommended
- Storage: 50GB+ free space
- Network: Stable broadband connection

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/Dragonwinner/gemini-youtube-automation.git
cd gemini-youtube-automation
```

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip ffmpeg imagemagick
sudo apt-get install -y libjpeg-dev zlib1g-dev
```

**macOS:**
```bash
brew install python ffmpeg imagemagick
```

**Windows:**
- Install Python from python.org
- Install FFmpeg from ffmpeg.org
- Install ImageMagick from imagemagick.org

### 3. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure API Keys

#### Required APIs

**Google Gemini API** (Required)
- Get from: https://makersuite.google.com/app/apikey
- Used for: AI content generation
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
```

**NewsAPI** (Recommended)
- Get from: https://newsapi.org/
- Free tier: 100 requests/day
```bash
export NEWSAPI_KEY="your_newsapi_key"
```

**YouTube API** (Required for uploading)
- Get from: https://console.cloud.google.com/
- Download client_secrets.json
- Place in project root
```bash
# First run will authenticate and create credentials.json
python news_main.py
```

**Pexels API** (Optional)
- Get from: https://www.pexels.com/api/
- Used for: Background images
```bash
export PEXELS_API_KEY="your_pexels_key"
```

#### Optional Premium APIs

**ElevenLabs TTS** (Premium voice)
```bash
export TTS_PROVIDER="elevenlabs"
export ELEVENLABS_API_KEY="your_elevenlabs_key"
export ELEVENLABS_VOICE_ID="your_voice_id"
```

**Google Cloud TTS** (Enterprise)
```bash
export TTS_PROVIDER="google_cloud"
export GOOGLE_CLOUD_TTS_KEY="your_credentials.json"
```

**Azure Speech** (Voice modulation)
```bash
export TTS_PROVIDER="azure"
export AZURE_SPEECH_KEY="your_azure_key"
export AZURE_SPEECH_REGION="eastus"
```

**D-ID Avatar** (AI presenter)
```bash
export VIDEO_MODE="avatar"
export DID_API_KEY="your_did_key"
```

**Synthesia Avatar** (Professional avatar)
```bash
export VIDEO_MODE="avatar"
export SYNTHESIA_API_KEY="your_synthesia_key"
```

**Weather Updates**
```bash
export OPENWEATHER_API_KEY="your_openweather_key"
```

**Stock Market Data**
```bash
export ALPHA_VANTAGE_API_KEY="your_alphavantage_key"
```

**Social Media Trends**
```bash
export TWITTER_BEARER_TOKEN="your_twitter_token"
```

### 6. ImageMagick Policy Configuration

For video generation, ImageMagick needs policy adjustment:

```bash
# Find policy file
POLICY_FILE=$(find /etc -name "policy.xml" 2>/dev/null | grep -i "ImageMagick" | head -n 1)

# Edit policy (requires sudo)
sudo sed -i 's/<policy domain="resource" name="width" value=".*"\/>/<policy domain="resource" name="width" value="16384"\/>/' "$POLICY_FILE"
sudo sed -i 's/<policy domain="resource" name="height" value=".*"\/>/<policy domain="resource" name="height" value="16384"\/>/' "$POLICY_FILE"
```

### 7. Create .env File (Optional)

Create a `.env` file in project root:

```bash
# Core APIs
GOOGLE_API_KEY=your_gemini_key
NEWSAPI_KEY=your_newsapi_key
PEXELS_API_KEY=your_pexels_key

# TTS Configuration
TTS_PROVIDER=gtts  # or elevenlabs, google_cloud, azure
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=default

# Video Configuration
VIDEO_MODE=standard  # or avatar, hybrid
DID_API_KEY=your_key
SYNTHESIA_API_KEY=your_key

# External Data
OPENWEATHER_API_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key
TWITTER_BEARER_TOKEN=your_token
```

## Usage

### Basic Operations

**1. Single News Bulletin**
```bash
python news_main_enhanced.py
```

**2. Continuous 24/7 Mode**
```bash
# Run every 60 minutes
python news_main_enhanced.py continuous 60

# Run every 30 minutes
python news_main_enhanced.py continuous 30
```

**3. Setup Live Stream**
```bash
python news_main_enhanced.py live
# Follow instructions to start streaming with OBS or FFmpeg
```

**4. Generate Analytics Report**
```bash
# Last 7 days
python news_main_enhanced.py analytics 7

# Last 30 days
python news_main_enhanced.py analytics 30
```

**5. Test Mode**
```bash
python news_main_enhanced.py test
```

### Original Educational Content

The original educational content automation is still available:

```bash
python main.py
```

## Configuration Options

### TTS Provider Selection

**gTTS (Free)**
```bash
export TTS_PROVIDER=gtts
```

**ElevenLabs (Premium)**
```bash
export TTS_PROVIDER=elevenlabs
export ELEVENLABS_API_KEY=your_key
```

**Google Cloud (Enterprise)**
```bash
export TTS_PROVIDER=google_cloud
export GOOGLE_CLOUD_TTS_KEY=path/to/credentials.json
```

**Azure Speech (Professional)**
```bash
export TTS_PROVIDER=azure
export AZURE_SPEECH_KEY=your_key
export AZURE_SPEECH_REGION=your_region
```

### Video Mode Selection

**Standard Mode (No avatar)**
```bash
export VIDEO_MODE=standard
```

**Avatar Mode (AI presenter)**
```bash
export VIDEO_MODE=avatar
export DID_API_KEY=your_did_key
# or
export SYNTHESIA_API_KEY=your_synthesia_key
```

**Hybrid Mode (Both)**
```bash
export VIDEO_MODE=hybrid
```

## GitHub Actions Setup (Automated 24/7)

### 1. Fork Repository

Fork the repository to your GitHub account.

### 2. Configure Secrets

Go to: Settings → Secrets and variables → Actions

Add these secrets:
- `GOOGLE_API_KEY` - Your Gemini API key
- `NEWSAPI_KEY` - Your NewsAPI key
- `PEXELS_API_KEY` - Your Pexels API key
- `CLIENT_SECRET_B64` - Base64 encoded client_secrets.json
- `CREDENTIALS_B64` - Base64 encoded credentials.json

**Encoding credentials:**
```bash
cat client_secrets.json | base64 -w 0
cat credentials.json | base64 -w 0
```

### 3. Enable Workflows

Go to: Actions → Enable workflows

The news automation will run every hour automatically.

## Monitoring and Maintenance

### Check Logs

```bash
# Main application log
tail -f logs/news_automation.log

# Error log
tail -f logs/errors.log

# Metrics log
tail -f logs/metrics.log
```

### View Analytics

```bash
python news_main_enhanced.py analytics 7
cat analytics_report_*.json
```

### Database Management

```bash
# View database
cat news_database.json | python -m json.tool

# View content queue
cat content_queue.json | python -m json.tool
```

### Cleanup Old Data

The system automatically cleans up:
- Old articles (7 days)
- Old queue items (7 days)
- Old logs (30 days)

Manual cleanup:
```python
from src.news_database import NewsDatabase
from src.content_queue import ContentQueue
from src.logging_system import NewsLogger

db = NewsDatabase()
db.cleanup_old_articles(days=7)

queue = ContentQueue()
queue.cleanup_old_content(days=7)

logger = NewsLogger()
logger.cleanup_old_logs(days=30)
```

## Troubleshooting

### Common Issues

**1. "gTTS synthesis failed"**
- Check internet connection
- Verify no firewall blocking Google TTS
- Try alternative TTS provider

**2. "NewsAPI rate limit"**
- Free tier: 100 requests/day
- System will use RSS feeds as fallback
- Consider upgrading NewsAPI plan

**3. "ImageMagick policy error"**
- Follow ImageMagick policy configuration above
- Restart after policy changes

**4. "YouTube quota exceeded"**
- Default: 10,000 units/day
- Each upload: ~1,600 units
- Monitor at: console.cloud.google.com

**5. "FFmpeg not found"**
- Install FFmpeg: `sudo apt-get install ffmpeg`
- Verify: `ffmpeg -version`

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```python
# Test news fetching
from src.news_fetcher import NewsFetcher
fetcher = NewsFetcher()
articles = fetcher.fetch_breaking_news('technology', max_articles=5)
print(f"Fetched {len(articles)} articles")

# Test TTS
from src.tts_provider import TTSProvider
tts = TTSProvider('gtts')
audio = tts.synthesize("Test message", "test.mp3")
print(f"Audio saved: {audio}")

# Test video generation
from src.video_generator import VideoGenerator
video_gen = VideoGenerator('standard')
background = video_gen.create_news_background('technology')
background.save('test_background.png')
```

## Performance Optimization

### Reduce Processing Time
- Use faster TTS provider (ElevenLabs)
- Lower video resolution
- Reduce video length
- Use GPU acceleration for FFmpeg

### Reduce Bandwidth
- Lower video bitrate
- Compress thumbnails
- Use CDN for assets

### Reduce API Costs
- Cache news articles
- Increase cycle interval
- Use free API tiers first

## Advanced Configuration

### Custom News Categories

Edit in code:
```python
NEWS_CATEGORIES = [
    "technology",
    "business",
    "science",
    "health",
    "entertainment",
    "sports",
    "general",
    # Add custom categories
]
```

### Custom RSS Feeds

Edit `src/news_fetcher.py`:
```python
self.rss_feeds = {
    "technology": [
        "https://your-feed-url.com/rss",
        # Add more feeds
    ],
}
```

### Custom Bulletin Types

Edit `news_main_enhanced.py`:
```python
if current_hour == 0:
    bulletin_type = "midnight"
elif current_hour == 12:
    bulletin_type = "noon"
# Add custom logic
```

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Rotate credentials** - Periodically update API keys
3. **Monitor usage** - Track API quotas
4. **Secure credentials** - Protect credentials.json
5. **Use HTTPS** - All API calls over HTTPS
6. **Regular updates** - Keep dependencies updated

## Support and Resources

- **Documentation**: README.md, QUICKSTART.md
- **Issues**: GitHub Issues
- **Logs**: logs/ directory
- **Analytics**: Generate reports regularly
- **Testing**: Run test_system.py

## Scaling

### Single Server
- Run on VPS or dedicated server
- Use process manager (systemd, supervisor)
- Monitor with cron jobs

### Multiple Servers
- Separate news fetching from video generation
- Use message queue (RabbitMQ, Redis)
- Shared database (PostgreSQL)
- Load balancer for distribution

### Cloud Deployment
- AWS, Google Cloud, or Azure
- Container orchestration (Kubernetes)
- Auto-scaling based on load
- CDN for content delivery

## License

MIT License - See LICENSE file for details.
