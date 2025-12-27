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

def create_test_video(path, duration=2, color=(255, 0, 0)):
    """Create a tiny test video."""
    clip = ColorClip(size=(640, 480), color=color, duration=duration)
    clip.write_videofile(path, fps=24, logger=None)

def test_outputs():
    print("Starting Project Output Enforcement Test...")
    
    # Initialize
    os.environ["SKIP_AUTH"] = "true"
    if not os.environ.get("SUPABASE_URL"):
        os.environ["SUPABASE_URL"] = "https://bebcwczcdpvrgmhzeyos.supabase.co"
    if not os.environ.get("SUPABASE_KEY"):
        os.environ["SUPABASE_KEY"] = "sb_publishable_WhyhXpfQ0ZJuZsqJYrJtLw_48Crs5RE"
        
    brain = BrainController(base_dir=".")
    db = brain.db
    
    project_id = str(uuid.uuid4())
    
    try:
        # 1. Create Project
        print("Step 1: Creating project...")
        db.create_project(project_id, "Output Enforcement Test", "00000000-0000-0000-0000-000000000000")
        
        # 2. Upload Multiple Clips (Footage Pool)
        print("Step 2: Mocking multiple clips in DB...")
        v1_path = "v1.mp4"
        v2_path = "v2.mp4"
        create_test_video(v1_path, duration=2, color=(255, 0, 0))
        create_test_video(v2_path, duration=2, color=(0, 255, 0))
        
        v1_id = str(uuid.uuid4())
        v2_id = str(uuid.uuid4())
        
        # Direct DB insert to avoid storage/duration calculation issues in test
        db.client.table("videos").insert([
            {"id": v1_id, "project_id": project_id, "filename": "v1.mp4", "status": "completed", "duration": 2.0},
            {"id": v2_id, "project_id": project_id, "filename": "v2.mp4", "status": "completed", "duration": 2.0}
        ]).execute()
        
        # Mock the files in uploads dir for VideoRenderer
        shutil.copy(v1_path, os.path.join(brain.uploads_dir, f"{v1_id}.mp4"))
        shutil.copy(v2_path, os.path.join(brain.uploads_dir, f"{v2_id}.mp4"))
        
        # Mock Analysis Results
        db.save_result(v1_id, {
            "transcript": "Hello world",
            "scenes": [{"start": "00:00:00", "end": "00:00:02", "motion_score": 5.0}],
            "emotion_map": [],
            "characters": [],
            "frame_samples": []
        })
        db.save_result(v2_id, {
            "transcript": "Goodbye world",
            "scenes": [{"start": "00:00:00", "end": "00:00:02", "motion_score": 5.0}],
            "emotion_map": [],
            "characters": [],
            "frame_samples": []
        })
        
        # 3. Test Draft Render (Should store draft_url)
        print("Step 3: Testing draft render...")
        result_d1 = brain.process_render_job(project_id, [v1_id, v2_id], is_draft=True, is_paid=False)
        url_d1 = result_d1["public_url"]
        
        # Verify in DB
        resp = db.client.table("projects").select("draft_url").eq("id", project_id).execute()
        assert resp.data[0]["draft_url"] == url_d1, "Draft URL should be stored in DB"
        
        # 4. Test Second Draft Render (Should update draft_url)
        print("Step 4: Testing second draft render (overwrite reference)...")
        result_d2 = brain.process_render_job(project_id, [v1_id, v2_id], is_draft=True, is_paid=False)
        url_d2 = result_d2["public_url"]
        
        resp = db.client.table("projects").select("draft_url").eq("id", project_id).execute()
        assert resp.data[0]["draft_url"] == url_d2, "Draft URL should be updated in DB"
        assert url_d1 != url_d2, "New render should have different URL"
        
        # 5. Test Final Render (Should store final_url)
        print("Step 5: Testing final render...")
        db.mark_project_paid(project_id)
        result_f1 = brain.process_render_job(project_id, [v1_id, v2_id], is_draft=False, is_paid=True)
        url_f1 = result_f1["public_url"]
        
        resp = db.client.table("projects").select("final_url").eq("id", project_id).execute()
        assert resp.data[0]["final_url"] == url_f1, "Final URL should be stored in DB"
        
        print("\nProject Output Enforcement Test Passed! ✅")
        
    finally:
        # Cleanup
        if os.path.exists("v1.mp4"): os.remove("v1.mp4")
        if os.path.exists("v2.mp4"): os.remove("v2.mp4")
        if 'project_id' in locals():
            db.client.table("projects").delete().eq("id", project_id).execute()

if __name__ == "__main__":
    test_outputs()
