1️⃣ PRD.md — MASTER LAW (LOCKED)

Purpose:
Defines identity, scope, and authority hierarchy.
Every model MUST read this first.

# CINEMA AI – MASTER PRD (LOCKED)

Version: MVP v1.2

⚠️ THIS FILE IS LAW

This is the SINGLE SOURCE OF TRUTH for Cinema AI.

If any instruction, code, suggestion, or model output
conflicts with this file → IT MUST BE REJECTED.

---

## NON-NEGOTIABLE RULES (FOR MODELS & DEVELOPERS)

Models MUST:
- Read this file fully before touching code
- Analyze existing code before modifying anything
- Make incremental changes only
- Respect MVP scope strictly

Models MUST NOT:
- Rewrite architecture
- Rename folders or files
- Add B-roll
- Add GPU-heavy or real-time features
- Add timeline-based editing

---

## PRODUCT IDENTITY (LOCKED)

Cinema AI IS:
- An AI Video Director
- A decision-making system
- A discussion-based editor

Cinema AI IS NOT:
- A timeline editor
- A camera enhancement tool
- A generative video platform
- A real-time editor

If a feature contradicts this identity → DO NOT IMPLEMENT.

---

## AUTHORITY HIERARCHY

1. This file (`PRD.md`) – FINAL LAW
2. `PRD-BACKEND.md` – Backend behavior & logic
3. `PRD-WORKERS.md` – Job execution & workers
4. `PRD-UI.md` – Dashboard & UI contract

If a conflict exists:
PRD.md > Backend > Workers > UI

---

## MVP SCOPE GUARANTEE

Cinema AI MVP prioritizes:
- Cost safety
- Deterministic behavior
- Async processing
- Human-in-the-loop approval

Advanced features are intentionally excluded.

---

✅ END OF MASTER PRD
