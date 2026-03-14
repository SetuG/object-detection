import requests
import base64

RUNPOD_API_KEY  = "runpod api"   # Settings → API Keys on runpod.io
RUNPOD_ENDPOINT = "runpod endpoint"  # Found in your RunPod dashboard under your pod's details

# Read and encode your test video
with open(r"video_path", "rb") as f:
    video_b64 = base64.b64encode(f.read()).decode("utf-8")

print("Sending video to RunPod...")

response = requests.post(
    RUNPOD_ENDPOINT,
    headers={
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "input": {
            "video_b64": video_b64,
            "sample_rate": 5
        }
    },
    timeout=300
)

print(response.json())