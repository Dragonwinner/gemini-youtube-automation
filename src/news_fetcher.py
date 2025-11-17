# FILE: src/news_fetcher.py
# News fetching module for automated news production platform

import os
import requests
from datetime import datetime, timedelta
import json

class NewsFetcher:
    """Fetches news from multiple sources for automated news production."""
    
    def __init__(self):
        # NewsAPI.org - Free tier: 100 requests/day
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        self.newsapi_url = "https://newsapi.org/v2/everything"
        self.newsapi_top_url = "https://newsapi.org/v2/top-headlines"
        
    def fetch_breaking_news(self, category="technology", country="us", max_articles=5):
        """
        Fetches breaking/top news headlines.
        
        Categories: business, entertainment, general, health, science, sports, technology
        """
        if not self.newsapi_key:
            print("⚠️ NEWSAPI_KEY not found. Using fallback news generation.")
            return self._generate_fallback_news(category, max_articles)
        
        try:
            params = {
                "apiKey": self.newsapi_key,
                "country": country,
                "category": category,
                "pageSize": max_articles
            }
            
            response = requests.get(self.newsapi_top_url, params=params, timeout=10)
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
                print(f"✅ Fetched {len(articles)} breaking news articles")
                return articles
            else:
                print(f"⚠️ No articles found in API response")
                return self._generate_fallback_news(category, max_articles)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error fetching news: {e}")
            return self._generate_fallback_news(category, max_articles)
        except Exception as e:
            print(f"❌ Error fetching news: {e}")
            return self._generate_fallback_news(category, max_articles)
    
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
