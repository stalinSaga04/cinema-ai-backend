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
from .edl_generator import EDLGenerator
from .video_renderer import VideoRenderer
from .database import Database
from .storage import Storage
from enum import Enum

class ProjectStatus(Enum):
    CREATED = "CREATED"
    UPLOADED = "UPLOADED"
    ANALYZING = "ANALYZING"
    DRAFT_READY = "DRAFT_READY"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"

logger = get_logger(__name__)

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
        
        # Persistent Storage (Supabase)
        self.db = Database()
        self.storage = Storage()
        
        # In-memory storage (Fallback/Cache)
        self.processing_status = {}
        self.results = {}
        
        # PRD-MONETIZATION: Local tracking for immediate limit enforcement
        self.project_clip_counts = {}
        self.project_durations = {}

    def check_role(self, user_id: str, required_roles: list) -> bool:
        """PRD 5. User Roles - Enforce roles at backend"""
        role = self.db.get_user_role(user_id)
        return role in required_roles

    def upload_clip(self, project_id: str, video_id: str, video_path: str):
        """PRD Step 2: Upload Clips - Enforce limits"""
        # 1. Check limits before processing
        # We use a mix of DB and local tracking for immediate enforcement during rapid uploads
        db_clip_count = self.db.get_project_clip_count(project_id)
        local_clip_count = self.project_clip_counts.get(project_id, 0)
        clip_count = max(db_clip_count, local_clip_count)
        
        if clip_count >= 20:
            raise Exception(f"Project clip limit reached (Max 20 clips, Current: {clip_count})")
            
        db_total_duration = self.db.get_project_total_duration(project_id)
        local_total_duration = self.project_durations.get(project_id, 0.0)
        total_duration = max(db_total_duration, local_total_duration)
        
        if total_duration >= 1800: # 30 minutes
            raise Exception("Project total duration limit reached (Max 30 minutes)")
            
        # 2. Get duration of the new clip
        from .utils import get_video_duration
        try:
            duration = get_video_duration(video_path)
        except Exception as e:
            logger.warning(f"Could not determine duration for {video_path}: {e}")
            duration = 0.0
            
        if total_duration + duration > 1800:
            raise Exception(f"Uploading this clip would exceed the 30-minute limit (Current total: {total_duration/60:.1f}m)")

        # 3. Upload to Supabase Storage
        filename = os.path.basename(video_path)
        storage_path = f"uploads/{video_id}{os.path.splitext(filename)[1]}"
        self.storage.upload_file("videos", storage_path, video_path)
        
        # 4. Save to DB
        self.db.save_video(video_id, project_id, filename, storage_path, duration=duration)
        self.db.update_project_status(project_id, ProjectStatus.UPLOADED.value)
        
        # Update local tracking
        self.project_clip_counts[project_id] = clip_count + 1
        self.project_durations[project_id] = total_duration + duration
        
        return video_id

    def start_analysis(self, project_id: str, video_ids: list):
        """
        Enqueue an analysis job.
        PRD-WORKERS-01: API server MUST ONLY enqueue jobs.
        """
        logger.info(f"Enqueuing analysis job for project {project_id}")
        self.db.update_project_status(project_id, ProjectStatus.ANALYZING.value)
        
        job_id = self.db.enqueue_job(project_id, "analyze", {"video_ids": video_ids})
        return {"job_id": job_id, "status": "ANALYZING"}

    # --- WORKER METHODS (PRD-WORKERS-01) ---

    def process_analysis_job(self, project_id: str, video_ids: list):
        """Internal method called by the worker to process analysis."""
        logger.info(f"Worker processing analysis for project {project_id}")
        
        for video_id in video_ids:
            # Resolve video path (assuming it's in uploads)
            import glob
            matches = glob.glob(os.path.join(self.uploads_dir, f"{video_id}.*"))
            if matches:
                video_path = matches[0]
                self._analyze_single_video(project_id, video_id, video_path)
            else:
                logger.error(f"Video file not found for {video_id}")

        self._check_project_completion(project_id)

    def _analyze_single_video(self, project_id: str, video_id: str, video_path: str):
        """Extracted logic for analyzing a single video."""
        try:
            logger.info(f"Processing video {video_id} for project {project_id}")
            
            # Get video FPS for timestamp conversion
            from .utils import get_video_fps, frame_to_timestamp, sample_frames_indices
            fps = get_video_fps(video_path)
            
            # 1 & 2. Extract Audio & Frames in Parallel
            if video_id not in self.processing_status:
                self.processing_status[video_id] = {}
            self.processing_status[video_id]["status"] = "extracting_media"
            
            def extract_audio_task():
                audio_path = self.audio_extractor.extract_audio(video_path)
                return audio_path

            def extract_frames_task():
                video_frames_dir = os.path.join(self.outputs_dir, "frames", video_id)
                ensure_directory(video_frames_dir)
                self.frame_extractor.extract_frames(video_path, output_dir=video_frames_dir)
                return video_frames_dir

            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_audio = executor.submit(extract_audio_task)
                future_frames = executor.submit(extract_frames_task)
                
                audio_path = future_audio.result()
                video_frames_dir = future_frames.result()

            self.processing_status[video_id]["status"] = "transcribing"
            if audio_path:
                transcript = self.speech_to_text.transcribe(audio_path)
            else:
                logger.info("No audio track found, skipping transcription")
                transcript = ""
            
            # 3. Detect Scenes
            self.processing_status[video_id]["status"] = "detecting_scenes"
            scenes_raw = self.scene_detector.detect_scenes(video_path)
            
            # Convert scenes to PRD format with timestamps in HH:MM:SS
            scenes = []
            for scene in scenes_raw:
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
                frame_filename = emotion.get("frame", "frame_0000.jpg")
                try:
                    frame_num = int(frame_filename.split("_")[1].split(".")[0])
                    emotion_map.append({
                        "time": frame_to_timestamp(frame_num, fps),
                        "emotion": emotion.get("emotion"),
                        "character_id": emotion.get("character_id")
                    })
                except:
                    pass
            
            # 5. Get frame samples
            import glob
            all_frames = sorted(glob.glob(os.path.join(video_frames_dir, "*.jpg")))
            sample_indices = sample_frames_indices(len(all_frames), sample_count=10)
            frame_samples = [os.path.basename(all_frames[i]) for i in sample_indices if i < len(all_frames)]
            
            # 6. Compile Result
            result = {
                "transcript": transcript,
                "scenes": scenes,
                "emotion_map": emotion_map,
                "characters": characters,
                "frame_samples": frame_samples
            }
            
            # Save JSON locally
            output_json_path = os.path.join(self.outputs_dir, f"{video_id}.json")
            with open(output_json_path, "w") as f:
                import json
                json.dump(result, f, indent=2)
            
            # Save to Supabase DB
            self.db.save_result(video_id, result)
            self.db.update_status(video_id, "completed")
                
            self.processing_status[video_id] = {"status": "completed", "result_path": output_json_path}
            self.results[video_id] = result
            logger.info(f"Processing completed for {video_id}")
            
        except Exception as e:
            logger.error(f"Processing failed for {video_id}: {e}")
            self.processing_status[video_id] = {"status": "failed", "error": str(e)}
            self.db.update_status(video_id, "failed")
            raise

    def _check_project_completion(self, project_id: str):
        """Check if all clips in a project are processed and transition state."""
        logger.info(f"Checking completion for project {project_id}")
        
        # PRD Step 4 & 5: Reverse Script Generation & Auto Edit Draft
        script = self._generate_reverse_script(project_id)
        self.db.save_project_script(project_id, script)
        
        # Enqueue Draft Render
        logger.info(f"Enqueuing draft render for project {project_id}")
        video_ids = self.db.get_project_clips(project_id)
        self.db.enqueue_job(project_id, "render", {
            "video_ids": video_ids,
            "reference_script": script,
            "is_draft": True
        })
        
        self.db.update_project_status(project_id, ProjectStatus.DRAFT_READY.value)
        
        # PRD Step 6: AI PAUSE (MANDATORY)
        # AI asks max 3 questions
        questions = [
            "Is the pacing OK?",
            "Is the tone OK?",
            "Are there any sections you want to change?"
        ]
        self.db.save_project_questions(project_id, questions)
        self.db.update_project_status(project_id, ProjectStatus.WAITING_APPROVAL.value)
        
        logger.info(f"Project {project_id} is now WAITING_APPROVAL (AI PAUSE)")

    def _generate_reverse_script(self, project_id: str) -> str:
        """
        PRD Step 4: Reverse Script Generation.
        Generates a timestamp-locked script based on analyzed footage.
        """
        logger.info(f"Generating reverse script for project {project_id}")
        
        video_ids = self.db.get_project_clips(project_id)
        script_lines = []
        
        current_time = 0.0
        for vid in video_ids:
            result = self.get_result(vid)
            if not result: continue
            
            transcript = result.get("transcript", "").strip()
            if not transcript: continue
            
            # Simple logic: each clip's transcript becomes a script segment
            # In a real system, we'd use LLM to clean this up.
            script_lines.append(f"[{current_time:.2f}s] Narrator: {transcript}")
            
            # Estimate duration (rough estimate for MVP)
            # In a real system, we'd get the actual duration from analysis.
            duration = len(transcript.split()) * 0.5 # 0.5s per word
            current_time += duration
            
        if not script_lines:
            return "No narration detected in uploaded clips."
            
        return "\n".join(script_lines)

    def get_status(self, video_id: str):
        # Check cache first
        status = self.processing_status.get(video_id)
        if status:
            return status
            
        # Check DB
        db_status = self.db.get_status(video_id)
        return {"id": video_id, "status": db_status}

    def get_result(self, video_id: str):
        # Check cache first
        if video_id in self.results:
            return self.results[video_id]
            
        # Check DB
        result = self.db.get_result(video_id)
        if result:
            self.results[video_id] = result
            return result
            
        # Fallback to local file
        status = self.get_status(video_id)
        if status.get("status") == "completed":
            result_path = os.path.join(self.outputs_dir, f"{video_id}.json")
            if os.path.exists(result_path):
                with open(result_path, "r") as f:
                    data = json.load(f)
                    self.results[video_id] = data
                    return data
        return None

    def compare_takes(self, video_ids: list, reference_script: str = None):
        takes_data = []
        for vid in video_ids:
            result = self.get_result(vid)
            if result:
                result["video_id"] = vid
                takes_data.append(result)
        
        if not takes_data:
            return {"error": "No valid processed videos found to compare."}
            
        return self.retake_matcher.compare_takes(takes_data, reference_script)

    def render_project(self, project_id: str, reference_script: str = None, bg_music_path: str = None, is_draft: bool = False):
        """PRD Step 7: Approval & Final Render - Enqueue job."""
        logger.info(f"Enqueuing {'draft ' if is_draft else 'final '}render for project {project_id}")
        
        video_ids = self.db.get_project_clips(project_id)
        if not video_ids:
            return {"error": "No clips found in project"}
            
        # PRD-MONETIZATION: Fetch payment status
        is_paid = self.db.is_project_paid(project_id)
        
        self.db.update_project_status(project_id, ProjectStatus.RENDERING.value)
        
        job_id = self.db.enqueue_job(project_id, "render", {
            "video_ids": video_ids,
            "reference_script": reference_script,
            "bg_music_path": bg_music_path,
            "is_paid": is_paid,
            "is_draft": is_draft
        })
        
        return {"job_id": job_id, "status": "RENDERING"}

    def process_render_job(self, project_id: str, video_ids: list, reference_script: str = None, bg_music_path: str = None, is_draft: bool = False, is_paid: bool = False):
        """Internal method called by the worker to process rendering."""
        logger.info(f"Worker processing {'draft ' if is_draft else ''}render for project {project_id} (Paid: {is_paid})")
        
        try:
            # Step 1: Compare A-roll takes
            comparison_result = self.compare_takes(video_ids, reference_script)
            if "error" in comparison_result:
                raise Exception(comparison_result["error"])
                
            # Step 2: Generate EDL
            edl = self.edl_generator.generate_edl(comparison_result)
            if not edl:
                raise Exception("Failed to generate EDL (No valid clips found)")
                
            # Step 3: Render
            render_id = generate_unique_id()
            output_filename = f"{'draft_' if is_draft else 'render_'}{render_id}.mp4"
            render_path = self.video_renderer.render_video(edl, output_filename, bg_music_path=bg_music_path, is_paid=is_paid)
            
            if not render_path:
                raise Exception("Rendering failed (VideoRenderer returned None)")
            
            # Step 4: Upload Render to Supabase Storage
            storage_path = f"renders/{output_filename}"
            upload_result = self.storage.upload_file("videos", storage_path, render_path)
            
            if upload_result:
                public_url = self.storage.get_public_url("videos", storage_path)
            else:
                logger.warning(f"Failed to upload render {output_filename} to Supabase. Falling back to local download.")
                public_url = None
            
            if not is_draft:
                self.db.update_project_status(project_id, ProjectStatus.COMPLETED.value)
                self.db.update_project_urls(project_id, final_url=public_url)
            else:
                # For drafts, we keep the status as WAITING_APPROVAL (which was set by _check_project_completion)
                # but we save the draft URL.
                logger.info(f"Draft render completed for project {project_id}: {public_url}")
                self.db.update_project_urls(project_id, draft_url=public_url)
                
            return {
                "status": "success",
                "render_id": render_id,
                "render_path": render_path,
                "storage_path": storage_path if upload_result else None,
                "public_url": public_url,
                "download_url": f"/download/{output_filename}",
                "edl": edl,
                "comparison": comparison_result
            }
        except Exception as e:
            logger.error(f"Render job failed: {e}")
            if not is_draft:
                # Rollback status to WAITING_APPROVAL so user can try again
                self.db.update_project_status(project_id, ProjectStatus.WAITING_APPROVAL.value)
            raise
