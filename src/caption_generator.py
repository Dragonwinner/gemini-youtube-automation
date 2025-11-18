# FILE: src/caption_generator.py
# Automatic caption/subtitle generation for videos

import os
import subprocess
from pathlib import Path
from datetime import timedelta
import json

class CaptionGenerator:
    """
    Generates captions/subtitles for videos:
    - From existing transcripts
    - Using speech recognition
    - Multiple formats (SRT, VTT, JSON)
    """
    
    def __init__(self):
        self.whisper_available = self._check_whisper()
    
    def _check_whisper(self):
        """Check if Whisper is available for transcription."""
        try:
            import whisper
            return True
        except ImportError:
            return False
    
    def generate_from_script(self, script, output_path, format='srt', duration=None):
        """
        Generate captions from a text script.
        
        Args:
            script: Text script
            output_path: Path to save caption file
            format: Caption format ('srt', 'vtt', 'json')
            duration: Optional video duration to distribute text
        
        Returns:
            Path to generated caption file
        """
        # Split script into sentences
        sentences = self._split_into_sentences(script)
        
        # Calculate timing for each sentence
        if duration:
            time_per_sentence = duration / len(sentences)
        else:
            # Estimate: ~3 seconds per sentence
            time_per_sentence = 3.0
        
        # Create caption entries
        captions = []
        current_time = 0.0
        
        for i, sentence in enumerate(sentences):
            start_time = current_time
            end_time = current_time + time_per_sentence
            
            captions.append({
                'index': i + 1,
                'start': start_time,
                'end': end_time,
                'text': sentence.strip()
            })
            
            current_time = end_time
        
        # Write to file in requested format
        output_path = Path(output_path)
        
        if format == 'srt':
            return self._write_srt(captions, output_path)
        elif format == 'vtt':
            return self._write_vtt(captions, output_path)
        elif format == 'json':
            return self._write_json(captions, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _split_into_sentences(self, text):
        """Split text into sentences."""
        import re
        
        # Simple sentence splitter
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _format_time_srt(self, seconds):
        """Format time for SRT format (HH:MM:SS,mmm)."""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_time_vtt(self, seconds):
        """Format time for VTT format (HH:MM:SS.mmm)."""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def _write_srt(self, captions, output_path):
        """Write captions in SRT format."""
        output_path = output_path.with_suffix('.srt')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for caption in captions:
                f.write(f"{caption['index']}\n")
                f.write(f"{self._format_time_srt(caption['start'])} --> {self._format_time_srt(caption['end'])}\n")
                f.write(f"{caption['text']}\n\n")
        
        print(f"✅ SRT captions generated: {output_path}")
        return output_path
    
    def _write_vtt(self, captions, output_path):
        """Write captions in WebVTT format."""
        output_path = output_path.with_suffix('.vtt')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for caption in captions:
                f.write(f"{self._format_time_vtt(caption['start'])} --> {self._format_time_vtt(caption['end'])}\n")
                f.write(f"{caption['text']}\n\n")
        
        print(f"✅ VTT captions generated: {output_path}")
        return output_path
    
    def _write_json(self, captions, output_path):
        """Write captions in JSON format."""
        output_path = output_path.with_suffix('.json')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(captions, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON captions generated: {output_path}")
        return output_path
    
    def generate_from_audio(self, audio_path, output_path, format='srt', language='en'):
        """
        Generate captions from audio using speech recognition.
        Requires Whisper library.
        
        Args:
            audio_path: Path to audio file
            output_path: Path to save caption file
            format: Caption format ('srt', 'vtt', 'json')
            language: Language code
        
        Returns:
            Path to generated caption file or None
        """
        if not self.whisper_available:
            print("⚠️ Whisper not available. Install with: pip install openai-whisper")
            return None
        
        try:
            import whisper
            
            print(f"🎤 Transcribing audio: {audio_path}")
            
            # Load Whisper model (small is good balance of speed/accuracy)
            model = whisper.load_model("base")
            
            # Transcribe
            result = model.transcribe(str(audio_path), language=language)
            
            # Convert segments to captions
            captions = []
            for i, segment in enumerate(result['segments']):
                captions.append({
                    'index': i + 1,
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip()
                })
            
            # Write to file
            if format == 'srt':
                return self._write_srt(captions, output_path)
            elif format == 'vtt':
                return self._write_vtt(captions, output_path)
            elif format == 'json':
                return self._write_json(captions, output_path)
            
        except Exception as e:
            print(f"❌ Error generating captions from audio: {e}")
            return None
    
    def upload_to_youtube(self, video_id, caption_file, language='en', name='English'):
        """
        Upload captions to YouTube video.
        Requires YouTube API credentials.
        
        Args:
            video_id: YouTube video ID
            caption_file: Path to caption file (SRT or VTT)
            language: Language code
            name: Caption track name
        
        Returns:
            True if successful
        """
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.oauth2.credentials import Credentials
            
            # Authenticate
            credentials = Credentials.from_authorized_user_file(
                'credentials.json',
                ['https://www.googleapis.com/auth/youtube.force-ssl']
            )
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Upload caption
            media = MediaFileUpload(str(caption_file), mimetype='application/octet-stream')
            
            request = youtube.captions().insert(
                part='snippet',
                body={
                    'snippet': {
                        'videoId': video_id,
                        'language': language,
                        'name': name,
                        'isDraft': False
                    }
                },
                media_body=media
            )
            
            response = request.execute()
            
            print(f"✅ Captions uploaded to video {video_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading captions: {e}")
            return False
    
    def translate_captions(self, caption_file, target_languages=None):
        """
        Translate captions to multiple languages.
        Uses Google Translate API.
        
        Args:
            caption_file: Path to original caption file
            target_languages: List of target language codes
        
        Returns:
            Dict of language: caption_file_path
        """
        if target_languages is None:
            target_languages = ['es', 'fr', 'de']  # Spanish, French, German
        
        try:
            from googletrans import Translator
            
            translator = Translator()
            
            # Load original captions
            with open(caption_file, 'r', encoding='utf-8') as f:
                if caption_file.suffix == '.json':
                    captions = json.load(f)
                else:
                    # Parse SRT/VTT
                    captions = self._parse_caption_file(caption_file)
            
            translated_files = {}
            
            for lang in target_languages:
                print(f"🌐 Translating to {lang}...")
                
                translated_captions = []
                for caption in captions:
                    translated_text = translator.translate(
                        caption['text'],
                        dest=lang
                    ).text
                    
                    translated_captions.append({
                        **caption,
                        'text': translated_text
                    })
                
                # Save translated file
                output_path = caption_file.parent / f"{caption_file.stem}_{lang}{caption_file.suffix}"
                
                if caption_file.suffix == '.srt':
                    self._write_srt(translated_captions, output_path)
                elif caption_file.suffix == '.vtt':
                    self._write_vtt(translated_captions, output_path)
                else:
                    self._write_json(translated_captions, output_path)
                
                translated_files[lang] = output_path
            
            return translated_files
            
        except ImportError:
            print("⚠️ googletrans not available. Install with: pip install googletrans==4.0.0-rc1")
            return {}
        except Exception as e:
            print(f"❌ Error translating captions: {e}")
            return {}
    
    def _parse_caption_file(self, caption_file):
        """Parse SRT/VTT caption file into list of dicts."""
        # Simplified parser - would need more robust implementation
        captions = []
        # Implementation would parse the file format
        return captions
