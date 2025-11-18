# FILE: src/video_generator.py
# Enhanced video generation with avatars, graphics, and transitions

import os
import requests
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json

class VideoGenerator:
    """
    Enhanced video generation with:
    - AI avatar integration (D-ID, Synthesia)
    - Dynamic news graphics
    - Lower-third graphics
    - Smooth transitions
    """
    
    def __init__(self, mode="standard"):
        """
        Initialize video generator.
        
        Args:
            mode: 'standard' (no avatar), 'avatar' (with AI avatar), or 'hybrid' (both)
        """
        self.mode = mode
        self.did_api_key = os.getenv('DID_API_KEY', '')
        self.synthesia_api_key = os.getenv('SYNTHESIA_API_KEY', '')
        
        if mode in ['avatar', 'hybrid']:
            if not self.did_api_key and not self.synthesia_api_key:
                print("⚠️ No avatar API keys found. Switching to standard mode.")
                self.mode = 'standard'
    
    def generate_lower_third(self, headline, ticker_text, width=1920, height=200):
        """
        Generate lower-third graphic with headline and ticker.
        
        Args:
            headline: Main headline text
            ticker_text: Scrolling ticker text
            width: Width in pixels
            height: Height in pixels
        
        Returns:
            PIL Image object
        """
        # Create semi-transparent background
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw background bar
        bar_height = height
        draw.rectangle([(0, 0), (width, bar_height)], fill=(0, 0, 139, 200))  # Dark blue with alpha
        
        # Draw accent line at top
        draw.rectangle([(0, 0), (width, 5)], fill=(255, 69, 0, 255))  # Red accent
        
        # Load font (use default if custom not available)
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            ticker_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except:
            title_font = ImageFont.load_default()
            ticker_font = ImageFont.load_default()
        
        # Draw headline
        headline_y = 20
        draw.text((30, headline_y), headline, font=title_font, fill=(255, 255, 255, 255))
        
        # Draw ticker
        ticker_y = height - 60
        draw.text((30, ticker_y), f"🔴 LIVE: {ticker_text}", font=ticker_font, fill=(255, 215, 0, 255))
        
        return img
    
    def create_news_background(self, category="general", width=1920, height=1080):
        """
        Create dynamic news background based on category.
        
        Args:
            category: News category for theme
            width: Width in pixels
            height: Height in pixels
        
        Returns:
            PIL Image object
        """
        # Category color themes
        themes = {
            'technology': (0, 100, 200),
            'business': (0, 128, 0),
            'sports': (255, 69, 0),
            'health': (32, 178, 170),
            'entertainment': (186, 85, 211),
            'science': (70, 130, 180),
            'general': (25, 25, 112)
        }
        
        base_color = themes.get(category, themes['general'])
        
        # Create gradient background
        img = Image.new('RGB', (width, height), base_color)
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for i in range(height):
            alpha = i / height
            color = tuple(int(c * (1 - alpha * 0.3)) for c in base_color)
            draw.rectangle([(0, i), (width, i + 1)], fill=color)
        
        # Add abstract shapes for visual interest
        for i in range(5):
            x = (i * width // 5) + 100
            y = height // 2
            radius = 150
            overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.ellipse(
                [(x - radius, y - radius), (x + radius, y + radius)],
                fill=(*base_color, 30)
            )
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        return img.convert('RGB')
    
    def generate_avatar_video(self, script, output_path, presenter_image=None):
        """
        Generate video with AI avatar using D-ID or Synthesia.
        
        Args:
            script: Text script for avatar to speak
            output_path: Path to save video
            presenter_image: Optional custom presenter image
        
        Returns:
            Path to generated video or None if failed
        """
        if self.did_api_key:
            return self._generate_did_avatar(script, output_path, presenter_image)
        elif self.synthesia_api_key:
            return self._generate_synthesia_avatar(script, output_path)
        else:
            print("⚠️ No avatar API available")
            return None
    
    def _generate_did_avatar(self, script, output_path, presenter_image=None):
        """Generate avatar video using D-ID API."""
        try:
            url = "https://api.d-id.com/talks"
            
            headers = {
                "Authorization": f"Basic {self.did_api_key}",
                "Content-Type": "application/json"
            }
            
            # Use default presenter or custom image
            presenter = presenter_image or "https://create-images-results.d-id.com/DefaultPresenters/Noelle_v1.png"
            
            payload = {
                "script": {
                    "type": "text",
                    "input": script,
                    "provider": {
                        "type": "microsoft",
                        "voice_id": "en-US-JennyNeural"
                    }
                },
                "source_url": presenter,
                "config": {
                    "result_format": "mp4"
                }
            }
            
            # Create talk
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            talk_id = response.json()['id']
            
            print(f"✅ D-ID avatar video created with ID: {talk_id}")
            print(f"   Check status at: https://studio.d-id.com/talks/{talk_id}")
            
            # Note: In production, you'd poll for completion and download the video
            # For now, return the talk ID as reference
            return talk_id
            
        except Exception as e:
            print(f"❌ ERROR: D-ID avatar generation failed: {e}")
            return None
    
    def _generate_synthesia_avatar(self, script, output_path):
        """Generate avatar video using Synthesia API."""
        try:
            url = "https://api.synthesia.io/v2/videos"
            
            headers = {
                "Authorization": f"Bearer {self.synthesia_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "test": False,
                "title": f"News Bulletin {datetime.now().strftime('%Y%m%d_%H%M')}",
                "input": [
                    {
                        "avatarSettings": {
                            "avatar": "anna_costume1_cameraA",
                            "style": "professional"
                        },
                        "scriptText": script,
                        "background": "news_studio"
                    }
                ]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            video_id = response.json()['id']
            
            print(f"✅ Synthesia avatar video created with ID: {video_id}")
            
            # Note: Poll for completion and download in production
            return video_id
            
        except Exception as e:
            print(f"❌ ERROR: Synthesia avatar generation failed: {e}")
            return None
    
    def add_transition_effect(self, clip1, clip2, transition_type="fade", duration=0.5):
        """
        Add transition effect between two video clips.
        
        Args:
            clip1: First video clip
            clip2: Second video clip
            transition_type: 'fade', 'wipe', 'slide', 'zoom'
            duration: Transition duration in seconds
        
        Returns:
            Combined clip with transition
        """
        # This would be implemented with moviepy's transition effects
        # For now, returning a simple concatenation
        try:
            from moviepy.editor import CompositeVideoClip, concatenate_videoclips
            from moviepy.video.fx import fadein, fadeout
            
            if transition_type == "fade":
                clip1 = clip1.fx(fadeout, duration)
                clip2 = clip2.fx(fadein, duration)
                return concatenate_videoclips([clip1, clip2], method="compose")
            else:
                return concatenate_videoclips([clip1, clip2])
                
        except Exception as e:
            print(f"⚠️ Transition effect failed: {e}")
            return concatenate_videoclips([clip1, clip2])
    
    def create_breaking_news_overlay(self, text, width=1920, height=1080):
        """
        Create breaking news banner overlay.
        
        Args:
            text: Breaking news text
            width: Width in pixels
            height: Height in pixels
        
        Returns:
            PIL Image with transparency
        """
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Red banner at top
        banner_height = 100
        draw.rectangle([(0, 0), (width, banner_height)], fill=(220, 20, 60, 255))
        
        # Flashing "BREAKING NEWS" text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
        except:
            font = ImageFont.load_default()
        
        # Add text
        draw.text((30, 20), "🔴 BREAKING NEWS", font=font, fill=(255, 255, 255, 255))
        draw.text((width // 3, 20), text[:50], font=font, fill=(255, 255, 255, 255))
        
        return img
