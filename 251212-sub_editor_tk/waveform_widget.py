import tkinter as tk
import subprocess
import struct
import array
import math

class WaveformWidget(tk.Canvas):
    def __init__(self, master, on_marker_change=None, **kwargs):
        if 'bg' not in kwargs:
            kwargs['bg'] = 'black'
        super().__init__(master, **kwargs)
        self.on_marker_change = on_marker_change
        self.audio_data = None # array of min/max pairs
        self.sample_rate = 100 # Visual sample rate (envelopes per second)
        self.duration = 0
        self.current_time = 0
        self.visible_duration = 30 # 30 seconds
        
        # Markers
        self.start_marker_time = None
        self.end_marker_time = None
        
        # Dragging state
        self.dragging_marker = None # 'start' or 'end'
        self.drag_start_y = 0
        
        # Bindings
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<ButtonRelease-1>', self.on_release)

    def load_audio(self, filepath):
        # Use ffmpeg to decode to raw s16le, 8000Hz, mono
        # 8000Hz is enough for visual, and easy to downsample to 100Hz
        cmd = [
            'ffmpeg',
            '-i', filepath,
            '-f', 's16le',
            '-ac', '1',
            '-ar', '8000',
            '-v', 'quiet',
            '-'
        ]
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            raw_data, _ = process.communicate()
            
            if not raw_data:
                print("Failed to read audio data")
                return

            # Convert to array of shorts
            samples = array.array('h', raw_data)
            total_samples = len(samples)
            original_rate = 8000
            self.duration = total_samples / original_rate
            
            # Downsample to self.sample_rate (100Hz)
            # We need 1 min/max pair for every (8000/100) = 80 samples
            chunk_size = int(original_rate / self.sample_rate)
            
            envelope = array.array('h')
            
            for i in range(0, total_samples, chunk_size):
                chunk = samples[i:i+chunk_size]
                if not chunk:
                    break
                envelope.append(min(chunk))
                envelope.append(max(chunk))
                
            self.audio_data = envelope
            self.redraw()
            
        except Exception as e:
            print(f"Error processing waveform: {e}")

    def set_position(self, time):
        self.current_time = time
        self.redraw()

    def set_markers(self, start, end):
        self.start_marker_time = start
        self.end_marker_time = end
        self.redraw()

    def redraw(self):
        self.delete('all')
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return

        # Draw Center Line (Current Time)
        center_y = height / 2
        self.create_line(0, center_y, width, center_y, fill='red', dash=(4, 4))
        
        if not self.audio_data:
            return

        # Calculate visible range
        # Top (y=0) is current_time - visible_duration/2
        # Bottom (y=height) is current_time + visible_duration/2
        
        half_window = self.visible_duration / 2
        start_time = self.current_time - half_window
        end_time = self.current_time + half_window
        
        # Convert to envelope indices
        # envelope has 2 values per time step (min, max)
        # index = time * sample_rate * 2
        
        start_idx = int(start_time * self.sample_rate) * 2
        end_idx = int(end_time * self.sample_rate) * 2
        
        # Clamp
        data_len = len(self.audio_data)
        
        # We iterate pixels or data?
        # Iterating data is better if data density < pixel density.
        # Here sample_rate is 100Hz. 
        # Height is ~1000px. Visible duration 180s.
        # 180s * 100Hz = 18000 points.
        # 18000 points on 1000px is dense.
        # So we should iterate pixels?
        # No, iterating data allows drawing the detailed waveform.
        # 18000 points is fine for create_line.
        
        # Map time to Y
        # y = (time - start_time) / visible_duration * height
        
        points = []
        scale_x = width / 2 / 32768 # Normalize 16-bit to half width
        
        # Optimization: Only draw if valid range
        iter_start = max(0, start_idx)
        iter_end = min(data_len, end_idx)
        
        # Ensure alignment to pairs
        if iter_start % 2 != 0: iter_start -= 1
        
        # Step size? If too many points, skip?
        # 18000 points is okay.
        
        for i in range(iter_start, iter_end, 2):
            min_val = self.audio_data[i]
            max_val = self.audio_data[i+1]
            
            # Time for this data point
            # index i corresponds to i/2 sample index
            t = (i / 2) / self.sample_rate
            
            y = (t - start_time) / self.visible_duration * height
            
            # Draw horizontal line at y from min to max?
            # Or draw continuous line?
            # Usually waveform is symmetric around center X.
            # So min_val is negative, max_val is positive.
            # x_center = width / 2
            # x_left = x_center + min_val * scale_x
            # x_right = x_center + max_val * scale_x
            # We can draw a horizontal line for this sample.
            
            x_center = width / 2
            x_left = x_center + min_val * scale_x
            x_right = x_center + max_val * scale_x
            
            self.create_line(x_left, y, x_right, y, fill='green')

        # Draw Markers
        if self.start_marker_time is not None:
            y_start = (self.start_marker_time - start_time) / self.visible_duration * height
            if 0 <= y_start <= height:
                self.create_line(0, y_start, width, y_start, fill='yellow', width=2)
                self.create_text(10, y_start, text="START", anchor='w', fill='yellow')

        if self.end_marker_time is not None:
            y_end = (self.end_marker_time - start_time) / self.visible_duration * height
            if 0 <= y_end <= height:
                self.create_line(0, y_end, width, y_end, fill='orange', width=2)
                self.create_text(10, y_end, text="END", anchor='w', fill='orange')

    def on_click(self, event):
        if not self.audio_data:
            return
            
        height = self.winfo_height()
        half_window = self.visible_duration / 2
        start_time = self.current_time - half_window
        
        # Check start marker
        if self.start_marker_time is not None:
            y_start = (self.start_marker_time - start_time) / self.visible_duration * height
            if abs(event.y - y_start) < 10: # 10px tolerance
                self.dragging_marker = 'start'
                return

        # Check end marker
        if self.end_marker_time is not None:
            y_end = (self.end_marker_time - start_time) / self.visible_duration * height
            if abs(event.y - y_end) < 10:
                self.dragging_marker = 'end'
                return

    def on_drag(self, event):
        if not self.dragging_marker:
            return
            
        height = self.winfo_height()
        half_window = self.visible_duration / 2
        start_time = self.current_time - half_window
        
        # Calculate new time from Y
        # y = (time - start_time) / visible_duration * height
        # time = (y / height * visible_duration) + start_time
        
        new_time = (event.y / height * self.visible_duration) + start_time
        
        if self.dragging_marker == 'start':
            self.start_marker_time = new_time
        elif self.dragging_marker == 'end':
            self.end_marker_time = new_time
            
        self.redraw()

    def on_release(self, event):
        if self.dragging_marker and self.on_marker_change:
            time = self.start_marker_time if self.dragging_marker == 'start' else self.end_marker_time
            self.on_marker_change(self.dragging_marker, time)
            
        self.dragging_marker = None


