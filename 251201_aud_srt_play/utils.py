def ms_to_timestamp(ms):
    """Converts milliseconds to HH:MM:SS format."""
    seconds = int(ms / 1000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def timestamp_to_ms(timestamp_str):
    """Converts HH:MM:SS or MM:SS to milliseconds."""
    parts = timestamp_str.split(':')
    if len(parts) == 3:
        h, m, s = map(int, parts)
        return (h * 3600 + m * 60 + s) * 1000
    elif len(parts) == 2:
        m, s = map(int, parts)
        return (m * 60 + s) * 1000
    else:
        return 0
