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

