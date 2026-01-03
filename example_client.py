"""
Example client script to test the Video Profanity Detection API
"""
import requests
import sys
from pathlib import Path


def process_video(video_path: str, api_url: str = "http://localhost:8000"):
    """
    Process a video through the profanity detection API
    
    Args:
        video_path: Path to the video file
        api_url: Base URL of the API
    """
    video_file = Path(video_path)
    
    if not video_file.exists():
        print(f"Error: Video file not found: {video_path}")
        return
    
    print(f"Processing video: {video_file.name}")
    print(f"File size: {video_file.stat().st_size / (1024*1024):.2f} MB")
    
    # Upload and process
    try:
        with open(video_file, "rb") as f:
            print("Uploading video...")
            response = requests.post(
                f"{api_url}/process-video",
                files={"file": (video_file.name, f, "video/mp4")},
                timeout=600  # 10 minute timeout for large files
            )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        
        print("\n" + "="*50)
        print("Processing Results:")
        print("="*50)
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Profanities Detected: {result['profanities_detected']}")
        print(f"Processing Time: {result['processing_time']} seconds")
        
        if result['profanity_list']:
            print("\nDetected Profanities:")
            for profanity in result['profanity_list']:
                print(f"  - '{profanity['word']}' at {profanity['start']:.2f}s - {profanity['end']:.2f}s")
        
        if result['output_filename']:
            print(f"\nDownloading processed video: {result['output_filename']}")
            download_url = f"{api_url}/download/{result['output_filename']}"
            video_response = requests.get(download_url)
            
            output_path = Path("output") / result['output_filename']
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(video_response.content)
            
            print(f"Saved to: {output_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python example_client.py <video_file_path> [api_url]")
        print("Example: python example_client.py test_video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    process_video(video_path, api_url)

