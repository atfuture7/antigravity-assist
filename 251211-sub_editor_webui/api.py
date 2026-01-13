import webview
import json
import os
import io
import subprocess
import array
from audio_handler import AudioHandler
from subtitle_manager import SubtitleManager

class Api:
    def __init__(self, window):
        self.window = window
        self.audio = AudioHandler()
        self.subs = SubtitleManager()
        self.waveform_data = None
        
    def load_file_dialog(self):
        # 1. Select Audio
        audio_file_types = ('Audio Files (*.wav;*.mp3)', 'WAV Files (*.wav)', 'MP3 Files (*.mp3)', 'All Files (*.*)')
        audio_result = self.window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=audio_file_types)
        
        if not audio_result:
            return {"success": False, "reason": "Audio selection cancelled"}
        
        audio_path = audio_result[0]
        
        # 2. Select Subtitles
        sub_file_types = ('Subtitle Files (*.srt)', 'All Files (*.*)')
        srt_result = self.window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=sub_file_types)
        
        if not srt_result:
             return {"success": False, "reason": "Subtitle selection cancelled"}
             
        srt_path = srt_result[0]
        
        # 3. Process Logic
        return self._process_load(audio_path, srt_path)

    def _process_load(self, audio_path, srt_path):
        # Load Audio
        self.audio.load_file(audio_path)
        
        # Load Subs
        self.subs.load_srt(srt_path)
        subs_list = [{
            'index': s.index,
            'start': s.start_time,
            'end': s.end_time,
            'text': s.text
        } for s in self.subs.subtitles]

        # Process Waveform
        envelope = []
        duration = 0
        try:
            cmd = [
                'ffmpeg', '-i', audio_path, '-f', 's16le', '-ac', '1', '-ar', '8000', '-v', 'quiet', '-'
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            raw_data, _ = process.communicate()
            
            if raw_data:
                samples = array.array('h', raw_data)
                total_samples = len(samples)
                original_rate = 8000
                
                # Downsample to 100Hz for visual
                target_rate = 100
                chunk_size = int(original_rate / target_rate)
                
                for i in range(0, total_samples, chunk_size):
                    chunk = samples[i:i+chunk_size]
                    if not chunk: break
                    envelope.append([min(chunk), max(chunk)])
                    
                self.waveform_data = envelope
                duration = total_samples / original_rate
                
        except Exception as e:
            print(f"Error processing waveform: {e}")
            return {"success": False, "error": str(e)}

        return {
            "success": True, 
            "duration": duration, 
            "waveform": envelope,
            "subtitles": subs_list
        }

    # Combined loader replaces separate dialogs
    
    def play(self, start_time):
        self.audio.play(float(start_time))
        return {"success": True}

    def pause(self):
        self.audio.pause()
        return {"success": True}

    def get_current_time(self):
        return self.audio.get_current_time()
        
    def save_subtitles_dialog(self):
        if not self.subs.subtitles:
            return {"success": False, "error": "No subtitles to save"}
            
        file_types = ('Subtitle Files (*.srt)', 'All Files (*.*)')
        # save_file_dialog returns a string (filepath), not a list (unlike create_file_dialog open)
        # Wait, pywebview create_file_dialog returns string in SAVE mode?
        # Check docs/usage. Usually create_file_dialog in SAVE mode returns string.
        filepath = self.window.create_file_dialog(webview.SAVE_DIALOG, save_filename='subtitles.srt', file_types=file_types)
        
        if filepath:
            # If it's a list (some versions), take first. If string, use it.
            if isinstance(filepath, (list, tuple)):
                filepath = filepath[0]
                
            self.subs.save_srt(filepath)
            return {"success": True}
        return {"success": False}

    def update_subtitle_timing(self, index, start, end):
        # index is 1-based from frontend usually, but let's check.
        # Front end uses s.index which is from subtitle file.
        # SubtitleManager.get_subtitle_by_index uses 1-based.
        sub = self.subs.get_subtitle_by_index(int(index))
        if sub:
            sub.start_time = float(start)
            sub.end_time = float(end)
            return {"success": True}
        return {"success": False, "error": "Subtitle not found"}

    def update_subtitle_text(self, index, text):
        sub = self.subs.get_subtitle_by_index(int(index))
        if sub:
            sub.text = text
            return {"success": True}
        return {"success": False, "error": "Subtitle not found"}
