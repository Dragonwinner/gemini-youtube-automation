# FILE: src/live_streamer.py
# YouTube Live Streaming module for 24/7 automated news broadcast

import os
from datetime import datetime, timedelta
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

CREDENTIALS_FILE = Path('credentials.json')
YOUTUBE_UPLOAD_SCOPE = ["https://www.googleapis.com/auth/youtube.upload",
                        "https://www.googleapis.com/auth/youtube"]


class LiveStreamer:
    """Manages YouTube Live Streaming for 24/7 news broadcast."""
    
    def __init__(self):
        self.youtube = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticates with YouTube API."""
        try:
            if CREDENTIALS_FILE.exists():
                credentials = Credentials.from_authorized_user_file(
                    str(CREDENTIALS_FILE), 
                    YOUTUBE_UPLOAD_SCOPE
                )
                
                if credentials and credentials.expired and credentials.refresh_token:
                    print("INFO: Refreshing credentials for live streaming...")
                    credentials.refresh(Request())
                
                self.youtube = build('youtube', 'v3', credentials=credentials)
                print("✅ YouTube Live Streaming API authenticated")
            else:
                print("❌ Credentials file not found for live streaming")
                
        except Exception as e:
            print(f"❌ ERROR: Failed to authenticate for live streaming: {e}")
    
    def create_live_broadcast(self, title, description, scheduled_start_time=None):
        """
        Creates a YouTube Live Broadcast.
        
        scheduled_start_time: datetime object or None for immediate start
        """
        if not self.youtube:
            print("❌ YouTube API not authenticated")
            return None
        
        try:
            print(f"📺 Creating live broadcast: {title}")
            
            # If no scheduled time, start immediately
            if scheduled_start_time is None:
                scheduled_start_time = datetime.utcnow()
            
            # Ensure scheduled_start_time is in ISO format
            if isinstance(scheduled_start_time, datetime):
                scheduled_start_time = scheduled_start_time.isoformat() + 'Z'
            
            broadcast_body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'scheduledStartTime': scheduled_start_time
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                },
                'contentDetails': {
                    'enableAutoStart': True,
                    'enableAutoStop': False,
                    'enableDvr': True,
                    'enableContentEncryption': False,
                    'enableEmbed': True,
                    'recordFromStart': True
                }
            }
            
            broadcast = self.youtube.liveBroadcasts().insert(
                part='snippet,status,contentDetails',
                body=broadcast_body
            ).execute()
            
            broadcast_id = broadcast['id']
            print(f"✅ Live broadcast created! ID: {broadcast_id}")
            
            return broadcast_id
            
        except Exception as e:
            print(f"❌ ERROR: Failed to create live broadcast: {e}")
            return None
    
    def create_live_stream(self, title):
        """
        Creates a YouTube Live Stream (the technical stream endpoint).
        """
        if not self.youtube:
            return None
        
        try:
            print(f"🔴 Creating live stream: {title}")
            
            stream_body = {
                'snippet': {
                    'title': title
                },
                'cdn': {
                    'frameRate': '30fps',
                    'ingestionType': 'rtmp',
                    'resolution': '1080p'
                }
            }
            
            stream = self.youtube.liveStreams().insert(
                part='snippet,cdn',
                body=stream_body
            ).execute()
            
            stream_id = stream['id']
            stream_key = stream['cdn']['ingestionInfo']['streamName']
            ingestion_address = stream['cdn']['ingestionInfo']['ingestionAddress']
            
            print(f"✅ Live stream created! ID: {stream_id}")
            print(f"🔑 Stream Key: {stream_key[:10]}...") # Don't log full key
            
            return {
                'stream_id': stream_id,
                'stream_key': stream_key,
                'ingestion_address': ingestion_address
            }
            
        except Exception as e:
            print(f"❌ ERROR: Failed to create live stream: {e}")
            return None
    
    def bind_broadcast_to_stream(self, broadcast_id, stream_id):
        """
        Binds a broadcast to a stream (connects them together).
        """
        if not self.youtube:
            return False
        
        try:
            print(f"🔗 Binding broadcast {broadcast_id} to stream {stream_id}")
            
            self.youtube.liveBroadcasts().bind(
                part='id,contentDetails',
                id=broadcast_id,
                streamId=stream_id
            ).execute()
            
            print(f"✅ Broadcast bound to stream successfully!")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to bind broadcast to stream: {e}")
            return False
    
    def start_broadcast(self, broadcast_id):
        """
        Transitions broadcast to 'live' state.
        """
        if not self.youtube:
            return False
        
        try:
            print(f"▶️ Starting live broadcast: {broadcast_id}")
            
            self.youtube.liveBroadcasts().transition(
                broadcastStatus='live',
                id=broadcast_id,
                part='status'
            ).execute()
            
            print(f"✅ Broadcast is now LIVE!")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to start broadcast: {e}")
            return False
    
    def end_broadcast(self, broadcast_id):
        """
        Ends a live broadcast.
        """
        if not self.youtube:
            return False
        
        try:
            print(f"⏹️ Ending live broadcast: {broadcast_id}")
            
            self.youtube.liveBroadcasts().transition(
                broadcastStatus='complete',
                id=broadcast_id,
                part='status'
            ).execute()
            
            print(f"✅ Broadcast ended successfully!")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to end broadcast: {e}")
            return False
    
    def setup_24x7_stream(self, channel_name="24/7 News Live"):
        """
        Sets up a continuous 24/7 live stream.
        Returns stream configuration for use with streaming software.
        """
        print(f"🚀 Setting up 24/7 live stream: {channel_name}")
        
        # Create broadcast
        title = f"{channel_name} - {datetime.utcnow().strftime('%B %d, %Y')}"
        description = f"""
🔴 LIVE 24/7 News Coverage

Welcome to our continuous news broadcast. We bring you the latest updates around the clock.

📰 Breaking News
🌍 World Updates  
💼 Business News
🔬 Technology & Science
⚡ Live Updates

Subscribe and turn on notifications 🔔 to never miss breaking news!

#LiveNews #Breaking #24x7 #NewsChannel #Updates
"""
        
        broadcast_id = self.create_live_broadcast(title, description)
        if not broadcast_id:
            return None
        
        # Create stream
        stream_info = self.create_live_stream(f"{channel_name} Stream")
        if not stream_info:
            return None
        
        # Bind broadcast to stream
        if not self.bind_broadcast_to_stream(broadcast_id, stream_info['stream_id']):
            return None
        
        result = {
            'broadcast_id': broadcast_id,
            'stream_id': stream_info['stream_id'],
            'stream_key': stream_info['stream_key'],
            'rtmp_url': stream_info['ingestion_address'],
            'youtube_watch_url': f"https://www.youtube.com/watch?v={broadcast_id}",
            'status': 'ready'
        }
        
        print(f"✅ 24/7 Stream setup complete!")
        print(f"🔗 Watch URL: {result['youtube_watch_url']}")
        
        return result
    
    def get_active_broadcasts(self):
        """
        Gets list of currently active broadcasts.
        """
        if not self.youtube:
            return []
        
        try:
            response = self.youtube.liveBroadcasts().list(
                part='id,snippet,status',
                broadcastStatus='active',
                maxResults=10
            ).execute()
            
            broadcasts = response.get('items', [])
            print(f"📺 Found {len(broadcasts)} active broadcast(s)")
            return broadcasts
            
        except Exception as e:
            print(f"❌ ERROR: Failed to get active broadcasts: {e}")
            return []
