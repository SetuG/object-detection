# Dockerfile — optimised for RunPod GPU workers
# Base image includes CUDA 11.8 + Python 3.10

FROM runpod/base:0.4.0-cuda11.8.0

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Pre-download YOLO weights at build time so cold starts are fast
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

EXPOSE 8000

CMD ["sh", "-c", "if [ \"$RUNPOD_MODE\" = '1' ]; then python app.py; else uvicorn app:app --host 0.0.0.0 --port 8000; fi"]