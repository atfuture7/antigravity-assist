# Voice Subtitle Editor

A Python application for editing subtitles synchronized with audio.

## Features
- Vertical scrolling waveform visualization.
- Subtitle synchronization and editing.
- Playback controls with seek-to-subtitle functionality.
- Support for WAV/MP3 audio and SRT subtitles.

## Requirements
- Python 3
- `pygame` library
- `ffmpeg` installed and in system PATH (for waveform generation)
- `tkinter` (usually included with Python)

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure `ffmpeg` is installed.

## Usage
Run the application:
```bash
python main.py
```

1. Click **Load File** to select an Audio file and a Subtitle (SRT) file.
2. Use **Play/Pause** to control playback.
3. Use **Up/Down** buttons next to the waveform to adjust Start/End times of the current subtitle.
4. Use **Up/Down** buttons at the bottom to navigate between subtitles.
5. Click **Save File** to save changes to a new SRT file.
