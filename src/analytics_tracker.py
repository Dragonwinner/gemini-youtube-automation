# FILE: src/analytics_tracker.py
# Analytics and viewer engagement tracking

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class AnalyticsTracker:
    """
    Tracks and analyzes:
    - Video performance metrics
    - Viewer engagement
    - Channel growth
    - Content effectiveness
    """
    
    def __init__(self, credentials_file='credentials.json'):
        self.credentials_file = Path(credentials_file)
        self.youtube = None
        self.analytics_file = Path('analytics_data.json')
        self.data = self._load_analytics()
        
        if self.credentials_file.exists():
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API."""
        try:
            credentials = Credentials.from_authorized_user_file(
                str(self.credentials_file),
                ['https://www.googleapis.com/auth/youtube.readonly',
                 'https://www.googleapis.com/auth/yt-analytics.readonly']
            )
            self.youtube = build('youtube', 'v3', credentials=credentials)
            print("✅ Analytics API authenticated")
        except Exception as e:
            print(f"⚠️ Analytics authentication failed: {e}")
    
    def _load_analytics(self):
        """Load analytics data from file."""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load analytics: {e}")
        
        return {
            'videos': [],
            'daily_stats': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def _save_analytics(self):
        """Save analytics data to file."""
        try:
            self.data['metadata']['last_updated'] = datetime.now().isoformat()
            with open(self.analytics_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"❌ Could not save analytics: {e}")
    
    def track_video(self, video_id, title, category, bulletin_id=None):
        """
        Start tracking a video.
        
        Args:
            video_id: YouTube video ID
            title: Video title
            category: News category
            bulletin_id: Optional bulletin ID
        """
        video_data = {
            'video_id': video_id,
            'title': title,
            'category': category,
            'bulletin_id': bulletin_id,
            'published_at': datetime.now().isoformat(),
            'metrics': {
                'views': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'watch_time_hours': 0,
                'avg_view_duration': 0,
                'click_through_rate': 0,
                'engagement_rate': 0
            },
            'last_checked': None
        }
        
        self.data['videos'].append(video_data)
        self._save_analytics()
        
        print(f"📊 Tracking video: {video_id}")
    
    def update_video_metrics(self, video_id):
        """
        Update metrics for a specific video from YouTube API.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Updated metrics dict or None
        """
        if not self.youtube:
            print("⚠️ YouTube API not authenticated")
            return None
        
        try:
            # Get video statistics
            response = self.youtube.videos().list(
                part='statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not response.get('items'):
                print(f"⚠️ Video {video_id} not found")
                return None
            
            stats = response['items'][0]['statistics']
            
            metrics = {
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'last_checked': datetime.now().isoformat()
            }
            
            # Update in local data
            for video in self.data['videos']:
                if video['video_id'] == video_id:
                    video['metrics'].update(metrics)
                    video['last_checked'] = metrics['last_checked']
                    
                    # Calculate engagement rate
                    views = metrics['views']
                    if views > 0:
                        engagement = (metrics['likes'] + metrics['comments']) / views * 100
                        video['metrics']['engagement_rate'] = round(engagement, 2)
                    
                    break
            
            self._save_analytics()
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error updating metrics for {video_id}: {e}")
            return None
    
    def update_all_metrics(self, hours_limit=24):
        """
        Update metrics for all videos published in last N hours.
        
        Args:
            hours_limit: Only update videos from last N hours
        """
        cutoff = datetime.now() - timedelta(hours=hours_limit)
        cutoff_str = cutoff.isoformat()
        
        updated = 0
        for video in self.data['videos']:
            if video.get('published_at', '') > cutoff_str:
                if self.update_video_metrics(video['video_id']):
                    updated += 1
        
        print(f"📊 Updated metrics for {updated} videos")
    
    def get_video_performance(self, video_id):
        """Get performance metrics for a specific video."""
        for video in self.data['videos']:
            if video['video_id'] == video_id:
                return video
        return None
    
    def get_top_performing_videos(self, metric='views', limit=10):
        """
        Get top performing videos by metric.
        
        Args:
            metric: 'views', 'likes', 'engagement_rate', etc.
            limit: Number of videos to return
        
        Returns:
            List of top performing videos
        """
        sorted_videos = sorted(
            self.data['videos'],
            key=lambda x: x['metrics'].get(metric, 0),
            reverse=True
        )
        
        return sorted_videos[:limit]
    
    def get_category_performance(self):
        """Get performance breakdown by category."""
        categories = {}
        
        for video in self.data['videos']:
            category = video.get('category', 'unknown')
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'total_views': 0,
                    'total_likes': 0,
                    'total_comments': 0,
                    'avg_engagement': 0
                }
            
            cat = categories[category]
            cat['count'] += 1
            cat['total_views'] += video['metrics'].get('views', 0)
            cat['total_likes'] += video['metrics'].get('likes', 0)
            cat['total_comments'] += video['metrics'].get('comments', 0)
        
        # Calculate averages
        for cat in categories.values():
            if cat['count'] > 0:
                cat['avg_views'] = cat['total_views'] / cat['count']
                cat['avg_engagement'] = (cat['total_likes'] + cat['total_comments']) / max(cat['total_views'], 1) * 100
        
        return categories
    
    def get_daily_summary(self):
        """Get summary of today's performance."""
        today = datetime.now().date().isoformat()
        
        today_videos = [
            v for v in self.data['videos']
            if v.get('published_at', '').startswith(today)
        ]
        
        summary = {
            'date': today,
            'videos_published': len(today_videos),
            'total_views': sum(v['metrics'].get('views', 0) for v in today_videos),
            'total_likes': sum(v['metrics'].get('likes', 0) for v in today_videos),
            'total_comments': sum(v['metrics'].get('comments', 0) for v in today_videos),
            'avg_engagement': 0
        }
        
        if summary['total_views'] > 0:
            summary['avg_engagement'] = (
                (summary['total_likes'] + summary['total_comments']) / 
                summary['total_views'] * 100
            )
        
        return summary
    
    def generate_report(self, days=7):
        """
        Generate comprehensive performance report.
        
        Args:
            days: Number of days to include in report
        
        Returns:
            Report dict
        """
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        recent_videos = [
            v for v in self.data['videos']
            if v.get('published_at', '') > cutoff_str
        ]
        
        report = {
            'period_days': days,
            'videos_count': len(recent_videos),
            'total_views': sum(v['metrics'].get('views', 0) for v in recent_videos),
            'total_likes': sum(v['metrics'].get('likes', 0) for v in recent_videos),
            'total_comments': sum(v['metrics'].get('comments', 0) for v in recent_videos),
            'avg_views_per_video': 0,
            'avg_engagement_rate': 0,
            'top_videos': [],
            'category_breakdown': self.get_category_performance(),
            'generated_at': datetime.now().isoformat()
        }
        
        if report['videos_count'] > 0:
            report['avg_views_per_video'] = report['total_views'] / report['videos_count']
            
            if report['total_views'] > 0:
                report['avg_engagement_rate'] = (
                    (report['total_likes'] + report['total_comments']) /
                    report['total_views'] * 100
                )
            
            # Get top 5 videos
            report['top_videos'] = [
                {
                    'title': v['title'],
                    'views': v['metrics']['views'],
                    'engagement': v['metrics'].get('engagement_rate', 0)
                }
                for v in self.get_top_performing_videos(limit=5)
            ]
        
        return report
    
    def save_report(self, report, filename=None):
        """Save report to file."""
        if filename is None:
            filename = f"analytics_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📊 Report saved: {filename}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")
