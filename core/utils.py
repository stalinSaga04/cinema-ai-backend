import os
import logging
import uuid
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def get_logger(name: str):
    return logging.getLogger(name)

logger = get_logger(__name__)

def generate_unique_id() -> str:
    return str(uuid.uuid4())

def ensure_directory(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def get_file_extension(filename: str) -> str:
    return Path(filename).suffix

def save_upload_file(upload_file, destination: str):
    with open(destination, "wb") as buffer:
        import shutil
        shutil.copyfileobj(upload_file.file, buffer)
    logger.info(f"Saved file to {destination}")

def frame_to_timestamp(frame_number: int, fps: float = 30.0) -> str:
    """Convert frame number to timestamp format HH:MM:SS"""
    total_seconds = frame_number / fps
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_video_fps(video_path: str) -> float:
    """Get FPS of video file"""
    import cv2
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.release()
    return fps if fps > 0 else 30.0

def sample_frames_indices(total_frames: int, sample_count: int = 10) -> list:
    """Get evenly distributed frame indices for sampling"""
    if total_frames <= sample_count:
        return list(range(total_frames))
    step = total_frames // sample_count
    return [i * step for i in range(sample_count)]
