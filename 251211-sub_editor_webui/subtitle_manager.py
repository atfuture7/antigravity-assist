import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Subtitle:
    index: int
    start_time: float  # in seconds
    end_time: float    # in seconds
    text: str

    @property
    def duration(self):
        return self.end_time - self.start_time

class SubtitleManager:
    def __init__(self):
        self.subtitles: List[Subtitle] = []
        self.filepath: Optional[str] = None

    def load_srt(self, filepath: str):
        self.filepath = filepath
        self.subtitles = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by double newlines, handling potential variations
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Index
                try:
                    index = int(lines[0].strip())
                except ValueError:
                    continue # Skip malformed blocks
                
                # Time
                time_line = lines[1].strip()
                match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})', time_line)
                if match:
                    h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
                    start = h1*3600 + m1*60 + s1 + ms1/1000.0
                    end = h2*3600 + m2*60 + s2 + ms2/1000.0
                    
                    # Text (rest of the lines)
                    text = '\n'.join(lines[2:])
                    
                    self.subtitles.append(Subtitle(index, start, end, text))

    def save_srt(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(self.subtitles):
                # Update index to match position in list (1-based)
                sub.index = i + 1
                
                start_h = int(sub.start_time // 3600)
                start_m = int((sub.start_time % 3600) // 60)
                start_s = int(sub.start_time % 60)
                start_ms = int((sub.start_time * 1000) % 1000)
                
                end_h = int(sub.end_time // 3600)
                end_m = int((sub.end_time % 3600) // 60)
                end_s = int(sub.end_time % 60)
                end_ms = int((sub.end_time * 1000) % 1000)
                
                time_str = f"{start_h:02}:{start_m:02}:{start_s:02},{start_ms:03} --> {end_h:02}:{end_m:02}:{end_s:02},{end_ms:03}"
                
                f.write(f"{sub.index}\n{time_str}\n{sub.text}\n\n")

    def get_subtitle_at_time(self, time: float) -> Optional[Subtitle]:
        # Find subtitle that contains time
        for sub in self.subtitles:
            if sub.start_time <= time <= sub.end_time:
                return sub
        return None

    def get_subtitle_by_index(self, index: int) -> Optional[Subtitle]:
        # 1-based index
        if 1 <= index <= len(self.subtitles):
            return self.subtitles[index - 1]
        return None
