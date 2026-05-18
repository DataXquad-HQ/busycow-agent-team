---
name: managing-cron-jobs
description: >
  Create, update, pause, resume, or delete Hermes cron jobs — and sync all
  changes to the Cron Registry in the Hermes Registry Lark Base.
  Use when user asks to schedule a task, change a cron schedule, stop a job,
  or review existing cron jobs.
triggers:
  - "schedule a task"
  - "create a cron job"
  - "change cron schedule"
  - "stop cron job"
  - "pause cron"
  - "新增排程"
  - "修改排程"
  - "刪除排程"
---

# Managing Cron Jobs

## Lark Base — Cron Registry (SSOT)
- App token and table ID: stored in Memory as "Hermes Registry Base → Cron Jobs table"
- Always update Lark Base **after** any cron change — it is the source of truth

## Time Convention
- All schedules in **UTC**
- Schedule cron jobs during off-hours (avoid active work periods)

## Workflow

### Create
1. `cronjob(action='create', schedule='...', prompt='...', name='...')`
2. Note the returned job_id
3. Add record to Lark Cron Registry:
   - Name, Schedule (UTC), Job ID, Deliver target, Skills attached, Status=Active

### Update
1. `cronjob(action='update', job_id='...', schedule='...', prompt='...')`
2. Update matching record in Lark Base

### Pause / Resume
1. `cronjob(action='pause'/'resume', job_id='...')`
2. Update Status field → Paused / Active

### Delete
1. `cronjob(action='remove', job_id='...')`
2. Mark record Status=Deleted in Lark Base

### Review
1. `cronjob(action='list')` — shows all jobs with status
2. Cross-check with Lark Base to catch orphaned jobs

## Lark Base Fields
| Field | Notes |
|-------|-------|
| Name | Human-readable job name |
| Job ID | From cronjob() return value |
| Schedule | Cron expression in UTC |
| Deliver | Destination platform:chat_id |
| Skills | Skill names attached |
| Status | Active / Paused / Deleted |
| Notes | Purpose and trigger context |

## Pitfalls
- Always verify job_id from `cronjob(action='list')` — don't rely on memory
- `cronjob(action='run')` triggers immediately — use for testing before setting schedule
- Changing deliver target requires update with full prompt re-specified
- Lark Base is the SSOT, not Memory
