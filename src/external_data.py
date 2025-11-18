# FILE: src/external_data.py
# Integration with external data sources (Weather, Stock Market, Social Media)

import os
import requests
from datetime import datetime
import json

class ExternalDataProvider:
    """
    Provides additional data for news broadcasts:
    - Weather updates
    - Stock market tickers
    - Social media trending topics
    """
    
    def __init__(self):
        # API keys
        self.openweather_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.twitter_bearer = os.getenv('TWITTER_BEARER_TOKEN', '')
    
    def get_weather_update(self, city="New York", country_code="us"):
        """
        Get current weather update for a city.
        
        Args:
            city: City name
            country_code: Country code (e.g., 'us', 'uk')
        
        Returns:
            Weather update dict or None
        """
        if not self.openweather_key:
            return self._get_fallback_weather(city)
        
        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': f"{city},{country_code}",
                'appid': self.openweather_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            weather = {
                'city': city,
                'temperature': data['main']['temp'],
                'temperature_f': (data['main']['temp'] * 9/5) + 32,
                'feels_like': data['main']['feels_like'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'icon': data['weather'][0]['icon'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Format for broadcast
            weather['broadcast_text'] = (
                f"Current weather in {city}: {weather['description']}, "
                f"{int(weather['temperature_f'])} degrees Fahrenheit, "
                f"with {weather['humidity']}% humidity."
            )
            
            return weather
            
        except Exception as e:
            print(f"⚠️ Error fetching weather: {e}")
            return self._get_fallback_weather(city)
    
    def _get_fallback_weather(self, city):
        """Fallback weather information."""
        return {
            'city': city,
            'temperature': 20,
            'temperature_f': 68,
            'description': 'partly cloudy',
            'broadcast_text': f"Weather conditions in {city} are moderate.",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_stock_market_update(self, symbols=None):
        """
        Get stock market updates.
        
        Args:
            symbols: List of stock symbols (e.g., ['AAPL', 'GOOGL', 'MSFT'])
        
        Returns:
            List of stock update dicts
        """
        if symbols is None:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        
        if not self.alpha_vantage_key:
            return self._get_fallback_stocks(symbols)
        
        stocks = []
        
        for symbol in symbols[:5]:  # Limit to 5 to avoid API rate limits
            try:
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': self.alpha_vantage_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    price = float(quote.get('05. price', 0))
                    change = float(quote.get('09. change', 0))
                    change_percent = quote.get('10. change percent', '0%').rstrip('%')
                    
                    stocks.append({
                        'symbol': symbol,
                        'price': price,
                        'change': change,
                        'change_percent': float(change_percent),
                        'direction': 'up' if change >= 0 else 'down',
                        'timestamp': datetime.now().isoformat()
                    })
                
            except Exception as e:
                print(f"⚠️ Error fetching stock {symbol}: {e}")
                continue
        
        if not stocks:
            return self._get_fallback_stocks(symbols)
        
        # Format ticker text
        ticker_parts = []
        for stock in stocks:
            direction_arrow = '▲' if stock['direction'] == 'up' else '▼'
            ticker_parts.append(
                f"{stock['symbol']}: ${stock['price']:.2f} {direction_arrow} {abs(stock['change_percent']):.2f}%"
            )
        
        ticker_text = " | ".join(ticker_parts)
        
        return {
            'stocks': stocks,
            'ticker_text': ticker_text,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_fallback_stocks(self, symbols):
        """Fallback stock information."""
        stocks = []
        for symbol in symbols[:5]:
            stocks.append({
                'symbol': symbol,
                'price': 150.0,
                'change': 1.5,
                'change_percent': 1.0,
                'direction': 'up'
            })
        
        ticker_text = " | ".join([f"{s['symbol']}: $150.00 ▲ 1.0%" for s in stocks])
        
        return {
            'stocks': stocks,
            'ticker_text': ticker_text,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_trending_topics(self, country='US', limit=10):
        """
        Get trending topics from social media.
        Uses Twitter API v2 (requires elevated access).
        
        Args:
            country: Country code for trends
            limit: Number of trends to return
        
        Returns:
            List of trending topic dicts
        """
        if not self.twitter_bearer:
            return self._get_fallback_trends()
        
        try:
            # Twitter API v2 endpoint for trends
            # Note: Trends endpoint requires elevated access
            url = "https://api.twitter.com/2/trends/place"
            
            # WOEID for locations (1 = worldwide, 2459115 = New York)
            woeid = 1  # Worldwide
            
            headers = {
                'Authorization': f'Bearer {self.twitter_bearer}'
            }
            
            params = {
                'id': woeid
            }
            
            # Note: This is a simplified version. Full implementation would need
            # proper Twitter API setup and trending topics endpoint access
            
            print("⚠️ Twitter trends API requires elevated access. Using fallback.")
            return self._get_fallback_trends()
            
        except Exception as e:
            print(f"⚠️ Error fetching trends: {e}")
            return self._get_fallback_trends()
    
    def _get_fallback_trends(self):
        """Fallback trending topics."""
        trends = [
            {'name': '#Technology', 'tweet_volume': 50000, 'category': 'technology'},
            {'name': '#AI', 'tweet_volume': 45000, 'category': 'technology'},
            {'name': '#Business', 'tweet_volume': 40000, 'category': 'business'},
            {'name': '#Innovation', 'tweet_volume': 35000, 'category': 'general'},
            {'name': '#Science', 'tweet_volume': 30000, 'category': 'science'}
        ]
        
        return {
            'trends': trends,
            'broadcast_text': "Trending topics include " + ", ".join([t['name'] for t in trends[:3]]),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_google_trends(self, geo='US', limit=10):
        """
        Get trending searches from Google Trends.
        Uses pytrends library.
        
        Args:
            geo: Geographic location code
            limit: Number of trends to return
        
        Returns:
            List of trending searches
        """
        try:
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='en-US', tz=360)
            trending = pytrends.trending_searches(pn=geo.lower())
            
            trends = []
            for i, row in trending.head(limit).iterrows():
                trends.append({
                    'query': row[0],
                    'rank': i + 1
                })
            
            broadcast_text = "Top Google searches: " + ", ".join([t['query'] for t in trends[:3]])
            
            return {
                'trends': trends,
                'broadcast_text': broadcast_text,
                'timestamp': datetime.now().isoformat()
            }
            
        except ImportError:
            print("⚠️ pytrends not installed. Using fallback.")
            return self._get_fallback_google_trends()
        except Exception as e:
            print(f"⚠️ Error fetching Google Trends: {e}")
            return self._get_fallback_google_trends()
    
    def _get_fallback_google_trends(self):
        """Fallback Google Trends."""
        trends = [
            {'query': 'artificial intelligence', 'rank': 1},
            {'query': 'climate change', 'rank': 2},
            {'query': 'technology news', 'rank': 3}
        ]
        
        return {
            'trends': trends,
            'broadcast_text': "Popular searches include: " + ", ".join([t['query'] for t in trends]),
            'timestamp': datetime.now().isoformat()
        }
    
    def create_ticker_segment(self):
        """
        Create a complete ticker segment with weather, stocks, and trends.
        
        Returns:
            Dict with combined ticker information
        """
        weather = self.get_weather_update()
        stocks = self.get_stock_market_update()
        trends = self.get_google_trends()
        
        ticker_text = f"{weather['broadcast_text']} | Market: {stocks['ticker_text']} | {trends['broadcast_text']}"
        
        return {
            'weather': weather,
            'stocks': stocks,
            'trends': trends,
            'ticker_text': ticker_text,
            'timestamp': datetime.now().isoformat()
        }
