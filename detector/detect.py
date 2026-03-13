# detector/detect.py
# Runs YOLO inference on a single frame and returns raw detections

from typing import List, Dict
import numpy as np
from ultralytics import YOLO

from config.suspicious_items import CONFIDENCE_THRESHOLD


def detect_objects(model: YOLO, frame: np.ndarray) -> List[Dict]:
    
    results = model(frame, verbose=False)
    detections: List[Dict] = []

    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue

        for box in boxes:
            confidence = float(box.conf[0])
            if confidence < CONFIDENCE_THRESHOLD:
                continue

            class_id = int(box.cls[0])
            label = model.names[class_id]
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append(
                {
                    "label": label,
                    "confidence": round(confidence, 3),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                }
            )

    return detections