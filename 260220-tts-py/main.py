import webview
import os
import requests
from bs4 import BeautifulSoup
import nltk
import urllib.parse
from gtts import gTTS
import pygame
import threading
import tempfile
import time
import glob
import sys

# Ensure nltk tokenizer is available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading NLTK punkt_tab data...")
    nltk.download('punkt')
    nltk.download('punkt_tab')

class Api:
    def __init__(self):
        self._window = None
        self.sentences = []
        self._playing = False
        pygame.mixer.init()

    def set_window(self, window):
        self._window = window

    def _process_text(self, text):
        """Proc-2nd: Converts raw text to sentences."""
        if not text.strip():
            return False
            
        # Optional: clean up excessive whitespace before tokenization
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = " ".join(lines)
        
        self.sentences = nltk.tokenize.sent_tokenize(cleaned_text)
        print(f"Processed {len(self.sentences)} sentences.")
        return True

    def load_file(self):
        """Proc-2nd triggered after file prompt"""
        file_types = ('Text Files (*.txt)', 'All files (*.*)')
        
        # We need to run create_file_dialog on the main thread or ensure we block it correctly.
        # pywebview file dialogs block.
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG, 
            allow_multiple=False, 
            file_types=file_types
        )
        
        if result and len(result) > 0:
            filepath = result[0]
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                return self._process_text(text_content)
            except Exception as e:
                print(f"Error reading file {filepath}: {e}")
                return False
        return False

    def load_url(self, url):
        """Proc-1st: Fetch content and extract user-visible text"""
        print(f"Loading URL: {url}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Using beautiful soup to extract visible text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, nav, footer, header, etc.
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "meta", "noscript"]):
                element.decompose()
                
            text = soup.get_text(separator='\n', strip=True)
            return self._process_text(text)
            
        except Exception as e:
            print(f"Error loading URL: {e}")
            return False

    def save_file(self):
        """Save sentences to file"""
        if not self.sentences:
            return False
            
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG, 
            save_filename='processed_sentences.txt'
        )
        
        if result:
            filepath = result if isinstance(result, str) else result[0]
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    for sentence in self.sentences:
                        f.write(sentence + '\n')
                print(f"Successfully saved {len(self.sentences)} sentences to {filepath}")
                return True
            except Exception as e:
                print(f"Error saving to {filepath}: {e}")
                return False
        return False

    def play(self, start_idx_str, lang):
        if not self.sentences:
            return

        try:
            start_idx = int(start_idx_str) - 1
        except ValueError:
            start_idx = 0
            
        if start_idx < 0:
            start_idx = 0
        if start_idx >= len(self.sentences):
            start_idx = len(self.sentences) - 1
            # Update frontend index if we capped it
            self._window.evaluate_js(f"update_index({start_idx + 1})")
            
        self._playing = True
        
        # Start playback in a daemon thread so it doesn't block pywebview
        t = threading.Thread(target=self._playback_loop, args=(start_idx, lang))
        t.daemon = True
        t.start()
        return True

    def stop(self):
        self._playing = False
        pygame.mixer.music.stop()
        return True

    def clear_cache(self):
        """Clear the audio cache from temp directory"""
        temp_dir = tempfile.gettempdir()
        try:
            # Delete all cached tts mp3 files
            files = glob.glob(os.path.join(temp_dir, "tts_cache_*.mp3"))
            for f in files:
                os.remove(f)
            print(f"Cleared {len(files)} cached audio files.")
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def _playback_loop(self, start_idx, lang):
        temp_dir = tempfile.gettempdir()
        
        for i in range(start_idx, len(self.sentences)):
            if not self._playing:
                break
                
            sentence = self.sentences[i]
            if not sentence.strip():
                continue
                
            self._window.evaluate_js(f"update_index({i + 1})")
            
            try:
                # Use a specific naming convention to associate with index/content
                # we will include the language and a hash of the text to be safe
                text_hash = hash(sentence) % ((sys.maxsize + 1) * 2)
                cache_filename = f"tts_cache_{i}_{lang}_{text_hash}.mp3"
                temp_audio_path = os.path.join(temp_dir, cache_filename)
                
                # Check cache
                if not os.path.exists(temp_audio_path):
                    # Cache miss: generate
                    tts = gTTS(text=sentence, lang=lang)
                    tts.save(temp_audio_path)
                    print(f"Cache miss: Generated audio for sentence {i}")
                else:
                    print(f"Cache hit: Playing existing audio for sentence {i}")
                
                pygame.mixer.music.load(temp_audio_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy() and self._playing:
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Error playing sentence {i}: {e}")
                
            # Move index to NEXT sentence for UI (according to spec)
            if self._playing and i + 1 < len(self.sentences):
                 self._window.evaluate_js(f"update_index({i + 2})")
                 
        self._playing = False
        self._window.evaluate_js("on_playback_stopped()")

if __name__ == '__main__':
    api = Api()
    
    # Path to index.html
    html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
    
    # Initialize pywebview (400x700 mobile view)
    window = webview.create_window(
        'Text-to-Speech Tool',
        url=f'file://{html_file}',
        js_api=api,
        width=400,
        height=700,
        resizable=False
    )
    
    api.set_window(window)
    webview.start(debug=True)
