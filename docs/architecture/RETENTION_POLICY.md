# Cinema AI — Storage Retention Policy (Cost & Safety)

This document defines how Cinema AI stores and deletes user media to prevent cost blow-ups while keeping the product reliable and fair.

Cinema AI handles large video files. Without strict retention, storage costs will grow faster than revenue.

---

## 1) Scope

Retention applies to:

1) **Raw Uploads (Assets)**
- A-roll, B-roll, screen recordings, audio files

2) **Rendered Outputs**
- Cinematic edit, highlights, hooks, vertical versions

3) **Analysis Artifacts**
- transcript.json
- scenes.json
- intensity_map.json
- master_edl.json
- director_metrics.json

4) **Temporary Local Processing Files**
- /tmp clips
- extracted audio
- intermediate render fragments

---

## 2) Storage Strategy (Where files live)

### Supabase Storage (Primary)
Bucket name: `videos`

Folder structure:

- `videos/assets/{user_id}/{project_id}/{asset_id}.mp4`
- `videos/outputs/{user_id}/{project_id}/{output_id}.mp4`
- `videos/analysis/{user_id}/{project_id}/{job_id}/{artifact}.json`
- `videos/thumbs/{user_id}/{project_id}/{output_id}.jpg`

### Render Persistent Disk (Processing Only)
Mount path: `/data`

Folders:

- `/data/tmp/` (always cleaned after job)
- `/data/cache/` (model caching allowed)
- `/data/whisper/` (optional, model storage)

⚠️ Persistent disk is NOT for long-term user storage.

---

## 3) Plan-Based Retention Rules

### Free Tier (Launch)
- Max assets: **50**
- Max outputs: **10**
- Output retention: **7 days**
- Analysis retention: **7 days**
- Auto-delete: ✅ enabled
- Storage: Supabase bucket `videos`

### Paid Tier (Creator/Pro/Studio)
Default:
- Output retention: **90 days**
- Analysis retention: **30 days** (safe, cheaper)
- Raw assets retention: **90 days**
- Auto-delete: ✅ enabled for expired items only

---

## 4) Deletion Priority (Cost-saving order)

When retention triggers or hard limit is exceeded, delete in this order:

1) **Temporary files**
- Always delete immediately after job completes/fails

2) **Analysis artifacts**
- Cheap to regenerate, not required after output is ready

3) **Outputs**
- Large files, biggest cost driver

4) **Raw assets**
- Delete only when:
  - beyond max limit OR
  - expired by retention policy

---

## 5) Hard Limits (Enforced on Upload / Job Creation)

Retention cleanup is not enough.
Hard limits prevent abuse and protect costs.

### On Upload Asset
If user exceeds `max_assets`:
- delete oldest assets first (respect deletion priority rules)
- delete dependent outputs/artifacts before deleting the asset

### On Job Create
If user exceeds `max_outputs`:
- block job OR force user to delete outputs
- (for free tier: delete oldest outputs automatically)

---

## 6) Cleanup Worker (Scheduled Job)

### Schedule
- Free users cleanup: every **6 hours**
- Paid users cleanup: once daily

### Cleanup logic (high level)
For each user:
1) compute cutoff time: `now - retention_days`
2) delete expired outputs
3) delete expired analysis artifacts
4) delete expired assets (only if allowed)
5) update DB `deleted_at`
6) write cleanup logs

✅ DB is source of truth  
✅ Storage deletion happens before DB marking

---

## 7) DB Fields Required

### users / profiles
- `plan_tier text`
- `retention_days int`
- `max_assets int`
- `max_outputs int`

### assets
- `created_at timestamptz`
- `last_accessed_at timestamptz null`
- `deleted_at timestamptz null`
- `size_bytes bigint`
- `storage_path text`

### job_outputs
- `created_at timestamptz`
- `last_accessed_at timestamptz null`
- `deleted_at timestamptz null`
- `size_bytes bigint`
- `storage_path text`

### analysis_artifacts (recommended)
- `job_id uuid`
- `type text`
- `storage_path text`
- `created_at timestamptz`
- `deleted_at timestamptz null`

---

## 8) Safety Rules (No Data Corruption)

Cleanup must NEVER delete:

- jobs in status: `QUEUED | PROCESSING | RENDERING`
- assets or outputs created within the last X minutes (safety buffer)
- active project currently in use (optional advanced guard)

Retry rules:
- if storage delete fails → do NOT mark DB deleted
- if DB update fails → log error, do not retry delete immediately (avoid loops)

---

## 9) User-Facing Transparency (UI/UX)

The UI must show:

- “Free plan retains outputs for 7 days.”
- countdown: “Expires in 3 days”
- download reminder banner
- upgrade CTA: “Upgrade to store longer”

This reduces support issues and increases conversion.

---

## 10) Security Notes

For MVP:
- Bucket may be public for simplicity

For production:
- Private bucket preferred
- Signed URLs for access/download
- user_id scoped policies

---

## 11) Expected Outcome

This retention policy ensures:

✅ predictable storage costs  
✅ platform stability  
✅ no runaway free-tier abuse  
✅ clear upgrade incentive  
✅ scalable SaaS foundation
