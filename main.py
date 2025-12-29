from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from core.utils import get_logger, generate_unique_id, save_upload_file
from core.brain_controller import BrainController
import threading
from worker import run_worker

logger = get_logger(__name__)

app = FastAPI(title="Cinema AI Brain V1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Brain Controller
# In production, these should be set in Render environment variables
if not os.environ.get("SUPABASE_URL"):
    # Fallback for local testing if not set in env
    os.environ["SUPABASE_URL"] = "https://bebcwczcdpvrgmhzeyos.supabase.co"
if not os.environ.get("SUPABASE_KEY"):
    os.environ["SUPABASE_KEY"] = "sb_publishable_WhyhXpfQ0ZJuZsqJYrJtLw_48Crs5RE"

brain = BrainController(base_dir=".")

@app.on_event("startup")
async def startup_event():
    """Start the background worker thread for MVP convenience."""
    logger.info(f"SKIP_AUTH status: {os.environ.get('SKIP_AUTH')}")
    if os.environ.get("RUN_INTERNAL_WORKER", "true").lower() == "true":
        logger.info("Starting background worker thread (MVP Mode)...")
        worker_thread = threading.Thread(target=run_worker, daemon=True)
        worker_thread.start()
    else:
        logger.info("Internal worker disabled. Ensure a separate worker process is running.")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the background worker thread."""
    import worker
    logger.info("Stopping background worker thread...")
    worker.running = False

async def get_current_user(authorization: str = Header(None)):
    """PRD 6. Permission Matrix - Enforced in backend"""
    if not authorization:
        # For local testing without auth, we can return a mock user if env is set
        if str(os.environ.get("SKIP_AUTH")).lower() == "true":
            class MockUser:
                id = "00000000-0000-0000-0000-000000000000"
            return MockUser()
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    try:
        user_response = brain.db.client.auth.get_user(token)
        return user_response.user
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Cinema AI Brain V1"}

class ProjectCreate(BaseModel):
    name: str

@app.post("/projects")
async def create_project(request: ProjectCreate, user=Depends(get_current_user)):
    """PRD Step 1: Project Creation"""
    if not brain.check_role(user.id, ["CREATOR"]):
        raise HTTPException(status_code=403, detail="Only Creators can create projects")
    
    project_id = generate_unique_id()
    brain.db.create_project(project_id, request.name, user.id)
    return {"id": project_id, "status": "CREATED"}

@app.post("/projects/{project_id}/upload")
async def upload_video(project_id: str, file: UploadFile = File(...), user=Depends(get_current_user)):
    """PRD Step 2: Upload Clips"""
    if not brain.check_role(user.id, ["CREATOR"]):
        raise HTTPException(status_code=403, detail="Only Creators can upload clips")
    
    try:
        video_id = generate_unique_id()
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(brain.uploads_dir, f"{video_id}{file_extension}")
        
        save_upload_file(file, file_path)
        brain.upload_clip(project_id, video_id, file_path)
        
        return {"id": video_id, "message": "Upload successful"}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/{project_id}/analyze")
async def analyze_project(project_id: str, user=Depends(get_current_user)):
    """PRD Step 3: Analysis Phase"""
    if not brain.check_role(user.id, ["CREATOR"]):
        raise HTTPException(status_code=403, detail="Only Creators can trigger analysis")
    
    clips = brain.db.get_project_clips(project_id)
    if not clips:
        raise HTTPException(status_code=400, detail="No clips found in project")
    
    result = brain.start_analysis(project_id, clips)
    return result

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str, user=Depends(get_current_user)):
    """PRD-WORKERS-01: Check status of a background job"""
    try:
        response = brain.db.client.table("jobs").select("*").eq("id", job_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Job not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/status")
async def get_project_status(project_id: str, user=Depends(get_current_user)):
    status = brain.db.get_project_status(project_id)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Project not found")
    return {"id": project_id, "status": status}

@app.get("/result/{video_id}")
async def get_result(video_id: str, user=Depends(get_current_user)):
    result = brain.get_result(video_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found or processing not completed")
    return result

@app.get("/projects/{project_id}/ai-pause")
async def get_ai_pause_questions(project_id: str, user=Depends(get_current_user)):
    """PRD Step 6: AI PAUSE (MANDATORY)"""
    status = brain.db.get_project_status(project_id)
    if status != "WAITING_APPROVAL":
        raise HTTPException(status_code=400, detail="Project is not in WAITING_APPROVAL state")
    
    questions = brain.db.get_project_questions(project_id)
    
    return {
        "questions": questions,
        "message": "AI has generated a draft. Please answer these questions before final render."
    }

@app.get("/projects/{project_id}/script")
async def get_project_script(project_id: str, user=Depends(get_current_user)):
    """PRD Step 5: Auto Edit Draft - Editable script text"""
    try:
        response = brain.db.client.table("projects").select("script").eq("id", project_id).execute()
        if response.data:
            return {"script": response.data[0].get("script")}
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ApprovalRequest(BaseModel):
    answers: dict
    approved: bool

@app.post("/projects/{project_id}/approve")
async def approve_draft(project_id: str, request: ApprovalRequest, user=Depends(get_current_user)):
    """PRD Step 7: Approval & Final Render"""
    if not brain.check_role(user.id, ["CREATOR", "EDITOR"]):
        raise HTTPException(status_code=403, detail="Only Creators or Editors can approve drafts")
    
    if not request.approved:
        logger.info(f"Draft rejected for project {project_id} with feedback: {request.answers}")
        return {"message": "Feedback received. Please update the script or clips."}
    
    return {"message": "Draft approved. Creator can now trigger final render."}

class RenderRequest(BaseModel):
    reference_script: str = None
    bg_music_path: str = None

@app.post("/projects/{project_id}/render")
async def render_video(project_id: str, request: RenderRequest, user=Depends(get_current_user)):
    """PRD Step 7: Approval & Final Render"""
    if not brain.check_role(user.id, ["CREATOR"]):
        raise HTTPException(status_code=403, detail="Only Creators can trigger render")
    
    # PRD-MONETIZATION: Check if project is paid
    if not brain.db.is_project_paid(project_id):
        raise HTTPException(status_code=402, detail="Payment required for final export ($7)")
    
    result = brain.render_project(project_id, request.reference_script, request.bg_music_path)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@app.post("/projects/{project_id}/pay")
async def pay_for_project(project_id: str, user=Depends(get_current_user)):
    """PRD-MONETIZATION: Mock payment endpoint ($7 per project)"""
    if not brain.check_role(user.id, ["CREATOR"]):
        raise HTTPException(status_code=403, detail="Only Creators can pay for projects")
    
    brain.db.mark_project_paid(project_id)
    return {"message": f"Payment successful for project {project_id}. Final export unlocked."}

from fastapi.responses import FileResponse

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a rendered video file. Redirects to Supabase if possible.
    """
    # Security check: prevent directory traversal
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    # Check if we should redirect to Supabase
    # For simplicity in MVP, we check if it's a render and try to get public URL
    if filename.startswith("render_"):
        storage_path = f"renders/{filename}"
        public_url = brain.storage.get_public_url("videos", storage_path)
        if public_url:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=public_url)

    file_path = os.path.join(brain.outputs_dir, "renders", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, media_type="video/mp4", filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
