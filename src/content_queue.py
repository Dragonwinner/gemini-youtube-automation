# FILE: src/content_queue.py
# Content queue and priority management system

import json
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

class Priority(Enum):
    """News priority levels."""
    BREAKING = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class ContentQueue:
    """
    Manages news content queue with:
    - Priority-based scheduling
    - Breaking news interruption
    - Content deduplication
    - Segment rotation
    """
    
    def __init__(self, queue_file="content_queue.json"):
        self.queue_file = Path(queue_file)
        self.queue = self._load_queue()
    
    def _load_queue(self):
        """Load queue from file."""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load queue: {e}")
        
        return {
            'items': [],
            'breaking_news': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def _save_queue(self):
        """Save queue to file."""
        try:
            self.queue['metadata']['last_updated'] = datetime.now().isoformat()
            with open(self.queue_file, 'w') as f:
                json.dump(self.queue, f, indent=2)
        except Exception as e:
            print(f"❌ Could not save queue: {e}")
    
    def add_content(self, article, priority=Priority.NORMAL, scheduled_time=None):
        """
        Add content to queue.
        
        Args:
            article: News article dict
            priority: Priority level (Priority enum)
            scheduled_time: Optional scheduled time (datetime or ISO string)
        
        Returns:
            Queue item ID
        """
        item = {
            'id': len(self.queue['items']) + 1,
            'article': article,
            'priority': priority.value,
            'priority_name': priority.name,
            'scheduled_time': scheduled_time.isoformat() if isinstance(scheduled_time, datetime) else scheduled_time,
            'added_at': datetime.now().isoformat(),
            'status': 'pending',
            'aired_at': None
        }
        
        self.queue['items'].append(item)
        self._save_queue()
        
        return item['id']
    
    def add_breaking_news(self, article, interrupt=True):
        """
        Add breaking news with highest priority.
        
        Args:
            article: Breaking news article
            interrupt: Whether to interrupt current broadcast
        
        Returns:
            Breaking news ID
        """
        breaking = {
            'id': len(self.queue['breaking_news']) + 1,
            'article': article,
            'added_at': datetime.now().isoformat(),
            'interrupt': interrupt,
            'aired': False
        }
        
        self.queue['breaking_news'].append(breaking)
        self._save_queue()
        
        print(f"🚨 BREAKING NEWS ADDED: {article.get('title', '')[:50]}")
        
        return breaking['id']
    
    def get_next_content(self):
        """
        Get next content to air based on priority and schedule.
        
        Returns:
            Content item dict or None
        """
        # Check for breaking news first
        for breaking in self.queue['breaking_news']:
            if not breaking['aired']:
                return {
                    'type': 'breaking',
                    'content': breaking,
                    'article': breaking['article']
                }
        
        # Get pending items
        pending = [item for item in self.queue['items'] if item['status'] == 'pending']
        
        if not pending:
            return None
        
        # Sort by priority and scheduled time
        pending.sort(key=lambda x: (
            x['priority'],
            x['scheduled_time'] or datetime.now().isoformat()
        ))
        
        # Check if top item is ready to air
        next_item = pending[0]
        if next_item['scheduled_time']:
            scheduled = datetime.fromisoformat(next_item['scheduled_time'])
            if datetime.now() < scheduled:
                return None  # Not yet time
        
        return {
            'type': 'regular',
            'content': next_item,
            'article': next_item['article']
        }
    
    def mark_as_aired(self, item_id, item_type='regular'):
        """Mark content as aired."""
        if item_type == 'breaking':
            for breaking in self.queue['breaking_news']:
                if breaking['id'] == item_id:
                    breaking['aired'] = True
                    breaking['aired_at'] = datetime.now().isoformat()
        else:
            for item in self.queue['items']:
                if item['id'] == item_id:
                    item['status'] = 'aired'
                    item['aired_at'] = datetime.now().isoformat()
        
        self._save_queue()
    
    def get_queue_stats(self):
        """Get queue statistics."""
        pending = sum(1 for item in self.queue['items'] if item['status'] == 'pending')
        aired = sum(1 for item in self.queue['items'] if item['status'] == 'aired')
        breaking = sum(1 for b in self.queue['breaking_news'] if not b['aired'])
        
        return {
            'total_items': len(self.queue['items']),
            'pending': pending,
            'aired': aired,
            'breaking_news': breaking
        }
    
    def cleanup_old_content(self, days=7):
        """Remove aired content older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        # Clean regular items
        original = len(self.queue['items'])
        self.queue['items'] = [
            item for item in self.queue['items']
            if item['status'] == 'pending' or 
            (item.get('aired_at', datetime.now().isoformat()) > cutoff_str)
        ]
        
        # Clean breaking news
        self.queue['breaking_news'] = [
            b for b in self.queue['breaking_news']
            if not b['aired'] or 
            (b.get('aired_at', datetime.now().isoformat()) > cutoff_str)
        ]
        
        removed = original - len(self.queue['items'])
        if removed > 0:
            print(f"🧹 Cleaned up {removed} old items from queue")
            self._save_queue()
    
    def create_segment_rotation(self, duration_minutes=5, categories=None):
        """
        Create a rotating segment schedule.
        
        Args:
            duration_minutes: Duration of each segment
            categories: List of news categories to rotate
        
        Returns:
            List of scheduled segments
        """
        if categories is None:
            categories = ['technology', 'business', 'sports', 'health', 'entertainment']
        
        segments = []
        start_time = datetime.now()
        
        for i, category in enumerate(categories):
            segment_time = start_time + timedelta(minutes=i * duration_minutes)
            segments.append({
                'category': category,
                'scheduled_time': segment_time,
                'duration': duration_minutes
            })
        
        return segments
