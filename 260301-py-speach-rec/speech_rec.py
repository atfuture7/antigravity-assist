import argparse
import speech_recognition as sr
import os
import sys
import math

def process_audio(input_file, language, output_file):
    try:
        from pydub import AudioSegment
    except ImportError:
        print("Error: 'pydub' is required to read non-WAV audio files.")
        print("Please install it running: pip install pydub")
        sys.exit(1)
        
    print(f"Loading '{input_file}' for processing...")
    try:
        audio = AudioSegment.from_file(input_file)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        sys.exit(1)

    # Google's free API struggles with large files (roughly > 1min or > 10MB)
    # We will chunk the audio into 60-second segments to process them safely.
    chunk_length_ms = 60 * 1000 # 60 seconds
    chunks = math.ceil(len(audio) / chunk_length_ms)
    print(f"Audio length is {len(audio)/1000:.1f} seconds. Splitting into {chunks} chunks...")

    recognizer = sr.Recognizer()
    full_text = []

    # Map friendly names to language codes for Google
    lang_mapping = {
        'chinese': 'zh-CN',
        'english': 'en-US',
        'spanish': 'es-ES'
    }
    lang = lang_mapping.get(language.lower(), language)

    # Make output file empty
    with open(output_file, 'w', encoding='utf-8') as f:
        pass

    for i in range(chunks):
        start_ms = i * chunk_length_ms
        end_ms = min((i + 1) * chunk_length_ms, len(audio))
        chunk = audio[start_ms:end_ms]

        chunk_filename = f"temp_chunk_{i}.wav"
        chunk.export(chunk_filename, format="wav")
        
        print(f"Processing chunk {i+1}/{chunks}...")
        try:
            with sr.AudioFile(chunk_filename) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio_data = recognizer.record(source)
                
            text = recognizer.recognize_google(audio_data, language=lang)
            print(f"  Result: {text[:50]}...") # Print a small snippet
            
            # Append immediately to file
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(text + "\n")
                
        except sr.UnknownValueError:
            print(f"  [Chunk {i+1} empty or unclear speech]")
        except sr.RequestError as e:
            print(f"  [Error contacting API for chunk {i+1}]: {e}")
        except Exception as e:
            print(f"  [Unexpected error on chunk {i+1}]: {e}")
        finally:
            if os.path.exists(chunk_filename):
                os.remove(chunk_filename)

    print(f"\nSuccess! Full transcription saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Command-line Speech Recognition Tool")
    parser.add_argument("-i", "--input", required=True, help="Path to the source audio file")
    parser.add_argument("-l", "--language", required=True, help="Language code (e.g., 'en-US', 'zh-CN')")
    parser.add_argument("-o", "--output", required=True, help="Path to the output text file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
        
    process_audio(args.input, args.language, args.output)

if __name__ == "__main__":
    main()
