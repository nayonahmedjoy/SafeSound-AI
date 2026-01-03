"""
Profanity detection module
"""
import re
from typing import List, Dict, Tuple
from config import PROFANITY_WORDS


class ProfanityDetector:
    """Detects profane words in transcribed text with timestamps"""
    
    def __init__(self, profanity_list: List[str] = None):
        """
        Initialize profanity detector
        
        Args:
            profanity_list: Custom list of profanity words. If None, uses default list.
        """
        self.profanity_words = set(profanity_list or PROFANITY_WORDS)
        # Create regex pattern for word boundaries to avoid partial matches
        # This ensures we match whole words only
        pattern_parts = [re.escape(word) for word in self.profanity_words]
        self.pattern = re.compile(
            r'\b(' + '|'.join(pattern_parts) + r')\b',
            re.IGNORECASE
        )
    
    def detect_profanities(self, words_with_timestamps: List[Dict]) -> List[Tuple[float, float, str]]:
        """
        Detect profane words in transcribed text with timestamps
        
        Args:
            words_with_timestamps: List of dicts with "word", "start", "end" keys
            
        Returns:
            List of tuples: (start_time, end_time, word)
            Sorted by start time
        """
        detected = []
        
        for word_info in words_with_timestamps:
            word = word_info["word"].lower().strip()
            # Remove punctuation for matching
            word_clean = re.sub(r'[^\w]', '', word)
            
            # Check if word matches any profanity
            if word_clean in self.profanity_words:
                detected.append((
                    word_info["start"],
                    word_info["end"],
                    word_clean
                ))
        
        # Sort by start time
        detected.sort(key=lambda x: x[0])
        
        return detected
    
    def add_profanity_word(self, word: str) -> None:
        """
        Add a word to the profanity list
        
        Args:
            word: Word to add
        """
        self.profanity_words.add(word.lower())
        # Rebuild pattern
        pattern_parts = [re.escape(w) for w in self.profanity_words]
        self.pattern = re.compile(
            r'\b(' + '|'.join(pattern_parts) + r')\b',
            re.IGNORECASE
        )
    
    def remove_profanity_word(self, word: str) -> None:
        """
        Remove a word from the profanity list
        
        Args:
            word: Word to remove
        """
        self.profanity_words.discard(word.lower())
        # Rebuild pattern
        pattern_parts = [re.escape(w) for w in self.profanity_words]
        self.pattern = re.compile(
            r'\b(' + '|'.join(pattern_parts) + r')\b',
            re.IGNORECASE
        )
    
    def get_profanity_list(self) -> List[str]:
        """
        Get current profanity word list
        
        Returns:
            Sorted list of profanity words
        """
        return sorted(list(self.profanity_words))

