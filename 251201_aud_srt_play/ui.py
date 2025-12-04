import tkinter as tk
from tkinter import filedialog, messagebox
import pysubs2
from player import AudioPlayer
from utils import ms_to_timestamp, timestamp_to_ms

class PlayerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio & Subtitle Player")
        self.root.geometry("400x900")
        
        self.player = AudioPlayer()
        self.subs = []
        self.current_sub_index = -1
        
        # UI Elements
        self.setup_ui()
        
        # Update Loop
        self.update_interval = 50 # ms
        self.root.after(self.update_interval, self.update_loop)

    def setup_ui(self):
        # Top Frame for Time and File Selection
        top_frame = tk.Frame(self.root, bg="#333", height=50)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        
        self.time_label = tk.Label(top_frame, text="00:00:00", font=("Arial", 14), fg="white", bg="#333")
        self.time_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        load_btn = tk.Button(top_frame, text="Load Files", command=self.load_files)
        load_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Canvas for Subtitles
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bottom Frame for Controls
        control_frame = tk.Frame(self.root, bg="#444", height=100)
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Seek Frame
        seek_frame = tk.Frame(control_frame, bg="#444")
        seek_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(seek_frame, text="Seek:", fg="white", bg="#444").pack(side=tk.LEFT, padx=5)
        self.seek_entry = tk.Entry(seek_frame, width=10)
        self.seek_entry.pack(side=tk.LEFT, padx=5)
        self.seek_entry.insert(0, "00:00:00")
        
        seek_btn = tk.Button(seek_frame, text="Go", command=self.seek_to_time)
        seek_btn.pack(side=tk.LEFT, padx=5)

        # Buttons
        btn_frame = tk.Frame(control_frame, bg="#444")
        btn_frame.pack(pady=10)
        
        play_btn = tk.Button(btn_frame, text="▶ Play", command=self.play_audio, width=8)
        play_btn.pack(side=tk.LEFT, padx=5)
        
        pause_btn = tk.Button(btn_frame, text="⏸ Pause", command=self.pause_audio, width=8)
        pause_btn.pack(side=tk.LEFT, padx=5)
        
        stop_btn = tk.Button(btn_frame, text="⏹ Stop", command=self.stop_audio, width=8)
        stop_btn.pack(side=tk.LEFT, padx=5)

    def load_files(self):
        audio_file = filedialog.askopenfilename(title="Select Audio File", filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        if not audio_file: return
        
        srt_file = filedialog.askopenfilename(title="Select Subtitle File", filetypes=[("Subtitle Files", "*.srt")])
        if not srt_file: return
        
        try:
            self.player.load(audio_file)
            self.subs = pysubs2.load(srt_file)
            messagebox.showinfo("Success", "Files loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load files: {e}")

    def play_audio(self):
        if self.player.paused:
            self.player.unpause()
        else:
            # If stopped or new, play from current seek time or 0?
            # Usually play button just plays. If we want to resume, unpause covers it.
            # If we are stopped, get_time is 0.
            current_ms = self.player.get_time()
            self.player.play(current_ms)

    def pause_audio(self):
        self.player.pause()

    def stop_audio(self):
        self.player.stop()
        self.update_display(0)

    def seek_to_time(self):
        time_str = self.seek_entry.get()
        try:
            ms = timestamp_to_ms(time_str)
            # Find closest subtitle
            # Requirement: "find the subtitle line whose start time is closest to, or just before, the entered time"
            # We can just set the time. The update loop will handle finding the subtitle.
            self.player.play(ms)
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM:SS")

    def update_loop(self):
        if self.player.is_playing():
            current_ms = self.player.get_time()
            self.update_display(current_ms)
        elif self.player.paused:
            pass # Do nothing if paused, display stays static
        else:
            # If stopped, maybe show 0?
            pass
            
        self.root.after(self.update_interval, self.update_loop)

    def update_display(self, current_ms):
        # Update Time Label
        self.time_label.config(text=ms_to_timestamp(current_ms))
        
        # Find active subtitle (the one that should be centered)
        # "When a subtitle's start time matches the audio playback time, that specific subtitle must always be positioned in the center"
        # We'll select the subtitle with the largest start_time <= current_ms
        
        target_idx = -1
        for i, sub in enumerate(self.subs):
            if sub.start <= current_ms:
                target_idx = i
            else:
                break
        
        self.canvas.delete("all")
        center_y = self.canvas.winfo_height() / 2
        
        # If no subtitle has started yet, maybe show the first one below center?
        # Or just show nothing centered.
        # Let's assume if target_idx is -1, we just draw from 0 downwards starting below center?
        # Or maybe we just don't draw anything centered.
        
        # Draw centered subtitle
        if target_idx != -1:
            bbox = self.draw_subtitle(target_idx, center_y, anchor="center")
            
            # Draw previous subtitles (going up)
            if bbox:
                # Start just above the centered text
                # bbox is (x1, y1, x2, y2)
                # y1 is top, y2 is bottom
                current_bottom_y = bbox[1] - 10 # 10px padding
                
                for i in range(target_idx - 1, -1, -1):
                    if current_bottom_y < 0:
                        break
                    # We draw with anchor="s" (south/bottom) so we can place it at current_bottom_y
                    bbox_prev = self.draw_subtitle(i, current_bottom_y, anchor="s")
                    if bbox_prev:
                        current_bottom_y = bbox_prev[1] - 10

            # Draw next subtitles (going down)
            if bbox:
                current_top_y = bbox[3] + 10 # 10px padding
                
                for i in range(target_idx + 1, len(self.subs)):
                    if current_top_y > self.canvas.winfo_height():
                        break
                    bbox_next = self.draw_subtitle(i, current_top_y, anchor="n")
                    if bbox_next:
                        current_top_y = bbox_next[3] + 10
        else:
            # No subtitle started yet. Draw all from index 0 starting somewhat below center?
            # Or just wait.
            # Let's draw index 0 at center + offset?
            # User said "pulling the upcoming lines up from the bottom".
            # If nothing started, maybe they are all below?
            # Let's just draw starting from 0 at center + some offset?
            # Or just leave blank until first one starts.
            # Let's try drawing index 0 slightly below center to indicate it's coming.
            
            current_top_y = center_y + 50
            for i in range(0, len(self.subs)):
                if current_top_y > self.canvas.winfo_height():
                    break
                bbox_next = self.draw_subtitle(i, current_top_y, anchor="n")
                if bbox_next:
                    current_top_y = bbox_next[3] + 10

    def draw_subtitle(self, index, y_pos, anchor="center"):
        text = self.subs[index].text
        text = text.replace("\\N", "\n")
        
        # Determine style
        # If this is the one we are calling "active" (passed as target_idx logic in caller), it gets highlighted.
        # But here we just get index. We need to know if it's the active one.
        # The caller knows.
        # Actually, the caller calls this.
        # Let's check against current time again or pass a flag?
        # Simpler: The caller is drawing the "centered" one specifically.
        # But wait, draw_subtitle logic inside used to check anchor="center" to decide color.
        # I should keep that logic or make it explicit.
        
        if anchor == "center":
            font = ("Arial", 16, "bold")
            color = "yellow"
        else:
            font = ("Arial", 12, "bold")
            color = "white"
            
        # We need x position to be center of window
        x_pos = self.canvas.winfo_width() / 2
        
        item = self.canvas.create_text(x_pos, y_pos, text=text, fill=color, font=font, width=350, justify=tk.CENTER, anchor=anchor)
        return self.canvas.bbox(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerUI(root)
    root.mainloop()
