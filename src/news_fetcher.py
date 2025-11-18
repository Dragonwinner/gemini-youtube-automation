# FILE: src/news_fetcher.py
# News fetching module for automated news production platform

import os
import requests
import feedparser
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse
import json
import re

class NewsFetcher:
    """Fetches news from multiple sources for automated news production."""
    
    def __init__(self):
        # NewsAPI.org - Free tier: 100 requests/day
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        self.newsapi_url = "https://newsapi.org/v2/everything"
        self.newsapi_top_url = "https://newsapi.org/v2/top-headlines"
        
        # RSS feed sources by category
        self.rss_feeds = {
            "technology": [
                "https://www.wired.com/feed/rss",
                "https://techcrunch.com/feed/",
                "https://www.theverge.com/rss/index.xml"
            ],
            "business": [
                "https://feeds.reuters.com/reuters/businessNews",
                "https://www.cnbc.com/id/100003114/device/rss/rss.html"
            ],
            "sports": [
                "https://www.espn.com/espn/rss/news",
                "https://feeds.reuters.com/reuters/sportsNews"
            ],
            "entertainment": [
                "https://variety.com/feed/",
                "https://www.hollywoodreporter.com/feed/"
            ],
            "general": [
                "https://feeds.reuters.com/reuters/topNews",
                "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
            ],
            "science": [
                "https://www.sciencedaily.com/rss/top.xml"
            ],
            "health": [
                "https://rss.medicalnewstoday.com/featurednews.xml"
            ]
        }
        
        # Cache for deduplication
        self.seen_articles = set()
        self._load_seen_articles()
    
    def _load_seen_articles(self):
        """Load previously seen articles from cache file."""
        cache_file = "news_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.seen_articles = set(cache_data.get('seen_articles', []))
                    # Keep only recent articles (last 7 days)
                    cutoff_time = datetime.now() - timedelta(days=7)
                    cutoff_str = cutoff_time.isoformat()
                    if cache_data.get('last_cleanup', '') < cutoff_str:
                        self.seen_articles = set(list(self.seen_articles)[-1000:])
            except Exception as e:
                print(f"Warning: Could not load article cache: {e}")
                self.seen_articles = set()
    
    def _save_seen_articles(self):
        """Save seen articles to cache file."""
        cache_file = "news_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'seen_articles': list(self.seen_articles),
                    'last_cleanup': datetime.now().isoformat()
                }, f)
        except Exception as e:
            print(f"Warning: Could not save article cache: {e}")
    
    def _generate_article_hash(self, article):
        """Generate unique hash for article deduplication."""
        # Use title and source as unique identifier
        unique_str = f"{article.get('title', '')}{article.get('source', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def _is_duplicate(self, article):
        """Check if article is a duplicate."""
        article_hash = self._generate_article_hash(article)
        return article_hash in self.seen_articles
    
    def _mark_as_seen(self, article):
        """Mark article as seen."""
        article_hash = self._generate_article_hash(article)
        self.seen_articles.add(article_hash)
    
    def _calculate_relevance_score(self, article, category):
        """Calculate relevance score for article ranking."""
        score = 0
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        # Recency score (fresher = higher)
        try:
            pub_time = datetime.fromisoformat(article.get('published_at', '').replace('Z', '+00:00'))
            hours_old = (datetime.now() - pub_time.replace(tzinfo=None)).total_seconds() / 3600
            recency_score = max(0, 100 - hours_old)
            score += recency_score
        except:
            score += 50  # Default for unparseable dates
        
        # Category relevance keywords
        category_keywords = {
            'technology': ['tech', 'ai', 'software', 'digital', 'computer', 'data', 'innovation'],
            'business': ['market', 'economy', 'finance', 'company', 'stock', 'trade'],
            'sports': ['game', 'team', 'player', 'match', 'championship', 'league'],
            'health': ['health', 'medical', 'disease', 'treatment', 'hospital', 'doctor'],
            'science': ['research', 'study', 'scientist', 'discovery', 'experiment'],
            'entertainment': ['movie', 'music', 'celebrity', 'film', 'show', 'actor'],
            'general': ['news', 'world', 'breaking', 'update']
        }
        
        keywords = category_keywords.get(category, [])
        for keyword in keywords:
            if keyword in title:
                score += 10
            if keyword in description:
                score += 5
        
        # Breaking news indicators
        breaking_words = ['breaking', 'urgent', 'alert', 'just in', 'developing']
        for word in breaking_words:
            if word in title or word in description:
                score += 20
        
        return score
    
    def fetch_from_rss(self, category="technology", max_articles=5):
        """Fetch news from RSS feeds for a given category."""
        feeds = self.rss_feeds.get(category, self.rss_feeds.get('general', []))
        articles = []
        
        for feed_url in feeds:
            try:
                print(f"📡 Fetching RSS feed: {urlparse(feed_url).netloc}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:max_articles]:
                    article = {
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', entry.get('description', '')),
                        'content': entry.get('content', [{}])[0].get('value', '') if 'content' in entry else '',
                        'source': feed.feed.get('title', urlparse(feed_url).netloc),
                        'url': entry.get('link', ''),
                        'published_at': entry.get('published', entry.get('updated', datetime.now().isoformat())),
                        'image_url': ''
                    }
                    
                    # Clean HTML tags from description
                    article['description'] = re.sub('<[^<]+?>', '', article['description'])
                    
                    # Skip duplicates
                    if not self._is_duplicate(article):
                        article['relevance_score'] = self._calculate_relevance_score(article, category)
                        articles.append(article)
                        self._mark_as_seen(article)
                
            except Exception as e:
                print(f"⚠️ Error fetching RSS feed {feed_url}: {e}")
                continue
        
        return articles
        
    def fetch_breaking_news(self, category="technology", country="us", max_articles=5):
        """
        Fetches breaking/top news headlines from multiple sources.
        
        Categories: business, entertainment, general, health, science, sports, technology
        """
        all_articles = []
        
        # Try NewsAPI first
        if self.newsapi_key:
            try:
                params = {
                    "apiKey": self.newsapi_key,
                    "country": country,
                    "category": category,
                    "pageSize": max_articles * 2  # Get more to filter duplicates
                }
                
                response = requests.get(self.newsapi_top_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "ok" and data.get("articles"):
                    for article in data["articles"]:
                        article_obj = {
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "content": article.get("content", ""),
                            "source": article.get("source", {}).get("name", "Unknown"),
                            "url": article.get("url", ""),
                            "published_at": article.get("publishedAt", ""),
                            "image_url": article.get("urlToImage", "")
                        }
                        
                        # Skip duplicates
                        if not self._is_duplicate(article_obj):
                            article_obj['relevance_score'] = self._calculate_relevance_score(article_obj, category)
                            all_articles.append(article_obj)
                            self._mark_as_seen(article_obj)
                    
                    print(f"✅ Fetched {len(all_articles)} articles from NewsAPI")
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error fetching NewsAPI: {e}")
            except Exception as e:
                print(f"❌ Error fetching NewsAPI: {e}")
        
        # Also fetch from RSS feeds
        rss_articles = self.fetch_from_rss(category, max_articles)
        all_articles.extend(rss_articles)
        
        # If we got no articles from any source, use fallback
        if not all_articles:
            print("⚠️ No articles from any source. Using fallback news generation.")
            return self._generate_fallback_news(category, max_articles)
        
        # Sort by relevance score and recency
        all_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Save seen articles
        self._save_seen_articles()
        
        return all_articles[:max_articles]
    
    def fetch_recent_news(self, query, hours_ago=24, max_articles=10):
        """
        Fetches recent news based on a search query.
        """
        if not self.newsapi_key:
            return self._generate_fallback_news(query, max_articles)
        
        try:
            from_date = (datetime.utcnow() - timedelta(hours=hours_ago)).isoformat()
            
            params = {
                "apiKey": self.newsapi_key,
                "q": query,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": max_articles
            }
            
            response = requests.get(self.newsapi_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok" and data.get("articles"):
                articles = []
                for article in data["articles"][:max_articles]:
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "content": article.get("content", ""),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "url": article.get("url", ""),
                        "published_at": article.get("publishedAt", ""),
                        "image_url": article.get("urlToImage", "")
                    })
                print(f"✅ Fetched {len(articles)} recent news articles for '{query}'")
                return articles
            else:
                return self._generate_fallback_news(query, max_articles)
                
        except Exception as e:
            print(f"❌ Error fetching recent news: {e}")
            return self._generate_fallback_news(query, max_articles)
    
    def _generate_fallback_news(self, topic, count=3):
        """
        Generates fallback news topics when API is unavailable.
        This ensures 24/7 operation even without external APIs.
        """
        print(f"📰 Generating fallback news topics for: {topic}")
        
        # Generic news templates based on topic
        fallback_articles = [
            {
                "title": f"Latest Developments in {topic.title()}",
                "description": f"Recent updates and trends in the {topic} sector continue to shape the industry.",
                "content": f"Industry experts discuss the evolving landscape of {topic}.",
                "source": "Automated News",
                "url": "",
                "published_at": datetime.utcnow().isoformat(),
                "image_url": ""
            },
            {
                "title": f"{topic.title()} Innovation Report",
                "description": f"New breakthroughs and innovations emerge in {topic}.",
                "content": f"Analysis of recent innovations and their impact on {topic}.",
                "source": "Automated News",
                "url": "",
                "published_at": datetime.utcnow().isoformat(),
                "image_url": ""
            },
            {
                "title": f"Global {topic.title()} Updates",
                "description": f"Worldwide perspective on current {topic} developments.",
                "content": f"International view of the latest {topic} news and trends.",
                "source": "Automated News",
                "url": "",
                "published_at": datetime.utcnow().isoformat(),
                "image_url": ""
            }
        ]
        
        return fallback_articles[:count]
    
    def get_news_categories(self):
        """Returns available news categories for 24/7 rotation."""
        return [
            "technology",
            "business",
            "science",
            "health",
            "entertainment",
            "sports",
            "general"
        ]
