# FastAPI server

import os
import uuid
import logging
import tempfile
import base64
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse

from detector.model import load_model
from detector.detect import detect_objects
from processing.video_reader import extract_frames, get_video_metadata
from processing.postprocess import SuspicionTracker, build_summary


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Cheat Detection API",
    description="Upload an exam video; receive timestamps of suspicious objects.",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    logger.info("Pre-loading YOLO model...")
    load_model("yolov8n.pt")
    logger.info("Model ready.")



@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/detect-suspicious")
async def detect_suspicious(
    file: UploadFile = File(..., description="Video file to analyse"),
    sample_rate: int = Query(
        default=5,
        ge=1,
        le=30,
        description="Process every Nth frame. Lower = slower but more precise.",
    ),
    model_size: str = Query(
        default="yolov8n.pt",
        description="YOLO model variant: yolov8n.pt | yolov8s.pt | yolov8m.pt",
    ),
):
    

    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    suffix = Path(file.filename or "video.mp4").suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. "
                   f"Allowed: {', '.join(allowed_extensions)}",
        )


    tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{suffix}")
    try:
        content = await file.read()
        with open(tmp_path, "wb") as f:
            f.write(content)
        logger.info(f"Saved upload to {tmp_path} ({len(content)/1024:.1f} KB)")


        model = load_model(model_size)

        metadata = get_video_metadata(tmp_path)
        logger.info(f"Video metadata: {metadata}")

        tracker = SuspicionTracker()
        frames_processed = 0

        for frame_idx, timestamp, frame in extract_frames(tmp_path, sample_rate):
            detections = detect_objects(model, frame)
            new_events = tracker.process_frame(detections, timestamp)

            for evt in new_events:
                logger.info(
                    f"  ⚠ FLAGGED  '{evt['suspicious_item']}'  "
                    f"@ {evt['timestamp']}  (frame {frame_idx})"
                )

            frames_processed += 1

        logger.info(
            f"Done. Frames processed: {frames_processed} | "
            f"Events: {len(tracker.events)}"
        )


        summary = build_summary(tracker.events, metadata)

        return JSONResponse(
            content={

                **summary["suspicious_items"],
                
                "_meta": {
                    "total_flags": summary["total_flags"],
                    "video_duration_seconds": summary["video_duration"],
                    "resolution": summary["resolution"],
                    "fps": summary["fps"],
                    "frames_analysed": frames_processed,
                    "sample_rate": sample_rate,
                    "model": model_size,
                },
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during detection")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)



# RUNPOD HANDLER - RUNPOD_MODE=1


def _run_detection(video_bytes: bytes, sample_rate: int, model_size: str) -> dict:
    """
    Core detection logic shared by both FastAPI and RunPod handler.
    Saves bytes to temp file, runs pipeline, returns result dict.
    """
    tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp4")

    try:
        with open(tmp_path, "wb") as f:
            f.write(video_bytes)

        model    = load_model(model_size)
        metadata = get_video_metadata(tmp_path)
        tracker  = SuspicionTracker()

        for _, timestamp, frame in extract_frames(tmp_path, sample_rate):
            detections = detect_objects(model, frame)
            tracker.process_frame(detections, timestamp)

        summary = build_summary(tracker.events, metadata)
        return {
            **summary["suspicious_items"],
            "_meta": {
                "total_flags":            summary["total_flags"],
                "video_duration_seconds": summary["video_duration"],
                "resolution":             summary["resolution"],
                "fps":                    summary["fps"],
                "model":                  model_size,
            },
        }

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if os.environ.get("RUNPOD_MODE") == "1":
    import runpod

    def runpod_handler(job):
        
        logger.info(f"RunPod job received: {job['id']}")
        job_input = job["input"]

        if "video_b64" not in job_input:
            return {"error": "Missing required field: video_b64"}

        try:
            video_bytes = base64.b64decode(job_input["video_b64"])
            sample_rate = int(job_input.get("sample_rate", 5))
            model_size  = job_input.get("model_size", "yolov8n.pt")

            result = _run_detection(video_bytes, sample_rate, model_size)
            logger.info(f"Job {job['id']} complete. Flags: {result.get('_meta', {}).get('total_flags', 0)}")
            return result

        except Exception as e:
            logger.exception(f"Job {job['id']} failed")
            return {"error": str(e)}

    
    logger.info("Starting in RunPod serverless mode...")
    load_model("yolov8n.pt")   
    runpod.serverless.start({"handler": runpod_handler})
