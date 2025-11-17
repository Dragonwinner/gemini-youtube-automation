# FILE: src/news_generator.py
# News content generator using Gemini AI for automated news videos

import os
import json
import google.generativeai as genai
from datetime import datetime

class NewsContentGenerator:
    """Generates professional news video content using Gemini AI."""
    
    def __init__(self, anchor_name="AI News Anchor"):
        self.anchor_name = anchor_name
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            print("⚠️ GOOGLE_API_KEY not found. Using fallback content generation.")
    
    def generate_news_bulletin(self, news_articles, bulletin_type="hourly"):
        """
        Generates a complete news bulletin from multiple articles.
        
        bulletin_type: 'breaking', 'hourly', 'daily', 'themed'
        """
        print(f"🤖 Generating {bulletin_type} news bulletin content...")
        
        if not self.model:
            print("⚠️ No AI model available, using fallback generation")
            return self._generate_fallback_bulletin(news_articles, bulletin_type)
        
        try:
            # Prepare articles summary for AI
            articles_text = ""
            for i, article in enumerate(news_articles, 1):
                articles_text += f"\n\nArticle {i}:\n"
                articles_text += f"Title: {article['title']}\n"
                articles_text += f"Source: {article['source']}\n"
                articles_text += f"Description: {article['description']}\n"
                if article.get('content'):
                    articles_text += f"Content: {article['content']}\n"
            
            prompt = f"""
            You are a professional news script writer for an automated 24/7 news channel. Create a news bulletin for the following articles.
            
            Bulletin Type: {bulletin_type.upper()}
            News Anchor: {self.anchor_name}
            Current Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            
            {articles_text}
            
            Create a professional news bulletin with the following structure:
            
            1. "opening": A brief, engaging opening greeting and introduction (2-3 sentences)
            2. "headlines": A list of 3-5 headline summaries (each 1 sentence, punchy)
            3. "detailed_stories": A list of story objects, each with:
               - "title": Story headline
               - "content": Full story script (3-5 sentences, professional news style)
               - "source": News source attribution
            4. "closing": A brief, professional closing statement (1-2 sentences)
            5. "hashtags": 5-7 relevant hashtags for social media (space-separated)
            6. "short_highlight": One single most important/interesting story formatted as a 60-second short (2-3 sentences max)
            
            Write in a professional, clear, and engaging news anchor style. Make it suitable for automated text-to-speech.
            Avoid complex punctuation. Use simple, declarative sentences.
            
            Return ONLY valid JSON with these exact keys.
            """
            
            response = self.model.generate_content(prompt)
            json_string = response.text.strip().replace("```json", "").replace("```", "")
            content = json.loads(json_string)
            
            print(f"✅ News bulletin content generated successfully!")
            return content
            
        except Exception as e:
            print(f"❌ ERROR: Failed to generate news bulletin: {e}")
            # Fallback content
            return self._generate_fallback_bulletin(news_articles, bulletin_type)
    
    def generate_breaking_news_alert(self, article):
        """
        Generates a quick breaking news alert script.
        """
        print(f"🚨 Generating breaking news alert...")
        
        if not self.model:
            print("⚠️ No AI model available, using fallback generation")
            return {
                "alert_intro": "This is a breaking news alert.",
                "story": f"{article['title']}. {article['description']}",
                "source_credit": f"Source: {article['source']}",
                "closing": "We will continue to monitor this story."
            }
        
        try:
            prompt = f"""
            You are a news anchor for a 24/7 automated news channel. Create a brief BREAKING NEWS alert script.
            
            Article Title: {article['title']}
            Source: {article['source']}
            Description: {article['description']}
            Content: {article.get('content', '')}
            
            Create a JSON response with:
            1. "alert_intro": Brief, urgent opening (1 sentence, e.g., "This is a breaking news alert...")
            2. "story": The main story content (3-4 sentences, clear and concise)
            3. "source_credit": Source attribution (1 sentence)
            4. "closing": Brief closing (1 sentence)
            
            Keep it urgent but professional. Suitable for text-to-speech.
            Return ONLY valid JSON.
            """
            
            response = self.model.generate_content(prompt)
            json_string = response.text.strip().replace("```json", "").replace("```", "")
            content = json.loads(json_string)
            
            print(f"✅ Breaking news alert generated!")
            return content
            
        except Exception as e:
            print(f"❌ ERROR: Failed to generate breaking news: {e}")
            return {
                "alert_intro": "This is a breaking news alert.",
                "story": f"{article['title']}. {article['description']}",
                "source_credit": f"Source: {article['source']}",
                "closing": "We will continue to monitor this story."
            }
    
    def generate_live_stream_script(self, news_articles, duration_minutes=60):
        """
        Generates a script for a live news stream with multiple segments.
        """
        print(f"📺 Generating {duration_minutes}-minute live stream script...")
        
        if not self.model:
            print("⚠️ No AI model available, using fallback generation")
            return self._generate_fallback_stream(news_articles)
        
        try:
            articles_text = ""
            for i, article in enumerate(news_articles, 1):
                articles_text += f"\n\nStory {i}:\n"
                articles_text += f"Title: {article['title']}\n"
                articles_text += f"Source: {article['source']}\n"
                articles_text += f"Summary: {article['description']}\n"
            
            prompt = f"""
            Create a {duration_minutes}-minute live news stream script for a 24/7 automated news channel.
            Anchor: {self.anchor_name}
            
            Available Stories:
            {articles_text}
            
            Structure the stream with:
            1. "stream_opening": Welcoming viewers to the live stream (2-3 sentences)
            2. "segments": A list of 4-6 news segments, each with:
               - "segment_number": Number (1, 2, 3, etc.)
               - "title": Segment title
               - "intro": Brief segment introduction (1 sentence)
               - "content": Full segment script (4-6 sentences)
               - "transition": Transition to next segment (1 sentence)
            3. "weather_sports": Brief weather and sports update section (3-4 sentences)
            4. "viewer_engagement": Call-to-action for viewers (2 sentences)
            5. "stream_closing": Closing statement (2-3 sentences)
            6. "loop_message": Message to play during stream loops (1 sentence)
            
            Make it professional, engaging, and suitable for continuous 24/7 broadcast.
            Return ONLY valid JSON.
            """
            
            response = self.model.generate_content(prompt)
            json_string = response.text.strip().replace("```json", "").replace("```", "")
            content = json.loads(json_string)
            
            print(f"✅ Live stream script generated!")
            return content
            
        except Exception as e:
            print(f"❌ ERROR: Failed to generate live stream script: {e}")
            return self._generate_fallback_stream(news_articles)
    
    def _generate_fallback_bulletin(self, news_articles, bulletin_type):
        """Generates a simple fallback bulletin when AI generation fails."""
        print("📰 Using fallback bulletin generation...")
        
        headlines = [article['title'] for article in news_articles[:5]]
        
        stories = []
        for article in news_articles[:3]:
            stories.append({
                "title": article['title'],
                "content": f"{article['description']} According to {article['source']}, this development continues to unfold.",
                "source": article['source']
            })
        
        return {
            "opening": f"Good day, I'm {self.anchor_name}. Here are today's top stories.",
            "headlines": headlines,
            "detailed_stories": stories,
            "closing": "That's all for now. Stay tuned for more updates.",
            "hashtags": "#News #Breaking #Updates #Live #Today",
            "short_highlight": headlines[0] if headlines else "Breaking news update."
        }
    
    def _generate_fallback_stream(self, news_articles):
        """Generates fallback stream content."""
        segments = []
        for i, article in enumerate(news_articles[:4], 1):
            segments.append({
                "segment_number": i,
                "title": article['title'],
                "intro": f"In our next story, {article['title']}.",
                "content": f"{article['description']} More details continue to emerge on this story.",
                "transition": "Now let's move to our next update."
            })
        
        return {
            "stream_opening": f"Welcome to our 24/7 news stream. I'm {self.anchor_name}.",
            "segments": segments,
            "weather_sports": "Weather and sports updates are available in our other segments.",
            "viewer_engagement": "Subscribe and turn on notifications for breaking news alerts.",
            "stream_closing": "Thank you for watching. We'll be back with more updates soon.",
            "loop_message": "This stream continues 24/7 with regular news updates."
        }
