# FILE: news_main.py
# Main entry point for 24/7 automated news production platform

import os
import json
import datetime
import time
import traceback
from pathlib import Path
from src.news_fetcher import NewsFetcher
from src.news_generator import NewsContentGenerator
from src.generator import (
    text_to_speech,
    generate_visuals,
    create_video
)
from src.uploader import upload_to_youtube
from src.live_streamer import LiveStreamer

# Configuration
OUTPUT_DIR = Path("output")
NEWS_CONFIG_FILE = Path("news_config.json")
ANCHOR_NAME = "AI News Anchor"

# News categories for 24/7 rotation
NEWS_CATEGORIES = [
    "technology",
    "business", 
    "science",
    "health",
    "entertainment",
    "sports",
    "general"
]


def get_or_create_news_config():
    """Gets or creates news configuration for tracking."""
    if NEWS_CONFIG_FILE.exists():
        try:
            with open(NEWS_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
    
    # Default configuration
    config = {
        "last_run": None,
        "total_bulletins": 0,
        "current_category_index": 0,
        "live_stream_active": False,
        "live_stream_id": None,
        "categories_covered": {},
        "created_at": datetime.datetime.now().isoformat()
    }
    
    save_news_config(config)
    return config


def save_news_config(config):
    """Saves news configuration."""
    with open(NEWS_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def produce_news_bulletin(news_articles, bulletin_type="hourly"):
    """
    Produces a complete news bulletin video.
    """
    print(f"\n{'='*60}")
    print(f"📰 PRODUCING {bulletin_type.upper()} NEWS BULLETIN")
    print(f"{'='*60}\n")
    
    unique_id = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{bulletin_type}"
    
    # Generate news content using AI
    news_gen = NewsContentGenerator(anchor_name=ANCHOR_NAME)
    bulletin_content = news_gen.generate_news_bulletin(news_articles, bulletin_type)
    
    # Build complete script
    full_script = f"{bulletin_content['opening']}\n\n"
    full_script += "Here are today's headlines:\n"
    for headline in bulletin_content['headlines'][:5]:
        full_script += f"{headline}\n"
    full_script += "\nNow for the detailed stories.\n\n"
    
    for story in bulletin_content['detailed_stories']:
        full_script += f"{story['content']}\n\n"
    
    full_script += bulletin_content['closing']
    
    print(f"📝 Script length: {len(full_script)} characters")
    
    # Create audio
    print("\n🎤 Generating audio...")
    audio_path = OUTPUT_DIR / f"news_audio_{unique_id}.mp3"
    wav_path = text_to_speech(full_script, audio_path)
    
    # Create visual slide
    print("\n🎨 Creating news visuals...")
    slide_dir = OUTPUT_DIR / f"slides_news_{unique_id}"
    slide_content = {
        "title": f"{bulletin_type.upper()} NEWS UPDATE",
        "content": f"{datetime.datetime.now().strftime('%B %d, %Y - %I:%M %p')}\n\n{ANCHOR_NAME}"
    }
    
    slide_path = generate_visuals(
        output_dir=slide_dir,
        video_type='long',
        slide_content=slide_content,
        slide_number=1,
        total_slides=1
    )
    
    # Create video
    video_path = OUTPUT_DIR / f"news_bulletin_{unique_id}.mp4"
    print(f"\n🎥 Creating news video: {video_path}")
    create_video([slide_path], [wav_path], video_path, 'long')
    
    # Generate thumbnail
    thumbnail_path = generate_visuals(
        output_dir=OUTPUT_DIR,
        video_type='long',
        thumbnail_title=f"🔴 LIVE NEWS - {datetime.datetime.now().strftime('%B %d')}"
    )
    
    # Upload to YouTube
    print("\n📤 Uploading to YouTube...")
    title = f"🔴 {bulletin_type.title()} News Update - {datetime.datetime.now().strftime('%B %d, %Y')}"
    description = f"""Live News Update - {datetime.datetime.now().strftime('%I:%M %p')}

{bulletin_content['opening']}

📰 Today's Headlines:
"""
    for headline in bulletin_content['headlines'][:5]:
        description += f"• {headline}\n"
    
    description += f"\n{bulletin_content['hashtags']}\n\n"
    description += "Subscribe for 24/7 news coverage! 🔔\n\n"
    description += "#LiveNews #Breaking #NewsUpdate #24x7News"
    
    tags = "news,breaking news,live news,updates,current events,24/7 news"
    
    video_id = upload_to_youtube(
        video_path,
        title,
        description,
        tags,
        thumbnail_path
    )
    
    # Produce short-form news clip
    if video_id and bulletin_content.get('short_highlight'):
        print("\n📱 Creating news SHORT...")
        time.sleep(15)  # Brief pause
        
        short_script = bulletin_content['short_highlight']
        short_audio_path = OUTPUT_DIR / f"news_short_audio_{unique_id}.mp3"
        short_wav = text_to_speech(short_script, short_audio_path)
        
        short_slide_dir = OUTPUT_DIR / f"slides_short_{unique_id}"
        short_slide_content = {
            "title": "⚡ BREAKING",
            "content": "News Update"
        }
        
        short_slide = generate_visuals(
            output_dir=short_slide_dir,
            video_type='short',
            slide_content=short_slide_content,
            slide_number=1,
            total_slides=1
        )
        
        short_video_path = OUTPUT_DIR / f"news_short_{unique_id}.mp4"
        create_video([short_slide], [short_wav], short_video_path, 'short')
        
        short_thumb = generate_visuals(
            output_dir=OUTPUT_DIR,
            video_type='short',
            thumbnail_title="⚡ BREAKING NEWS"
        )
        
        short_title = f"⚡ {bulletin_content['short_highlight'][:80]} #Shorts"
        short_desc = f"{short_script}\n\n📺 Full coverage: https://www.youtube.com/watch?v={video_id}\n\n{bulletin_content['hashtags']}"
        
        upload_to_youtube(
            short_video_path,
            short_title,
            short_desc,
            "news,shorts,breaking,update",
            short_thumb
        )
    
    return video_id


def run_news_cycle():
    """
    Runs a complete news production cycle.
    """
    print(f"\n{'#'*60}")
    print(f"# 24/7 AUTOMATED NEWS PLATFORM")
    print(f"# {datetime.datetime.now().strftime('%B %d, %Y - %I:%M:%S %p')}")
    print(f"{'#'*60}\n")
    
    try:
        # Create output directory
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        # Load configuration
        config = get_or_create_news_config()
        
        # Get current category for rotation
        category_index = config.get('current_category_index', 0) % len(NEWS_CATEGORIES)
        current_category = NEWS_CATEGORIES[category_index]
        
        print(f"📡 Fetching news - Category: {current_category.upper()}")
        
        # Fetch news
        news_fetcher = NewsFetcher()
        news_articles = news_fetcher.fetch_breaking_news(
            category=current_category,
            max_articles=5
        )
        
        if not news_articles:
            print("⚠️ No news articles fetched, trying general news...")
            news_articles = news_fetcher.fetch_breaking_news(
                category="general",
                max_articles=5
            )
        
        if news_articles:
            # Determine bulletin type based on time
            current_hour = datetime.datetime.now().hour
            if current_hour % 6 == 0:
                bulletin_type = "major"
            elif current_hour % 3 == 0:
                bulletin_type = "midday"
            else:
                bulletin_type = "hourly"
            
            # Produce bulletin
            video_id = produce_news_bulletin(news_articles, bulletin_type)
            
            if video_id:
                # Update configuration
                config['last_run'] = datetime.datetime.now().isoformat()
                config['total_bulletins'] += 1
                config['current_category_index'] = (category_index + 1) % len(NEWS_CATEGORIES)
                
                if current_category not in config['categories_covered']:
                    config['categories_covered'][current_category] = 0
                config['categories_covered'][current_category] += 1
                
                save_news_config(config)
                
                print(f"\n✅ News cycle completed successfully!")
                print(f"📊 Total bulletins produced: {config['total_bulletins']}")
                print(f"🎯 Next category: {NEWS_CATEGORIES[config['current_category_index']]}")
        else:
            print("❌ Failed to fetch news articles")
    
    except Exception as e:
        print(f"\n❌ ERROR in news cycle: {e}")
        traceback.print_exc()
    
    finally:
        # Cleanup temporary files
        try:
            for file in OUTPUT_DIR.glob("*.wav"):
                file.unlink()
                print(f"🧹 Deleted: {file}")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")


def setup_live_stream():
    """
    Sets up a 24/7 YouTube Live Stream (manual trigger).
    This creates the stream configuration but requires external streaming software.
    """
    print(f"\n{'='*60}")
    print(f"📺 SETTING UP 24/7 LIVE STREAM")
    print(f"{'='*60}\n")
    
    try:
        streamer = LiveStreamer()
        stream_config = streamer.setup_24x7_stream("Automated News 24/7")
        
        if stream_config:
            print("\n" + "="*60)
            print("✅ LIVE STREAM SETUP COMPLETE!")
            print("="*60)
            print(f"\n📺 YouTube Watch URL: {stream_config['youtube_watch_url']}")
            print(f"\n🔴 RTMP Settings for OBS/FFmpeg:")
            print(f"   Server: {stream_config['rtmp_url']}")
            print(f"   Stream Key: {stream_config['stream_key'][:20]}...")
            print("\n⚠️ NOTE: Use streaming software (OBS/FFmpeg) to push video to this stream.")
            print("="*60)
            
            # Save stream config
            config = get_or_create_news_config()
            config['live_stream_active'] = True
            config['live_stream_id'] = stream_config['broadcast_id']
            config['live_stream_url'] = stream_config['youtube_watch_url']
            save_news_config(config)
            
            return stream_config
        else:
            print("❌ Failed to setup live stream")
            return None
            
    except Exception as e:
        print(f"❌ ERROR setting up live stream: {e}")
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "live":
            # Setup live stream
            setup_live_stream()
            return
        elif command == "continuous":
            # Run continuous news cycles (for testing)
            print("🔄 Running in CONTINUOUS mode (Ctrl+C to stop)...")
            try:
                while True:
                    run_news_cycle()
                    print("\n⏳ Waiting 60 minutes until next cycle...\n")
                    time.sleep(3600)  # Wait 1 hour
            except KeyboardInterrupt:
                print("\n\n⏹️ Stopped by user")
            return
    
    # Default: Run single news cycle
    run_news_cycle()


if __name__ == "__main__":
    main()
