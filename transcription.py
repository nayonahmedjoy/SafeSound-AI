"""
Speech-to-text transcription module using OpenAI Whisper
"""
import whisper
from pathlib import Path
from typing import List, Dict
from config import WHISPER_MODEL, WHISPER_LANGUAGE


class TranscriptionService:
    """Service for transcribing audio to text with word-level timestamps"""
    
    def __init__(self, model_name: str = WHISPER_MODEL):
        """
        Initialize the transcription service
        
        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large)
        """
        print(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        self.model_name = model_name
    
    def transcribe_with_timestamps(self, audio_path: Path) -> List[Dict]:
        """
        Transcribe audio file and return word-level timestamps
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of dictionaries with word, start, and end timestamps
            Format: [{"word": "hello", "start": 0.5, "end": 0.8}, ...]
        """
        print(f"Transcribing audio: {audio_path}")
        
        # Transcribe with word timestamps
        result = self.model.transcribe(
            str(audio_path),
            language=WHISPER_LANGUAGE,
            word_timestamps=True,
            verbose=False
        )
        
        # Extract word-level timestamps
        words = []
        for segment in result.get("segments", []):
            for word_info in segment.get("words", []):
                words.append({
                    "word": word_info["word"].strip().lower(),
                    "start": word_info["start"],
                    "end": word_info["end"]
                })
        
        print(f"Transcribed {len(words)} words")
        return words
    
    def get_full_transcript(self, audio_path: Path) -> str:
        """
        Get full transcript text without timestamps
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Full transcript as a string
        """
        result = self.model.transcribe(
            str(audio_path),
            language=WHISPER_LANGUAGE,
            verbose=False
        )
        return result.get("text", "")

