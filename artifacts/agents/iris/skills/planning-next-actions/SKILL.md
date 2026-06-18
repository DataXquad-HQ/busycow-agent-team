---
name: planning-next-actions
description: >
  Use when user asks "what should I do next", "help me prioritize today", "what should I focus on",
  "what should I do first today", or wants a prioritised action recommendation (not just a task list).
  Pulls active tasks, scores by Goal importance × urgency × priority, and outputs
  the top 3–5 actions with reasoning — not a list, but a clear recommendation.
triggers:
  - "what should I do next"
  - "what should I do first today"
  - "help me prioritize"
  - "what should I focus on"
  - "most important thing"
  - "where should I start"
  - "help me plan today"
version: "1.0"
author: [Org]
---

# Planning Next Actions

## Source-of-Truth Guard

Before using this skill, confirm the task source.

- Use this skill only when the prioritisation should be based on the **[Org] Task Tracker in Lark Base**.
- If the user wants prioritisation from **default Lark Tasks / Feishu Tasks**, route to `lark-task` first and build recommendations from that source instead.
- If the user does not specify which task system they mean, do not assume the Base table by default.

## [Org] Task System Rule (2026-06)

For [Org] internal operations, **Lark default tasks are the primary structural task layer**.

Use default Lark tasks when deciding what the user should do next.
Use GBrain / Hindsight for memory, decisions, and supporting context — **not** as the execution tracker.
Use the older Lark Base task layer only if the user explicitly asks for the legacy Base workflow.

Output must stay short and highly scannable: 3–5 actions max, one-line reason each, no long paragraphs.

## Scope guard — Base tracker vs Lark default Tasks

This skill is for planning from the **[Org] Lark Base task tracker**.

If the user explicitly wants planning based on **Lark default Tasks / Task Lists / OKR lists** instead of Base:
- do **not** use this skill's Base workflow
- route to the `lark-task` workflow instead
- keep OKR in one list and execution tasks in another, with execution tasks linked back to KR via task metadata or naming

## Output style

When giving a recommendation:
- lead with the recommendation first
- keep it short and highly scannable
- prefer 3–5 high-signal bullets
- avoid long explanatory paragraphs unless the user asks for depth

## Purpose
Not a list — a recommendation. Tell the user what to do next and why.
Output should feel like a thinking partner, not a task manager.

## Output Discipline
- Keep the final answer short and highly scannable.
- Default to 3–5 items max.
- Each item gets one reason sentence, not a paragraph.
- Prefer one-screen answers unless the user explicitly asks for detail.

## Base & Tables
- **App Token:** `{{LARK_APP_TOKEN}}`
- **Tasks:** `{{LARK_TABLE_ID}}`
- **Initiatives:** `{{LARK_TABLE_ID}}`
- **Goals:** `{{LARK_TABLE_ID}}`

---

## Scoring Logic

For each active task (Done = false), compute a score:

```
Score = Urgency × 3 + Priority × 2 + Goal_Weight × 1

Urgency:
  5 = overdue
  4 = due today
  3 = due this week
  2 = due this month
  1 = no deadline + High priority
  0 = no deadline + Medium/Low

Priority:
  🔴 High   = 3
  🟡 Medium = 2
  🟢 Low    = 1

Goal_Weight:
  Revenue-generating Goals = 2
  Internal/ops Goals       = 1
```

Sort descending by Score. Take top 5.

---

## Output Format

```
🎯 Top [N] next actions:

1. [Task Name] — [Owner]
   → Why:[one-line reason: deadline / goal / blocking others]
   → Goal:[Goal > Initiative]

2. ...

---
💡 [Optional: one insight — e.g. "[Product B] two tasks are both blocked on the same person,
    so one follow-up can unblock both"]
```

Rules:
- Max 5 items — if fewer than 5, show all
- Each item gets ONE reason sentence — no paragraphs
- End with one optional insight if there's a pattern (same owner, same blocker, same Goal)
- If everything is low urgency / no deadline → say so and ask if priorities need updating

---

## In Cron Context
MCP tools unavailable — use direct REST API.
See `references/lark-api-auth.md` for credentials and curl pattern.

---

## Pitfalls
- Don't recommend Blocked tasks as "do next" — flag them separately
- Don't recommend tasks where Responsible Person ≠ the person asking (unless they asked for full team view)
- If user asks for "today" specifically, filter to their name only

## References
- `references/lark-api-auth.md` — API credentials and curl pattern
- `references/timestamp-helper.md` — date to ms conversion
