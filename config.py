"""
Configuration file for Video Profanity Detection & Auto-Beep System
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# File upload settings
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".m4v"}

# Audio/Video processing settings
AUDIO_SAMPLE_RATE = 44100
BEEP_FREQUENCY = 1000  # Hz
BEEP_DURATION_PADDING = 0.05  # Add 50ms padding before/after beep for smooth transition

# Profanity word list (YouTube-safe level)
PROFANITY_WORDS = [
    "fuck", "fucking", "fucked", "fucker",
    "shit", "shitting", "shitted",
    "ass", "asshole", "asses",
    "bitch", "bitches", "bitching",
    "damn", "damned", "damnit",
    "hell", "hells",
    "crap", "crappy",
    "piss", "pissing", "pissed",
    "dick", "dicks",
    "cock", "cocks",
    "pussy", "pussies",
    "bastard", "bastards",
    "whore", "whores",
    "slut", "sluts",
    "cunt", "cunts",
    "motherfucker", "motherfuckers",
    "bullshit",
    "goddamn", "goddamnit",
    "faggot", "faggots",
    "nigger", "niggers",  # Note: This is for detection/censoring, not endorsement
    "retard", "retarded",
]

# Speech recognition settings
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
WHISPER_LANGUAGE = None  # None = auto-detect

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000

