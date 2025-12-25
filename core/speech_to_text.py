import whisper
from .utils import get_logger

logger = get_logger(__name__)

class SpeechToText:
    def __init__(self, model_size: str = "base"):
        logger.info(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        Returns the transcription text.
        """
        logger.info(f"Starting transcription for {audio_path}")
        try:
            result = self.model.transcribe(audio_path)
            text = result["text"]
            logger.info("Transcription completed")
            return text
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
