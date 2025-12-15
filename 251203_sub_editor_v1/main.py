import tkinter as tk
from tkinter import filedialog, messagebox
import os
from waveform_widget import WaveformWidget
from subtitle_manager import SubtitleManager
from audio_handler import AudioHandler

class VoiceSubtitleEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Subtitle Editor")
        self.root.geometry("400x1200")
        
        # Managers
        self.audio = AudioHandler()
        self.subs = SubtitleManager()
        
        # State
        self.current_sub_index = 0 # 1-based index internally managed as 0-based for list access? 
                                   # SubtitleManager uses 1-based for display, but list is 0-based.
                                   # Let's use 0-based index for list access.
        self.current_time = 0.0
        
        # UI Setup
        self.setup_ui()
        
        # Timer
        self.update_ui()

    def setup_ui(self):
        # Top: Current Time
        self.top_frame = tk.Frame(self.root, bg='black', height=50)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        self.time_label = tk.Label(self.top_frame, text="00:00.00", fg='white', bg='black', font=("Arial", 20))
        self.time_label.pack(pady=10)

        # Middle: Waveform and Time Controls
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Left Controls (Time Adjust)
        self.left_controls = tk.Frame(self.middle_frame, width=50, bg='#333')
        self.left_controls.pack(side=tk.LEFT, fill=tk.Y)
        
        # Start Time Controls
        tk.Label(self.left_controls, text="Start", fg='white', bg='#333').pack(pady=(20, 5))
        self.btn_start_up = tk.Button(self.left_controls, text="▲", command=lambda: self.adjust_time('start', 0.1))
        self.btn_start_up.pack()
        self.btn_start_down = tk.Button(self.left_controls, text="▼", command=lambda: self.adjust_time('start', -0.1))
        self.btn_start_down.pack()
        
        # Spacer
        tk.Label(self.left_controls, text="", bg='#333').pack(pady=20)
        
        # End Time Controls
        tk.Label(self.left_controls, text="End", fg='white', bg='#333').pack(pady=(0, 5))
        self.btn_end_up = tk.Button(self.left_controls, text="▲", command=lambda: self.adjust_time('end', 0.1))
        self.btn_end_up.pack()
        self.btn_end_down = tk.Button(self.left_controls, text="▼", command=lambda: self.adjust_time('end', -0.1))
        self.btn_end_down.pack()

        # Waveform
        self.waveform = WaveformWidget(self.middle_frame, bg='black', on_marker_change=self.update_subtitle_timing)
        self.waveform.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bottom: Controls and Subtitle
        self.bottom_frame = tk.Frame(self.root, bg='#222')
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Transport Controls
        self.transport_frame = tk.Frame(self.bottom_frame, bg='#222')
        self.transport_frame.pack(pady=10)
        
        self.btn_load = tk.Button(self.transport_frame, text="Load File", command=self.load_file)
        self.btn_load.pack(side=tk.LEFT, padx=5)
        
        self.btn_play = tk.Button(self.transport_frame, text="Play", command=self.play_audio)
        self.btn_play.pack(side=tk.LEFT, padx=5)
        
        self.btn_pause = tk.Button(self.transport_frame, text="Pause", command=self.pause_audio, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, padx=5)
        
        self.btn_save = tk.Button(self.transport_frame, text="Save File", command=self.save_file)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        # Subtitle Display
        self.sub_text = tk.Text(self.bottom_frame, height=3, width=40, font=("Arial", 12))
        self.sub_text.pack(pady=10, padx=10)
        
        # Subtitle Index Controls
        self.index_frame = tk.Frame(self.bottom_frame, bg='#222')
        self.index_frame.pack(pady=10)
        
        self.btn_prev_sub = tk.Button(self.index_frame, text="▲", command=self.prev_sub) # Up = Previous
        self.btn_prev_sub.pack(side=tk.LEFT, padx=5)
        
        self.lbl_index = tk.Label(self.index_frame, text="Subtitle: 0", fg='white', bg='#222', font=("Arial", 12))
        self.lbl_index.pack(side=tk.LEFT, padx=10)
        
        self.btn_next_sub = tk.Button(self.index_frame, text="▼", command=self.next_sub) # Down = Next
        self.btn_next_sub.pack(side=tk.LEFT, padx=5)

    def load_file(self):
        # Load Audio
        audio_path = filedialog.askopenfilename(title="Select Audio File", 
                                              filetypes=[("Audio Files", "*.wav *.mp3"), 
                                                         ("WAV Files", "*.wav"), 
                                                         ("MP3 Files", "*.mp3"),
                                                         ("All Files", "*.*")])
        if not audio_path:
            return
            
        # Load SRT
        srt_path = filedialog.askopenfilename(title="Select Subtitle File", filetypes=[("Subtitle Files", "*.srt")])
        if not srt_path:
            return
            
        self.audio.load_file(audio_path)
        self.waveform.load_audio(audio_path)
        self.subs.load_srt(srt_path)
        
        if self.subs.subtitles:
            self.current_sub_index = 0
            self.update_subtitle_display()
            
        self.current_time = 0.0
        self.waveform.set_position(0.0)

    def play_audio(self):
        # Jump to start of current subtitle
        if self.subs.subtitles:
            sub = self.subs.subtitles[self.current_sub_index]
            start_time = sub.start_time
            self.audio.play(start_time)
        else:
            self.audio.play(self.current_time)
            
        self.update_button_states(playing=True)

    def pause_audio(self):
        self.audio.pause()
        self.update_button_states(playing=False)

    def save_file(self):
        if not self.subs.subtitles:
            return
        path = filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("Subtitle Files", "*.srt")])
        if path:
            self.subs.save_srt(path)
            messagebox.showinfo("Saved", "Subtitle file saved successfully.")

    def update_button_states(self, playing):
        if playing:
            self.btn_load.config(state=tk.DISABLED)
            self.btn_play.config(state=tk.DISABLED)
            self.btn_save.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)
            
            # Disable editing
            self.btn_start_up.config(state=tk.DISABLED)
            self.btn_start_down.config(state=tk.DISABLED)
            self.btn_end_up.config(state=tk.DISABLED)
            self.btn_end_down.config(state=tk.DISABLED)
            self.btn_prev_sub.config(state=tk.DISABLED)
            self.btn_next_sub.config(state=tk.DISABLED)
        else:
            self.btn_load.config(state=tk.NORMAL)
            self.btn_play.config(state=tk.NORMAL)
            self.btn_save.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            
            # Enable editing
            self.btn_start_up.config(state=tk.NORMAL)
            self.btn_start_down.config(state=tk.NORMAL)
            self.btn_end_up.config(state=tk.NORMAL)
            self.btn_end_down.config(state=tk.NORMAL)
            self.update_nav_buttons()

    def update_nav_buttons(self):
        if not self.subs.subtitles:
            self.btn_prev_sub.config(state=tk.DISABLED)
            self.btn_next_sub.config(state=tk.DISABLED)
            return
            
        self.btn_prev_sub.config(state=tk.NORMAL if self.current_sub_index > 0 else tk.DISABLED)
        self.btn_next_sub.config(state=tk.NORMAL if self.current_sub_index < len(self.subs.subtitles) - 1 else tk.DISABLED)

    def prev_sub(self):
        if self.current_sub_index > 0:
            self.current_sub_index -= 1
            self.update_subtitle_display()

    def next_sub(self):
        if self.current_sub_index < len(self.subs.subtitles) - 1:
            self.current_sub_index += 1
            self.update_subtitle_display()

    def adjust_time(self, type_, amount):
        if not self.subs.subtitles:
            return
        
        sub = self.subs.subtitles[self.current_sub_index]
        if type_ == 'start':
            sub.start_time += amount
            if sub.start_time < 0: sub.start_time = 0
            # Ensure start <= end
            if sub.start_time > sub.end_time: sub.start_time = sub.end_time
        else:
            sub.end_time += amount
            # Ensure end >= start
            if sub.end_time < sub.start_time: sub.end_time = sub.start_time
            
            
        self.update_subtitle_display() # Updates markers

    def update_subtitle_timing(self, marker_type, new_time):
        if not self.subs.subtitles:
            return
            
        sub = self.subs.subtitles[self.current_sub_index]
        
        if marker_type == 'start':
            sub.start_time = max(0, new_time)
            # Ensure start <= end
            if sub.start_time > sub.end_time:
                sub.start_time = sub.end_time
        elif marker_type == 'end':
            sub.end_time = max(0, new_time)
            # Ensure end >= start
            if sub.end_time < sub.start_time:
                sub.end_time = sub.start_time
                
        self.update_subtitle_display()

    def update_subtitle_display(self):
        if not self.subs.subtitles:
            return
            
        sub = self.subs.subtitles[self.current_sub_index]
        
        # Update Text
        self.sub_text.delete(1.0, tk.END)
        self.sub_text.insert(tk.END, sub.text)
        
        # Update Index Label
        self.lbl_index.config(text=f"Subtitle: {sub.index}")
        
        # Update Markers on Waveform
        self.waveform.set_markers(sub.start_time, sub.end_time)
        
        # Update Nav Buttons
        self.update_nav_buttons()

    def update_ui(self):
        if self.audio.is_playing():
            self.current_time = self.audio.get_current_time()
            self.waveform.set_position(self.current_time)
            
            # Format time
            mins = int(self.current_time // 60)
            secs = int(self.current_time % 60)
            frac = int((self.current_time * 100) % 100)
            self.time_label.config(text=f"{mins:02}:{secs:02}.{frac:02}")
            
            # Check for subtitle update based on time
            # "If the audio playback time reaches a subtitle's start time... update"
            # We iterate to find if we entered a new subtitle
            found = self.subs.get_subtitle_at_time(self.current_time)
            if found and found.index - 1 != self.current_sub_index:
                self.current_sub_index = found.index - 1
                self.update_subtitle_display()
        
        self.root.after(30, self.update_ui)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceSubtitleEditor(root)
    root.mainloop()
