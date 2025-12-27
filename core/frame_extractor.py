import os
from .utils import get_logger, ensure_directory

logger = get_logger(__name__)

class FrameExtractor:
    def __init__(self, output_dir: str = "outputs/frames"):
        self.output_dir = output_dir
        ensure_directory(output_dir)

    def extract_frames(self, video_path: str, interval: int = 1, output_dir: str = None) -> int:
        """
        Extract frames from video at a given interval (in seconds).
        Returns the number of frames extracted.
        """
        import cv2
        target_dir = output_dir or self.output_dir
        logger.info(f"Starting frame extraction for {video_path} to {target_dir}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video file: {video_path}")
            return 0

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * interval)
        
        count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if count % frame_interval == 0:
                frame_name = os.path.join(target_dir, f"frame_{saved_count:04d}.jpg")
                cv2.imwrite(frame_name, frame)
                saved_count += 1
            
            count += 1
            
        cap.release()
        logger.info(f"Extracted {saved_count} frames to {target_dir}")
        return saved_count
