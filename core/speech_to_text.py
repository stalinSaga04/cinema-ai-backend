from .utils import get_logger

logger = get_logger(__name__)

class SpeechToText:
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None

    def _load_model(self):
        if self.model is None:
            import whisper
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        Returns the transcription text.
        """
        self._load_model()
        logger.info(f"Starting transcription for {audio_path}")
        try:
            result = self.model.transcribe(audio_path)
            text = result["text"]
            logger.info("Transcription completed")
            return text
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
