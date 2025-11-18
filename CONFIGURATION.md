# Configuration Examples and Templates

## Environment Variables Template

Create a `.env` file with these variables:

```bash
# ============================================
# CORE APIS (Required)
# ============================================

# Google Gemini AI for content generation
GOOGLE_API_KEY=your_gemini_api_key_here

# NewsAPI for news fetching (100 requests/day free)
NEWSAPI_KEY=your_newsapi_key_here

# Pexels for background images (optional but recommended)
PEXELS_API_KEY=your_pexels_api_key_here

# ============================================
# TEXT-TO-SPEECH CONFIGURATION
# ============================================

# TTS Provider: gtts (free), elevenlabs, google_cloud, azure
TTS_PROVIDER=gtts

# ElevenLabs (Premium, natural voices)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Default voice

# Google Cloud TTS (Enterprise)
GOOGLE_CLOUD_TTS_KEY=/path/to/google-credentials.json

# Azure Cognitive Services (Professional)
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=eastus

# ============================================
# VIDEO GENERATION CONFIGURATION
# ============================================

# Video Mode: standard, avatar, hybrid
VIDEO_MODE=standard

# D-ID AI Avatar
DID_API_KEY=your_did_api_key

# Synthesia AI Avatar
SYNTHESIA_API_KEY=your_synthesia_api_key

# ============================================
# EXTERNAL DATA SOURCES
# ============================================

# OpenWeatherMap for weather updates
OPENWEATHER_API_KEY=your_openweather_key

# Alpha Vantage for stock market data
ALPHA_VANTAGE_API_KEY=your_alphavantage_key

# Twitter API for trending topics (optional)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# ============================================
# SYSTEM CONFIGURATION
# ============================================

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Output directory
OUTPUT_DIR=output

# Database file
DB_FILE=news_database.json
```

## Example Configurations

### Minimal Configuration (Free Tier)

```bash
# Basic setup with free services
GOOGLE_API_KEY=your_gemini_key
NEWSAPI_KEY=your_newsapi_key
TTS_PROVIDER=gtts
VIDEO_MODE=standard
```

### Premium Configuration (Best Quality)

```bash
# Premium setup with paid services
GOOGLE_API_KEY=your_gemini_key
NEWSAPI_KEY=your_newsapi_key
PEXELS_API_KEY=your_pexels_key

# Premium TTS
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=your_voice

# AI Avatar
VIDEO_MODE=avatar
DID_API_KEY=your_did_key

# External data
OPENWEATHER_API_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key
```

### Enterprise Configuration (Full Features)

```bash
# Enterprise setup with all features
GOOGLE_API_KEY=your_gemini_key
NEWSAPI_KEY=your_newsapi_key
PEXELS_API_KEY=your_pexels_key

# Enterprise TTS
TTS_PROVIDER=google_cloud
GOOGLE_CLOUD_TTS_KEY=/path/to/credentials.json

# Professional Avatar
VIDEO_MODE=avatar
SYNTHESIA_API_KEY=your_synthesia_key

# All external data sources
OPENWEATHER_API_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key
TWITTER_BEARER_TOKEN=your_token

# Enhanced logging
LOG_LEVEL=DEBUG
```

## GitHub Actions Configuration

### Repository Secrets

Add these in: Settings → Secrets and variables → Actions

```
GOOGLE_API_KEY
NEWSAPI_KEY
PEXELS_API_KEY
CLIENT_SECRET_B64
CREDENTIALS_B64
```

### Encoding Credentials

```bash
# Encode client_secrets.json
base64 -w 0 client_secrets.json

# Encode credentials.json
base64 -w 0 credentials.json

# Copy output and add as GitHub secret
```

## News Configuration (news_config.json)

Auto-generated, but here's the structure:

```json
{
  "last_run": "2024-01-15T10:30:00",
  "total_bulletins": 150,
  "current_category_index": 3,
  "live_stream_active": false,
  "live_stream_id": null,
  "categories_covered": {
    "technology": 25,
    "business": 22,
    "science": 20,
    "health": 18,
    "entertainment": 21,
    "sports": 23,
    "general": 21
  },
  "created_at": "2024-01-01T00:00:00"
}
```

## Content Queue Configuration (content_queue.json)

```json
{
  "items": [
    {
      "id": 1,
      "article": { "title": "...", "description": "..." },
      "priority": 2,
      "priority_name": "HIGH",
      "scheduled_time": null,
      "added_at": "2024-01-15T10:00:00",
      "status": "pending",
      "aired_at": null
    }
  ],
  "breaking_news": [
    {
      "id": 1,
      "article": { "title": "...", "description": "..." },
      "added_at": "2024-01-15T10:30:00",
      "interrupt": true,
      "aired": false
    }
  ],
  "metadata": {
    "created_at": "2024-01-01T00:00:00",
    "last_updated": "2024-01-15T10:30:00"
  }
}
```

## Systemd Service Configuration

Create `/etc/systemd/system/news-automation.service`:

```ini
[Unit]
Description=24/7 News Automation Service
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/gemini-youtube-automation
Environment="PATH=/path/to/venv/bin"
EnvironmentFile=/path/to/.env
ExecStart=/path/to/venv/bin/python news_main_enhanced.py continuous 60
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable news-automation
sudo systemctl start news-automation
sudo systemctl status news-automation
```

## Docker Configuration (Optional)

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["python", "news_main_enhanced.py", "continuous", "60"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  news-automation:
    build: .
    container_name: news-automation
    restart: always
    env_file:
      - .env
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
      - ./credentials.json:/app/credentials.json
      - ./client_secrets.json:/app/client_secrets.json
    environment:
      - TTS_PROVIDER=gtts
      - VIDEO_MODE=standard
```

Run with:
```bash
docker-compose up -d
```

## Nginx Configuration (For Live Streaming)

If hosting stream manager:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /stream {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Monitoring Configuration

### Prometheus Metrics (Optional)

Add metrics endpoint:
```python
from prometheus_client import Counter, Histogram, Gauge

bulletins_produced = Counter('bulletins_produced_total', 'Total bulletins produced')
video_upload_duration = Histogram('video_upload_duration_seconds', 'Video upload duration')
```

### Grafana Dashboard (Optional)

Import dashboard JSON for visualization.

## Backup Configuration

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/news-automation"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
cp news_database.json "$BACKUP_DIR/news_database_$DATE.json"
cp content_queue.json "$BACKUP_DIR/content_queue_$DATE.json"
cp news_config.json "$BACKUP_DIR/news_config_$DATE.json"

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "*.json" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Schedule with cron:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

## Rate Limiting Configuration

Adjust API call frequencies:

```python
# In news_main_enhanced.py

# Slower for free tiers
FETCH_INTERVAL = 90  # minutes

# Faster for paid tiers
FETCH_INTERVAL = 30  # minutes
```

## Troubleshooting Configuration

### Debug Mode

Enable verbose output:
```bash
export LOG_LEVEL=DEBUG
python news_main_enhanced.py
```

### Test Mode

Isolated testing:
```bash
# Test without uploading
export DRY_RUN=true
python news_main_enhanced.py test
```
