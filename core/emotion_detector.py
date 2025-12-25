import os
import glob
from .utils import get_logger

logger = get_logger(__name__)

class EmotionDetector:
    def __init__(self):
        pass

    def analyze_emotions(self, frames_dir: str):
        """
        Analyze emotions in a directory of frames.
        Returns a list of emotion data.
        """
        # Lazy import to avoid slow startup
        from deepface import DeepFace
        
        logger.info(f"Starting emotion analysis for frames in {frames_dir}")
        
        frame_paths = sorted(glob.glob(os.path.join(frames_dir, "*.jpg")))
        emotions = []
        
        for frame_path in frame_paths:
            try:
                # enforce_detection=False to avoid exception if no face is found
                analysis = DeepFace.analyze(img_path=frame_path, actions=['emotion'], enforce_detection=False)
                
                # DeepFace.analyze returns a list of dicts
                if isinstance(analysis, list):
                    result = analysis[0]
                else:
                    result = analysis
                
                dominant_emotion = result['dominant_emotion']
                score = result['emotion'][dominant_emotion]
                
                emotions.append({
                    "frame": os.path.basename(frame_path),
                    "emotion": dominant_emotion,
                    "score": score
                })
            except Exception as e:
                logger.warning(f"Could not analyze frame {frame_path}: {e}")
                
        logger.info(f"Analyzed emotions for {len(emotions)} frames")
        return emotions
