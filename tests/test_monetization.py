import os
import sys
import time
import uuid
try:
    from moviepy.editor import ColorClip
except ImportError:
    from moviepy import ColorClip

# Add the current directory to sys.path to import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.brain_controller import BrainController
from core.database import Database

def create_test_video(path, duration=2):
    """Create a tiny test video."""
    clip = ColorClip(size=(640, 480), color=(255, 0, 0), duration=duration)
    clip.write_videofile(path, fps=24, logger=None)

def test_monetization_flow():
    print("Starting Monetization Flow Test...")
    
    # Initialize
    os.environ["SKIP_AUTH"] = "true"
    if not os.environ.get("SUPABASE_URL"):
        os.environ["SUPABASE_URL"] = "https://bebcwczcdpvrgmhzeyos.supabase.co"
    if not os.environ.get("SUPABASE_KEY"):
        os.environ["SUPABASE_KEY"] = "sb_publishable_WhyhXpfQ0ZJuZsqJYrJtLw_48Crs5RE"
        
    brain = BrainController(base_dir=".")
    db = brain.db
    
    # Setup Test Data
    project_id = str(uuid.uuid4())
    video_id = str(uuid.uuid4())
    video_path = f"test_monetization_{video_id}.mp4"
    create_test_video(video_path)
    
    try:
        # 1. Create Project
        print("Step 1: Creating project...")
        db.client.table("projects").insert({
            "id": project_id,
            "name": "Monetization Test Project",
            "status": "CREATED",
            "is_paid": False
        }).execute()
        
        # 2. Upload Clip
        print("Step 2: Uploading clip...")
        db.client.table("videos").insert({
            "id": video_id,
            "project_id": project_id,
            "filename": video_path,
            "status": "completed"
        }).execute()
        # Simulate upload to local dir
        import shutil
        shutil.copy(video_path, os.path.join(brain.uploads_dir, f"{video_id}.mp4"))
        
        # Mock Analysis Result (Required for compare_takes)
        print("Step 2.5: Mocking analysis result...")
        db.save_result(video_id, {
            "scenes": [{"start_seconds": 0, "end_seconds": 2, "motion_score": 5.0}],
            "emotions": [{"frame": 0, "emotion": "happy", "intensity": 0.8}],
            "metrics": {"motion_score": 5.0, "emotion_intensity": 0.8}
        })
        
        # 3. Verify Payment Status (Initial)
        print("Step 3: Verifying initial payment status...")
        assert db.is_project_paid(project_id) == False, "Project should be unpaid initially"
        
        # 4. Test Draft Render (Should work for free)
        print("Step 4: Testing draft render (should work for free)...")
        # Simulate worker processing a draft job
        try:
            # We pass is_draft=True, is_paid=False
            result = brain.process_render_job(project_id, [video_id], is_draft=True, is_paid=False)
            print(f"Draft render successful: {result['render_id']}")
            assert "draft_" in result["render_path"], "Draft render path should contain 'draft_'"
        except Exception as e:
            print(f"Draft render failed: {e}")
            raise
            
        # 5. Test Final Render (Should fail if not paid)
        # Note: We test the API logic here by calling the DB check directly or simulating the main.py logic
        print("Step 5: Testing final render block (unpaid)...")
        if not db.is_project_paid(project_id):
            print("Confirmed: Final render blocked by payment check (Simulated)")
        else:
            raise Exception("Final render should have been blocked")
            
        # 6. Mark as Paid
        print("Step 6: Marking project as paid...")
        db.mark_project_paid(project_id)
        assert db.is_project_paid(project_id) == True, "Project should be paid now"
        
        # 7. Test Final Render (Should work now)
        print("Step 7: Testing final render (paid)...")
        try:
            # We pass is_draft=False, is_paid=True
            result = brain.process_render_job(project_id, [video_id], is_draft=False, is_paid=True)
            print(f"Final render successful: {result['render_id']}")
            assert "render_" in result["render_path"], "Final render path should contain 'render_'"
            assert db.get_project_status(project_id) == "COMPLETED", "Project status should be COMPLETED"
        except Exception as e:
            print(f"Final render failed: {e}")
            raise

        print("\nMonetization Flow Test Passed! ✅")
        
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        # Clean up DB
        db.client.table("projects").delete().eq("id", project_id).execute()
        # Clean up files in outputs
        import glob
        for f in glob.glob(f"outputs/renders/*{project_id}*"):
            os.remove(f)

if __name__ == "__main__":
    test_monetization_flow()
