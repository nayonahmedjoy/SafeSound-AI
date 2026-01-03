"""
Flask web application for Video Profanity Detection & Auto-Beep System
"""
import os
import time
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from config import UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
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

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)

# Initialize services
transcription_service = TranscriptionService()
profanity_detector = ProfanityDetector()

# Store processing status
processing_status = {}


def process_video_task(video_path: Path, task_id: str):
    """
    Background task to process video
    
    Args:
        video_path: Path to uploaded video
        task_id: Unique task identifier
    """
    audio_path = None
    censored_audio_path = None
    
    try:
        processing_status[task_id] = {
            "status": "processing",
            "message": "Extracting audio from video...",
            "progress": 10
        }
        
        # Step 1: Extract audio
        audio_path = extract_audio_from_video(video_path)
        
        processing_status[task_id]["message"] = "Transcribing audio..."
        processing_status[task_id]["progress"] = 30
        
        # Step 2: Transcribe
        words_with_timestamps = transcription_service.transcribe_with_timestamps(audio_path)
        
        if not words_with_timestamps:
            processing_status[task_id] = {
                "status": "error",
                "message": "Failed to transcribe audio. No words detected.",
                "progress": 0
            }
            return
        
        processing_status[task_id]["message"] = "Detecting profanities..."
        processing_status[task_id]["progress"] = 60
        
        # Step 3: Detect profanities
        profanity_timestamps = profanity_detector.detect_profanities(words_with_timestamps)
        
        processing_status[task_id]["message"] = f"Found {len(profanity_timestamps)} profanities. Inserting beeps..."
        processing_status[task_id]["progress"] = 70
        
        # Step 4: Insert beeps
        if profanity_timestamps:
            beep_timestamps = [(start, end) for start, end, word in profanity_timestamps]
            censored_audio_path = insert_beep_in_audio(audio_path, beep_timestamps)
        else:
            censored_audio_path = audio_path
        
        processing_status[task_id]["message"] = "Merging audio back into video..."
        processing_status[task_id]["progress"] = 85
        
        # Step 5: Merge audio to video
        output_filename = generate_unique_filename(video_path.name, "censored")
        output_video_path = OUTPUT_DIR / output_filename
        merge_audio_to_video(video_path, censored_audio_path, output_video_path)
        
        # Prepare profanity details
        profanity_details = [
            {"word": word, "start": start, "end": end}
            for start, end, word in profanity_timestamps
        ]
        
        processing_status[task_id] = {
            "status": "completed",
            "message": "Processing completed successfully!",
            "progress": 100,
            "output_filename": output_filename,
            "profanities_detected": len(profanity_timestamps),
            "profanity_list": profanity_details
        }
        
        # Cleanup temporary files
        if audio_path and audio_path != censored_audio_path:
            cleanup_file(audio_path)
        if censored_audio_path and censored_audio_path != audio_path:
            cleanup_file(censored_audio_path)
        cleanup_file(video_path)
        
    except Exception as e:
        processing_status[task_id] = {
            "status": "error",
            "message": f"Processing failed: {str(e)}",
            "progress": 0
        }
        # Cleanup on error
        for path in [audio_path, censored_audio_path, video_path]:
            if path and path.exists():
                cleanup_file(path)


@app.route('/')
def index():
    """Main page with upload interface"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and start processing"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file
    is_valid, error_msg = validate_video_file(file.filename, request.content_length or 0)
    if not is_valid:
        return jsonify({"error": error_msg}), 400
    
    # Generate unique filename and save
    video_filename = generate_unique_filename(file.filename, "video")
    video_path = UPLOAD_DIR / video_filename
    
    try:
        file.save(str(video_path))
        
        # Generate task ID
        task_id = generate_unique_filename("task", "")[:-4]  # Remove extension
        
        # Start background processing
        thread = threading.Thread(
            target=process_video_task,
            args=(video_path, task_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "task_id": task_id,
            "message": "Video uploaded successfully. Processing started..."
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500


@app.route('/status/<task_id>')
def get_status(task_id):
    """Get processing status for a task"""
    if task_id not in processing_status:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(processing_status[task_id])


@app.route('/download/<filename>')
def download_video(filename):
    """Download processed video"""
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    
    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=filename,
        mimetype='video/mp4'
    )


@app.route('/profanity-list')
def get_profanity_list():
    """Get current profanity word list"""
    words = profanity_detector.get_profanity_list()
    return jsonify({
        "profanity_words": words,
        "total_count": len(words)
    })


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """Handle file size limit exceeded"""
    return jsonify({
        "error": f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f} MB"
    }), 413


if __name__ == '__main__':
    # Create necessary directories
    UPLOAD_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    
    print("Starting Video Profanity Detection Web Application...")
    print("Open your browser and navigate to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



