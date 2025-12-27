import os
from supabase import create_client, Client
from .utils import get_logger

logger = get_logger(__name__)

class Database:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        if not self.url or not self.key:
            logger.warning("SUPABASE_URL or SUPABASE_KEY not set. Database operations will fail.")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)
            logger.info("Supabase client initialized")

    def save_video(self, video_id: str, project_id: str, filename: str, storage_path: str, duration: float = None):
        if not self.client: return
        try:
            data = {
                "id": video_id,
                "project_id": project_id,
                "filename": filename,
                "storage_path": storage_path,
                "duration": duration,
                "status": "processing"
            }
            self.client.table("videos").insert(data).execute()
            logger.info(f"Video metadata saved for {video_id} in project {project_id} (Duration: {duration})")
        except Exception as e:
            logger.error(f"Failed to save video metadata: {e}")

    def create_project(self, project_id: str, name: str, owner_id: str):
        if not self.client: return
        try:
            data = {
                "id": project_id,
                "name": name,
                "owner_id": owner_id,
                "status": "CREATED"
            }
            self.client.table("projects").insert(data).execute()
            logger.info(f"Project created: {project_id}")
        except Exception as e:
            logger.error(f"Failed to create project: {e}")

    def update_project_status(self, project_id: str, status: str):
        if not self.client: return
        try:
            self.client.table("projects").update({"status": status}).eq("id", project_id).execute()
            logger.info(f"Project {project_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Failed to update project status: {e}")

    def save_project_questions(self, project_id: str, questions: list):
        if not self.client: return
        try:
            self.client.table("projects").update({"questions": questions}).eq("id", project_id).execute()
            logger.info(f"Questions saved for project {project_id}")
        except Exception as e:
            logger.error(f"Failed to save project questions: {e}")

    def save_project_script(self, project_id: str, script: str):
        if not self.client: return
        try:
            self.client.table("projects").update({"script": script}).eq("id", project_id).execute()
            logger.info(f"Script saved for project {project_id}")
        except Exception as e:
            logger.error(f"Failed to save project script: {e}")

    def get_project_questions(self, project_id: str):
        if not self.client: return []
        try:
            response = self.client.table("projects").select("questions").eq("id", project_id).execute()
            if response.data:
                return response.data[0].get("questions", [])
            return []
        except Exception as e:
            logger.error(f"Failed to get project questions: {e}")
            return []

    def get_project_status(self, project_id: str):
        if not self.client: return "not_found"
        try:
            response = self.client.table("projects").select("status").eq("id", project_id).execute()
            if response.data:
                return response.data[0]["status"]
            return "not_found"
        except Exception as e:
            logger.error(f"Failed to get project status: {e}")
            return "error"

    def is_project_paid(self, project_id: str) -> bool:
        if not self.client: return False
        try:
            response = self.client.table("projects").select("is_paid").eq("id", project_id).execute()
            if response.data:
                return response.data[0].get("is_paid", False)
            return False
        except Exception as e:
            logger.error(f"Failed to check project payment status: {e}")
            return False

    def mark_project_paid(self, project_id: str):
        if not self.client: return
        try:
            self.client.table("projects").update({"is_paid": True}).eq("id", project_id).execute()
            logger.info(f"Project {project_id} marked as paid")
        except Exception as e:
            logger.error(f"Failed to mark project as paid: {e}")

    def update_project_urls(self, project_id: str, draft_url: str = None, final_url: str = None):
        """PRD-MONETIZATION: Store single draft/final URL per project."""
        if not self.client: return
        try:
            update_data = {}
            if draft_url: update_data["draft_url"] = draft_url
            if final_url: update_data["final_url"] = final_url
            
            if update_data:
                self.client.table("projects").update(update_data).eq("id", project_id).execute()
                logger.info(f"Project {project_id} URLs updated: {update_data}")
        except Exception as e:
            logger.error(f"Failed to update project URLs: {e}")

    def get_project_clips(self, project_id: str):
        if not self.client: return []
        try:
            response = self.client.table("videos").select("id").eq("project_id", project_id).execute()
            return [v["id"] for v in response.data]
        except Exception as e:
            logger.error(f"Failed to get project clips: {e}")
            return []

    def get_project_total_duration(self, project_id: str) -> float:
        """PRD-MONETIZATION: Get total duration of all clips in a project."""
        if not self.client: return 0.0
        try:
            response = self.client.table("videos").select("duration").eq("project_id", project_id).execute()
            total = sum([v.get("duration", 0) or 0 for v in response.data])
            return total
        except Exception as e:
            logger.error(f"Failed to get project total duration: {e}")
            return 0.0

    def get_project_clip_count(self, project_id: str) -> int:
        """PRD-MONETIZATION: Get total number of clips in a project."""
        if not self.client: return 0
        try:
            response = self.client.table("videos").select("id", count="exact").eq("project_id", project_id).execute()
            return response.count if response.count is not None else len(response.data)
        except Exception as e:
            logger.error(f"Failed to get project clip count: {e}")
            return 0

    def get_user_role(self, user_id: str):
        if not self.client: return "CREATOR" # Default for MVP
        try:
            response = self.client.table("user_roles").select("role").eq("user_id", user_id).execute()
            if response.data:
                return response.data[0]["role"]
            return "CREATOR"
        except Exception as e:
            logger.error(f"Failed to get user role: {e}")
            return "CREATOR"

    # --- JOB QUEUE METHODS (PRD-WORKERS-01) ---

    def enqueue_job(self, project_id: str, job_type: str, payload: dict):
        if not self.client: return None
        try:
            data = {
                "project_id": project_id,
                "type": job_type,
                "payload": payload,
                "status": "pending"
            }
            response = self.client.table("jobs").insert(data).execute()
            if response.data:
                return response.data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}")
            return None

    def fetch_next_job(self):
        """Atomically fetch and lock the next pending job."""
        if not self.client: return None
        try:
            # 1. Find a pending job
            response = self.client.table("jobs").select("*").eq("status", "pending").order("created_at").limit(1).execute()
            if not response.data:
                return None
            
            job = response.data[0]
            job_id = job["id"]
            
            # 2. Try to lock it by updating status to 'processing'
            # Note: In a high-concurrency environment, this would need a more robust lock (e.g. SELECT FOR UPDATE)
            # but for MVP on Supabase REST API, we'll do a simple update check.
            lock_response = self.client.table("jobs").update({"status": "processing", "updated_at": "now()"}).eq("id", job_id).eq("status", "pending").execute()
            
            if lock_response.data:
                return lock_response.data[0]
            return None # Someone else grabbed it
        except Exception as e:
            logger.error(f"Failed to fetch next job: {e}")
            return None

    def update_job_status(self, job_id: str, status: str, error: str = None):
        if not self.client: return
        try:
            update_data = {"status": status, "updated_at": "now()"}
            if error:
                update_data["error"] = error
            self.client.table("jobs").update(update_data).eq("id", job_id).execute()
            logger.info(f"Job {job_id} updated to {status}")
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")

    def update_status(self, video_id: str, status: str):
        if not self.client: return
        try:
            self.client.table("videos").update({"status": status}).eq("id", video_id).execute()
            logger.info(f"Status updated to {status} for {video_id}")
        except Exception as e:
            logger.error(f"Failed to update status: {e}")

    def save_result(self, video_id: str, result_data: dict):
        if not self.client: return
        try:
            data = {
                "video_id": video_id,
                "data": result_data
            }
            # Use upsert if possible, or insert
            self.client.table("results").upsert(data).execute()
            logger.info(f"Result saved for {video_id}")
        except Exception as e:
            logger.error(f"Failed to save result: {e}")

    def get_result(self, video_id: str):
        if not self.client: return None
        try:
            response = self.client.table("results").select("data").eq("video_id", video_id).execute()
            if response.data:
                return response.data[0]["data"]
            return None
        except Exception as e:
            logger.error(f"Failed to get result: {e}")
            return None

    def get_status(self, video_id: str):
        if not self.client: return "not_found"
        try:
            response = self.client.table("videos").select("status").eq("id", video_id).execute()
            if response.data:
                return response.data[0]["status"]
            return "not_found"
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return "error"


