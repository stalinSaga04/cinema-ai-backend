import os
import json
import threading
from typing import Dict, Any
from .utils import get_logger, ensure_directory, generate_unique_id
from .frame_extractor import FrameExtractor
from .audio_extractor import AudioExtractor
from .speech_to_text import SpeechToText
from .scene_detector import SceneDetector
from .emotion_detector import EmotionDetector
from .retake_matcher import RetakeMatcher

logger = get_logger(__name__)

from .edl_generator import EDLGenerator
from .video_renderer import VideoRenderer

class BrainController:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.uploads_dir = os.path.join(base_dir, "uploads")
        self.outputs_dir = os.path.join(base_dir, "outputs")
        
        # Ensure directories exist
        ensure_directory(self.uploads_dir)
        ensure_directory(self.outputs_dir)
        
        # Initialize modules
        self.frame_extractor = FrameExtractor(os.path.join(self.outputs_dir, "frames"))
        self.audio_extractor = AudioExtractor(os.path.join(self.outputs_dir, "audio"))
        self.speech_to_text = SpeechToText() # Lazy loaded
        self.scene_detector = SceneDetector() # Lazy loaded
        self.emotion_detector = EmotionDetector() # Lazy loaded
        self.retake_matcher = RetakeMatcher()
        self.edl_generator = EDLGenerator()
        self.video_renderer = VideoRenderer(os.path.join(self.outputs_dir, "renders"), self.uploads_dir)
        
        # In-memory storage (Replace with DB in Phase 4)
        self.processing_status = {}
        self.results = {}

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
            if audio_path:
                transcript = self.speech_to_text.transcribe(audio_path)
            else:
                logger.info("No audio track found, skipping transcription")
                transcript = ""
            
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
            
            # Convert scenes to PRD format with timestamps in HH:MM:SS
            scenes = []
            for scene in scenes_raw:
                # Scene detector now returns: start_seconds, end_seconds, start_timecode, end_timecode
                # We'll use start_seconds/end_seconds and convert to HH:MM:SS
                start_seconds = scene.get("start_seconds", 0)
                end_seconds = scene.get("end_seconds", 0)
                scenes.append({
                    "start": frame_to_timestamp(int(start_seconds * fps), fps),
                    "end": frame_to_timestamp(int(end_seconds * fps), fps)
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

    def compare_takes(self, video_ids: list, reference_script: str = None):
        """
        Compare multiple processed videos.
        """
        takes_data = []
        for vid in video_ids:
            result = self.get_result(vid)
            if result:
                # Add video_id to the result dict for identification if not present
                result["video_id"] = vid
                takes_data.append(result)
            else:
                logger.warning(f"Video ID {vid} not found or not processed.")
        
        if not takes_data:
            return {"error": "No valid processed videos found to compare."}
            
        return self.retake_matcher.compare_takes(takes_data, reference_script)

    def render_project(self, video_ids: list, reference_script: str = None) -> dict:
        """
        Generate a final video from a list of takes.
        1. Compare takes to find the best ones.
        2. Generate an EDL (Edit Decision List).
        3. Render the final video.
        """
        logger.info(f"Starting render project for {len(video_ids)} videos")
        
        # Step 1: Compare
        comparison_result = self.compare_takes(video_ids, reference_script)
        if "error" in comparison_result:
            return comparison_result
            
        # Step 2: Generate EDL
        edl = self.edl_generator.generate_edl(comparison_result)
        if not edl:
            return {"error": "Failed to generate EDL (No valid clips found)"}
            
        # Step 3: Render
        try:
            output_filename = f"render_{generate_unique_id()}.mp4"
            render_path = self.video_renderer.render_video(edl, output_filename)
            
            if not render_path:
                return {"error": "Rendering failed (VideoRenderer returned None)"}
                
            return {
                "status": "success",
                "render_path": render_path,
                "download_url": f"/download/{output_filename}", # We need to serve this
                "edl": edl,
                "comparison": comparison_result
            }
        except Exception as e:
            logger.error(f"Render project failed: {e}")
            return {"error": f"Render failed: {str(e)}"}
