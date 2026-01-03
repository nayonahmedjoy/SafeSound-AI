#!/bin/bash
# Quick start script for Video Profanity Detection Web Application

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🔥 Starting Video Profanity Detection Web Application..."
echo ""
echo "Make sure you have:"
echo "  1. Python 3.8+ installed"
echo "  2. FFmpeg installed (sudo apt-get install ffmpeg)"
echo "  3. All dependencies installed (pip install -r requirements.txt)"
echo ""
echo "Starting Flask server..."
echo "Open your browser at: http://localhost:5000"
echo ""

python app.py


