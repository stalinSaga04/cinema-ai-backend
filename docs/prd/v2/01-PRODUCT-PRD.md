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

