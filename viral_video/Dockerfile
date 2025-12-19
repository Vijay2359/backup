# Use an official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for video + ComfyUI
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app/ComfyUI

# Set working directory to ComfyUI
WORKDIR /app/ComfyUI

# Install ComfyUI dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install video processing tools
RUN pip install --no-cache-dir openai-whisper sentence-transformers tqdm scenedetect

# Expose ComfyUI default port
EXPOSE 8188

# Start ComfyUI server by default
CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188", "--cpu"]
