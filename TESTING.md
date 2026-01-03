# Testing Guide

## Quick Test Commands

### 1. Check Server Status
```bash
curl http://localhost:8000/health
```

### 2. Get Profanity List
```bash
curl http://localhost:8000/profanity-list
```

### 3. Process a Video
Replace `/path/to/your/video.mp4` with an actual video file path:

```bash
# Using the example client
python example_client.py /path/to/your/video.mp4

# Or using curl directly
curl -X POST "http://localhost:8000/process-video" \
  -F "file=@/path/to/your/video.mp4"
```

### 4. Download Processed Video
After processing, download the result:
```bash
curl -O "http://localhost:8000/download/censored_<filename>.mp4"
```

## Finding Video Files

### Search for video files in common locations:
```bash
# Search in home directory
find ~ -maxdepth 3 -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.mkv" \) 2>/dev/null

# Search in Downloads
ls ~/Downloads/*.{mp4,mov,mkv} 2>/dev/null

# Search in Videos
ls ~/Videos/*.{mp4,mov,mkv} 2>/dev/null
```

## Example Usage

Once you have a video file, for example at `~/Videos/test.mp4`:

```bash
cd /home/nayon-ahmed/dev/video_profanity_censor
python example_client.py ~/Videos/test.mp4
```

## Testing Without a Video File

You can test the API endpoints without processing a video:

1. **Health Check**: `curl http://localhost:8000/health`
2. **Profanity List**: `curl http://localhost:8000/profanity-list`
3. **API Docs**: Open `http://localhost:8000/docs` in your browser

