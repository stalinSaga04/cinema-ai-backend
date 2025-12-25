import os
import json
import threading
from typing import Dict, Any
from .utils import get_logger, ensure_directory
from .frame_extractor import FrameExtractor
from .audio_extractor import AudioExtractor
from .speech_to_text import SpeechToText
from .scene_detector import SceneDetector
from .emotion_detector import EmotionDetector

logger = get_logger(__name__)

class BrainController:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.uploads_dir = os.path.join(base_dir, "uploads")
        self.outputs_dir = os.path.join(base_dir, "outputs")
        
        ensure_directory(self.uploads_dir)
        ensure_directory(self.outputs_dir)
        
        self.processing_status: Dict[str, Dict[str, Any]] = {}
        
        # Initialize modules
        self.frame_extractor = FrameExtractor(output_dir=os.path.join(self.outputs_dir, "frames"))
        self.audio_extractor = AudioExtractor(output_dir=os.path.join(self.outputs_dir, "audio"))
        self.speech_to_text = SpeechToText()
        self.scene_detector = SceneDetector()
        self.emotion_detector = EmotionDetector()

    def start_processing(self, video_id: str, video_path: str):
        """
        Start processing a video in a background thread.
        """
        self.processing_status[video_id] = {"status": "processing", "progress": 0}
        
        thread = threading.Thread(target=self._process_video, args=(video_id, video_path))
        thread.start()

    def _process_video(self, video_id: str, video_path: str):
        try:
            logger.info(f"Processing video {video_id}")
            
            # 1. Extract Audio & Transcribe
            self.processing_status[video_id]["status"] = "extracting_audio"
            audio_path = self.audio_extractor.extract_audio(video_path)
            
            self.processing_status[video_id]["status"] = "transcribing"
            transcript = self.speech_to_text.transcribe(audio_path)
            
            # 2. Extract Frames
            self.processing_status[video_id]["status"] = "extracting_frames"
            # Create a specific directory for this video's frames to avoid collisions
            video_frames_dir = os.path.join(self.outputs_dir, "frames", video_id)
            ensure_directory(video_frames_dir)
            # Temporarily override output dir for this call
            original_frames_dir = self.frame_extractor.output_dir
            self.frame_extractor.output_dir = video_frames_dir
            frame_count = self.frame_extractor.extract_frames(video_path)
            self.frame_extractor.output_dir = original_frames_dir # Restore
            
            # 3. Detect Scenes
            self.processing_status[video_id]["status"] = "detecting_scenes"
            scenes = self.scene_detector.detect_scenes(video_path)
            
            # 4. Detect Emotions
            self.processing_status[video_id]["status"] = "detecting_emotions"
            emotions = self.emotion_detector.analyze_emotions(video_frames_dir)
            
            # 5. Compile Result
            result = {
                "id": video_id,
                "file": os.path.basename(video_path),
                "frame_count": frame_count,
                "transcript": transcript,
                "scenes": scenes,
                "emotions": emotions
            }
            
            # Save JSON
            output_json_path = os.path.join(self.outputs_dir, f"{video_id}.json")
            with open(output_json_path, "w") as f:
                json.dump(result, f, indent=2)
                
            self.processing_status[video_id] = {"status": "completed", "result_path": output_json_path}
            logger.info(f"Processing completed for {video_id}")
            
        except Exception as e:
            logger.error(f"Processing failed for {video_id}: {e}")
            self.processing_status[video_id] = {"status": "failed", "error": str(e)}

    def get_status(self, video_id: str):
        return self.processing_status.get(video_id, {"status": "not_found"})

    def get_result(self, video_id: str):
        status = self.get_status(video_id)
        if status["status"] == "completed":
            with open(status["result_path"], "r") as f:
                return json.load(f)
        return None
