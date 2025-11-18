# FILE: src/news_database.py
# Database module for news storage and tracking

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

class NewsDatabase:
    """
    Manages news article storage and tracking.
    Uses JSON file storage by default. PostgreSQL support can be added.
    """
    
    def __init__(self, db_file="news_database.json"):
        self.db_file = Path(db_file)
        self.data = self._load_database()
    
    def _load_database(self):
        """Load database from file."""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load database: {e}")
        
        # Default structure
        return {
            'articles': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_articles': 0
            }
        }
    
    def _save_database(self):
        """Save database to file."""
        try:
            self.data['metadata']['last_updated'] = datetime.now().isoformat()
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"❌ Could not save database: {e}")
    
    def add_article(self, article):
        """
        Add article to database with timestamp.
        Returns article ID.
        """
        article_data = {
            'id': len(self.data['articles']) + 1,
            'title': article.get('title', ''),
            'description': article.get('description', ''),
            'content': article.get('content', ''),
            'source': article.get('source', ''),
            'url': article.get('url', ''),
            'published_at': article.get('published_at', ''),
            'image_url': article.get('image_url', ''),
            'category': article.get('category', 'general'),
            'relevance_score': article.get('relevance_score', 0),
            'stored_at': datetime.now().isoformat(),
            'used_in_bulletin': False,
            'bulletin_ids': []
        }
        
        self.data['articles'].append(article_data)
        self.data['metadata']['total_articles'] = len(self.data['articles'])
        self._save_database()
        
        return article_data['id']
    
    def mark_article_used(self, article_id, bulletin_id):
        """Mark article as used in a bulletin."""
        for article in self.data['articles']:
            if article['id'] == article_id:
                article['used_in_bulletin'] = True
                article['bulletin_ids'].append(bulletin_id)
                break
        self._save_database()
    
    def get_unused_articles(self, category=None, limit=10):
        """Get articles that haven't been used in bulletins yet."""
        unused = [a for a in self.data['articles'] if not a['used_in_bulletin']]
        
        if category:
            unused = [a for a in unused if a['category'] == category]
        
        # Sort by relevance and recency
        unused.sort(key=lambda x: (x['relevance_score'], x['published_at']), reverse=True)
        
        return unused[:limit]
    
    def cleanup_old_articles(self, days=7):
        """Remove articles older than specified days."""
        cutoff_time = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_time.isoformat()
        
        original_count = len(self.data['articles'])
        self.data['articles'] = [
            a for a in self.data['articles']
            if a['stored_at'] > cutoff_str
        ]
        
        removed = original_count - len(self.data['articles'])
        if removed > 0:
            print(f"🧹 Cleaned up {removed} old articles")
            self._save_database()
    
    def get_statistics(self):
        """Get database statistics."""
        total = len(self.data['articles'])
        used = sum(1 for a in self.data['articles'] if a['used_in_bulletin'])
        
        categories = {}
        for article in self.data['articles']:
            cat = article['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_articles': total,
            'used_articles': used,
            'unused_articles': total - used,
            'categories': categories,
            'last_updated': self.data['metadata']['last_updated']
        }
