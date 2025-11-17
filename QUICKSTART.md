# Quick Start Guide - 24/7 Automated News Platform

## 🚀 Getting Started in 5 Minutes

### Step 1: Get Your API Keys (Free)

1. **Google Gemini API** (Required for AI content)
   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

2. **NewsAPI** (Optional but recommended)
   - Visit: https://newsapi.org/register
   - Free tier: 100 requests/day (enough for hourly updates)
   - Copy your API key

3. **Pexels API** (Optional - for background images)
   - Visit: https://www.pexels.com/api/
   - Free tier: 200 requests/hour
   - Copy your API key

4. **YouTube API Credentials**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download `client_secrets.json`

### Step 2: Run Locally (First Time)

```bash
# Clone the repository
git clone https://github.com/Dragonwinner/gemini-youtube-automation.git
cd gemini-youtube-automation

# Install dependencies
pip install -r requirements.txt


setx GOOGLE_API_KEY "your-gemini-key"
setx NEWSAPI_KEY "your-newsapi-key"
setx PEXELS_API_KEY "your-pexels-key"


# Set environment variables
export GOOGLE_API_KEY="your-gemini-api-key"
export NEWSAPI_KEY="your-newsapi-key"
export PEXELS_API_KEY="your-pexels-key"

# Place your client_secrets.json in the root directory

# Run once to authenticate with YouTube (opens browser)
python news_main.py
```

This will:
- Open your browser for YouTube authentication
- Generate `credentials.json` for future runs
- Fetch news, generate content, create video
- Upload to YouTube automatically

### Step 3: Enable 24/7 Automation (GitHub Actions)

1. **Fork/Clone to your GitHub account**

2. **Add GitHub Secrets**
   - Go to: Settings → Secrets and variables → Actions
   - Add these secrets:
     - `GOOGLE_API_KEY` - Your Gemini API key
     - `NEWSAPI_KEY` - Your NewsAPI key
     - `PEXELS_API_KEY` - Your Pexels key
     - `CLIENT_SECRET_B64` - Base64 encoded client_secrets.json
     - `CREDENTIALS_B64` - Base64 encoded credentials.json

3. **Encode credentials for GitHub**
   ```bash
   # On Linux/Mac
   cat client_secrets.json | base64 -w 0 > client_secret_b64.txt
   cat credentials.json | base64 -w 0 > credentials_b64.txt
   
   # On Windows PowerShell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("client_secrets.json")) > client_secret_b64.txt
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json")) > credentials_b64.txt
   ```

4. **Enable GitHub Actions**
   - Go to Actions tab
   - Enable workflows
   - The system will run automatically every hour!

## 📺 Usage Modes

### Automated Mode (Default)
Runs every hour via GitHub Actions - no action needed!

### Manual Single Run
```bash
python news_main.py
```

### Continuous Mode (for testing)
```bash
python news_main.py continuous
```
Runs every 60 minutes in a loop.

### Live Streaming Setup
```bash
python news_main.py live
```
Creates a YouTube Live stream. Use OBS/FFmpeg to push video.

## 🔧 Customization

### Change News Categories
Edit `NEWS_CATEGORIES` in `news_main.py`:
```python
NEWS_CATEGORIES = [
    "technology",
    "business",
    "your-custom-category"
]
```

### Change Anchor Name
Edit in `news_main.py`:
```python
ANCHOR_NAME = "Your Anchor Name"
```

### Change Update Frequency
Edit `.github/workflows/news_automation.yml`:
```yaml
schedule:
  - cron: '0 * * * *'  # Every hour
  # - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 */2 * * *'  # Every 2 hours
```

## 📊 Monitoring

Check your automation status:
- `news_config.json` - Production statistics
- GitHub Actions logs - Execution logs
- YouTube Studio - Video performance

## 🆘 Troubleshooting

**Problem: Videos not uploading**
- Verify YouTube API credentials are correct
- Check YouTube API quota (default: 10,000 units/day)
- Ensure `credentials.json` has valid refresh token

**Problem: No news fetched**
- Check NewsAPI key is valid
- Free tier limit: 100 requests/day
- System uses fallback if API unavailable

**Problem: GitHub Actions failing**
- Verify all secrets are set correctly
- Check action logs for specific errors
- Ensure base64 encoding is correct (no line breaks)

**Problem: Out of API quota**
- NewsAPI free: 100/day (sufficient for hourly)
- Gemini free: Generous limits
- Consider upgrading for higher volume

## 🎯 What Happens Automatically

Every hour, the system:
1. ✅ Fetches latest news from NewsAPI
2. ✅ Generates professional scripts with Gemini AI
3. ✅ Creates video with TTS narration
4. ✅ Generates thumbnail
5. ✅ Uploads to YouTube (long video)
6. ✅ Creates and uploads YouTube Short
7. ✅ Updates tracking configuration
8. ✅ Rotates to next news category

## 🎬 Example Output

Each cycle produces:
- **Long-form video** (2-5 minutes): Full news bulletin
- **YouTube Short** (60 seconds): Highlight clip
- **Professional thumbnails**: Auto-generated
- **SEO-optimized metadata**: Title, description, tags, hashtags

## 📈 Expected Performance

With free API tiers:
- **News bulletins per day**: 24 (hourly)
- **Videos uploaded per day**: 48 (24 long + 24 shorts)
- **Categories covered**: All 7 categories rotated
- **Human intervention required**: ZERO ✨

## 🌟 Pro Tips

1. **Test locally first** before enabling GitHub Actions
2. **Monitor YouTube quota** in first few days
3. **Customize news categories** for your niche
4. **Review first few videos** to ensure quality
5. **Enable YouTube monetization** once eligible
6. **Add custom branding** by updating assets/
7. **Scale up** with paid API tiers for higher frequency

## 🔒 Security Notes

- Never commit `client_secrets.json` or `credentials.json` to git
- Use GitHub Secrets for sensitive data
- Rotate API keys periodically
- Use base64 encoding for GitHub Actions secrets

## 📞 Support

- Check documentation: README.md
- Review logs: GitHub Actions tab
- Test locally: `python news_main.py`
- Validate modules: Run integration tests

---

**Ready to launch your 24/7 news channel? Let's go! 🚀**
