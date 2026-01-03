#!/bin/bash
# Quick script to run the example client

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ $# -eq 0 ]; then
    echo "Usage: ./run_example.sh <video_file_path> [api_url]"
    echo "Example: ./run_example.sh ~/Videos/test.mp4"
    exit 1
fi

python example_client.py "$@"

