"""
Utility functions for file handling and validation
"""
import os
import hashlib
import time
from pathlib import Path
from typing import Optional
from config import UPLOAD_DIR, TEMP_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """
    Generate a unique filename to avoid conflicts
    
    Args:
        original_filename: Original filename from upload
        prefix: Optional prefix for the filename
        
    Returns:
        Unique filename string
    """
    timestamp = int(time.time() * 1000)
    file_hash = hashlib.md5(f"{original_filename}{timestamp}".encode()).hexdigest()[:8]
    ext = Path(original_filename).suffix
    if prefix:
        return f"{prefix}_{timestamp}_{file_hash}{ext}"
    return f"{timestamp}_{file_hash}{ext}"


def validate_video_file(filename: str, file_size: int) -> tuple[bool, Optional[str]]:
    """
    Validate uploaded video file
    
    Args:
        filename: Name of the uploaded file
        file_size: Size of the file in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type {ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        return False, f"File size {file_size / (1024*1024):.2f} MB exceeds maximum {MAX_FILE_SIZE / (1024*1024):.2f} MB"
    
    return True, None


def cleanup_file(file_path: Path) -> None:
    """
    Safely delete a file if it exists
    
    Args:
        file_path: Path to the file to delete
    """
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Warning: Could not delete file {file_path}: {e}")


def cleanup_temp_files(pattern: str = "*") -> None:
    """
    Clean up temporary files older than 1 hour
    
    Args:
        pattern: File pattern to match (default: all files)
    """
    current_time = time.time()
    for file_path in TEMP_DIR.glob(pattern):
        try:
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > 3600:  # 1 hour
                    cleanup_file(file_path)
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}")

