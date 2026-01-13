# Implementation Plan - Webview Integration

## Goal Description
Replace the existing Tkinter UI with a modern `pywebview` interface using the recently created `ui_overhaul.html`. This involves creating a Python API to expose backend functionality (audio playback, subtitle management, waveform processing) to the JavaScript frontend.

## User Review Required
> [!IMPORTANT]
> This change introduces a new dependency: `pywebview`.
> The `ffmpeg` dependency remains for audio processing.

## Proposed Changes

### Backend (Python)
#### [NEW] [api.py](file:///home/csadmin/dev/251203-aud-sub-edit/api.py)
- **Purpose**: Bridge between JS and Python.
- **Methods**:
    - `load_audio_dialog()`: Opens file dialog, loads audio, returns waveform data (list of min/max).
    - `load_subtitle_dialog()`: Opens file dialog, loads SRT, returns subtitles list.
    - `play(start_time)`: Plays audio from specific time.
    - `pause()`: Pauses audio.
    - `get_current_time()`: Returns current playback time.
    - `save_subtitles(subtitle_data)`: Saves the current subtitles to file.
    - `update_subtitle_time(index, start, end)`: Updates specific subtitle timing.

#### [NEW] [main_webview.py](file:///home/csadmin/dev/251203-aud-sub-edit/main_webview.py)
- **Purpose**: Entry point for the webview application.
- **Logic**:
    - Initialize `AudioHandler` and `SubtitleManager`.
    - Initialize `Api` class.
    - Create webview window pointing to `ui_overhaul.html`.
    - Start webview.

#### [MODIFY] [waveform_widget.py](file:///home/csadmin/dev/251203-aud-sub-edit/waveform_widget.py)
- **Refactor**: Extract the `ffmpeg` and data processing logic into a standalone function or helper class that returns raw data/envelope, so it can be used by `api.py` without Tkinter dependencies.

### Frontend (HTML/JS)
#### [MODIFY] [ui_overhaul.html](file:///home/csadmin/dev/251203-aud-sub-edit/ui_overhaul.html)
- **Canvas**: Add `<canvas>` element for waveform.
- **JS Logic**:
    - Replace mock data.
    - Connect buttons (Load, Play, Save, etc.) to `window.pywebview.api`.
    - Implement a render loop (using `requestAnimationFrame`) to:
        - Poll `api.get_current_time()`.
        - Draw waveform on Canvas (vertical scrolling based on time).
        - Update Subtitle Text display based on time.

## Verification Plan

### Manual Verification
1.  **Install Dependencies**: `pip install pywebview`.
2.  **Run Application**: `python main_webview.py`.
3.  **Test Flows**:
    -   **Load Audio**: Verify file dialog opens, and after selection, waveform appears on canvas.
    -   **Load Subtitles**: Verify file dialog opens, and subtitle text appears.
    -   **Play/Pause**: Verify audio plays/pauses and waveform scrolls.
    -   **Jump to Subtitle**: Verify entering a number and clicking Play jumps to that spot.
    -   **Save**: Verify changes to subtiles (if edited) are saved (though full editing in UI might be limited to what was requested: jump and timing display).

## Interactive Subtitle Timing (New Request)

### Backend (Python)
- **`api.py`**: Add `update_subtitle_timing(index, start_time, end_time)` to update the `Subtitlemanager`'s data in memory. This allows the "Save" function to persist changes.

### Frontend (HTML/JS)
- **State**:
    - Track `activeSubtitle` (current one being edited).
    - Track `startMarker` and `endMarker` times.
- **Rendering**:
    - In `drawWaveform`, draw vertical lines for `startMarker` (Yellow) and `endMarker` (Orange).
    - Draw "handles" or hit areas for mouse interaction.
- **Interaction**:
    - `mousedown`: Check if cursor is near a marker. Set `dragging` state.
    - `mousemove`: If dragging, update corresponding marker time based on X position. Call `drawWaveform`.
    - `mouseup`: Commit change to backend via `api.update_subtitle_timing`. Update internal `subtitles` array.
- **Sync**:
    - When `currentTime` updates (during playback), check if we entered a new subtitle. If so, update `startMarker`/`endMarker` to match.
    - When user jumps (inputs number), update markers.
