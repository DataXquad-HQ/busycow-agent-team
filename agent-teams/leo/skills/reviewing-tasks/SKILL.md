---
name: reviewing-tasks
description: >
  Query and summarise tasks from the {{COMPANY_NAME}} Task Tracker with Goal-first
  prioritisation. Use when user asks "what tasks do I have", "what's due today",
  "standup", "task list", "this week's priorities", or wants a workload overview grouped by Goal.
triggers:
  - "what tasks"
  - "what's due"
  - "standup"
  - "task list"
  - "today's tasks"
  - "this week"
  - "task overview"
  - "this week's priorities"
  - "what do I need to do"
version: "2.0"
author: {{COMPANY_NAME}}
---

# Reviewing Tasks

## Base & Tables
- **App Token:** `MtvNbgCHXaRAaUsWXsCjnekep2g`
- **Tasks:** `tblOqgxrhF6o1nUX`
- **Initiatives:** `tbl2xxpxkLIQuRPM`
- **Goals:** `tblkpN1cyt1CWwoY`

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
🔴 Due today / Overdue
  • [Task] — [Owner] — [Goal > Initiative]

⚡ High priority, no scheduled time
  • [Task] — [Owner] — [Goal > Initiative]

📋 Grouped by Goal
  [Goal Name]
    [Initiative Name]
      • [Task] — [Owner] — [Deadline / no deadline]
```

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
