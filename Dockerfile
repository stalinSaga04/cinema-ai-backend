# Production Dockerfile for Cinema AI Backend
# Optimized for heavy ML dependencies (TensorFlow, Torch, DeepFace, Whisper)

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libfreetype6-dev \
    fontconfig \
    build-essential \
    wget \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy only the download script first to cache models
COPY scripts/download_models.py scripts/
RUN python scripts/download_models.py || echo "Model download failed, will retry at runtime"

# Copy the rest of the application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs/frames outputs/audio

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Start command using uvicorn (FastAPI's recommended server)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
