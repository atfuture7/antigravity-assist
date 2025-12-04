# Subtitle Editor Walkthrough

I have created the `adjust_subtitles.py` script to allow extending and reducing subtitle timings.

## Verification Results

### Test Case 1: Extend
- **Input**: Pivot `00:00:10,000`, Shift `+5.0s`.
- **Target**: Block 4 (Original Start `00:00:11,108`).
- **Result**:
    - Block 3 (Start `00:00:05,520`) -> **Unchanged**.
    - Block 4 (Start `00:00:11,108`) -> Shifted to `00:00:16,108` (+5s).
    - Subsequent blocks shifted by +5s.

### Test Case 2: Reduce
- **Input**: Pivot `00:00:05,000`.
- **Target**: Block 3 (Original Start `00:00:05,520`).
- **Result**:
    - Block 2 (Original Start `00:00:02,064`, End `00:00:05,520`) -> **Deleted** (Overlaps with new start time).
    - Block 3 -> Moved to `00:00:05,000` (Shift -0.52s).
    - Subsequent blocks shifted by -0.52s.

## Usage
Run the script interactively:
```bash
python3 adjust_subtitles.py
```
Or via command line:
```bash
python3 adjust_subtitles.py <filename> <pivot_time> <mode> [shift_amount]
```
Example:
```bash
python3 adjust_subtitles.py video.srt 00:01:30,000 extend 2.5
```
