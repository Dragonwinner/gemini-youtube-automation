# 24/7 Automated News Production Platform

A fully automated news production and broadcasting platform powered by AI. This system:
- 🤖 Fetches real-time news from multiple sources automatically
- 📰 Generates professional news scripts using Gemini AI
- 🎥 Produces news videos with audio narration and visuals
- 📺 Uploads to YouTube automatically (long-form + shorts)
- 🔴 Supports 24/7 live streaming capability
- ⏰ Runs continuously every hour via GitHub Actions
- 🌍 Covers multiple news categories (tech, business, science, health, etc.)
- 🚀 **Requires ZERO human intervention** - fully autonomous operation

## 🎯 Key Features

### Automated News Production
- Hourly news bulletins produced automatically
- Multiple news categories rotated for diverse coverage
- Professional AI-generated scripts and narration
- Automatic thumbnail generation
- Both long-form videos and YouTube Shorts

### 24/7 Live Streaming
- YouTube Live stream setup and management
- Continuous broadcasting capability
- RTMP streaming support

### Original Features (Educational Content)
The platform also maintains the original educational content automation:
- Daily AI lesson generation using Gemini
- Automated educational video production
- Structured curriculum management


## Project Structure
```text
gemini-youtube-automation/
├── .github/
│   └── workflows/
│       ├── main.yml              # Original educational content workflow (daily)
│       └── news_automation.yml   # NEW: 24/7 news automation (hourly)
├── src/                          # Source directory for Python modules
│   ├── __init__.py               # Initializes the 'src' package
│   ├── generator.py              # Content and video generation (original)
│   ├── uploader.py               # YouTube upload functionality
│   ├── news_fetcher.py           # NEW: Fetches news from APIs
│   ├── news_generator.py         # NEW: AI-powered news script generation
│   └── live_streamer.py          # NEW: YouTube Live streaming support
├── assets/                       # Media assets (fonts, music, images)
├── .gitignore                    # Files and directories to ignore
├── content_plan.json             # Educational content tracking (original)
├── news_config.json              # NEW: News automation configuration
├── main.py                       # Original entry point (educational content)
├── news_main.py                  # NEW: Main entry point for news automation
└── requirements.txt              # Python dependencies
```

## Setup Instructions

### 1. Clone the repository:
```bash
git clone https://github.com/Dragonwinner/gemini-youtube-automation.git
cd gemini-youtube-automation
```

### 2. Install dependencies:
Make sure you have Python 3.11+ installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys:

You'll need the following API keys:

