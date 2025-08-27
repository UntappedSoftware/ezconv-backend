#!/bin/bash
# Update system packages
sudo apt-get update

# Install ffmpeg
sudo apt-get install -y ffmpeg

# Upgrade pip in the virtual environment
$VIRTUAL_ENV/bin/pip install --upgrade pip

# Install latest yt-dlp in the virtual environment
$VIRTUAL_ENV/bin/pip install --upgrade yt-dlp
