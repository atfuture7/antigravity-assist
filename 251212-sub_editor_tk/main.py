import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from waveform_widget import WaveformWidget
from subtitle_manager import SubtitleManager
from audio_handler import AudioHandler

class VoiceSubtitleEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Subtitle Editor")
        self.root.geometry("500x850")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Managers
        self.audio = AudioHandler()
        self.subs = SubtitleManager()
        
        # State
        self.current_sub_index = 0 
        self.current_time = 0.0
        
        # UI Setup
        self.setup_ui()
        
        # Timer
        self.update_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10))

        # Main container frame
        main_frame = ttk.Frame(self.root, padding="50 30 50 30")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure columns
        for i in range(4):
            main_frame.columnconfigure(i, weight=1)

        # --- Row 0: Time Display ---
        self.a_time = ttk.Label(main_frame, text="00:00.00", anchor="center", font=("Arial", 24))
        self.a_time.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 20))

        # --- Row 1: Waveform (Canvas) ---
        self.a_wave = WaveformWidget(main_frame, bg="#d0d0d0", highlightthickness=1, highlightbackground="gray", on_marker_change=self.update_subtitle_timing)
        self.a_wave.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 20))
        main_frame.rowconfigure(1, weight=1)

        # --- Row 2: Control Buttons ---
        self.b_load = ttk.Button(main_frame, text="Load", command=self.load_file)
        self.b_load.grid(row=2, column=0, sticky="ew", padx=2, ipady=5)

        self.b_play = ttk.Button(main_frame, text="Play", command=self.play_audio)
        self.b_play.grid(row=2, column=1, sticky="ew", padx=2, ipady=5)

        self.b_pause = ttk.Button(main_frame, text="Pause", command=self.pause_audio, state=tk.DISABLED)
        self.b_pause.grid(row=2, column=2, sticky="ew", padx=2, ipady=5)

        self.b_save = ttk.Button(main_frame, text="Save", command=self.save_file)
        self.b_save.grid(row=2, column=3, sticky="ew", padx=2, ipady=5)

        main_frame.rowconfigure(2, minsize=60)

        # --- Row 3: Subtitle Input ---
        self.i_sub = tk.Text(main_frame, height=5, width=40, bg="#2a2e37", fg="white", insertbackground="white")
        self.i_sub.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 20))
        self.i_sub.bind('<KeyRelease>', self.on_text_change)

        # --- Row 4: Bottom Navigation & Info ---
        self.b_up = ttk.Button(main_frame, text="Up", command=self.prev_sub)
        self.b_up.grid(row=4, column=0, sticky="ew", padx=2, ipady=5)

        self.a_on_show = ttk.Label(main_frame, text="Line #", anchor="center")
        self.a_on_show.grid(row=4, column=1, sticky="ew", padx=2)

        self.i_no = ttk.Entry(main_frame, width=5)
        self.i_no.insert(0, "1")
        self.i_no.grid(row=4, column=2, sticky="ew", padx=2)
        
        self.b_down = ttk.Button(main_frame, text="Down", command=self.next_sub)
        self.b_down.grid(row=4, column=3, sticky="ew", padx=2, ipady=5)

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
        self.a_wave.load_audio(audio_path)
        self.subs.load_srt(srt_path)
        
        if self.subs.subtitles:
            self.current_sub_index = 0
            self.update_subtitle_display()
            
        self.current_time = 0.0
        self.a_wave.set_position(0.0)

    def play_audio(self):
        if not self.subs.subtitles:
            self.audio.play(self.current_time)
            self.update_button_states(playing=True)
            return

        # Check and validate index from i_no
        try:
            val = int(self.i_no.get())
        except ValueError:
            val = 1
            
        # Clamp value
        total_subs = len(self.subs.subtitles)
        if val < 1:
            val = 1
        elif val > total_subs:
            val = total_subs
            
        # Update Entry
        self.i_no.delete(0, tk.END)
        self.i_no.insert(0, str(val))
        
        # Update current index
        self.current_sub_index = val - 1
        
        # NOTE: If we jump to a new subtitle, we should probably update the display
        # to match that subtitle's text/waveform, then play.
        # However, update_subtitle_display updates i_no, so we might have a loop if not careful.
        # But here we just set i_no to val, so update_subtitle_display setting it to val again is fine.
        self.update_subtitle_display()

        # Jump to start of current subtitle
        sub = self.subs.subtitles[self.current_sub_index]
        start_time = sub.start_time
        self.audio.play(start_time)
            
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
            self.b_load.config(state=tk.DISABLED)
            self.b_play.config(state=tk.DISABLED)
            self.b_save.config(state=tk.DISABLED)
            self.b_pause.config(state=tk.NORMAL)
            
            # Disable navigation
            self.b_up.config(state=tk.DISABLED)
            self.b_down.config(state=tk.DISABLED)
        else:
            self.b_load.config(state=tk.NORMAL)
            self.b_play.config(state=tk.NORMAL)
            self.b_save.config(state=tk.NORMAL)
            self.b_pause.config(state=tk.DISABLED)
            
            self.update_nav_buttons()

    def update_nav_buttons(self):
        if not self.subs.subtitles:
            self.b_up.config(state=tk.DISABLED)
            self.b_down.config(state=tk.DISABLED)
            return
            
        self.b_up.config(state=tk.NORMAL if self.current_sub_index > 0 else tk.DISABLED)
        self.b_down.config(state=tk.NORMAL if self.current_sub_index < len(self.subs.subtitles) - 1 else tk.DISABLED)

    def prev_sub(self):
        if self.current_sub_index > 0:
            self.current_sub_index -= 1
            self.update_subtitle_display()

    def next_sub(self):
        if self.current_sub_index < len(self.subs.subtitles) - 1:
            self.current_sub_index += 1
            self.update_subtitle_display()

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
        self.i_sub.delete(1.0, tk.END)
        self.i_sub.insert(tk.END, sub.text)
        
        # Update Index Label
        self.i_no.delete(0, tk.END)
        self.i_no.insert(0, str(sub.index))
        
        # Update Markers on Waveform
        self.a_wave.set_markers(sub.start_time, sub.end_time)
        
        # Update Nav Buttons
        self.update_nav_buttons()

    def update_ui(self):
        if self.audio.is_playing():
            self.current_time = self.audio.get_current_time()
            self.a_wave.set_position(self.current_time)
            
            # Format time
            mins = int(self.current_time // 60)
            secs = int(self.current_time % 60)
            frac = int((self.current_time * 100) % 100)
            self.a_time.config(text=f"{mins:02}:{secs:02}.{frac:02}")
            
            # Check for subtitle update based on time
            # "If the audio playback time reaches a subtitle's start time... update"
            # We iterate to find if we entered a new subtitle
            found = self.subs.get_subtitle_at_time(self.current_time)
            if found and found.index - 1 != self.current_sub_index:
                self.current_sub_index = found.index - 1
                self.update_subtitle_display()
        
        self.root.after(30, self.update_ui)

    def on_text_change(self, event):
        if self.subs.subtitles:
             text = self.i_sub.get("1.0", "end-1c")
             self.subs.subtitles[self.current_sub_index].text = text

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceSubtitleEditor(root)
    root.mainloop()
