# Items flagged as suspicious in an exam/test environment


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


CONFIDENCE_THRESHOLD = 0.40

# Minimum number of consecutive frames an item must appear
MIN_FRAME_STREAK = 2
