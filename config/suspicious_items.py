# config/suspicious_items.py
# Items flagged as suspicious in an exam/test environment
# These map directly to YOLO COCO class names

SUSPICIOUS_ITEMS = [
    "cell phone",
    "mobile phone",
    "book",
    "laptop",
    "keyboard",
    "remote",
    "mouse",
    "tablet",   
    "earpiece",  
    "paper",     
]


COCO_SUSPICIOUS_CLASSES = {
    "cell phone": "cell phone",
    "book": "book",
    "laptop": "laptop",
    "keyboard": "keyboard",
    "remote": "earphone / remote",
    "mouse": "mouse",
}

# Confidence threshold — detections below this are ignored
CONFIDENCE_THRESHOLD = 0.40

# Minimum number of consecutive frames an item must appear
# before it's considered a real detection (reduces false positives)
MIN_FRAME_STREAK = 2