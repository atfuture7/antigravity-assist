import pygame
import os

class AudioHandler:
    def __init__(self):
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Warning: Audio device not available: {e}")
        
        self.filepath = None
        self.playing = False
        self.paused = False
        self.start_offset = 0.0
        self.duration = 0.0

    def load_file(self, filepath):
        self.filepath = filepath
        try:
            pygame.mixer.music.load(filepath)
            # Estimate duration? Pygame doesn't give duration easily for streamed music.
            # We can use wave or mutagen if needed, but for now we might not need exact duration 
            # except for clamping. We'll rely on the waveform loader to get duration if needed.
            self.playing = False
            self.paused = False
            self.start_offset = 0.0
        except pygame.error as e:
            print(f"Error loading file: {e}")

    def play(self, start_time=0.0):
        if not self.filepath:
            return
        
        try:
            # pygame.mixer.music.play(loops=0, start=start_time)
            # start argument accepts seconds
            pygame.mixer.music.play(start=start_time)
            self.start_offset = start_time
            self.playing = True
            self.paused = False
        except pygame.error as e:
            print(f"Error playing: {e}")

    def pause(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def unpause(self):
        if self.playing and self.paused:
            pygame.mixer.music.unpause()
            self.paused = False

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False

    def get_current_time(self):
        if not self.playing:
            return self.start_offset
        
        # get_pos returns ms
        pos = pygame.mixer.music.get_pos()
        if pos == -1:
            return self.start_offset
        
        return self.start_offset + (pos / 1000.0)

    def is_playing(self):
        return self.playing and not self.paused
