import re

def split_sentences(text):
    """
    Splits text into sentences using regex.
    Handles common punctuation marks like ., !, ?
    """
    # Replace newlines with spaces to treat the text as a continuous stream
    text = text.replace('\n', ' ')
    
    # Split by punctuation followed by space or end of string
    # This regex looks for (. or ! or ?) followed by a space or end of string
    # We keep the punctuation with the sentence
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter out empty strings and strip whitespace
    return [s.strip() for s in sentences if s.strip()]

def split_subtitle(text, max_chars, duration):
    """
    Splits a sentence into segments if it exceeds max_chars.
    Duration is distributed proportionally based on character count.
    
    Args:
        text (str): The sentence text.
        max_chars (int): Maximum characters per segment.
        duration (float): Total duration of the sentence audio.
        
    Returns:
        list of dict: Each dict contains 'text', 'start_ratio', 'end_ratio', 'duration'
    """
    if len(text) <= max_chars:
        return [{'text': text, 'duration': duration}]
    
    words = text.split()
    segments = []
    current_segment = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + (1 if current_segment else 0) <= max_chars:
            current_segment.append(word)
            current_length += len(word) + (1 if len(current_segment) > 1 else 0)
        else:
            segments.append(" ".join(current_segment))
            current_segment = [word]
            current_length = len(word)
            
    if current_segment:
        segments.append(" ".join(current_segment))
        
    # Calculate durations
    total_chars = len(text) # Approximation using original text length (including spaces)
    # Better to use sum of segment lengths to avoid mismatch if spaces differ
    total_segment_chars = sum(len(s) for s in segments)
    
    result = []
    for segment in segments:
        seg_len = len(segment)
        # Proportional duration
        seg_duration = (seg_len / total_segment_chars) * duration
        result.append({'text': segment, 'duration': seg_duration})
        
    return result
