# Cinema AI — System Overview (Architecture)

Cinema AI is a cloud-native AI Video Director SaaS built with a decoupled architecture.

## 1) High-Level Components

### Frontend (Vercel) — Creator Console
- Next.js UI for project management
- Multi-asset uploads
- Job creation (select output variants)
- Live progress tracking
- Output gallery (download/share)
- Analytics dashboard (director metrics)

### Backend API (Render) — FastAPI Gateway
- Auth verification (Supabase JWT)
- Project / Asset / Job management APIs
- Signed URL generation
- Webhook/event support (future)
- Controls job orchestration + stage updates

### Worker System (Render Worker / VPS later)
- Runs heavy compute: analysis + EDL + rendering
- Pulls jobs from DB queue
- Produces multiple outputs per job
- Updates job + output status progressively
- Uploads final outputs to Supabase Storage

### Supabase
- Postgres: state store + metadata
- Storage: raw assets + outputs
- Auth: user identity + access control policies

---

## 2) Core Workflow (PRD v2)

Cinema AI follows:
**Project → Assets → Jobs → Outputs**

### A) Project
A folder/episode containing assets, processing jobs, and outputs.

### B) Assets
Uploaded raw media:
- A-roll (talking head)
- B-roll (cutaways)
- Screen recording
- Audio tracks

Assets are uploaded to Supabase Storage + metadata saved to DB.

### C) Jobs
A job represents a processing request (e.g., Cinematic + Shorts + Hooks).
Jobs are queued, then processed by workers.

### D) Outputs
Job produces multiple outputs:
- Cinematic Full (16:9)
- Short Highlight (30–60s)
- Hook Cut (3–5s)
- Vertical Reel (9:16)

Each output has its own status and progress.

---

## 3) Data & Storage

### Storage Buckets (Recommended)
- `assets/` — raw user uploads
- `outputs/` — rendered videos
- `analysis/` — json artifacts (transcript, scenes, edl)
- `thumbs/` — thumbnails for outputs

### DB is the Source of Truth
- Never trust file existence alone
- Outputs must be attached to job_outputs table
- Jobs are complete only when outputs finish/failed deterministically

---

## 4) Reliability Model (High Sensitivity)

Cinema AI is designed for production reliability:

### Job Locking
Workers claim jobs using DB locking:
- `SELECT ... FOR UPDATE SKIP LOCKED`

### Idempotent Output Rendering
Each output is rendered independently.
Retry does not duplicate outputs:
- deterministic storage path per output id

### Partial Success
If one output fails:
- other outputs can still complete
- job shows mixed results
- allow user to retry failed outputs only

### Cleanup
- temp files always removed after render
- retention policies by plan

---

## 5) Security

### Auth
All API endpoints must verify:
- valid Supabase JWT
- user owns project/assets/jobs/outputs

### Storage Access
- Use signed URLs for downloads
- Use scoped upload policies

---

## 6) Scalability Plan

### MVP
- Backend API on Render
- 1 worker process
- Supabase for DB/storage

### Scale
- Separate queue service (later)
- Dedicated rendering workers (horizontal scaling)
- Spot instances / GPU options (optional)
- caching Whisper/analysis model in persistent disk
