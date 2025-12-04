# Audio and Subtitle Player Walkthrough

I have created a Python application that plays audio and displays scrolling subtitles.

## Features
- **Vertical Display**: 1:3 aspect ratio window.
- **Scrolling Subtitles**: 
    - Current subtitle is always centered and highlighted.
    - Previous subtitles are displayed above the center.
    - Upcoming subtitles are displayed below the center.
- **Playback Controls**: Play, Pause, Stop.
- **Seek**: Jump to specific time (HH:MM:SS) and auto-sync audio/subtitles.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install pygame pysubs2
    ```
    *(Note: If you are in a managed environment, you might need to use a virtual environment or `pip install --break-system-packages`)*

2.  **Run the Application**:
    ```bash
    python main.py
    ```

## Usage

1.  **Load Files**: Click "Load Files" (top right) to select your Audio (`.mp3`, `.wav`) and Subtitle (`.srt`) files.
2.  **Play**: Click "▶ Play" to start.
3.  **Seek**: Enter a time (e.g., `00:00:10`) in the box and click "Go".
4.  **Controls**: Use Pause/Stop as needed.

## Verification
I have verified the following:
- `pysubs2` correctly parses SRT files.
- Time conversion logic (`utils.py`) is correct.
- Audio player logic (`player.py`) wraps `pygame.mixer` correctly.
- UI logic (`ui.py`) calculates subtitle positions based on current playback time.

## Files
- [main.py](file:///home/csadmin/dev/ai-audio-srt-play/main.py): Entry point.
- [ui.py](file:///home/csadmin/dev/ai-audio-srt-play/ui.py): GUI implementation.
- [player.py](file:///home/csadmin/dev/ai-audio-srt-play/player.py): Audio handling.
- [utils.py](file:///home/csadmin/dev/ai-audio-srt-play/utils.py): Helper functions.
