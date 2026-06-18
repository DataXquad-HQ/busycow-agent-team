---
name: reviewing-tasks
description: >
  Query and summarise tasks from the DataXquad Task Tracker with Goal-first
  prioritisation. Use when user asks "what tasks do I have", "what's due today",
  "standup", "任務清單", "本週重點", or wants a workload overview grouped by Goal.
triggers:
  - "what tasks"
  - "what's due"
  - "standup"
  - "任務清單"
  - "today's tasks"
  - "this week"
  - "task overview"
  - "本週重點"
  - "有什麼事要做"
version: "2.0"
author: DataXquad
---

# Reviewing Tasks

## Scope guard — Base tracker vs Lark default Tasks

This skill is for the **DataXquad Lark Base task tracker** only.

If the user explicitly wants to use **Lark default Tasks / Task Lists / OKR lists** instead of Base:
- do **not** use this skill's Base workflow
- route to the `lark-task` workflow instead
- treat default Tasks as the structural execution layer, and keep GBrain / Hindsight for memory and knowledge

## Output style

For task reviews and ops summaries:
- lead with the conclusion first
- keep the response short and highly scannable
- prefer a few high-signal bullets over exhaustive lists
- do not add long explanatory paragraphs after the bullets unless the user asks

## Source-of-Truth Guidance

Before using this skill, confirm the task source.

- Use this skill only when the user wants the **DataXquad Task Tracker in Lark Base**.
- If the user wants **default Lark Tasks / Feishu Tasks**, do **not** use this skill — route to `lark-task` instead.
# Reviewing Tasks

## Scope Guard — DataXquad task source of truth

This skill is for the **legacy DataXquad Lark Base task tracker** only.

When the user means **Lark default Tasks / tasklists**, do **not** use this skill — route to `lark-task` instead.

If the user says "tasks" ambiguously, first resolve whether they mean:
- default Lark Tasks / tasklists → use `lark-task`
- legacy custom task tracker in Lark Base → use this skill

Current DataXquad operating preference: for live task management and review, prefer **default Lark task features** over the older custom Base.

## DataXquad Task System Rule (2026-06)

For DataXquad internal operations, **Lark default tasks are the primary structural task layer**.

Use default Lark tasks for active work review, owner visibility, follow-up tracking, and operational execution.
Use GBrain / Hindsight for memory, decisions, and knowledge context — **not** as the task system.
Treat the older Lark Base task table as legacy: only query it if the user explicitly asks for the Base system or if you are cleaning up historical records.

When presenting task reviews, keep the output short and highly scannable — priorities first, compact bullets, no long explanatory prose.

## Base & Tables
- **App Token:** `MtvNbgCHXaRAaUsWXsCjnekep2g`
- **Tasks:** `tblOqgxrhF6o1nUX`
- **Initiatives:** `tbl4DGbsJFmx3Mfd`
- **Goals:** `tblt9kHfcRVm3he9`

> 2026-06 schema note: verify live field names against the Tasks table before querying. Current observed field names include `Title`, `Done`, `Deadline`, `Business Line`, `Responsible Person`, `Priority`, `Description`, `Agent Advice`, `Related Deal`, `Related Partnership`, and `Output Link`. Older references to `Task Name`, `Opportunity`, or legacy linked-table IDs are stale.

---

## Query Pattern

1. Fetch all tasks (page_size=100, paginate if has_more)
2. Filter: `Done = false`
3. For each task, resolve Initiative name + Goal name via linked record IDs
4. Apply Goal-first grouping and sort (see below)

---

## Goal-First Output Structure

Present tasks in this order — not a flat list:

```
🔴 今天到期 / 已逾期
  • [Task] — [Owner] — [Goal > Initiative]

⚡ 高優先、未排時間
  • [Task] — [Owner] — [Goal > Initiative]

📋 按 Goal 分組
  [Goal Name]
    [Initiative Name]
      • [Task] — [Owner] — [Deadline / no deadline]
```

Output discipline:
- Keep the summary short and easy to scan.
- Default to the minimum useful grouping, not a full dump.
- Prefer bullets over prose blocks.
- If the user did not ask for exhaustive detail, stop once the priorities are clear.

Rules:
- Overdue = deadline < TODAY_START → always surface first, mark ⚠️
- Due today = TODAY_START ≤ deadline ≤ TODAY_END → 🔴
- High priority + no deadline → ⚡ section
- Everything else → grouped by Goal → Initiative
- Within each group: sort by deadline asc, then priority

---

## Date Windows (UTC+8)

```python
from datetime import datetime, timezone, timedelta
tz = timezone(timedelta(hours=8))
today = datetime.now(tz).date()
TODAY_START = int(datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=tz).timestamp() * 1000)
TODAY_END   = int(datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=tz).timestamp() * 1000)
```

---

## Name Resolution

```python
uid = responsible[0].get('id', '')
if uid == 'ou_f1117d10f3560d86cf7c99ce0a156be1':
    name = 'Hunter'
elif uid == 'ou_9ba57313a31d3033aad77865df63cb3f':
    name = 'Kevin'
```

---

## In Cron Context
MCP tools unavailable — use direct REST API.
See `references/lark-api-auth.md` for credentials and curl pattern.

---

## Pitfalls
- Lookup fields (Goal on Tasks table) are read-only computed — don't try to write them
- Initiative DuplexLink returns array of record objects — resolve name via separate fetch if needed
- Empty deadline = no deadline, not overdue — don't treat as urgent unless Priority = High

## References
- `references/lark-api-auth.md` — API credentials and curl pattern
- `references/timestamp-helper.md` — date to ms conversion
