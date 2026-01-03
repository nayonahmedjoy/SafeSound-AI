# 🔥 Video Profanity Detection & Auto-Beep System

A full-stack web application that automatically detects profane words in videos and replaces them with beep sounds, making videos YouTube-safe.

## 🎯 Features

- **Web Interface**: Beautiful, modern web UI for easy video processing
- **Video Upload**: Drag-and-drop or click to upload MP4, MOV, MKV, AVI, M4V formats
- **Real-time Progress**: Live progress updates during processing
- **Audio Extraction**: Preserves original audio quality
- **Speech-to-Text**: Uses OpenAI Whisper for accurate transcription with word-level timestamps
- **Profanity Detection**: Customizable word list with precise timestamp matching
- **Beep Insertion**: Smooth beep sounds with volume matching and fade transitions
- **Video Reconstruction**: Maintains original video quality and sync
- **One-Click Download**: Easy download of processed videos

## 🛠️ Tech Stack

- **Backend**: Python 3.8+
- **Web Framework**: Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Audio/Video**: FFmpeg, MoviePy, Pydub
- **Speech Recognition**: OpenAI Whisper
- **Audio Processing**: Librosa, NumPy

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **FFmpeg** installed on your system:
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)

## 🚀 Installation

1. **Navigate to the project directory**:
   ```bash
   cd video_profanity_censor
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify FFmpeg installation**:
   ```bash
   ffmpeg -version
   ```

## 🎬 Usage

### Starting the Web Application

```bash
python app.py
```

The web application will start on `http://localhost:5000`

### Using the Web Interface

1. **Open your browser** and navigate to `http://localhost:5000`

2. **Upload a video**:
   - Click "Choose Video File" button, or
   - Drag and drop a video file onto the upload area

3. **Wait for processing**:
   - The system will show real-time progress
   - You'll see status updates: "Extracting audio...", "Transcribing...", "Detecting profanities...", etc.

4. **Download the result**:
   - Once processing is complete, click "Download Censored Video"
   - The processed video will be downloaded to your computer

### Web Interface Features

- **Drag & Drop Upload**: Simply drag your video file onto the upload area
- **Real-time Progress**: See exactly what's happening during processing
- **Profanity Report**: View list of detected profanities with timestamps
- **One-Click Download**: Download processed video with a single click
- **Error Handling**: Clear error messages if something goes wrong
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 📁 Project Structure

```
video_profanity_censor/
├── app.py                  # Flask web application
├── config.py               # Configuration settings
├── utils.py                # Utility functions
├── audio_processor.py      # Audio extraction and manipulation
├── transcription.py         # Speech-to-text with Whisper
├── profanity_detector.py   # Profanity detection logic
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   └── index.html         # Main web interface
├── static/                # Static files
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── main.js       # Frontend JavaScript
├── uploads/               # Temporary upload storage
├── outputs/               # Processed video outputs
└── temp/                  # Temporary processing files
```

## ⚙️ Configuration

Edit `config.py` to customize:

- **File size limits**: `MAX_FILE_SIZE`
- **Allowed formats**: `ALLOWED_EXTENSIONS`
- **Beep settings**: `BEEP_FREQUENCY`, `BEEP_DURATION_PADDING`
- **Whisper model**: `WHISPER_MODEL` (tiny, base, small, medium, large)
- **Profanity words**: `PROFANITY_WORDS` list
- **Server settings**: `API_HOST`, `API_PORT` (in app.py)

## 🔧 Processing Pipeline

1. **Upload**: Video file is validated and saved
2. **Audio Extraction**: FFmpeg extracts audio track
3. **Transcription**: Whisper transcribes with word-level timestamps
4. **Detection**: Profanity detector matches words with timestamps
5. **Censoring**: Beep sounds replace detected words
6. **Merging**: Censored audio merged back into video
7. **Download**: Final video available for download

## 🎨 Features & Quality

- ✅ **Precise Timing**: Word-level timestamps ensure accurate beep placement
- ✅ **Volume Matching**: Beep volume matches surrounding audio
- ✅ **Smooth Transitions**: Fade in/out prevents harsh cuts
- ✅ **Quality Preservation**: Original video quality maintained
- ✅ **Modern UI**: Beautiful, responsive web interface
- ✅ **Real-time Updates**: Live progress tracking
- ✅ **Error Handling**: Comprehensive error handling and cleanup
- ✅ **Modular Design**: Easy to extend and customize

## 🌐 API Endpoints (for programmatic access)

The Flask app also exposes REST API endpoints:

- `POST /upload` - Upload and process video
- `GET /status/<task_id>` - Get processing status
- `GET /download/<filename>` - Download processed video
- `GET /profanity-list` - Get current profanity word list

## 🚧 Future Enhancements

- [ ] Multi-language profanity detection
- [ ] Custom beep sound uploads
- [ ] Adjustable strictness levels (YouTube-safe, family-safe, etc.)
- [ ] Batch processing
- [ ] Cloud storage integration
- [ ] User accounts and history

## 🐛 Troubleshooting

### FFmpeg not found
```
Error: Failed to extract audio: ffmpeg: command not found
```
**Solution**: Install FFmpeg (see Prerequisites)

### Whisper model download
On first run, Whisper will download the model. This may take a few minutes depending on your internet connection.

### Memory issues
For large videos, consider using a smaller Whisper model (`tiny` or `base`) in `config.py`.

### Port already in use
If port 5000 is already in use, edit `app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Audio sync issues
If audio/video sync is off, try re-encoding the video instead of copying:
```python
# In audio_processor.py, change:
"-c:v", "copy"  # to "-c:v", "libx264"
```

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

**Note**: This system is designed to help content creators make their videos platform-safe. Always review the output to ensure accuracy, as speech recognition may have errors.
