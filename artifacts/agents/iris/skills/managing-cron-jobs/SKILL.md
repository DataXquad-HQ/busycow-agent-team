---
name: managing-cron-jobs
description: >
  Create, update, pause, resume, or delete Hermes cron jobs — and sync all changes
  to the Hermes Backend Lark Base. Use when user asks to schedule a task, change a
  cron schedule, stop a cron job, or review existing cron jobs.
triggers:
  - "schedule a task"
  - "create a cron job"
  - "change cron schedule"
  - "stop cron job"
  - "pause cron"
  - "create cron"
  - "update cron"
  - "delete cron"
version: "1.0"
author: [Org]/[Product A]
---

# Managing Cron Jobs

## Lark Base — Cron Registry (SSoT)
- **App token**: `{{LARK_APP_TOKEN}}`
- **Table**: `{{LARK_TABLE_ID}}`
- Always update Base **after** any cron change — it is the source of truth

## Time Convention
- All schedules stored and discussed in **UTC**
- TWN = UTC+8 (e.g. 03:00 TWN = 19:00 UTC)
- Cron jobs run in **02:00–06:00 TWN window** (UTC 18:00–22:00) — avoid active work hours
- See `hermes-cron-scheduling` skill for full windowing rules

## Workflow

### Create
1. `cronjob(action='create', schedule='...', prompt='...', name='...')`
2. Note the returned job_id
3. Add record to Lark Base:
   - Name, Schedule (UTC), Job ID, Deliver target, Skills attached, Status=Active

### Update schedule/prompt
1. `cronjob(action='update', job_id='...', schedule='...', prompt='...')`
2. Update matching record in Lark Base

### Pause / Resume
1. `cronjob(action='pause'/'resume', job_id='...')`
2. Update Status field in Lark Base → Paused / Active

### Delete
1. `cronjob(action='remove', job_id='...')`
2. Delete or mark Status=Deleted in Lark Base record

### List / Review
1. `cronjob(action='list')` — shows all jobs with status
2. Cross-check with Lark Base to catch orphaned jobs (in Base but not in scheduler, or vice versa)

## Lark Base Fields
| Field | Notes |
|-------|-------|
| Name | Human-readable job name |
| Job ID | From cronjob() return value |
| Schedule | Cron expression in UTC |
| Deliver | e.g. `feishu:oc_xxx` or `telegram:-100xxx:thread` |
| Skills | Comma-separated skill names attached |
| Status | Active / Paused / Deleted |
| Notes | Purpose / trigger context |

## Current Cron Jobs (reference — verify with cronjob(action='list'))
| Name | Schedule UTC | Job ID |
|------|-------------|--------|
| GBrain Nightly Dream + Memory Sync | 20:00 daily | e48c20e44c01 |

## Batch Delete from Lark Base (when clearing stale records)
```bash
source ~/.hermes/.env
TOKEN=$(curl -s -X POST "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")
for RID in recXXX recYYY recZZZ; do
  curl -s -X DELETE "https://open.larksuite.com/open-apis/bitable/v1/apps/{{LARK_APP_TOKEN}}/tables/{{LARK_TABLE_ID}}/records/$RID" \
    -H "Authorization: Bearer $TOKEN"
done
```

## Per-Profile Cron Jobs (Multi-Agent)

To create a cron job that runs under a specific agent profile (e.g. Leo, Maya), pass `profile=`:

```python
cronjob(
    action='create',
    name='Leo Daily Task Poller',
    profile='leo',                  # ← runs as this profile
    schedule='0 1 * * *',           # 09:00 TWN = 01:00 UTC
    skills=['managing-tasks', 'reviewing-tasks', 'lark-base'],
    prompt='You are Leo... query Task Board for Worker Type=Leo tasks...',
    deliver='feishu:oc_xxx'
)
```

**Key rules:**
- `profile=` must match an existing profile name (`hermes profile list`)
- Jobs with `profile=` run sequentially (not parallel) — by design for isolation
- The profile's own skills, memory, GBrain, and SOUL.md are active during the run
- Taiwan 09:00 = UTC 01:00 (`0 1 * * *`)

**Standard Kanban Task Poller prompt pattern (per agent):**
```
You are {Name}, the {Role} agent. Load the managing-tasks skill.

Query the Task Board (app_token: {{LARK_APP_TOKEN}}, table: {{LARK_TABLE_ID}}) for tasks where:
- Worker Type = "{Name}"
- Task Status = "Pending" or "Not Started"

For each task found:
1. Update Task Status → "In Progress"
2. Execute the task per its description
3. Update Task Status → "Done", write output to execution log field
4. If blocked → set "Blocked" + note reason

If no tasks: reply "{Name} online — no pending tasks today."
```

## Pitfalls
- Always verify job_id from `cronjob(action='list')` — don't rely on memory
- `cronjob(action='run')` triggers immediately for testing — use before committing schedule
- Changing deliver target requires update action with full prompt re-specified
- Memory.md cron section is NOT the registry — Lark Base is SSoT
- `cronjob(action='list')` only shows jobs for the **current/default profile** — per-profile jobs only appear when listed from that profile's context. Use `hermes --profile <name> cron list` from terminal to verify.
- **Skill referencing a schedule ≠ cron exists.** A skill description may say "called by cron at 03:00 TWN" but that cron may never have been created. When installing or auditing a skill that mentions a schedule, always verify the cron actually exists with `cronjob(action='list')`. If missing, create it.
- **Self-audit prompt pattern:** when sending an agent a self-audit, explicitly include a cron jobs check — list the profile's jobs.json and verify last_status for each enabled job. Agents won't check crons unless explicitly asked.
