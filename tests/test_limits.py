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

def create_test_video(path, duration=2):
    """Create a tiny test video."""
    clip = ColorClip(size=(640, 480), color=(255, 0, 0), duration=duration)
    clip.write_videofile(path, fps=24, logger=None)

def test_limits():
    print("Starting Limits Verification Test...")
    
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
        db.create_project(project_id, "Limits Test Project", "00000000-0000-0000-0000-000000000000")
        
        # 2. Test Clip Count Limit (20)
        print("Step 2: Testing clip count limit (20)...")
        video_path = "test_limit_clip.mp4"
        create_test_video(video_path, duration=1)
        
        for i in range(20):
            video_id = str(uuid.uuid4())
            # Mock the file in uploads dir
            shutil.copy(video_path, os.path.join(brain.uploads_dir, f"{video_id}.mp4"))
            brain.upload_clip(project_id, video_id, os.path.join(brain.uploads_dir, f"{video_id}.mp4"))
            count = db.get_project_clip_count(project_id)
            print(f"Uploaded clip {i+1}/20. Current DB count: {count}")
            time.sleep(0.2) # Give Supabase a moment to breathe
            
        # 21st clip should fail
        print("Attempting 21st clip (should fail)...")
        try:
            video_id = str(uuid.uuid4())
            brain.upload_clip(project_id, video_id, video_path)
            print("ERROR: 21st clip was NOT blocked!")
            raise Exception("Should have failed at 21st clip")
        except Exception as e:
            print(f"Caught expected exception: {e}")
            if "clip limit reached" in str(e):
                print("Confirmed: 21st clip blocked correctly.")
            else:
                print(f"ERROR: Unexpected exception message: {e}")
                raise

        # 3. Test Duration Limit (30 mins)
        print("Step 3: Testing duration limit (30 mins)...")
        # Create a new project for duration test
        project_id_dur = str(uuid.uuid4())
        db.create_project(project_id_dur, "Duration Limit Test", "00000000-0000-0000-0000-000000000000")
        
        # Create a 10-minute video (mocked by setting duration in DB if we don't want to render 10 mins)
        # But our upload_clip calculates it. Let's create a 1s video and mock the duration check.
        # Actually, let's just test the logic by uploading a few clips and checking the sum.
        
        # We'll mock a large duration by manually inserting into DB for one clip
        video_id_large = str(uuid.uuid4())
        db.save_video(video_id_large, project_id_dur, "large.mp4", "uploads/large.mp4", duration=1795.0) # 29m 55s
        # Sync with local tracking in brain
        brain.project_durations[project_id_dur] = 1795.0
        
        # Next 10s clip should fail
        try:
            video_id_fail = str(uuid.uuid4())
            # Create a 10s video
            create_test_video("test_10s.mp4", duration=10)
            brain.upload_clip(project_id_dur, video_id_fail, "test_10s.mp4")
            raise Exception("Should have failed due to duration limit")
        except Exception as e:
            print(f"Confirmed: Duration limit blocked: {e}")
            assert "duration limit reached" in str(e) or "exceed the 30-minute limit" in str(e)

        print("\nLimits Verification Test Passed! ✅")
        
    finally:
        # Cleanup
        if os.path.exists("test_limit_clip.mp4"): os.remove("test_limit_clip.mp4")
        if os.path.exists("test_10s.mp4"): os.remove("test_10s.mp4")
        if 'project_id' in locals():
            db.client.table("projects").delete().eq("id", project_id).execute()
        if 'project_id_dur' in locals():
            db.client.table("projects").delete().eq("id", project_id_dur).execute()

if __name__ == "__main__":
    test_limits()
