from .utils import get_logger
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector

logger = get_logger(__name__)

class SceneDetector:
    def __init__(self, threshold: float = 30.0):
        self.threshold = threshold

    def detect_scenes(self, video_path: str):
        """
        Detect scenes and calculate motion scores.
        PRD 9. Video Editing Rules - Deterministic motion scoring.
        """
        logger.info(f"Starting scene detection and motion scoring for {video_path}")
        
        video = open_video(video_path)
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=self.threshold))
        
        scene_manager.detect_scenes(video=video)
        scene_list = scene_manager.get_scene_list()
        
        # Calculate motion scores using OpenCV
        import cv2
        cap = cv2.VideoCapture(video_path)
        
        scenes = []
        for scene in scene_list:
            start, end = scene
            start_frame = start.get_frames()
            end_frame = end.get_frames()
            
            # Sample frames to calculate motion
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            ret, prev_frame = cap.read()
            if not ret: continue
            
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            total_diff = 0
            count = 0
            
            # Sample every 10th frame for efficiency
            for f in range(start_frame + 10, end_frame, 10):
                cap.set(cv2.CAP_PROP_POS_FRAMES, f)
                ret, frame = cap.read()
                if not ret: break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(gray, prev_gray)
                total_diff += diff.mean()
                prev_gray = gray
                count += 1
            
            motion_score = total_diff / count if count > 0 else 0
            
            scenes.append({
                "start_seconds": start.get_seconds(),
                "end_seconds": end.get_seconds(),
                "start_timecode": start.get_timecode(),
                "end_timecode": end.get_timecode(),
                "motion_score": float(motion_score) # PRD 9. High motion -> short cuts
            })
            
        cap.release()
        logger.info(f"Detected {len(scenes)} scenes with motion scores")
        return scenes
