# FILE: news_main_enhanced.py
# Enhanced main entry point integrating all 24/7 news automation features

import os
import json
import time
import traceback
from pathlib import Path
from datetime import datetime

# Import existing modules
from src.news_fetcher import NewsFetcher
from src.news_generator import NewsContentGenerator
from src.live_streamer import LiveStreamer
from src.uploader import upload_to_youtube

# Import new enhanced modules
from src.news_database import NewsDatabase
from src.tts_provider import TTSProvider
from src.video_generator import VideoGenerator
from src.stream_manager import StreamManager
from src.content_queue import ContentQueue, Priority
from src.external_data import ExternalDataProvider
from src.logging_system import NewsLogger
from src.analytics_tracker import AnalyticsTracker
from src.caption_generator import CaptionGenerator

# Import generator functions for backward compatibility
from src.generator import text_to_speech, generate_visuals, create_video

# Configuration
OUTPUT_DIR = Path("output")
NEWS_CONFIG_FILE = Path("news_config.json")
ANCHOR_NAME = "AI News Anchor"

# News categories
NEWS_CATEGORIES = [
    "technology",
    "business",
    "science",
    "health",
    "entertainment",
    "sports",
    "general"
]


class EnhancedNewsAutomation:
    """
    Enhanced 24/7 News Automation System with:
    - Multi-source news aggregation
    - Premium TTS options
    - AI avatar support
    - Live streaming
    - Analytics tracking
    - Automatic captions
    - Weather & stock tickers
    """
    
    def __init__(self):
        """Initialize all components."""
        # Core components
        self.news_fetcher = NewsFetcher()
        self.news_generator = NewsContentGenerator(ANCHOR_NAME)
        self.database = NewsDatabase()
        self.queue = ContentQueue()
        
        # TTS provider (can be configured: gtts, elevenlabs, google_cloud, azure)
        tts_provider = os.getenv('TTS_PROVIDER', 'gtts')
        self.tts = TTSProvider(provider=tts_provider)
        
        # Video generation (standard or avatar mode)
        video_mode = os.getenv('VIDEO_MODE', 'standard')  # or 'avatar', 'hybrid'
        self.video_gen = VideoGenerator(mode=video_mode)
        
        # External data
        self.external_data = ExternalDataProvider()
        
        # Logging and analytics
        self.logger = NewsLogger()
        self.analytics = AnalyticsTracker()
        
        # Caption generator
        self.caption_gen = CaptionGenerator()
        
        # Configuration
        self.config = self._load_config()
        
        self.logger.info("Enhanced News Automation System initialized")
    
    def _load_config(self):
        """Load or create configuration."""
        if NEWS_CONFIG_FILE.exists():
            try:
                with open(NEWS_CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
        
        config = {
            "last_run": None,
            "total_bulletins": 0,
            "current_category_index": 0,
            "live_stream_active": False,
            "live_stream_id": None,
            "categories_covered": {},
            "created_at": datetime.now().isoformat()
        }
        
        self._save_config(config)
        return config
    
    def _save_config(self, config):
        """Save configuration."""
        try:
            with open(NEWS_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def fetch_and_store_news(self, category="technology", max_articles=10):
        """
        Fetch news from multiple sources and store in database.
        
        Returns:
            List of article IDs
        """
        start_time = time.time()
        
        self.logger.info(f"Fetching news for category: {category}")
        
        # Fetch from NewsAPI + RSS feeds
        articles = self.news_fetcher.fetch_breaking_news(
            category=category,
            max_articles=max_articles
        )
        
        duration = time.time() - start_time
        self.logger.log_api_call('news_fetch', category, duration * 1000, bool(articles))
        
        # Store in database
        article_ids = []
        for article in articles:
            article['category'] = category
            article_id = self.database.add_article(article)
            article_ids.append(article_id)
            
            # Add to content queue with priority
            priority = Priority.BREAKING if 'breaking' in article.get('title', '').lower() else Priority.NORMAL
            self.queue.add_content(article, priority=priority)
        
        self.logger.info(f"Stored {len(article_ids)} articles in database")
        
        return article_ids
    
    def create_enhanced_bulletin(self, articles, bulletin_type="hourly"):
        """
        Create news bulletin with enhanced features:
        - Weather updates
        - Stock tickers
        - Trending topics
        - Premium TTS
        - Lower-third graphics
        """
        start_time = time.time()
        bulletin_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{bulletin_type}"
        
        self.logger.info(f"Creating bulletin: {bulletin_id}")
        
        try:
            # Generate AI script
            bulletin_content = self.news_generator.generate_news_bulletin(articles, bulletin_type)
            
            # Get external data (weather, stocks, trends)
            ticker_data = self.external_data.create_ticker_segment()
            
            # Build complete script with ticker info
            full_script = f"{bulletin_content['opening']}\n\n"
            
            # Add ticker segment
            full_script += f"{ticker_data['ticker_text']}\n\n"
            
            # Add headlines
            full_script += "Here are today's headlines:\n"
            for headline in bulletin_content['headlines'][:5]:
                full_script += f"{headline}\n"
            
            # Add detailed stories
            full_script += "\nNow for the detailed stories.\n\n"
            for story in bulletin_content['detailed_stories']:
                full_script += f"{story['content']}\n\n"
            
            full_script += bulletin_content['closing']
            
            # Generate audio with premium TTS
            self.logger.info("Generating audio with TTS...")
            audio_path = OUTPUT_DIR / f"bulletin_audio_{bulletin_id}.mp3"
            audio_file = self.tts.synthesize(
                full_script,
                audio_path,
                language='en',
                emotion='neutral'
            )
            
            # Create video with enhanced graphics
            self.logger.info("Creating video with enhanced graphics...")
            
            # Generate news background
            category = articles[0].get('category', 'general') if articles else 'general'
            background = self.video_gen.create_news_background(category)
            
            # Save background
            background_path = OUTPUT_DIR / f"background_{bulletin_id}.png"
            background.save(background_path)
            
            # Generate lower-third with ticker
            lower_third = self.video_gen.generate_lower_third(
                headline=bulletin_content['headlines'][0] if bulletin_content['headlines'] else "Live News Update",
                ticker_text=ticker_data['ticker_text']
            )
            lower_third_path = OUTPUT_DIR / f"lower_third_{bulletin_id}.png"
            lower_third.save(lower_third_path)
            
            # Create slide with background and lower-third
            slide_content = {
                "title": f"{bulletin_type.upper()} NEWS UPDATE",
                "content": f"{datetime.now().strftime('%B %d, %Y - %I:%M %p')}\n\n{ANCHOR_NAME}"
            }
            
            slide_dir = OUTPUT_DIR / f"slides_{bulletin_id}"
            slide_path = generate_visuals(
                output_dir=slide_dir,
                video_type='long',
                slide_content=slide_content,
                slide_number=1,
                total_slides=1
            )
            
            # Create final video
            video_path = OUTPUT_DIR / f"bulletin_{bulletin_id}.mp4"
            create_video([slide_path], [audio_file], video_path, 'long')
            
            # Generate captions
            self.logger.info("Generating captions...")
            caption_path = OUTPUT_DIR / f"captions_{bulletin_id}.srt"
            self.caption_gen.generate_from_script(
                full_script,
                caption_path,
                format='srt',
                duration=None  # Will be auto-calculated
            )
            
            # Generate thumbnail
            thumbnail_path = generate_visuals(
                output_dir=OUTPUT_DIR,
                video_type='long',
                thumbnail_title=f"🔴 LIVE NEWS - {datetime.now().strftime('%B %d')}"
            )
            
            duration = time.time() - start_time
            self.logger.log_bulletin_production(bulletin_id, category, duration, success=True)
            
            return {
                'bulletin_id': bulletin_id,
                'video_path': video_path,
                'caption_path': caption_path,
                'thumbnail_path': thumbnail_path,
                'content': bulletin_content,
                'ticker_data': ticker_data
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error creating bulletin: {e}", exception=e)
            self.logger.log_bulletin_production(bulletin_id, category, duration, success=False)
            raise
    
    def upload_with_captions(self, bulletin_data):
        """Upload video to YouTube with captions."""
        try:
            # Prepare metadata
            title = f"🔴 {datetime.now().strftime('%B %d, %Y')} - {bulletin_data['content']['headlines'][0][:50]}"
            
            description = f"""Live News Update - {datetime.now().strftime('%I:%M %p')}

{bulletin_data['content']['opening']}

📰 Today's Headlines:
"""
            for headline in bulletin_data['content']['headlines'][:5]:
                description += f"• {headline}\n"
            
            # Add ticker info
            description += f"\n🌤️ {bulletin_data['ticker_data']['weather']['broadcast_text']}\n"
            description += f"📈 {bulletin_data['ticker_data']['stocks']['ticker_text']}\n"
            
            description += f"\n{bulletin_data['content']['hashtags']}\n\n"
            description += "Subscribe for 24/7 news coverage! 🔔\n\n"
            description += "#LiveNews #Breaking #NewsUpdate #24x7News"
            
            tags = "news,breaking news,live news,updates,current events,24/7 news"
            
            # Upload video
            upload_start = time.time()
            video_id = upload_to_youtube(
                bulletin_data['video_path'],
                title,
                description,
                tags,
                bulletin_data['thumbnail_path']
            )
            
            if video_id:
                upload_time = time.time() - upload_start
                video_size = bulletin_data['video_path'].stat().st_size / (1024 * 1024)  # MB
                
                self.logger.log_video_upload(video_id, title, video_size, upload_time)
                
                # Upload captions
                self.logger.info("Uploading captions...")
                self.caption_gen.upload_to_youtube(
                    video_id,
                    bulletin_data['caption_path'],
                    language='en',
                    name='English'
                )
                
                # Track in analytics
                category = bulletin_data.get('category', 'general')
                self.analytics.track_video(
                    video_id,
                    title,
                    category,
                    bulletin_id=bulletin_data['bulletin_id']
                )
                
                return video_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error uploading video: {e}", exception=e)
            return None
    
    def run_bulletin_cycle(self):
        """Run a complete news bulletin cycle."""
        self.logger.info("="*60)
        self.logger.info("Starting news bulletin cycle")
        self.logger.info("="*60)
        
        try:
            # Create output directory
            OUTPUT_DIR.mkdir(exist_ok=True)
            
            # Get current category
            category_index = self.config.get('current_category_index', 0) % len(NEWS_CATEGORIES)
            current_category = NEWS_CATEGORIES[category_index]
            
            self.logger.info(f"Current category: {current_category}")
            
            # Fetch and store news
            self.fetch_and_store_news(current_category, max_articles=10)
            
            # Get unused articles from database
            articles = self.database.get_unused_articles(category=current_category, limit=5)
            
            if not articles:
                self.logger.warning("No unused articles, fetching more...")
                self.fetch_and_store_news(current_category, max_articles=5)
                articles = self.database.get_unused_articles(category=current_category, limit=5)
            
            if articles:
                # Determine bulletin type
                current_hour = datetime.now().hour
                if current_hour % 6 == 0:
                    bulletin_type = "major"
                elif current_hour % 3 == 0:
                    bulletin_type = "midday"
                else:
                    bulletin_type = "hourly"
                
                # Create bulletin
                bulletin_data = self.create_enhanced_bulletin(articles, bulletin_type)
                bulletin_data['category'] = current_category
                
                # Upload
                video_id = self.upload_with_captions(bulletin_data)
                
                if video_id:
                    # Mark articles as used
                    for article in articles:
                        self.database.mark_article_used(article['id'], bulletin_data['bulletin_id'])
                    
                    # Update configuration
                    self.config['last_run'] = datetime.now().isoformat()
                    self.config['total_bulletins'] += 1
                    self.config['current_category_index'] = (category_index + 1) % len(NEWS_CATEGORIES)
                    
                    if current_category not in self.config['categories_covered']:
                        self.config['categories_covered'][current_category] = 0
                    self.config['categories_covered'][current_category] += 1
                    
                    self._save_config(self.config)
                    
                    self.logger.info(f"✅ Bulletin cycle completed successfully!")
                    self.logger.info(f"Total bulletins: {self.config['total_bulletins']}")
                    
                    # Log system stats
                    self.logger.log_system_stats()
                    
                    # Cleanup old data
                    if self.config['total_bulletins'] % 10 == 0:
                        self.database.cleanup_old_articles(days=7)
                        self.queue.cleanup_old_content(days=7)
                        self.logger.cleanup_old_logs(days=30)
                    
                    return True
                else:
                    self.logger.error("Video upload failed")
                    return False
            else:
                self.logger.error("No articles available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in bulletin cycle: {e}", exception=e)
            return False
        finally:
            # Cleanup temporary files
            try:
                for file in OUTPUT_DIR.glob("*.wav"):
                    file.unlink()
            except Exception as e:
                self.logger.warning(f"Cleanup error: {e}")
    
    def run_continuous(self, interval_minutes=60):
        """Run continuous news cycles."""
        self.logger.info(f"Starting continuous mode (every {interval_minutes} minutes)")
        
        try:
            while True:
                success = self.run_bulletin_cycle()
                
                if success:
                    self.logger.info(f"Waiting {interval_minutes} minutes until next cycle...")
                else:
                    self.logger.warning(f"Cycle failed, waiting {interval_minutes} minutes before retry...")
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.logger.info("Continuous mode stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error in continuous mode: {e}", exception=e)
    
    def setup_24x7_stream(self):
        """Setup 24/7 live streaming."""
        self.logger.info("Setting up 24/7 live stream")
        
        try:
            # Create YouTube live stream
            streamer = LiveStreamer()
            stream_config = streamer.setup_24x7_stream("Automated News 24/7")
            
            if stream_config:
                self.logger.info("✅ Live stream setup complete!")
                self.logger.info(f"Watch URL: {stream_config['youtube_watch_url']}")
                
                # Save configuration
                self.config['live_stream_active'] = True
                self.config['live_stream_id'] = stream_config['broadcast_id']
                self.config['live_stream_url'] = stream_config['youtube_watch_url']
                self._save_config(self.config)
                
                # Setup stream manager
                stream_manager = StreamManager()
                stream_manager.setup_stream(
                    stream_config['rtmp_url'],
                    stream_config['stream_key']
                )
                
                # Create test video for streaming
                test_video = OUTPUT_DIR / "stream_test.mp4"
                stream_manager.create_test_video(test_video, duration=300)
                
                self.logger.info("Starting stream monitoring...")
                stream_manager.monitor_stream(test_video, check_interval=30)
                
                return True
            else:
                self.logger.error("Failed to setup live stream")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting up stream: {e}", exception=e)
            return False
    
    def generate_analytics_report(self, days=7):
        """Generate and save analytics report."""
        self.logger.info(f"Generating {days}-day analytics report")
        
        try:
            # Update metrics for recent videos
            self.analytics.update_all_metrics(hours_limit=days * 24)
            
            # Generate report
            report = self.analytics.generate_report(days=days)
            
            # Save report
            report_file = f"analytics_report_{datetime.now().strftime('%Y%m%d')}.json"
            self.analytics.save_report(report, report_file)
            
            # Log summary
            self.logger.info(f"Report generated: {report_file}")
            self.logger.info(f"Videos: {report['videos_count']}")
            self.logger.info(f"Total views: {report['total_views']}")
            self.logger.info(f"Avg engagement: {report['avg_engagement_rate']:.2f}%")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}", exception=e)
            return None


def main():
    """Main entry point."""
    import sys
    
    # Initialize system
    system = EnhancedNewsAutomation()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "live":
            # Setup and start live streaming
            system.setup_24x7_stream()
            
        elif command == "continuous":
            # Run continuous cycles
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            system.run_continuous(interval_minutes=interval)
            
        elif command == "analytics":
            # Generate analytics report
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            system.generate_analytics_report(days=days)
            
        elif command == "test":
            # Run test cycle
            system.logger.info("Running test cycle...")
            system.run_bulletin_cycle()
            
        else:
            print("Unknown command. Available commands:")
            print("  python news_main_enhanced.py          # Run single cycle")
            print("  python news_main_enhanced.py live     # Setup live stream")
            print("  python news_main_enhanced.py continuous [minutes]  # Continuous mode")
            print("  python news_main_enhanced.py analytics [days]      # Generate report")
            print("  python news_main_enhanced.py test     # Test cycle")
    else:
        # Default: Run single bulletin cycle
        system.run_bulletin_cycle()


if __name__ == "__main__":
    main()
