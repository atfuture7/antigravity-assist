import datetime

def format_time(seconds):
    """
    Formats seconds into SRT time format: HH:MM:SS,mmm
    """
    td = datetime.timedelta(seconds=seconds)
    # Get total seconds
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_srt(subtitles, output_file):
    """
    Writes subtitles to an SRT file.
    
    Args:
        subtitles (list of dict): Each dict contains 'text', 'start_time', 'end_time'
        output_file (str): Path to save the SRT file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, 1):
            start = format_time(sub['start_time'])
            end = format_time(sub['end_time'])
            text = sub['text']
            
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
