"""
Main FastAPI application for Video Profanity Detection & Auto-Beep System
"""
import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, MAX_FILE_SIZE
from utils import (
    generate_unique_filename,
    validate_video_file,
    cleanup_file,
    cleanup_temp_files
)
from audio_processor import (
    extract_audio_from_video,
    insert_beep_in_audio,
    merge_audio_to_video
)
from transcription import TranscriptionService
from profanity_detector import ProfanityDetector

app = FastAPI(
    title="Video Profanity Detection & Auto-Beep System",
    description="Automatically detect and censor profane words in videos with beep sounds",
    version="1.0.0"
)

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
transcription_service = TranscriptionService()
profanity_detector = ProfanityDetector()


class ProcessingResult(BaseModel):
    """Response model for processing results"""
    success: bool
    message: str
    output_filename: Optional[str] = None
    profanities_detected: int = 0
    profanity_list: Optional[list] = None
    processing_time: Optional[float] = None


class ProfanityListResponse(BaseModel):
    """Response model for profanity list"""
    profanity_words: list[str]
    total_count: int


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Video Profanity Detection & Auto-Beep System API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/process-video",
            "health": "/health",
            "profanity_list": "/profanity-list"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "video-profanity-censor"}


@app.get("/profanity-list", response_model=ProfanityListResponse)
async def get_profanity_list():
    """Get current profanity word list"""
    words = profanity_detector.get_profanity_list()
    return ProfanityListResponse(
        profanity_words=words,
        total_count=len(words)
    )


@app.post("/profanity-list/add")
async def add_profanity_word(word: str):
    """Add a word to the profanity list"""
    if not word or not word.strip():
        raise HTTPException(status_code=400, detail="Word cannot be empty")
    profanity_detector.add_profanity_word(word.strip())
    return {"message": f"Added '{word}' to profanity list", "word": word}


@app.post("/profanity-list/remove")
async def remove_profanity_word(word: str):
    """Remove a word from the profanity list"""
    if not word or not word.strip():
        raise HTTPException(status_code=400, detail="Word cannot be empty")
    profanity_detector.remove_profanity_word(word.strip())
    return {"message": f"Removed '{word}' from profanity list", "word": word}


def cleanup_processing_files(*file_paths: Path):
    """Background task to clean up temporary files"""
    for file_path in file_paths:
        if file_path and file_path.exists():
            cleanup_file(file_path)


@app.post("/process-video", response_model=ProcessingResult)
async def process_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Main endpoint to process video and censor profanities
    
    Processing pipeline:
    1. Upload and validate video
    2. Extract audio
    3. Transcribe with timestamps
    4. Detect profanities
    5. Insert beep sounds
    6. Merge audio back to video
    7. Return processed video
    """
    import time
    start_time = time.time()
    
    # Step 1: Validate and save uploaded file
    file_size = 0
    try:
        # Read file content to get size
        content = await file.read()
        file_size = len(content)
        
        # Validate file
        is_valid, error_msg = validate_video_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate unique filename
        video_filename = generate_unique_filename(file.filename, "video")
        video_path = UPLOAD_DIR / video_filename
        
        # Save uploaded file
        with open(video_path, "wb") as f:
            f.write(content)
        
        print(f"Uploaded video: {video_path} ({file_size / (1024*1024):.2f} MB)")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
    
    # Initialize paths for cleanup
    audio_path = None
    censored_audio_path = None
    output_video_path = None
    
    try:
        # Step 2: Extract audio from video
        print("Extracting audio from video...")
        audio_path = extract_audio_from_video(video_path)
        print(f"Audio extracted: {audio_path}")
        
        # Step 3: Transcribe audio with word-level timestamps
        print("Transcribing audio...")
        words_with_timestamps = transcription_service.transcribe_with_timestamps(audio_path)
        
        if not words_with_timestamps:
            raise HTTPException(
                status_code=500,
                detail="Failed to transcribe audio. No words detected."
            )
        
        # Step 4: Detect profanities
        print("Detecting profanities...")
        profanity_timestamps = profanity_detector.detect_profanities(words_with_timestamps)
        
        print(f"Detected {len(profanity_timestamps)} profanity instances")
        
        # Step 5: Insert beep sounds
        if profanity_timestamps:
            print("Inserting beep sounds...")
            beep_timestamps = [(start, end) for start, end, word in profanity_timestamps]
            censored_audio_path = insert_beep_in_audio(audio_path, beep_timestamps)
            print(f"Censored audio created: {censored_audio_path}")
        else:
            # No profanities found, use original audio
            print("No profanities detected, using original audio")
            censored_audio_path = audio_path
        
        # Step 6: Merge censored audio back into video
        print("Merging audio back into video...")
        output_filename = generate_unique_filename(file.filename, "censored")
        output_video_path = OUTPUT_DIR / output_filename
        merge_audio_to_video(video_path, censored_audio_path, output_video_path)
        print(f"Final video created: {output_video_path}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare profanity list for response
        profanity_details = [
            {"word": word, "start": start, "end": end}
            for start, end, word in profanity_timestamps
        ]
        
        # Schedule cleanup of temporary files (keep output video)
        if audio_path and audio_path != censored_audio_path:
            background_tasks.add_task(cleanup_processing_files, audio_path)
        if censored_audio_path and censored_audio_path != audio_path:
            background_tasks.add_task(cleanup_processing_files, censored_audio_path)
        background_tasks.add_task(cleanup_processing_files, video_path)
        
        return ProcessingResult(
            success=True,
            message="Video processed successfully",
            output_filename=output_filename,
            profanities_detected=len(profanity_timestamps),
            profanity_list=profanity_details,
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup on error
        for path in [audio_path, censored_audio_path, video_path]:
            if path and path.exists():
                cleanup_file(path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/download/{filename}")
async def download_video(filename: str):
    """
    Download processed video file
    
    Args:
        filename: Name of the output file
    """
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="video/mp4"
    )


@app.post("/cleanup")
async def cleanup_old_files():
    """Manually trigger cleanup of old temporary files"""
    cleanup_temp_files()
    return {"message": "Cleanup completed"}


if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    
    print(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)

