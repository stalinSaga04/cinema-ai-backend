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

