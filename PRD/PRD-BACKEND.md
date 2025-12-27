BACKEND & LOGIC CONTRACT
Purpose:
Defines how the system thinks, enforces rules, and transitions state.

# PRD-BACKEND.md
CINEMA AI – BACKEND CONTRACT

---

## CORE WORKFLOW

1. Project Creation (Creator only)
2. Clip Upload
3. Analysis (async, CPU-only)
4. Reverse Script Generation
5. Auto Draft Creation
6. AI PAUSE (Mandatory)
7. Approval & Final Render

---

## REVERSE-ENGINEERED VIDEO CREATION

- Script is written AFTER footage analysis
- Script must fit scene durations
- Script must not invent visuals
- Output must be timestamp-locked

---

## PROJECT STATE MACHINE (MANDATORY)

CREATED
→ UPLOADED
→ ANALYZING
→ DRAFT_READY
→ WAITING_APPROVAL
→ RENDERING
→ COMPLETED

Illegal transitions MUST be blocked.

---

## USER ROLES (STRICT)

### ADMIN
- System operator only
- No content editing

### CREATOR
- Owns project
- Uploads footage
- Approves renders
- Downloads output

### EDITOR
- Review & suggest only
- Cannot upload or render

---

## PERMISSION MATRIX (ENFORCED IN BACKEND)

| Action | Admin | Creator | Editor |
|------|------|--------|--------|
| Create project | ❌ | ✅ | ❌ |
| Upload clips | ❌ | ✅ | ❌ |
| Trigger analysis | ❌ | ✅ | ❌ |
| Edit script | ❌ | ✅ | ✅ |
| Approve draft | ❌ | ✅ | ✅ |
| Final render | ❌ | ✅ | ❌ |
| Download | ❌ | ✅ | ❌ |

Frontend must not be trusted.

---

## DECISION AUTHORITY (LOCKED)

`brain_controller.py` is the SINGLE authority for:
- Camera behavior
- Stabilization & clarity
- Render limits
- Role enforcement
- State transitions

All other files MUST execute instructions only.

---

## CAMERA & EDITING RULES (MVP)

✔ Light stabilization (micro-jitter only)  
✔ Soft clarity / contrast lift  
✔ Audio normalization  

❌ No camera correction  
❌ No cinematic smoothing  
❌ No AI upscaling  

Editing rules:
- High motion → short cuts
- Low motion → longer narration
- Face detected → minimal transitions

---

## RENDERING RULES (FREE TIER)

- FFmpeg only
- CPU-only
- Async queue
- 720p output
- Watermark
- Duration cap

---

## OUT OF SCOPE (MVP)

- B-roll
- Timeline UI
- Real-time preview
- AI video generation
- Advanced VFX

---

✅ END OF BACKEND PRD