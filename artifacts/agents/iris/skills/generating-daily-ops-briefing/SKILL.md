---
name: generating-daily-ops-briefing
description: >
  Generate and post the daily internal operations briefing to the [Ops] Internal Operations
  Lark channel. Covers pending internal tasks, blocked items, agent cron health, and any
  infrastructure flags. Separate from the founder task briefing — this is the team-facing
  daily ops pulse. Use when called by the daily ops briefing cron or when user says
  "post ops briefing", "daily ops update".
triggers:
  - "post ops briefing"
  - "daily ops update"
  - "ops briefing"
  - "internal operations update"
version: "1.0"
---

# Daily Ops Briefing

## Purpose
Post a concise daily operations update to `[Ops] Internal Operations` channel
(`oc_593217cd09595c75ea4dbc4dbe4ee96c`). Covers internal task health, agent status,
and any flags needing founder attention. NOT a task board summary — that goes to founders
separately. This is the team-facing ops pulse.

---

## Step 1: Confirm Taiwan Date/Time

```bash
TZ=Asia/Taipei date '+%Y-%m-%d %H:%M'
```

---

## Step 2: Pull Internal Task Status

Query the Lark Base task board for internal ops tasks (non-sales):

Using `reviewing-tasks` skill — filter for:
- Tasks NOT assigned to Leo (non-sales)
- Status = In Progress or Blocked
- Due today or overdue

Focus on: ops, infrastructure, product, team management tasks.

---

## Step 3: Check Agent Cron Health

Quick check — were any Iris crons in error state in the last 24 hours?

```bash
# Check last run status of key crons via cron list
hermes cron list 2>/dev/null | grep -E "error|failed" | head -10
```

Flag any cron with `last_status: error`.

---

## Step 4: Check GBrain & Hindsight

Quick health pulse (not the full audit — that's the health check cron):

```bash
# GBrain: any sync failures?
TZ=Asia/Taipei date  # confirm time
# Check dx-gbrain git log for last commit
cd /mnt/disks/data/dx-gbrain && git log --oneline -1 2>/dev/null
```

```
GET http://localhost:8888/v1/default/banks
```
Confirm all banks reachable. Flag if any bank returns error.

---

## Step 5: Compose and Post Briefing

**Format:**

```
📋 Ops Briefing — [DATE] [TIME] TWN

**Internal Tasks**
- ✅ [N] tasks on track
- ⚠️ [N] tasks blocked: [brief description]
- 🔴 [N] tasks overdue: [brief description]

**Agent Health**
- [Cron status summary — "all green" or list issues]

**Memory Health**
- GBrain last sync: [date/time]
- Hindsight banks: [ok / issues]

**Flags for Founders**
- [Any item needing decision or attention — or "None today"]
```

**Post to Lark:**
```
lark-cli im +messages-send --chat-id oc_593217cd09595c75ea4dbc4dbe4ee96c \
  --text "[briefing content]" --as bot
```

**Rules:**
- Keep it under 20 lines — this is a pulse, not a report
- Only flag items that need human attention — don't list everything
- If everything is green: post a one-liner: "📋 Ops [DATE] — all green ✅"
- Never post to [System] Backend Report — that's for machine logs only

---

## Pitfalls

- Skip this briefing if it's a weekend AND there are no active blockers or errors — reduce noise
- If task board is unreachable, note it as a flag rather than crashing the briefing
- Hindsight check is a lightweight ping only — do not run full health audit here
