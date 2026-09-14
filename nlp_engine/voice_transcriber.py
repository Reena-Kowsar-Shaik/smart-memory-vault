"""
nlp_engine/voice_transcriber.py
Voice transcription intelligence for Smart Memory Vault using speech recognition.
Supports direct audio stream decoding and Google Web Speech API transcription.
"""

import io
import speech_recognition as sr
from typing import Dict, Any, Union


class VoiceTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Fine tune energy threshold and dynamic adjustments
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    def transcribe(self, audio_source: Union[bytes, io.BytesIO, Any], language: str = "en-US") -> Dict[str, Any]:
        """
        Transcribe audio input (BytesIO, bytes, or Streamlit UploadedFile) to text.
        Returns a dictionary with status, transcribed text, or descriptive error.
        """
        if audio_source is None:
            return {"success": False, "text": "", "error": "No audio input provided."}

        try:
            # Extract raw bytes
            if hasattr(audio_source, "getvalue"):
                raw_bytes = audio_source.getvalue()
            elif isinstance(audio_source, bytes):
                raw_bytes = audio_source
            elif hasattr(audio_source, "read"):
                raw_bytes = audio_source.read()
            else:
                raw_bytes = bytes(audio_source)

            if not raw_bytes or len(raw_bytes) < 100:
                return {
                    "success": False,
                    "text": "",
                    "error": "Audio recording is empty or too short. Please speak clearly into the microphone."
                }

            with io.BytesIO(raw_bytes) as audio_file:
                with sr.AudioFile(audio_file) as source:
                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data, language=language)
                    return {
                        "success": True,
                        "text": text.strip(),
                        "error": None
                    }

        except sr.UnknownValueError:
            # Try alternate English locales (e.g. en-IN, en-GB, en)
            for alt_lang in ["en-IN", "en-GB", "en-US", "en"]:
                if alt_lang == language:
                    continue
                try:
                    with io.BytesIO(raw_bytes) as audio_file:
                        with sr.AudioFile(audio_file) as source:
                            audio_data = self.recognizer.record(source)
                            text = self.recognizer.recognize_google(audio_data, language=alt_lang)
                            if text and text.strip():
                                return {
                                    "success": True,
                                    "text": text.strip(),
                                    "error": None
                                }
                except Exception:
                    continue

            return {
                "success": False,
                "text": "",
                "error": "No clear speech recognized. Please speak into the mic and try again."
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "text": "",
                "error": f"Speech recognition service unavailable ({e}). Please check your internet connection."
            }
        except Exception as e:
            # If standard wav header issue or unsupported format
            return {
                "success": False,
                "text": "",
                "error": f"Audio parsing error: {str(e)}"
            }


# Singleton instance
voice_transcriber = VoiceTranscriber()
