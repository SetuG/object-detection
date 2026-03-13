# Filters detections down to suspicious items only,

from typing import List, Dict
from collections import defaultdict

from config.suspicious_items import COCO_SUSPICIOUS_CLASSES, MIN_FRAME_STREAK
from processing.timestamp import seconds_to_timestamp


class SuspicionTracker:
    

    def __init__(self, gap_frames: int = 15):
        
        self._streak: Dict[str, int] = defaultdict(int)       
        self._confirmed: Dict[str, bool] = defaultdict(bool)  
        self._absent: Dict[str, int] = defaultdict(int)       
        self._gap_frames = gap_frames

        
        self.events: List[Dict] = []

    def process_frame(self, detections: List[Dict], timestamp_seconds: float) -> List[Dict]:
        
        
        seen_in_frame = set()
        for det in detections:
            label = det["label"].lower()
            if label in COCO_SUSPICIOUS_CLASSES:
                seen_in_frame.add(COCO_SUSPICIOUS_CLASSES[label])

        new_events = []

        for item in list(COCO_SUSPICIOUS_CLASSES.values()):
            if item in seen_in_frame:
                self._absent[item] = 0
                self._streak[item] += 1

                # Reset confirmed flag if item disappeared long enough
                
                if (
                    self._streak[item] >= MIN_FRAME_STREAK
                    and not self._confirmed[item]
                ):
                    self._confirmed[item] = True
                    ts = seconds_to_timestamp(timestamp_seconds)
                    event = {
                        "suspicious_item": item,
                        "timestamp": ts,
                        "timestamp_seconds": round(timestamp_seconds, 2),
                    }
                    self.events.append(event)
                    new_events.append(event)
            else:
                self._streak[item] = 0
                self._absent[item] += 1

                # re-detection
                if self._absent[item] >= self._gap_frames:
                    self._confirmed[item] = False

        return new_events

    def get_results(self) -> Dict:
        
        output = {}
        counts: Dict[str, int] = defaultdict(int)

        for event in self.events:
            item = event["suspicious_item"]
            counts[item] += 1
            if counts[item] == 1:
                key = item
            else:
                
                if counts[item] == 2:
                    old_val = output.pop(item, None)
                    if old_val:
                        output[f"{item} #1"] = old_val
                key = f"{item} #{counts[item]}"
            output[key] = event["timestamp"]

        return output


def build_summary(events: List[Dict], video_metadata: dict) -> dict:
    
    result_map = {}
    counts: Dict[str, int] = defaultdict(int)

    for event in events:
        item = event["suspicious_item"]
        counts[item] += 1
        if counts[item] == 1:
            key = item
        else:
            if counts[item] == 2:
                old_val = result_map.pop(item, None)
                if old_val:
                    result_map[f"{item} #1"] = old_val
            key = f"{item} #{counts[item]}"
        result_map[key] = event["timestamp"]

    return {
        "suspicious_items": result_map,
        "total_flags": len(events),
        "video_duration": video_metadata.get("duration_seconds"),
        "resolution": video_metadata.get("resolution"),
        "fps": video_metadata.get("fps"),
    }