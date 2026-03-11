USER / CLIENT
     │
     │  (upload video)
     ▼
FastAPI Endpoint
/detect-suspicious
     │
     ▼
Video Processor
(OpenCV frame extractor)
     │
     ▼
Object Detection Model
(YOLOv8n)
     │
     ▼
Post Processing Layer
(SuspicionTracker — streak filter + dedup)
     │
     ▼
Timestamp Generator
(frame → MM:SS.mmm)
     │
     ▼
JSON Response
