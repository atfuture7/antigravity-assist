import wave
import struct
import math

# Generate 10 seconds of silence/noise
sample_rate = 44100
duration = 15 # seconds
frequency = 440.0

with wave.open('test.wav', 'w') as obj:
    obj.setnchannels(1) # mono
    obj.setsampwidth(2) # 2 bytes per sample
    obj.setframerate(sample_rate)
    
    for i in range(int(duration * sample_rate)):
        value = int(32767.0 * math.sin(frequency * math.pi * 2 * i / sample_rate))
        data = struct.pack('<h', value)
        obj.writeframesraw(data)
