import re
import sys
import datetime
from datetime import timedelta

def parse_time(time_str):
    """Parses an SRT time string (HH:MM:SS,mmm) into a timedelta."""
    try:
        # Handle comma or dot for milliseconds
        time_str = time_str.replace('.', ',')
        hours, minutes, rest = time_str.split(':')
        seconds, milliseconds = rest.split(',')
        return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds), milliseconds=int(milliseconds))
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM:SS,mmm")

def format_time(td):
    """Formats a timedelta into an SRT time string (HH:MM:SS,mmm)."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def parse_srt(filename):
    """Parses an SRT file into a list of blocks."""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by double newlines, but handle potential extra whitespace
    raw_blocks = re.split(r'\n\s*\n', content.strip())
    blocks = []
    
    for rb in raw_blocks:
        lines = rb.strip().split('\n')
        if len(lines) >= 3:
            index = lines[0]
            time_line = lines[1]
            text = '\n'.join(lines[2:])
            
            # Parse times
            if '-->' in time_line:
                start_str, end_str = time_line.split('-->')
            else:
                # Fallback or error
                raise ValueError(f"Invalid time line format: {time_line}")
                
            start_time = parse_time(start_str.strip())
            end_time = parse_time(end_str.strip())
            
            blocks.append({
                'index': index,
                'start': start_time,
                'end': end_time,
                'text': text
            })
    return blocks

def save_srt(blocks, filename):
    """Saves a list of blocks to an SRT file."""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, block in enumerate(blocks):
            f.write(f"{i + 1}\n")
            f.write(f"{format_time(block['start'])} --> {format_time(block['end'])}\n")
            f.write(f"{block['text']}\n\n")

def get_user_input():
    filename = input("Enter the subtitle filename (e.g., video.srt): ").strip()
    pivot_str = input("Enter the pivot time (HH:MM:SS,mmm): ").strip()
    pivot_time = parse_time(pivot_str)
    
    print("Select mode:")
    print("1. Extend (Shift Backward/Later)")
    print("2. Reduce (Shift Forward/Earlier)")
    mode_choice = input("Enter choice (1 or 2): ").strip()
    
    mode = 'extend' if mode_choice == '1' else 'reduce'
    
    shift_amount = None
    source_time = None
    
    if mode == 'extend':
        shift_str = input("Enter shift amount (seconds, e.g., 2.5): ").strip()
        shift_amount = timedelta(seconds=float(shift_str))
    elif mode == 'reduce':
        source_str = input("Enter the time to move (HH:MM:SS,mmm): ").strip()
        source_time = parse_time(source_str)
        
    return filename, pivot_time, mode, shift_amount, source_time

def adjust_subtitles(filename, pivot_time, mode, shift_amount=None, source_time=None):
    blocks = parse_srt(filename)
    
    # Find target block: first block where start > pivot_time
    target_index = -1
    for i, block in enumerate(blocks):
        if block['start'] > pivot_time:
            target_index = i
            break
            
    if target_index == -1:
        print("No subtitle block found after the specified pivot time.")
        return

    if mode == 'reduce':
        if source_time is None:
            print("Error: source_time is required for reduce mode.")
            return

        # Find the block to move (move_block)
        # 1. If source_time is inside a block (start <= source < end), that's the block.
        # 2. Otherwise, it's the first block where start >= source_time.
        move_block_index = -1
        for i, block in enumerate(blocks):
            if block['start'] <= source_time < block['end']:
                move_block_index = i
                break
            if block['start'] >= source_time:
                move_block_index = i
                break
        
        if move_block_index == -1:
             print("No suitable subtitle block found for the given source time.")
             return

        target_block = blocks[move_block_index]
        
        # Calculate shift: how much we are moving the target BACK (earlier)
        # The target's NEW start will be pivot_time.
        # So shift = target.start - pivot_time (this is a positive duration)
        shift = target_block['start'] - pivot_time
        
        print(f"Target block found at {format_time(target_block['start'])} (Index {target_block['index']}). shifting to {format_time(pivot_time)}.")
        print(f"Shift amount: {shift.total_seconds()}s")

        # Delete intermediate blocks
        # We need to remove blocks that fall between pivot_time and target_block['start']
        # Specifically, any block BEFORE the move_block that ends AFTER the pivot_time (new start)
        # will overlap with the shifted content.
        
        blocks_to_keep = []
        # Iterate up to move_block_index
        for i in range(move_block_index):
            # Check if this block overlaps with the new start time (Pivot)
            # Overlap condition: Block.End > Pivot
            if blocks[i]['end'] > pivot_time:
                print(f"Deleting intermediate/overlapping block {blocks[i]['index']} ({format_time(blocks[i]['start'])} --> {format_time(blocks[i]['end'])})")
                continue # Skip/Delete
            blocks_to_keep.append(blocks[i])
            
        # Now process Target and subsequent
        shifted_blocks = []
        for i in range(move_block_index, len(blocks)):
            block = blocks[i]
            block['start'] -= shift
            block['end'] -= shift
            shifted_blocks.append(block)
            
        final_blocks = blocks_to_keep + shifted_blocks
        blocks = final_blocks

    elif mode == 'extend':
        # Shift Target and subsequent by +shift_amount
        print(f"Target block found at {format_time(blocks[target_index]['start'])}. Shifting by +{shift_amount.total_seconds()}s.")
        
        for i in range(target_index, len(blocks)):
            blocks[i]['start'] += shift_amount
            blocks[i]['end'] += shift_amount
            
    # Save
    out_filename = filename.replace('.srt', '_adjusted.srt')
    if out_filename == filename:
        out_filename = filename + ".adjusted.srt"
        
    save_srt(blocks, out_filename)
    print(f"Saved adjusted subtitles to {out_filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Argument mode for testing/automation
        # python adjust_subtitles.py filename pivot_time mode [shift_amount]
        fname = sys.argv[1]
        pivot = parse_time(sys.argv[2])
        mode = sys.argv[3]
        shift = None
        source_time = None
        if mode == 'extend':
            shift = timedelta(seconds=float(sys.argv[4]))
        elif mode == 'reduce':
            source_time = parse_time(sys.argv[4])
        adjust_subtitles(fname, pivot, mode, shift, source_time)
    else:
        # Interactive mode
        try:
            f, p, m, s, src = get_user_input()
            adjust_subtitles(f, p, m, s, src)
        except Exception as e:
            print(f"Error: {e}")
