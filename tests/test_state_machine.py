import os
import sys
import uuid
import time

# Add parent directory to path to import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brain_controller import BrainController, ProjectStatus

def test_state_machine():
    print("Starting State Machine Test...")
    
    # Initialize BrainController
    # Ensure env vars are set for local testing
    os.environ["SKIP_AUTH"] = "true"
    os.environ["SUPABASE_URL"] = os.environ.get("SUPABASE_URL", "https://bebcwczcdpvrgmhzeyos.supabase.co")
    os.environ["SUPABASE_KEY"] = os.environ.get("SUPABASE_KEY", "sb_publishable_WhyhXpfQ0ZJuZsqJYrJtLw_48Crs5RE")
    
    brain = BrainController(base_dir=".")
    
    project_id = str(uuid.uuid4())
    user_id = "00000000-0000-0000-0000-000000000000"
    
    # 1. Create Project
    print(f"Step 1: Creating project {project_id}")
    brain.db.create_project(project_id, "Test Project", user_id)
    status = brain.db.get_project_status(project_id)
    print(f"Status: {status}")
    assert status == ProjectStatus.CREATED.value
    
    # 2. Upload Clip
    print("Step 2: Uploading clip")
    video_id = str(uuid.uuid4())
    video_path = os.path.join(brain.uploads_dir, f"{video_id}.mp4")
    
    # Create a real tiny video using moviepy
    try:
        from moviepy.editor import ColorClip
    except ImportError:
        from moviepy import ColorClip
    clip = ColorClip(size=(160, 120), color=(255, 0, 0), duration=1)
    clip.write_videofile(video_path, fps=10, logger=None)
    
    brain.upload_clip(project_id, video_id, video_path)
    status = brain.db.get_project_status(project_id)
    print(f"Status: {status}")
    assert status == ProjectStatus.UPLOADED.value
    
    # 3. Try illegal transition (Render from UPLOADED)
    print("Step 3: Attempting illegal transition (Render from UPLOADED)")
    result = brain.render_project(project_id, [video_id])
    print(f"Result: {result}")
    assert "error" in result
    assert "Illegal state transition" in result["error"]
    
    # 4. Start Analysis
    print("Step 4: Starting analysis")
    brain.start_analysis(project_id, [video_id])
    status = brain.db.get_project_status(project_id)
    print(f"Status: {status}")
    assert status == ProjectStatus.ANALYZING.value
    
    # 5. Manually transition to WAITING_APPROVAL (AI PAUSE)
    print("Step 5: Manually transitioning to WAITING_APPROVAL")
    brain.db.update_project_status(project_id, ProjectStatus.WAITING_APPROVAL.value)
    status = brain.db.get_project_status(project_id)
    print(f"Status: {status}")
    assert status == ProjectStatus.WAITING_APPROVAL.value
    
    # 6. Render from WAITING_APPROVAL
    print("Step 6: Attempting render from WAITING_APPROVAL")
    result = brain.render_project(project_id, [video_id])
    print(f"Result: {result}")
    assert "job_id" in result
    status = brain.db.get_project_status(project_id)
    assert status == ProjectStatus.RENDERING.value
    
    print("State Machine Test Passed!")
    
    # Cleanup
    if 'video_path' in locals() and os.path.exists(video_path):
        os.remove(video_path)

if __name__ == "__main__":
    try:
        test_state_machine()
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
