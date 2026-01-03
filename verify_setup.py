"""
Setup verification script - checks if all dependencies are installed
"""
import sys
import subprocess


def check_command(command, name):
    """Check if a system command is available"""
    try:
        subprocess.run(
            [command, "--version"],
            capture_output=True,
            check=True
        )
        print(f"✅ {name} is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {name} is NOT installed")
        return False


def check_python_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False


def main():
    """Run all verification checks"""
    print("="*50)
    print("Video Profanity Detection - Setup Verification")
    print("="*50)
    print()
    
    all_ok = True
    
    # Check Python version
    print("Python Version:")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        all_ok = False
    print()
    
    # Check system dependencies
    print("System Dependencies:")
    ffmpeg_ok = check_command("ffmpeg", "FFmpeg")
    if not ffmpeg_ok:
        print("   Install: sudo apt-get install ffmpeg (Ubuntu/Debian)")
        print("   Install: brew install ffmpeg (macOS)")
        all_ok = False
    print()
    
    # Check Python packages
    print("Python Packages:")
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydub", "pydub"),
        ("whisper", "whisper"),
        ("numpy", "numpy"),
        ("pydantic", "pydantic"),
    ]
    
    for package_name, import_name in packages:
        if not check_python_package(package_name, import_name):
            all_ok = False
    
    print()
    print("="*50)
    if all_ok:
        print("✅ All dependencies are installed!")
        print("You can start the server with: python main.py")
    else:
        print("❌ Some dependencies are missing")
        print("Install missing packages with: pip install -r requirements.txt")
    print("="*50)


if __name__ == "__main__":
    main()

