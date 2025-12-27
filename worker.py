import os
import time
import logging
import signal
import sys
import threading
from core.brain_controller import BrainController
from core.utils import get_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger("worker")

running = True

def signal_handler(sig, frame):
    global running
    logger.info("Shutdown signal received. Stopping worker...")
    running = False

def run_worker():
    global running
    logger.info("Cinema AI Worker starting...")
    
    # Register signal handlers for standalone mode
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize BrainController
    # Ensure env vars are set for local testing
    if not os.environ.get("SUPABASE_URL"):
        os.environ["SUPABASE_URL"] = "https://bebcwczcdpvrgmhzeyos.supabase.co"
    if not os.environ.get("SUPABASE_KEY"):
        os.environ["SUPABASE_KEY"] = "sb_publishable_WhyhXpfQ0ZJuZsqJYrJtLw_48Crs5RE"
        
    brain = BrainController(base_dir=".")
    
    while running:
        try:
            # 1. Fetch next pending job
            job = brain.db.fetch_next_job()
            
            if not job:
                # No jobs, sleep for a bit
                time.sleep(5)
                continue
                
            job_id = job["id"]
            job_type = job["type"]
            project_id = job["project_id"]
            payload = job.get("payload", {})
            
            logger.info(f"Processing job {job_id} (Type: {job_type}, Project: {project_id})")
            
            try:
                if job_type == "analyze":
                    video_ids = payload.get("video_ids", [])
                    brain.process_analysis_job(project_id, video_ids)
                elif job_type == "render":
                    video_ids = payload.get("video_ids", [])
                    reference_script = payload.get("reference_script")
                    bg_music_path = payload.get("bg_music_path")
                    is_draft = payload.get("is_draft", False)
                    is_paid = payload.get("is_paid", False)
                    brain.process_render_job(project_id, video_ids, reference_script, bg_music_path, is_draft, is_paid)
                else:
                    logger.warning(f"Unknown job type: {job_type}")
                    brain.db.update_job_status(job_id, "failed", error=f"Unknown job type: {job_type}")
                    continue
                
                # 2. Mark job as completed
                brain.db.update_job_status(job_id, "completed")
                logger.info(f"Job {job_id} completed successfully")
                
            except Exception as e:
                logger.error(f"Job {job_id} failed: {e}")
                brain.db.update_job_status(job_id, "failed", error=str(e))
                
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            time.sleep(10) # Wait longer on system error

if __name__ == "__main__":
    run_worker()
