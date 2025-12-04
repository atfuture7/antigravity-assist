import pygame
import os

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.music = pygame.mixer.music
        self.paused = False
        self.start_time_offset = 0 # ms offset when seeking
        self.last_play_time = 0 # timestamp when play started

    def load(self, filepath):
        self.music.load(filepath)

    def play(self, start_time_ms=0):
        """
        Play audio from a specific time.
        start_time_ms: Time in milliseconds to start playing from.
        """
        # pygame.mixer.music.play takes start time in seconds
        start_seconds = start_time_ms / 1000.0
        self.music.play(start=start_seconds)
        self.start_time_offset = start_time_ms
        self.paused = False
        self.last_play_time = pygame.time.get_ticks()

    def pause(self):
        self.music.pause()
        self.paused = True

    def unpause(self):
        self.music.unpause()
        self.paused = False

    def stop(self):
        self.music.stop()
        self.paused = False
        self.start_time_offset = 0

    def get_time(self):
        """Returns current playback time in milliseconds."""
        if self.music.get_busy() or self.paused:
            # get_pos returns time played since last play() call
            current_pos = self.music.get_pos()
            if current_pos == -1:
                return self.start_time_offset
            return self.start_time_offset + current_pos
        return 0

    def is_playing(self):
        return self.music.get_busy() and not self.paused
