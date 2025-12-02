from gtts import gTTS
from pydub import AudioSegment
import os

def generate_audio(text, output_file):
    """
    Generates audio from text using gTTS and saves it to output_file.
    """
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)

def get_audio_duration(file_path):
    """
    Returns the duration of the audio file in seconds.
    """
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000.0

def concatenate_audio(files, output_file):
    """
    Concatenates multiple audio files into one and saves it.
    """
    combined = AudioSegment.empty()
    for file in files:
        audio = AudioSegment.from_file(file)
        combined += audio
    
    combined.export(output_file, format="mp3")
