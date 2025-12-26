try:
    from moviepy.editor import VideoFileClip
except ImportError:
    # Fallback for older MoviePy versions
    from moviepy import VideoFileClip
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
            
            # Check if video has audio
            if video.audio is None:
                logger.warning(f"Video {video_path} has no audio track")
                video.close()
                # Return empty audio file path or None
                return None
            
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
