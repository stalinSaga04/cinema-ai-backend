📘 CINEMA AI — FULL VIDEO SAAS PRD

Reverse Engineering → Build from Brain → then Features → then Frontend → then Scale

0. Vision Statement

CinemaAI is a full AI-powered video editing SaaS that can:

Understand uploaded raw video

Detect scenes, emotions, mistakes

Merge multiple retakes automatically

Auto-edit into reels/YouTube/movies

Allow pause-&-ask conversation editing

Apply reference styles

Generate full productions from footage

Not templates — brain-driven editing like human director.

1. Build Philosophy (Reverse Engineering)

We DO NOT start with UI or website first.

Order of build:

1. Brain Backend (Render)
2. Multi-Model Understanding
3. Auto Editor Core
4. Pause & Ask Conversational Editing
5. Reference Style/VFX Engine
6. Frontend SaaS UI
7. Cloud Worker Scaling & GPU integration

2. Phase-1: Backend Core Creation (Brain V1)

First we deploy backend on Render.
No UI, no website, only brain.

Goals:

Upload video via API

Process video using modules

Extract structure + emotion + transcript

Output TIMELINE.json

Tech Stack:
Component	Tech
Backend	FastAPI (Python)
Deploy	Render Web Service
Processing	ffmpeg + OpenCV
Speech	Whisper-small (CPU cost saving)
Emotion/Face	DeepFace
Storage	Supabase/S3 IA tier
Worker	Render initially → Runpod later
Directory:
/cinema-ai-backend
 ├ main.py
 ├ requirements.txt
 ├ core/
 │ ├ frame_extractor.py
 │ ├ audio_extractor.py
 │ ├ speech_to_text.py
 │ ├ scene_detector.py
 │ ├ emotion_detector.py
 │ ├ retake_detector.py (later)
 │ └ brain_controller.py
 ├ uploads/
 └ outputs/

API Endpoints:
POST /upload → video file
GET /status/{job_id}
GET /result/{job_id}

BrainV1 Output JSON:
{
 "transcript": "speech text...",
 "scenes":[{"start":"00:00","end":"00:14"}],
 "emotion_map":[{"time":"00:05","emotion":"happy"}],
 "characters":[{"id":"face_001"}],
 "frame_samples": ["f1.jpg","f30.jpg"]
}

Cost Control:

Delete source video after 12-24 hours

Save JSON only

Store only sampled frames (NOT full)

CPU inference only first 2 phases

GPU only when needed for long render

3. Phase-2: Retake Matching & Performance Selection (Brain V2)

User uploads 5–10 retakes → AI selects best parts.

Tasks:

✔ Compare takes using transcript similarity
✔ Detect strongest emotional expression
✔ Score clarity, pacing, delivery
✔ Build Supercut plan JSON

{
 "supercut":[
   {"scene1": "take3"},
   {"scene2": "take1"},
   {"scene3": "take4"}
 ]
}

No GPU required yet.
4. Phase-3: Auto Editing Engine (Brain V3)

Now we build video generation.

Engine functions:

Auto cut silence & mistakes

Merge best takes into master scene

Add transitions

Basic LUT color tone

Music bed placement

Render final MP4 via ffmpeg

Output Formats:
Full Video
YouTube Right Cut
Reels/Shorts highlights

5. Phase-4: Conversational Pause-Ask Editing

Core innovation — when watching video, user can pause anywhere & talk to AI.

Example:

User pauses →

“Reduce silence here”
AI edits → returns preview.

User:

“Replace with take 5 at 02:13”
AI re-cuts timeline.

We need:

✔ Real-time timeline graph
✔ Edit-by-natural-language parser
✔ Partial re-render (no full export each time)

6. Phase-5: Reference & Style Brain

User uploads reference clip or screenshot:

“Make style like KGF dark cinematic”

AI extracts:

LUT/style tone

pacing rhythm

audio mood

Applies to editing stack.

This stage requires GPU worker (Runpod hourly).

7. Phase-6: Frontend SaaS UI (after brain stable)
Tech:
Layer	Tech
Web	Next.js + Vercel
Upload UI → Render API	Axios
Player	Video.js / custom

Pages:

Upload Video

Processing Status

Video Editor Screen

Pause-Ask Chat (WebSocket or SSE)

Export Dashboard

Login/Plans/Payments

UI Preview:

[Upload Video]
[Processing...]
-------------------------------------
|      Video Player                |
|  ▌Pause   ▶Play   ◼ Stop         |
-------------------------------------
Chat:
> Make this scene bright
AI: Done. preview updated.

8. Scalable & Cost-Efficient Hosting Architecture
Frontend (Vercel)
API (Render)
Storage (S3/Supabase)
GPU Worker (On-demand Runpod)
Queue (Redis or Supabase Realtime)


🚫 No full-time GPU to avoid burn
✔ Spin GPU only during heavy rendering

9. Monetization Plan
Tier	Price	Features
Free	0$	720p, watermark, limited minutes
Pro	$15–$49	1080p, retake editor, pause-AI
Studio	$79–$199	4K, style transfer, batch
Agency	$499+	Unlimited render, team slots

Extra revenue:

Pay per render credits

Cloud storage upgrade

LUT/Style packs marketplace

10. Development Timeline (rapid speed better security and performance )

Week-1 → Render Backend Setup + Upload API
Week-2 → Frame+Audio extraction
Week-3 → Whisper + Scene detect
Week-4 → Emotion map + JSON brain
Week-5 → Retake scoring
Week-6 → Auto editor MVP
Week-7 → UI Upload + Result page
Week-8-12 → Pause edit + style engine
6–12 months → full film-grade system

Final Checklist (Everything Covered)
Feature	Phase
Video brain & analysis	✔ V1
Multi retake selection	✔ V2
Auto editing engine	✔ V3
Pause & ask AI	✔ V4
Reference style	✔ V5
Full SaaS UI	✔ V6
GPU scaling	✔ Later
Long film generation	✔ Advanced future