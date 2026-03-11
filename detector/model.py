# detector/model.py
# Handles loading and caching the YOLOv8 model

from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

_model_cache = {}


def load_model(model_name: str = "yolov8n.pt") -> YOLO:
    """
    Load a YOLOv8 model by name.
    Results are cached in memory so the model is only loaded once per process.

    Args:
        model_name: YOLOv8 model variant.
                    Options: yolov8n.pt (nano/fastest),
                             yolov8s.pt (small),
                             yolov8m.pt (medium),
                             yolov8l.pt (large),
                             yolov8x.pt (extra-large/most accurate)

    Returns:
        Loaded YOLO model instance.
    """
    if model_name not in _model_cache:
        logger.info(f"Loading YOLO model: {model_name}")
        _model_cache[model_name] = YOLO(model_name)
        logger.info(f"Model {model_name} loaded successfully.")
    return _model_cache[model_name]