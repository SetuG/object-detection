# Extracts frames from a video file at a configurable sample rate

import cv2
from typing import Generator, Tuple
import logging

logger = logging.getLogger(__name__)


def extract_frames(
    video_path: str,
    sample_every_n_frames: int = 5,
) -> Generator[Tuple[int, float, any], None, None]:
    
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    logger.info(
        f"Video: {video_path} | FPS: {fps:.1f} | "
        f"Frames: {total_frames} | Duration: {duration:.1f}s"
    )

    frame_index = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_index % sample_every_n_frames == 0:
                timestamp = frame_index / fps
                yield frame_index, round(timestamp, 2), frame

            frame_index += 1
    finally:
        cap.release()
        logger.info(f"Frame extraction complete. Processed {frame_index} frames.")


def get_video_metadata(video_path: str) -> dict:
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    return {
        "fps": fps,
        "total_frames": total_frames,
        "duration_seconds": round(total_frames / fps, 2),
        "resolution": f"{width}x{height}",
    }
