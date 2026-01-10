# Cinema AI — PRD v2 Backend Spec

## 1. Architecture
- Frontend: Next.js (Vercel)
- Backend: FastAPI (Render)
- Storage: Supabase Storage
- DB/Auth: Supabase Postgres + Auth

---

## 2. Database Schema

### 2.1 `projects`
- id (uuid, pk)
- user_id (uuid)
- name (text)
- status (text) ACTIVE/ARCHIVED
- created_at (timestamptz)
- updated_at (timestamptz)

### 2.2 `assets`
- id (uuid, pk)
- project_id (uuid, fk)
- user_id (uuid)
- type (text) video/audio/image
- role (text) A_ROLL/B_ROLL/SCREEN/AUDIO
- storage_path (text)
- duration_sec (int)
- width (int), height (int), fps (numeric)
- size_bytes (bigint)
- created_at (timestamptz)

### 2.3 `jobs`
- id (uuid, pk)
- project_id (uuid, fk)
- user_id (uuid)
- status (text) QUEUED/PROCESSING/RENDERING/COMPLETED/FAILED/CANCELED
- stage (text) UPLOAD_READY/ANALYSIS/EDL/RENDERING/FINALIZING
- progress (int 0-100)
- config (jsonb)
- error_code (text null)
- error_message (text null)
- created_at, updated_at

### 2.4 `job_outputs`
- id (uuid, pk)
- job_id (uuid, fk)
- output_type (text) cinematic/short/hook/vertical/dialogue
- aspect_ratio (text) 16:9/9:16
- status (text) QUEUED/RENDERING/COMPLETED/FAILED
- progress (int)
- output_url (text null)
- storage_path (text null)
- duration_sec (int null)
- created_at

### 2.5 `director_metrics_snapshots`
- id (uuid, pk)
- job_id (uuid)
- snapshot (jsonb)
- created_at

---

## 3. API Endpoints

### Projects
- POST `/projects`
- GET `/projects`
- GET `/projects/{project_id}`

### Assets
- POST `/projects/{project_id}/assets/upload`
- GET `/projects/{project_id}/assets`

### Jobs
- POST `/projects/{project_id}/jobs`
- GET `/jobs/{job_id}`
- GET `/projects/{project_id}/jobs`
- POST `/jobs/{job_id}/cancel`

### Outputs
- GET `/jobs/{job_id}/outputs`

---

## 4. Job Request Schema
```json
{
  "output_types": ["cinematic", "short", "hook"],
  "aspect_ratios": ["16:9", "9:16"],
  "caption_style": "bold",
  "music_mode": "auto",
  "quality": "1080p"
}
```

---

## 5. Security & Limits
- Auth required for all endpoints
- user_id scoping on every query
- Plan limits enforced at job creation:
  - max assets
  - max duration
  - max resolution
- Signed URLs for output downloads
Retention details: see `docs/architecture/RETENTION_POLICY.md`

