# Converts raw frame numbers to readable timestamps

def frame_to_timestamp(frame_index: int, fps: float) -> str:
    
    total_seconds = frame_index / fps
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:06.3f}"


def seconds_to_timestamp(seconds: float) -> str:
    
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"
