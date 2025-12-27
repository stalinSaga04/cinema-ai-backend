DASHBOARD & UI CONTRACT

Purpose:
Defines the only allowed UI for MVP.

# PRD-UI.md
CINEMA AI – UI CONTRACT (MVP)

---

## CORE PRINCIPLE

The UI MUST reflect backend state.
The UI MUST NOT invent workflows.

---

## REQUIRED SCREENS

1. Login (Supabase Auth)
2. Project List
3. Create Project
4. Upload Clips
5. Processing (Read-only)
6. Draft Review (AI PAUSE)
7. Paywall ($7 one-time)
8. Rendering
9. Download

---

## STATE → UI MAPPING

| State | UI |
|----|----|
| CREATED | Upload |
| ANALYZING | Spinner |
| WAITING_APPROVAL | Draft Review |
| RENDERING | Progress |
| COMPLETED | Download |

---

## DRAFT REVIEW (CORE SCREEN)

- Draft video player
- 3 AI questions
- Editable script text
- Approve Draft button (Creator only)

❌ No timeline  
❌ No skip  

---

## PAYWALL

Triggered when:
- Creator approves draft
- Free-tier limits exceeded

Copy:
“Unlock final video export for $7 (one-time)”

---

## UI MUST NOT INCLUDE

- Timeline editor
- Camera controls
- ML sliders
- Analytics
- Admin controls

---

## SUCCESS CRITERIA

- User understands what’s happening
- AI PAUSE feels intentional
- User reaches paywall naturally
- Backend states never violated

---

✅ END OF UI PRD