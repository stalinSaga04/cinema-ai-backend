WORKER & EXECUTION CONTRACT

Purpose:
Defines how slow work is executed safely and cheaply.

# PRD-WORKERS.md
CINEMA AI – WORKER CONTRACT

---

## WHAT IS A WORKER

A Worker is a background Python process that performs
slow, non-interactive tasks so the API remains fast.

A Worker is NOT:
- A microservice
- A user role
- A frontend concept

---

## RESPONSIBILITY SPLIT

### API SERVER
- Auth & RBAC
- Project creation
- Job enqueue
- State updates
- Immediate responses

MUST NOT:
- Run FFmpeg
- Analyze video
- Perform rendering

---

### WORKER PROCESS
- Poll jobs table
- Execute analysis / draft / render
- Update job & project status

MUST NOT:
- Decide product behavior
- Bypass brain_controller.py
- Expose HTTP endpoints

---

## JOB QUEUE MODEL

Jobs are stored in the database:
- id
- type (analyze / draft / render)
- status
- payload
- timestamps

Workers:
- poll
- lock one job
- process
- update status

No external queue systems allowed in MVP.

---

## MVP vs PRODUCTION MODE

Controlled by `RUN_INTERNAL_WORKER`.

### MVP (Free Tier)
- Worker MAY run as internal background thread
- RUN_INTERNAL_WORKER=true (default)
- Jobs MUST still use jobs table

### Production
- Worker MUST be a separate service
- RUN_INTERNAL_WORKER=false
- API must NOT execute background jobs

Architecture MUST remain identical.

---

## FORBIDDEN

❌ Celery, Kafka, Redis, RabbitMQ  
❌ Real-time workers  
❌ Per-user workers  
❌ Worker-side decisions  

---

## FINAL RULE

If a task is slow → Worker  
If a task decides behavior → brain_controller.py  
If a task talks to users → API  

---

✅ END OF WORKER PRD