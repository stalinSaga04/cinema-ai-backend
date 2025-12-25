from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from .utils import get_logger

logger = get_logger(__name__)

class SceneDetector:
    def __init__(self, threshold: float = 30.0):
        self.threshold = threshold

    def detect_scenes(self, video_path: str):
        """
        Detect scenes in a video.
        Returns a list of tuples (start_time, end_time).
        """
        logger.info(f"Starting scene detection for {video_path}")
        
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=self.threshold))
        
        video_manager.set_downscale_factor()
        video_manager.start()
        
        scene_manager.detect_scenes(frame_source=video_manager)
        
        scene_list = scene_manager.get_scene_list()
        
        scenes = []
        for scene in scene_list:
            start, end = scene
            scenes.append({
                "start": start.get_seconds(),
                "end": end.get_seconds()
            })
            
        logger.info(f"Detected {len(scenes)} scenes")
        return scenes
