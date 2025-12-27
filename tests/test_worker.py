import os
import sys
import uuid
import time

# Add parent directory to path to import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brain_controller import BrainController, ProjectStatus

def test_worker_flow():
    print("Starting Worker Flow Test...")
    
    # Initialize BrainController
    os.environ["SKIP_AUTH"] = "true"
    os.environ["SUPABASE_URL"] = os.environ.get("SUPABASE_URL", "https://bebcwczcdpvrgmhzeyos.supabase.co")
    os.environ["SUPABASE_KEY"] = os.environ.get("SUPABASE_KEY", "sb_publishable_WhyhXpfQ0ZJuZsqJYrJtLw_48Crs5RE")
    
    brain = BrainController(base_dir=".")
    
    project_id = str(uuid.uuid4())
    user_id = "00000000-0000-0000-0000-000000000000"
    
    # 1. Create Project
    print(f"Step 1: Creating project {project_id}")
    brain.db.create_project(project_id, "Worker Test", user_id)
    
    # 2. Enqueue Analysis Job (Simulating API call)
    print("Step 2: Enqueuing analysis job")
    video_id = str(uuid.uuid4())
    video_path = os.path.join(brain.uploads_dir, f"{video_id}.mp4")
    
    # Create a real tiny video using moviepy
    try:
        from moviepy.editor import ColorClip
    except ImportError:
        from moviepy import ColorClip
        
    clip = ColorClip(size=(160, 120), color=(255, 0, 0), duration=1)
    clip.write_videofile(video_path, fps=10, logger=None)
        
    result = brain.start_analysis(project_id, [video_id])
    job_id = result["job_id"]
    print(f"Job enqueued: {job_id}")
    
    # 3. Wait for Worker to pick it up and process
    print("Step 3: Waiting for worker to process job...")
    
    # Simulation: Fetch the specific job we just created
    response = brain.db.client.table("jobs").select("*").eq("id", job_id).execute()
    if response.data:
        job = response.data[0]
        print(f"Worker picked up job {job_id}")
        # Lock it
        brain.db.client.table("jobs").update({"status": "processing"}).eq("id", job_id).execute()
        try:
            brain.process_analysis_job(project_id, [video_id])
            brain.db.update_job_status(job_id, "completed")
            print("Job completed by simulated worker")
        except Exception as e:
            brain.db.update_job_status(job_id, "failed", error=str(e))
            print(f"Job failed: {e}")
    else:
        print(f"Failed to fetch job {job_id} from queue")
        sys.exit(1)
        
    # 4. Verify Final State
    status = brain.db.get_project_status(project_id)
    print(f"Final Project Status: {status}")
    assert status == ProjectStatus.WAITING_APPROVAL.value
    
    print("Worker Flow Test Passed!")
    
    # Cleanup
    if os.path.exists(video_path):
        os.remove(video_path)

if __name__ == "__main__":
    try:
        test_worker_flow()
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
