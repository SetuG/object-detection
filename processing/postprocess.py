# processing/postprocess.py
# Filters detections down to suspicious items only,
# deduplicates across frames, and formats the final output.

from typing import List, Dict
from collections import defaultdict

from config.suspicious_items import COCO_SUSPICIOUS_CLASSES, MIN_FRAME_STREAK
from processing.timestamp import seconds_to_timestamp


class SuspicionTracker:
    """
    Stateful tracker that:
    1. Filters raw YOLO detections to suspicious classes only.
    2. Requires MIN_FRAME_STREAK consecutive detections before reporting
       (reduces spurious single-frame false positives).
    3. Records the FIRST timestamp each item is reliably confirmed.
    4. Avoids duplicate events (same item flagged only once per appearance
       window, then resets after it disappears for >gap_frames frames).
    """

    def __init__(self, gap_frames: int = 15):
        """
        Args:
            gap_frames: If an item disappears for this many consecutive
                        sampled frames it's considered a new event next time.
        """
        self._streak: Dict[str, int] = defaultdict(int)       # item → consecutive frame count
        self._confirmed: Dict[str, bool] = defaultdict(bool)  # item → already reported?
        self._absent: Dict[str, int] = defaultdict(int)       # item → absent frame count
        self._gap_frames = gap_frames

        # Final results: list of {item, timestamp}
        self.events: List[Dict] = []

    def process_frame(self, detections: List[Dict], timestamp_seconds: float) -> List[Dict]:
        """
        Feed one frame's worth of detections into the tracker.

        Args:
            detections:        Output of detect_objects() for this frame.
            timestamp_seconds: Elapsed seconds at this frame.

        Returns:
            List of NEW suspicious events detected in this frame (may be empty).
        """
        # Collect suspicious labels seen in this frame
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
                # (handled in the absent branch below — on re-appearance
                #  the absent counter was already reset to 0 above, so
                #  nothing extra needed here)

                # Check if we've hit the streak threshold for a new event
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

                # If item has been gone long enough, allow re-detection
                if self._absent[item] >= self._gap_frames:
                    self._confirmed[item] = False

        return new_events

    def get_results(self) -> Dict:
        """
        Return the final results in the required output format:
        { "suspicious_item": "timestamp", ... }

        When the same item appears multiple times, entries are suffixed
        with an occurrence index: "cell phone #1", "cell phone #2", …
        """
        output = {}
        counts: Dict[str, int] = defaultdict(int)

        for event in self.events:
            item = event["suspicious_item"]
            counts[item] += 1
            if counts[item] == 1:
                key = item
            else:
                # Rename earlier entry too on second occurrence
                if counts[item] == 2:
                    old_val = output.pop(item, None)
                    if old_val:
                        output[f"{item} #1"] = old_val
                key = f"{item} #{counts[item]}"
            output[key] = event["timestamp"]

        return output


def build_summary(events: List[Dict], video_metadata: dict) -> dict:
    """
    Wrap events in a richer summary payload for the API response.
    """
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