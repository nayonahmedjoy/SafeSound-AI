"""
Audio processing module for extraction and manipulation
"""
import subprocess
from pathlib import Path
from typing import Optional
from pydub import AudioSegment
from pydub.effects import normalize
import numpy as np
from config import TEMP_DIR, AUDIO_SAMPLE_RATE, BEEP_FREQUENCY, BEEP_DURATION_PADDING


def extract_audio_from_video(video_path: Path, output_audio_path: Optional[Path] = None) -> Path:
    """
    Extract audio track from video file using FFmpeg
    
    Args:
        video_path: Path to the input video file
        output_audio_path: Optional path for output audio file
        
    Returns:
        Path to the extracted audio file
    """
    if output_audio_path is None:
        output_audio_path = TEMP_DIR / f"{video_path.stem}_audio.wav"
    
    # Use FFmpeg to extract audio
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # PCM 16-bit little-endian
        "-ar", str(AUDIO_SAMPLE_RATE),  # Sample rate
        "-ac", "2",  # Stereo
        "-y",  # Overwrite output file
        str(output_audio_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return output_audio_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to extract audio: {e.stderr}")


def generate_beep(duration_ms: float, frequency: int = BEEP_FREQUENCY, sample_rate: int = AUDIO_SAMPLE_RATE) -> AudioSegment:
    """
    Generate a beep sound of specified duration
    
    Args:
        duration_ms: Duration in milliseconds
        frequency: Frequency of the beep in Hz
        sample_rate: Audio sample rate
        
    Returns:
        AudioSegment containing the beep sound
    """
    # Generate sine wave
    t = np.linspace(0, duration_ms / 1000.0, int(sample_rate * duration_ms / 1000.0), False)
    wave = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit PCM
    wave_normalized = np.int16(wave * 32767 * 0.7)  # 70% volume
    
    # Create stereo audio (same signal on both channels)
    stereo_wave = np.array([wave_normalized, wave_normalized]).T
    
    # Create AudioSegment
    beep = AudioSegment(
        stereo_wave.tobytes(),
        frame_rate=sample_rate,
        channels=2,
        sample_width=2  # 16-bit = 2 bytes
    )
    
    return beep


def insert_beep_in_audio(
    audio_path: Path,
    beep_timestamps: list[tuple[float, float]],
    output_path: Optional[Path] = None
) -> Path:
    """
    Insert beep sounds at specified timestamps in the audio
    
    Args:
        audio_path: Path to the original audio file
        beep_timestamps: List of (start_time, end_time) tuples in seconds
        output_path: Optional path for output audio file
        
    Returns:
        Path to the censored audio file
    """
    if output_path is None:
        output_path = TEMP_DIR / f"{audio_path.stem}_censored.wav"
    
    # Load original audio
    audio = AudioSegment.from_wav(str(audio_path))
    
    # Sort timestamps by start time
    beep_timestamps = sorted(beep_timestamps, key=lambda x: x[0])
    
    # Process from end to start to avoid index shifting issues
    for start_time, end_time in reversed(beep_timestamps):
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)
        duration_ms = end_ms - start_ms
        
        # Add padding for smooth transitions
        padded_start = max(0, start_ms - int(BEEP_DURATION_PADDING * 1000))
        padded_end = min(len(audio), end_ms + int(BEEP_DURATION_PADDING * 1000))
        
        # Generate beep with fade in/out
        beep = generate_beep(duration_ms + int(BEEP_DURATION_PADDING * 2000))
        beep = beep.fade_in(50).fade_out(50)  # 50ms fade
        
        # Match the volume level of the original audio segment
        original_segment = audio[padded_start:padded_end]
        if len(original_segment) > 0:
            # Get RMS (root mean square) for volume matching
            original_rms = original_segment.rms
            beep_rms = beep.rms
            if beep_rms > 0 and original_rms > 0:
                # Calculate volume difference in decibels
                volume_ratio = original_rms / beep_rms
                # Limit volume adjustment to avoid distortion (max 6dB increase/decrease)
                volume_ratio = max(0.5, min(volume_ratio, 2.0))
                # Convert ratio to decibels (pydub uses dB for volume adjustments)
                volume_db = 20 * np.log10(volume_ratio)
                beep = beep + volume_db
        
        # Replace the segment with beep
        audio = audio[:padded_start] + beep + audio[padded_end:]
    
    # Normalize audio to prevent clipping
    audio = normalize(audio)
    
    # Export censored audio
    audio.export(str(output_path), format="wav")
    
    return output_path


def merge_audio_to_video(video_path: Path, audio_path: Path, output_path: Path) -> Path:
    """
    Merge censored audio back into the original video
    
    Args:
        video_path: Path to the original video file
        audio_path: Path to the censored audio file
        output_path: Path for the final output video
        
    Returns:
        Path to the final video file
    """
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",  # Copy video stream without re-encoding
        "-c:a", "aac",  # Encode audio as AAC
        "-map", "0:v:0",  # Use video from first input
        "-map", "1:a:0",  # Use audio from second input
        "-shortest",  # Finish encoding when the shortest input stream ends
        "-y",  # Overwrite output file
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return output_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to merge audio to video: {e.stderr}")

