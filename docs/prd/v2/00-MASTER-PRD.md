# Cinema AI — MASTER PRD v2 (Director Workflow SaaS Upgrade)
> Combined PRD bundle: Product + UI + Backend + Workers + Monetization + Legal
> Generated: 2026-01-10

---

## Table of Contents
1. [PRD v2 — Master](#prd-v2--master)
2. [PRD v2 — UI](#prd-v2--ui)
3. [PRD v2 — Backend](#prd-v2--backend)
4. [PRD v2 — Workers](#prd-v2--workers)
5. [PRD v2 — Monetization](#prd-v2--monetization)
6. [PRD v2 — Legal](#prd-v2--legal)

---



---

## PRD v2 — Master

# Cinema AI — PRD v2 (Director Workflow SaaS Upgrade)

## 1. Product Overview

**Cinema AI** is an **AI Video Director SaaS**. Creators upload raw footage and Cinema AI produces a **content pack**: a full cinematic edit + shorts/highlights + hooks + captions, along with director-grade analytics.

### One-liner
**Upload raw footage → get a content pack + editable structure + exports.**

### Positioning (no confusion)
Cinema AI is **not** a template tool (CapCut), an AI video generator (Runway/Pika), or only an auto-cutter (Descript).
Cinema AI is an **AI Video Director** that produces **editing decisions** and **multiple output versions**.

---

## 2. Goals

### Primary Goal
Transform the current **upload → process → single output** into a **Creator-grade SaaS workflow**:

> **Project → Assets → Jobs → Outputs**

### Success Criteria (v2)
- Users can manage multiple projects and re-run jobs.
- Users can upload multiple assets per project with roles.
- 1 job can produce **multiple outputs**.
- Job progress is transparent (stage + ETA + per-output status).
- Outputs are durable (history + share/download).
- Platform is cost-controlled and production-stable.

---

## 3. Target Users

- YouTube creators (talking head, vlog, tutorials)
- Podcast creators (single or multi-cam)
- Short-form creators (Reels/TikTok/Shorts)
- Agencies editing content weekly

---

## 4. Core Concepts & Definitions

### Project
A folder/episode/client unit that contains assets, jobs, and outputs.

### Assets
Uploaded media used to make outputs:
- video clips (A-roll/B-roll/screen recordings)
- audio tracks

### Job
A processing request for a project (e.g., “Generate Cinematic + Shorts + Hooks”).

### Outputs
Rendered videos produced from a job (multiple per job).

---

## 5. MVP v2 Deliverables

### Pillar A — Creator Workflow
- Projects dashboard
- Project detail view with tabs: Assets / Jobs / Outputs / Analytics
- Multi-upload assets with tagging (A-roll/B-roll/screen/audio)
- Job history + rerun / re-render outputs

### Pillar B — Real Editing Power
- Output variants (multi-select):
  - Cinematic Full (16:9)
  - Short Highlight (30–60s)
  - Hook Cut (3–5s)
  - Vertical Reel (9:16)
  - Dialogue Cut (optional)
- Captions:
  - SRT export
  - Burned-in captions for shorts/vertical

### Pillar C — Control (lightweight)
- Timeline preview **as segment list** (not a full NLE editor):
  - segments with start/end timestamps
  - transcript per segment
  - remove/reorder controls
- Export:
  - MP4
  - SRT
  - JSON EDL-like structure

### Director Analytics
- pacing score
- clarity score
- mistake count
- emotional peaks
- best moments list
- improvement suggestions

---

## 6. Roadmap

### Phase 1 (7–10 days)
- Projects + Assets + Jobs + job_outputs DB
- Multi-upload with tagging
- Job stages + progress
- 2 outputs only:
  - Cinematic Full
  - Short Highlight

### Phase 2 (2–3 weeks)
- Vertical Reel + Hook Cut
- Segment-list “timeline preview”
- Caption style options
- Re-render specific output types

### Phase 3 (growth)
- Content Pack generator
- Titles/descriptions/hashtags
- Billing + credits
- Teams + brand presets

---

## 7. Non-Functional Requirements (High Sensitivity)

### Stability
- Job locking (one worker per job)
- Idempotent rendering per output
- Retry strategy per output (max 2)

### Cost Control
- Analysis runs once per job
- Render only requested outputs
- Enforce plan-based limits (duration, file count, resolution)
- Cleanup temp files + retention cleanup

### Security
- Auth required
- Resource ownership checks (user_id scoping)
- Signed URLs for downloads


---

## PRD v2 — UI

# Cinema AI — PRD v2 UI Spec (Director Workflow)

## 1. Navigation

- Dashboard
- Projects
- Outputs
- Settings

---

## 2. Pages

### 2.1 Dashboard `/dashboard`
Cards:
- Minutes used this month
- Active jobs (queued/processing/rendering)
- Latest outputs

CTA:
- **New Project**

---

### 2.2 Projects List `/projects`
Project card fields:
- name
- created date / last updated
- latest job status badge
- outputs count

Actions:
- Open
- Duplicate
- Delete

Filters:
- All
- Processing
- Completed
- Failed

---

### 2.3 Project Detail `/projects/:id`

Tabs:

#### A) Assets
- MultiUploadDropzone
- AssetRoleTagger (A-roll/B-roll/screen/audio)
- Per-file upload progress
- Asset list with metadata (duration, resolution)

#### B) Jobs
- New Job form:
  - output variants (checkbox multi-select)
  - aspect ratio selection
  - caption style
  - music mode
- Job list:
  - stage
  - started/finished timestamps
  - outputs summary
  - rerun button

#### C) Outputs
- Output grid (cards):
  - thumbnail
  - output type
  - aspect ratio
  - duration
  - status
  - download/share
  - re-render if failed

#### D) Analytics
- Show metrics from director snapshots:
  - pacing/clarity/mistakes
  - emotional peaks
  - best timestamps
  - suggestions

---

### 2.4 Job Progress `/jobs/:jobId`
Displays:
- stage timeline:
  1) Upload verified
  2) Analysis
  3) Master EDL
  4) Rendering outputs
  5) Finalizing
- Outputs list (each with status + progress)
- ETA range label

---

## 3. UI Components

- `MultiUploadDropzone`
- `AssetRoleTagger`
- `JobProgressTracker`
- `OutputCard`
- `TimelineSegmentsList` (segment list, not timeline editor)

---

## 4. UX Requirements
- Always show stage clarity: no “stuck uploading”
- Allow leaving page: state persists
- Errors must show next action (retry, contact)


---

## PRD v2 — Backend

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


---

## PRD v2 — Workers

# Cinema AI — PRD v2 Workers Spec (Stable + Cost-Controlled)

## 1. Worker Responsibilities
Workers pull jobs from DB, run analysis once, build master EDL once, then render multiple outputs.

---

## 2. Job State Machine
- QUEUED
- PROCESSING
- RENDERING
- COMPLETED
- FAILED
- CANCELED

Stages:
- UPLOAD_READY
- ANALYSIS
- EDL
- RENDERING
- FINALIZING

---

## 3. Processing Pipeline

### Step 0 — Lock
Select job FOR UPDATE SKIP LOCKED.

### Step 1 — Analysis (once per job)
- scene detection
- audio extraction
- whisper transcription
- scoring (emotion/audio/speech)
- director metrics snapshot logging

Outputs:
- analysis.json
- transcript.json
- scene_boundaries.json

### Step 2 — Build Master EDL (once per job)
Create canonical segment list.

Outputs:
- master_edl.json

### Step 3 — Render Outputs (N)
For each `job_outputs` row:
- apply variant rules
- render video
- upload to Supabase Storage
- update job_outputs status/progress

### Step 4 — Finalize
Mark job COMPLETED when all outputs are completed OR failed (partial success allowed).

---

## 4. Output Variant Rules

### Cinematic Full
- best takes
- smooth pacing
- optional music bed

### Short Highlight
- top scoring segments
- 30–60 seconds
- captions burned-in

### Hook Cut
- highest energy/emotion moment early
- 3–5 seconds
- big captions

### Vertical Reel
- 9:16 crop / face focus
- aggressive cuts
- captions

### Dialogue Cut
- only dialogue segments
- remove silences

---

## 5. Reliability & Sensitivity

### Retries
- max 2 retries per output
- if 1 output fails, others can still complete

### Timeouts
- job watchdog: abort long-running tasks
- per-output max runtime

### Cleanup
- cleanup tmp files always
- retention cleanup by plan (scheduled)


---

## PRD v2 — Monetization

# Cinema AI — PRD v2 Monetization (Minutes + Content Packs)

## 1. Pricing Model
Charge based on **minutes processed** and **outputs generated**.

---

## 2. Plans

### Free
- 10 minutes/month
- 1 output per job
- 720p
- watermark
- slow queue
- output retention: 7 days

### Creator ₹999/mo
- 120 minutes/month
- up to 5 outputs/job
- 1080p
- captions + SRT
- retention: 90 days

### Pro ₹2999/mo
- 400 minutes/month
- content pack outputs
- vertical + hooks
- priority queue
- JSON EDL export
- retention: 1 year

### Studio ₹9999/mo
- 1500 minutes/month
- teams
- brand presets
- API access
- retention: 1 year+

---

## 3. Credit Rules (implementation)
- analysis cost: low credits/minute
- rendering cost: high credits/minute
- each extra output consumes credits

---

## 4. Upgrade Incentives
- Free users see preview of additional outputs locked
- Paid users get faster queue + more outputs


---

## PRD v2 — Legal

# Cinema AI — PRD v2 Legal & Compliance

## 1. Ownership
- Users retain full ownership of uploaded footage.
- Users own the generated outputs.

## 2. Privacy
- No training on user media unless explicit opt-in.
- Access controls ensure user_id scoping.

## 3. Storage & Retention
Retention by plan:
- Free: 7 days
- Creator: 90 days
- Pro/Studio: 1 year+

User can delete:
- projects
- assets
- outputs (permanent deletion)

## 4. Acceptable Use
- No illegal content.
- No copyright infringing uploads unless user has rights.
