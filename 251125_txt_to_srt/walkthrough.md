# Text to Audio and SRT Converter Walkthrough

## Overview
I have created a Python program that converts a text file into an audio file (MP3) and a subtitle file (SRT). The program uses `gTTS` for text-to-speech and `pydub` for audio manipulation. It splits long sentences into smaller subtitle segments to ensure readability.

## Usage

### Prerequisites
- Python 3
- `ffmpeg` installed
- `gTTS` and `pydub` python packages

### Running the Program
To run the program, use the following command:

```bash
python3 main.py <input_file> --output_audio <output_audio_path> --output_srt <output_srt_path> --max_chars <max_chars>
```

- `<input_file>`: Path to the input text file.
- `--output_audio`: (Optional) Path to the output audio file. Default: `output.mp3`.
- `--output_srt`: (Optional) Path to the output SRT file. Default: `output.srt`.
- `--max_chars`: (Optional) Maximum characters per subtitle segment. Default: 80.

### Example
```bash
python3 main.py podcast1202.txt --output_audio podcast.mp3 --output_srt podcast.srt
```

## Verification Results
I verified the program using a subset of the `podcast1202.txt` file.

### Input
A text file containing the first few sentences of the podcast script.

### Output
- **Audio**: An MP3 file containing the spoken text.
- **SRT**: A subtitle file with correct timestamps and text segmentation.

#### SRT Snippet
```srt
1
00:00:00,000 --> 00:00:03,216
Hey everyone, and welcome back to the channel!

2
00:00:03,216 --> 00:00:08,714
Today, we're talking about something every serious Linux user or developer

3
00:00:08,714 --> 00:00:14,213
eventually deals with: compiling and installing system-level programs from
```
