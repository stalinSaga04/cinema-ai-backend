from moviepy.editor import VideoFileClip
import os
from .utils import get_logger, ensure_directory

logger = get_logger(__name__)

class AudioExtractor:
    def __init__(self, output_dir: str = "outputs/audio"):
        self.output_dir = output_dir
        ensure_directory(output_dir)

    def extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video and save as MP3.
        Returns the path to the extracted audio file.
        """
        logger.info(f"Starting audio extraction for {video_path}")
        
        try:
            video = VideoFileClip(video_path)
            filename = os.path.basename(video_path)
            audio_filename = os.path.splitext(filename)[0] + ".mp3"
            output_path = os.path.join(self.output_dir, audio_filename)
            
            video.audio.write_audiofile(output_path, logger=None)
            video.close()
            
            logger.info(f"Audio extracted to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
