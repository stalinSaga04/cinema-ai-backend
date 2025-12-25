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
