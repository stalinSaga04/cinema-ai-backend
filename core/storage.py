import os
from supabase import create_client, Client
from .utils import get_logger

logger = get_logger(__name__)

class Storage:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        if not self.url or not self.key:
            logger.warning("SUPABASE_URL or SUPABASE_KEY not set. Storage operations will fail.")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)
            logger.info("Supabase storage client initialized")

    def upload_file(self, bucket: str, storage_path: str, local_path: str):
        if not self.client: return None
        try:
            with open(local_path, 'rb') as f:
                self.client.storage.from_(bucket).upload(storage_path, f)
            logger.info(f"File uploaded to {bucket}/{storage_path}")
            return storage_path
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return None

    def get_public_url(self, bucket: str, storage_path: str):
        if not self.client: return None
        try:
            return self.client.storage.from_(bucket).get_public_url(storage_path)
        except Exception as e:
            logger.error(f"Failed to get public URL: {e}")
            return None

    def download_file(self, bucket: str, storage_path: str, local_path: str):
        if not self.client: return False
        try:
            res = self.client.storage.from_(bucket).download(storage_path)
            with open(local_path, 'wb') as f:
                f.write(res)
            logger.info(f"File downloaded from {bucket}/{storage_path} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return False
