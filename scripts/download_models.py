import os
import whisper
from deepface import DeepFace
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_models():
    # 1. Download Whisper Model
    logger.info("Downloading Whisper 'base' model...")
    # This will download to ~/.cache/whisper or XDG_CACHE_HOME/whisper
    whisper.load_model("base")
    logger.info("Whisper model downloaded.")

    # 2. Download DeepFace Emotion Model
    logger.info("Downloading DeepFace emotion model...")
    try:
        from deepface import DeepFace
        DeepFace.build_model("Emotion")
        logger.info("DeepFace emotion model downloaded.")
    except ImportError:
        logger.warning("DeepFace not installed. Skipping emotion model download (Lite Mode).")
    except Exception as e:
        logger.error(f"Error downloading DeepFace model: {e}")

if __name__ == "__main__":
    download_models()
