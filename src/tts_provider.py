# FILE: src/tts_provider.py
# Text-to-Speech provider abstraction with multiple backend support

import os
from pathlib import Path
from gtts import gTTS

class TTSProvider:
    """
    Text-to-Speech provider supporting multiple backends:
    - gTTS (Google TTS) - Free, basic
    - ElevenLabs - Premium, natural voices
    - Google Cloud TTS - Enterprise, multi-language
    - Azure Speech - Enterprise, voice modulation
    """
    
    def __init__(self, provider="gtts"):
        """
        Initialize TTS provider.
        
        Args:
            provider: 'gtts', 'elevenlabs', 'google_cloud', or 'azure'
        """
        self.provider = provider.lower()
        self.supported_providers = ['gtts', 'elevenlabs', 'google_cloud', 'azure']
        
        if self.provider not in self.supported_providers:
            print(f"⚠️ Unknown provider '{provider}', falling back to gTTS")
            self.provider = 'gtts'
        
        # Initialize provider-specific settings
        self._init_provider()
    
    def _init_provider(self):
        """Initialize provider-specific configuration."""
        if self.provider == 'elevenlabs':
            self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY', '')
            self.elevenlabs_voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'default')
            if not self.elevenlabs_api_key:
                print("⚠️ ELEVENLABS_API_KEY not found, falling back to gTTS")
                self.provider = 'gtts'
        
        elif self.provider == 'google_cloud':
            self.google_cloud_key = os.getenv('GOOGLE_CLOUD_TTS_KEY', '')
            if not self.google_cloud_key:
                print("⚠️ GOOGLE_CLOUD_TTS_KEY not found, falling back to gTTS")
                self.provider = 'gtts'
        
        elif self.provider == 'azure':
            self.azure_key = os.getenv('AZURE_SPEECH_KEY', '')
            self.azure_region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
            if not self.azure_key:
                print("⚠️ AZURE_SPEECH_KEY not found, falling back to gTTS")
                self.provider = 'gtts'
    
    def synthesize(self, text, output_path, language='en', emotion=None):
        """
        Synthesize speech from text.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            language: Language code (e.g., 'en', 'es', 'fr')
            emotion: Optional emotion for voice modulation ('neutral', 'excited', 'serious')
        
        Returns:
            Path to generated audio file
        """
        output_path = Path(output_path)
        
        if self.provider == 'gtts':
            return self._synthesize_gtts(text, output_path, language)
        elif self.provider == 'elevenlabs':
            return self._synthesize_elevenlabs(text, output_path, emotion)
        elif self.provider == 'google_cloud':
            return self._synthesize_google_cloud(text, output_path, language, emotion)
        elif self.provider == 'azure':
            return self._synthesize_azure(text, output_path, language, emotion)
        
        # Fallback
        return self._synthesize_gtts(text, output_path, language)
    
    def _synthesize_gtts(self, text, output_path, language):
        """Synthesize using Google TTS (gTTS)."""
        try:
            mp3_path = str(output_path.with_suffix('.mp3'))
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(mp3_path)
            print(f"✅ Speech generated with gTTS")
            return Path(mp3_path)
        except Exception as e:
            print(f"❌ ERROR: gTTS synthesis failed: {e}")
            raise
    
    def _synthesize_elevenlabs(self, text, output_path, emotion=None):
        """Synthesize using ElevenLabs API."""
        try:
            import requests
            
            # ElevenLabs API endpoint
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # Voice settings with emotion
            stability = 0.5
            similarity_boost = 0.75
            
            if emotion == 'excited':
                stability = 0.3
                similarity_boost = 0.9
            elif emotion == 'serious':
                stability = 0.8
                similarity_boost = 0.6
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            mp3_path = str(output_path.with_suffix('.mp3'))
            with open(mp3_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Speech generated with ElevenLabs")
            return Path(mp3_path)
            
        except Exception as e:
            print(f"❌ ERROR: ElevenLabs synthesis failed: {e}")
            print("   Falling back to gTTS...")
            return self._synthesize_gtts(text, output_path, 'en')
    
    def _synthesize_google_cloud(self, text, output_path, language, emotion=None):
        """Synthesize using Google Cloud Text-to-Speech."""
        try:
            from google.cloud import texttospeech
            
            client = texttospeech.TextToSpeechClient()
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Select voice based on language
            voice = texttospeech.VoiceSelectionParams(
                language_code=language,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Audio config
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0
            )
            
            # Adjust parameters based on emotion
            if emotion == 'excited':
                audio_config.speaking_rate = 1.1
                audio_config.pitch = 2.0
            elif emotion == 'serious':
                audio_config.speaking_rate = 0.9
                audio_config.pitch = -2.0
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            mp3_path = str(output_path.with_suffix('.mp3'))
            with open(mp3_path, 'wb') as f:
                f.write(response.audio_content)
            
            print(f"✅ Speech generated with Google Cloud TTS")
            return Path(mp3_path)
            
        except Exception as e:
            print(f"❌ ERROR: Google Cloud TTS synthesis failed: {e}")
            print("   Falling back to gTTS...")
            return self._synthesize_gtts(text, output_path, language)
    
    def _synthesize_azure(self, text, output_path, language, emotion=None):
        """Synthesize using Azure Cognitive Services Speech."""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_key,
                region=self.azure_region
            )
            
            # Set voice based on language
            voice_map = {
                'en': 'en-US-JennyNeural',
                'es': 'es-ES-ElviraNeural',
                'fr': 'fr-FR-DeniseNeural'
            }
            speech_config.speech_synthesis_voice_name = voice_map.get(language, 'en-US-JennyNeural')
            
            mp3_path = str(output_path.with_suffix('.mp3'))
            audio_config = speechsdk.audio.AudioOutputConfig(filename=mp3_path)
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Add SSML for emotion if specified
            if emotion:
                ssml_text = f"""
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">
                    <voice name="{speech_config.speech_synthesis_voice_name}">
                        <prosody rate="1.0" pitch="0%">
                            {text}
                        </prosody>
                    </voice>
                </speak>
                """
                result = synthesizer.speak_ssml_async(ssml_text).get()
            else:
                result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"✅ Speech generated with Azure TTS")
                return Path(mp3_path)
            else:
                raise Exception(f"Azure synthesis failed: {result.reason}")
            
        except Exception as e:
            print(f"❌ ERROR: Azure TTS synthesis failed: {e}")
            print("   Falling back to gTTS...")
            return self._synthesize_gtts(text, output_path, language)
    
    def get_available_voices(self):
        """Get list of available voices for current provider."""
        if self.provider == 'gtts':
            return ['default']
        elif self.provider == 'elevenlabs':
            # In production, would query ElevenLabs API for voice list
            return ['default', 'custom']
        elif self.provider == 'google_cloud':
            return ['en-US-Neural', 'en-GB-Neural', 'es-ES-Neural']
        elif self.provider == 'azure':
            return ['JennyNeural', 'GuyNeural', 'AriaNeural']
        return ['default']
