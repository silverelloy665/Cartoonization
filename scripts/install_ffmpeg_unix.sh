#!/usr/bin/env bash
# Installs ffmpeg using the system package manager when possible, or prints manual instructions.
set -euo pipefail

TOOLS_DIR="$(dirname "$0")/../tools"
mkdir -p "$TOOLS_DIR"

if command -v apt-get >/dev/null 2>&1; then
  echo "Detected apt-get. Installing ffmpeg via apt..."
  sudo apt-get update
  sudo apt-get install -y ffmpeg
  echo "ffmpeg installed. Verify with: ffmpeg -version"
  exit 0
fi

if command -v brew >/dev/null 2>&1; then
  echo "Detected Homebrew. Installing ffmpeg via brew..."
  brew install ffmpeg
  echo "ffmpeg installed. Verify with: ffmpeg -version"
  exit 0
fi

echo "No supported package manager detected. Please install ffmpeg manually from https://ffmpeg.org/download.html"
exit 2
