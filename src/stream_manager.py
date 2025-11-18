# FILE: src/stream_manager.py
# 24/7 Live streaming manager with health monitoring and auto-reconnection

import os
import subprocess
import time
import signal
from pathlib import Path
from datetime import datetime
import requests

class StreamManager:
    """
    Manages 24/7 YouTube Live streaming with:
    - RTMP streaming via FFmpeg
    - Stream health monitoring
    - Auto-reconnection on failure
    - Stream key security
    """
    
    def __init__(self):
        self.stream_process = None
        self.stream_url = None
        self.stream_key = None
        self.is_streaming = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
    
    def setup_stream(self, stream_url, stream_key):
        """
        Setup stream configuration.
        
        Args:
            stream_url: RTMP stream URL from YouTube
            stream_key: Stream key from YouTube
        """
        self.stream_url = stream_url
        self.stream_key = stream_key
        print(f"✅ Stream configured: {stream_url[:30]}...")
    
    def start_stream(self, video_source, audio_source=None, loop=True):
        """
        Start RTMP streaming to YouTube Live.
        
        Args:
            video_source: Path to video file or 'camera' for webcam
            audio_source: Path to audio file or None
            loop: Whether to loop the video indefinitely
        
        Returns:
            True if stream started successfully
        """
        if not self.stream_url or not self.stream_key:
            print("❌ Stream not configured. Call setup_stream() first.")
            return False
        
        try:
            # Build FFmpeg command
            cmd = self._build_ffmpeg_command(video_source, audio_source, loop)
            
            print(f"🔴 Starting RTMP stream...")
            print(f"   Video source: {video_source}")
            if audio_source:
                print(f"   Audio source: {audio_source}")
            
            # Start FFmpeg process
            self.stream_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            self.is_streaming = True
            self.reconnect_attempts = 0
            
            print(f"✅ Stream started! PID: {self.stream_process.pid}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to start stream: {e}")
            return False
    
    def _build_ffmpeg_command(self, video_source, audio_source, loop):
        """Build FFmpeg command for streaming."""
        cmd = ['ffmpeg']
        
        # Input options
        if loop:
            cmd.extend(['-re', '-stream_loop', '-1'])
        else:
            cmd.append('-re')
        
        # Video input
        if video_source == 'camera':
            cmd.extend(['-f', 'v4l2', '-i', '/dev/video0'])
        else:
            cmd.extend(['-i', str(video_source)])
        
        # Audio input
        if audio_source:
            cmd.extend(['-i', str(audio_source)])
        
        # Video encoding
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-b:v', '3000k',
            '-maxrate', '3000k',
            '-bufsize', '6000k',
            '-pix_fmt', 'yuv420p',
            '-g', '50',
            '-r', '30'
        ])
        
        # Audio encoding
        cmd.extend([
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '44100'
        ])
        
        # Output format
        cmd.extend([
            '-f', 'flv',
            f'{self.stream_url}/{self.stream_key}'
        ])
        
        return cmd
    
    def stop_stream(self):
        """Stop the streaming process."""
        if self.stream_process:
            try:
                print("⏹️ Stopping stream...")
                self.stream_process.send_signal(signal.SIGTERM)
                self.stream_process.wait(timeout=5)
                print("✅ Stream stopped")
            except subprocess.TimeoutExpired:
                print("⚠️ Stream didn't stop gracefully, forcing...")
                self.stream_process.kill()
            except Exception as e:
                print(f"❌ ERROR stopping stream: {e}")
            finally:
                self.stream_process = None
                self.is_streaming = False
    
    def check_stream_health(self):
        """
        Check if stream is healthy.
        
        Returns:
            True if stream is running and healthy
        """
        if not self.stream_process:
            return False
        
        # Check if process is still running
        poll = self.stream_process.poll()
        if poll is not None:
            print(f"⚠️ Stream process exited with code {poll}")
            self.is_streaming = False
            return False
        
        # Check stderr for errors
        try:
            stderr = self.stream_process.stderr.read(1024).decode('utf-8', errors='ignore')
            if 'error' in stderr.lower() or 'failed' in stderr.lower():
                print(f"⚠️ Stream error detected: {stderr[:100]}")
                return False
        except:
            pass
        
        return True
    
    def auto_reconnect(self, video_source, audio_source=None):
        """
        Automatically reconnect stream if it fails.
        
        Args:
            video_source: Video source for streaming
            audio_source: Optional audio source
        
        Returns:
            True if reconnection successful
        """
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"❌ Max reconnection attempts ({self.max_reconnect_attempts}) reached")
            return False
        
        self.reconnect_attempts += 1
        print(f"🔄 Attempting to reconnect (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})...")
        
        # Stop existing stream
        if self.stream_process:
            self.stop_stream()
        
        # Wait before reconnecting
        wait_time = min(30 * self.reconnect_attempts, 300)  # Max 5 minutes
        print(f"⏳ Waiting {wait_time} seconds before reconnect...")
        time.sleep(wait_time)
        
        # Try to restart
        return self.start_stream(video_source, audio_source)
    
    def monitor_stream(self, video_source, audio_source=None, check_interval=30):
        """
        Continuously monitor stream and reconnect if needed.
        
        Args:
            video_source: Video source for streaming
            audio_source: Optional audio source
            check_interval: Seconds between health checks
        """
        print(f"👁️ Starting stream monitoring (checking every {check_interval}s)...")
        
        try:
            while True:
                if not self.is_streaming:
                    print("⚠️ Stream not active, starting...")
                    self.start_stream(video_source, audio_source)
                
                # Wait before checking
                time.sleep(check_interval)
                
                # Check health
                if not self.check_stream_health():
                    print("⚠️ Stream unhealthy, attempting reconnection...")
                    self.auto_reconnect(video_source, audio_source)
                else:
                    # Reset reconnect counter on successful check
                    if self.reconnect_attempts > 0:
                        print(f"✅ Stream recovered! Resetting reconnect counter.")
                        self.reconnect_attempts = 0
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            self.stop_stream()
    
    def get_stream_stats(self):
        """Get current stream statistics."""
        return {
            'is_streaming': self.is_streaming,
            'process_id': self.stream_process.pid if self.stream_process else None,
            'reconnect_attempts': self.reconnect_attempts,
            'stream_url': self.stream_url[:30] + '...' if self.stream_url else None
        }
    
    def create_test_video(self, output_path, duration=60):
        """
        Create a test video for streaming.
        
        Args:
            output_path: Path to save test video
            duration: Duration in seconds
        """
        try:
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c=blue:s=1920x1080:d={duration}',
                '-vf', f'drawtext=text=\'24/7 News Stream - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
                '-pix_fmt', 'yuv420p',
                '-y',
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Test video created: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR creating test video: {e}")
            return False
