#!/bin/bash
# Update system packages
sudo apt-get update

# Install ffmpeg
sudo apt-get install -y ffmpeg

# Upgrade pip
pip install --upgrade pip

# Install yt-dlp in the virtual environment
pip install --upgrade yt-dlp
