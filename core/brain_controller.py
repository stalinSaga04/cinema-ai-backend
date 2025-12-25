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
            
            # Get video FPS for timestamp conversion
            from .utils import get_video_fps, frame_to_timestamp, sample_frames_indices
            fps = get_video_fps(video_path)
            
            # 1. Extract Audio & Transcribe
            self.processing_status[video_id]["status"] = "extracting_audio"
            audio_path = self.audio_extractor.extract_audio(video_path)
            
            self.processing_status[video_id]["status"] = "transcribing"
            transcript = self.speech_to_text.transcribe(audio_path)
            
            # 2. Extract Frames
            self.processing_status[video_id]["status"] = "extracting_frames"
            video_frames_dir = os.path.join(self.outputs_dir, "frames", video_id)
            ensure_directory(video_frames_dir)
            original_frames_dir = self.frame_extractor.output_dir
            self.frame_extractor.output_dir = video_frames_dir
            frame_count = self.frame_extractor.extract_frames(video_path)
            self.frame_extractor.output_dir = original_frames_dir
            
            # 3. Detect Scenes
            self.processing_status[video_id]["status"] = "detecting_scenes"
            scenes_raw = self.scene_detector.detect_scenes(video_path)
            
            # Convert scenes to PRD format with timestamps
            scenes = []
            for scene in scenes_raw:
                start_frame = scene.get("start_frame", 0)
                end_frame = scene.get("end_frame", 0)
                scenes.append({
                    "start": frame_to_timestamp(start_frame, fps),
                    "end": frame_to_timestamp(end_frame, fps)
                })
            
            # 4. Detect Emotions & Characters
            self.processing_status[video_id]["status"] = "detecting_emotions"
            emotions_raw, characters = self.emotion_detector.analyze_emotions(video_frames_dir)
            
            # Convert emotions to PRD format with timestamps
            emotion_map = []
            for emotion in emotions_raw:
                # Extract frame number from filename (e.g., "frame_0045.jpg" -> 45)
                frame_filename = emotion.get("frame", "frame_0000.jpg")
                try:
                    frame_num = int(frame_filename.split("_")[1].split(".")[0])
                    emotion_map.append({
                        "time": frame_to_timestamp(frame_num, fps),
                        "emotion": emotion.get("emotion"),
                        "character_id": emotion.get("character_id")
                    })
                except:
                    pass  # Skip if frame number can't be extracted
            
            # 5. Get frame samples (save only key frames)
            import glob
            all_frames = sorted(glob.glob(os.path.join(video_frames_dir, "*.jpg")))
            sample_indices = sample_frames_indices(len(all_frames), sample_count=10)
            frame_samples = [os.path.basename(all_frames[i]) for i in sample_indices if i < len(all_frames)]
            
            # 6. Compile Result in PRD format
            result = {
                "transcript": transcript,
                "scenes": scenes,
                "emotion_map": emotion_map,
                "characters": characters,
                "frame_samples": frame_samples
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
