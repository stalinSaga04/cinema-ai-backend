import os
import sys
import uuid
import shutil
import time
try:
    from moviepy.editor import ColorClip
except ImportError:
    from moviepy import ColorClip

# Add the current directory to sys.path to import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.brain_controller import BrainController
from core.database import Database

def create_test_video(path, duration=120, color=(255, 0, 0)):
    """Create a 2-minute test video."""
    print(f"Creating {duration}s test video at {path}...")
    clip = ColorClip(size=(640, 480), color=color, duration=duration)
    clip.write_videofile(path, fps=24, logger=None)
    clip.close()

def test_preview_compression():
    print("Starting Preview Compression Verification Test...")
    
    # Initialize
    os.environ["SKIP_AUTH"] = "true"
    if not os.environ.get("SUPABASE_URL"):
        os.environ["SUPABASE_URL"] = "https://bebcwczcdpvrgmhzeyos.supabase.co"
    if not os.environ.get("SUPABASE_KEY"):
        os.environ["SUPABASE_KEY"] = "sb_publishable_WhyhXpfQ0ZJuZsqJYrJtLw_48Crs5RE"
        
    brain = BrainController(base_dir=".")
    db = brain.db
    
    project_id = str(uuid.uuid4())
    video_id = str(uuid.uuid4())
    video_path = "long_video.mp4"
    
    try:
        # 1. Create Project
        db.create_project(project_id, "Preview Compression Test", "00000000-0000-0000-0000-000000000000")
        
        # 2. Create and Upload 2-minute video
        if not os.path.exists(video_path):
            create_test_video(video_path, duration=120)
            
        shutil.copy(video_path, os.path.join(brain.uploads_dir, f"{video_id}.mp4"))
        
        # Mock DB entry
        db.client.table("videos").insert({
            "id": video_id,
            "project_id": project_id,
            "filename": "long_video.mp4",
            "status": "completed",
            "duration": 120.0
        }).execute()
        
        # Mock Analysis Result
        db.save_result(video_id, {
            "transcript": "Long transcript...",
            "scenes": [{"start": "00:00:00", "end": "00:02:00", "motion_score": 5.0}],
            "emotion_map": [],
            "characters": [],
            "frame_samples": []
        })
        
        # 3. Trigger Draft Render (Should compress)
        print("\nStep 3: Triggering draft render (should apply compression)...")
        result_draft = brain.process_render_job(project_id, [video_id], is_draft=True, is_paid=False)
        
        # Check duration of rendered file
        try:
            from moviepy.editor import VideoFileClip
        except ImportError:
            from moviepy import VideoFileClip
            
        draft_clip = VideoFileClip(result_draft["render_path"])
        print(f"Draft Duration: {draft_clip.duration}s")
        
        assert abs(draft_clip.duration - 60.0) < 1.0, f"Draft should be ~60s, got {draft_clip.duration}s"
        draft_clip.close()
        
        # 4. Trigger Final Render (Should NOT compress, but truncate to 300s if needed)
        print("\nStep 4: Triggering final render (should NOT apply compression)...")
        db.mark_project_paid(project_id)
        result_final = brain.process_render_job(project_id, [video_id], is_draft=False, is_paid=True)
        
        final_clip = VideoFileClip(result_final["render_path"])
        print(f"Final Duration: {final_clip.duration}s")
        
        assert abs(final_clip.duration - 120.0) < 1.0, f"Final should be ~120s, got {final_clip.duration}s"
        final_clip.close()
        
        print("\nPreview Compression Verification Test Passed! ✅")
        
    finally:
        # Cleanup
        if os.path.exists(video_path): os.remove(video_path)
        if 'project_id' in locals():
            db.client.table("projects").delete().eq("id", project_id).execute()

if __name__ == "__main__":
    test_preview_compression()
