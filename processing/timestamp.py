# processing/timestamp.py
# Converts raw frame numbers to human-readable timestamps

def frame_to_timestamp(frame_index: int, fps: float) -> str:
    """
    Convert a frame index to a human-readable MM:SS.mmm timestamp string.

    Args:
        frame_index: Zero-based frame number.
        fps:         Frames per second of the source video.

    Returns:
        String like "01:23.456"
    """
    total_seconds = frame_index / fps
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:06.3f}"


def seconds_to_timestamp(seconds: float) -> str:
    """
    Convert raw seconds (float) to MM:SS.mmm string.

    Args:
        seconds: Elapsed time in seconds.

    Returns:
        String like "00:05.200"
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"