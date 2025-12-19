FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git wget curl build-essential libgl1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone ComfyUI repo (backend only)
RUN git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git

WORKDIR /workspace/ComfyUI

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt

# Default command will be overridden at runtime
CMD ["python", "runny1.py"]
