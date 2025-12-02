import argparse
import os
import shutil
import tempfile
from text_processor import split_sentences, split_subtitle
from audio_generator import generate_audio, get_audio_duration, concatenate_audio
from srt_generator import generate_srt

def main():
    parser = argparse.ArgumentParser(description="Convert text file to audio and SRT.")
    parser.add_argument("input_file", help="Path to the input text file.")
    parser.add_argument("--output_audio", help="Path to the output audio file.", default="output.mp3")
    parser.add_argument("--output_srt", help="Path to the output SRT file.", default="output.srt")
    parser.add_argument("--max_chars", type=int, default=80, help="Maximum characters per subtitle segment.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return

    print(f"Reading input file: {args.input_file}")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        text = f.read()
        
    sentences = split_sentences(text)
    print(f"Found {len(sentences)} sentences.")
    
    temp_dir = tempfile.mkdtemp()
    print(f"Created temporary directory: {temp_dir}")
    
    audio_files = []
    subtitles = []
    current_time = 0.0
    
    try:
        for i, sentence in enumerate(sentences):
            print(f"Processing sentence {i+1}/{len(sentences)}...")
            
            # Generate audio for the sentence
            temp_audio_path = os.path.join(temp_dir, f"sentence_{i}.mp3")
            generate_audio(sentence, temp_audio_path)
            audio_files.append(temp_audio_path)
            
            # Get duration
            duration = get_audio_duration(temp_audio_path)
            
            # Split subtitle if needed
            segments = split_subtitle(sentence, args.max_chars, duration)
            
            for segment in segments:
                subtitles.append({
                    'text': segment['text'],
                    'start_time': current_time,
                    'end_time': current_time + segment['duration']
                })
                current_time += segment['duration']
                
        print("Concatenating audio files...")
        concatenate_audio(audio_files, args.output_audio)
        print(f"Audio saved to: {args.output_audio}")
        
        print("Generating SRT file...")
        generate_srt(subtitles, args.output_srt)
        print(f"SRT saved to: {args.output_srt}")
        
    finally:
        print("Cleaning up temporary files...")
        shutil.rmtree(temp_dir)
        print("Done.")

if __name__ == "__main__":
    main()
