from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from core.utils import get_logger, generate_unique_id, save_upload_file
from core.brain_controller import BrainController

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
brain = BrainController(base_dir=".")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Cinema AI Brain V1"}

@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        video_id = generate_unique_id()
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(brain.uploads_dir, f"{video_id}{file_extension}")
        
        save_upload_file(file, file_path)
        
        # Start processing in background
        background_tasks.add_task(brain.start_processing, video_id, file_path)
        
        return {"id": video_id, "message": "Upload successful, processing started"}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{video_id}")
async def get_status(video_id: str):
    status = brain.get_status(video_id)
    if status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Video ID not found")
    return status

@app.get("/result/{video_id}")
async def get_result(video_id: str):
    result = brain.get_result(video_id)
    if result is None:
        status = brain.get_status(video_id)
        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail="Video ID not found")
        else:
            raise HTTPException(status_code=400, detail="Processing not completed yet")
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
