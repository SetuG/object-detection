# Handles loading and caching the YOLOv8 model

from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

_model_cache = {}


def load_model(model_name: str = "yolov8n.pt") -> YOLO:
    
    if model_name not in _model_cache:
        logger.info(f"Loading YOLO model: {model_name}")
        _model_cache[model_name] = YOLO(model_name)
        logger.info(f"Model {model_name} loaded successfully.")
    return _model_cache[model_name]