#### Required for News Automation:
- **Google Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **NewsAPI Key**: Get free key from [NewsAPI.org](https://newsapi.org/) (100 requests/day free)
- **Pexels API Key**: Get from [Pexels API](https://www.pexels.com/api/) for background images
- **YouTube API Credentials**: Follow the [YouTube API documentation](https://developers.google.com/youtube/v3)

#### Set up GitHub Secrets (for automation):
Add these secrets to your GitHub repository:
- `GOOGLE_API_KEY` - Your Gemini API key
- `NEWSAPI_KEY` - Your NewsAPI.org key  
- `PEXELS_API_KEY` - Your Pexels API key
- `CLIENT_SECRET_B64` - Base64 encoded YouTube client_secrets.json
- `CREDENTIALS_B64` - Base64 encoded YouTube credentials.json

### 4. Local Environment Variables:
Create a `.env` file or export these variables:
```bash
export GOOGLE_API_KEY="your-gemini-api-key"
export NEWSAPI_KEY="your-newsapi-key"
export PEXELS_API_KEY="your-pexels-api-key"
```

## Usage

### 🆕 24/7 News Automation

#### Automated Mode (GitHub Actions):
The system runs **automatically every hour** via GitHub Actions workflow. No manual intervention needed!

#### Manual Testing:

**Run single news cycle:**
```bash
python news_main.py
```

**Run continuous mode (every 60 minutes):**
```bash
python news_main.py continuous
```

**Setup YouTube Live Stream:**
```bash
python news_main.py live
```
This creates a 24/7 live stream endpoint. Use OBS or FFmpeg to push video to the RTMP URL provided.

### 📚 Original Educational Content

To run the original educational content automation:
```bash
python main.py
```

This will generate and upload an AI educational lesson.

## 🔄 How 24/7 Automation Works

1. **Hourly Execution**: GitHub Actions runs `news_main.py` every hour
2. **News Fetching**: System fetches latest news from NewsAPI
3. **AI Script Generation**: Gemini AI creates professional news scripts
4. **Video Production**: Automated video creation with TTS narration
5. **YouTube Upload**: Videos automatically uploaded with metadata
6. **Category Rotation**: News categories rotate for diverse coverage
7. **Error Recovery**: Built-in fallback mechanisms ensure 24/7 operation
8. **Zero Human Input**: Completely autonomous operation

## 📊 News Categories Covered

The system rotates through these categories hourly:
- 💻 Technology
- 💼 Business
- 🔬 Science
- 🏥 Health
- 🎬 Entertainment
- ⚽ Sports
- 🌍 General News

## 🎥 Live Streaming (24/7)

The platform supports YouTube Live streaming for continuous 24/7 news broadcast:

### Setup Process:
1. Run: `python news_main.py live`
2. System creates YouTube Live broadcast and stream
3. You receive RTMP URL and Stream Key
4. Use OBS Studio or FFmpeg to push video to the stream

### Example FFmpeg command:
```bash
ffmpeg -re -loop 1 -i news_background.jpg \
  -i news_audio.mp3 \
  -c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k \
  -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 \
  -f flv rtmp://[RTMP_URL]/[STREAM_KEY]
```

### Continuous Operation:
- Stream runs 24/7 once started
- News segments can be pushed continuously
- Automated script generation supports live content

## 🛡️ Reliability Features

- **Fallback News Generation**: Works even if NewsAPI is unavailable
- **Error Recovery**: Automatic retry mechanisms
- **Rate Limit Handling**: Respects API rate limits
- **Continuous Logging**: Tracks all operations
- **Config Persistence**: Maintains state across runs
## 🚀 Deployment

### GitHub Actions (Recommended)

The system is designed to run automatically on GitHub Actions:

1. **Fork/Clone this repository**
2. **Add GitHub Secrets** (Settings → Secrets and variables → Actions):
   - `GOOGLE_API_KEY`
   - `NEWSAPI_KEY`
   - `PEXELS_API_KEY`
   - `CLIENT_SECRET_B64`
   - `CREDENTIALS_B64`

3. **Enable GitHub Actions** (Actions tab → Enable workflows)
4. **Workflows will run automatically**:
   - News: Every hour (24/7)
   - Educational: Daily at 7:00 AM UTC

### Self-Hosted / VPS Deployment

For more control, run on your own server:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="..."
export NEWSAPI_KEY="..."
export PEXELS_API_KEY="..."

# Run continuously
python news_main.py continuous
```

Use a process manager like `systemd`, `supervisor`, or `pm2` for production.

## 📊 Daily Production Infographic

Here's a visual summary of the bot's daily performance and workflow:

![Gemini YouTube Automation Daily Report Infographic](images/infographic.png)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or features.


## 📈 Monitoring

Track your automation with:
- **news_config.json**: Tracks bulletins produced, categories covered, timestamps
- **GitHub Actions logs**: View production runs and status
- **YouTube Analytics**: Monitor video performance

## 🔧 Troubleshooting

**News not fetching?**
- Check NEWSAPI_KEY is valid (100 req/day limit on free tier)
- System uses fallback news generation if API unavailable

**Videos not uploading?**
- Verify YouTube API credentials are properly configured
- Check YouTube quota limits

**GitHub Actions failing?**
- Check all secrets are properly configured
- Review action logs for specific error messages

## License

This project is licensed under the MIT License. See the LICENSE file for details.

