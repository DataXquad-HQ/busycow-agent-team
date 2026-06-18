---
name: managing-tasks
description: >
  Create and update tasks in the DataXquad Task Tracker (Lark Base). Triages
  multi-task dumps automatically — extracts every action item from a message,
  auto-assigns Initiative and Goal, and saves in one batch. Use when user says
  "記下來", "追蹤一下", "寫進去", "add a task", "update task", "mark done",
  or mentions anything that needs to be tracked as an action item.
triggers:
  - "記下來"
  - "追蹤一下"
  - "寫進去"
  - "add a task"
  - "update task"
  - "mark done"
  - "task status"
  - "new task"
version: "2.0"
author: DataXquad
---

# Managing Tasks

## Source-of-Truth Guard

Before creating or updating a task, confirm which task system the user means.

- Use this skill only for the **DataXquad Task Tracker in Lark Base**.
- If the user wants to use **default Lark Tasks / Feishu Tasks**, route to `lark-task` instead of writing into the Base table.
# Managing Tasks

## Scope Guard — DataXquad task source of truth

This skill manages the **legacy DataXquad Lark Base task tracker**.

When the user wants to use **default Lark Tasks / tasklists**, do **not** use this skill — route to `lark-task` instead.

If the user says "create a task" or "update a task" ambiguously, first determine whether they mean:
- default Lark Tasks / tasklists → use `lark-task`
- legacy custom Base tracker → use this skill

Current DataXquad operating preference: live task execution should use **default Lark task features** rather than the older custom Base.

## DataXquad Task System Rule (2026-06)

For DataXquad internal operations, **Lark default tasks are the primary structural task layer**.

Use default Lark tasks when the user wants to create, track, assign, review, or close actual work items.
Use GBrain / Hindsight for memory, decisions, entity knowledge, and context — **not** for execution tracking.
Use the older Lark Base task table only when the user explicitly asks for that legacy system or when maintaining old records during migration.

When operating on default tasks, keep output short and highly scannable: brief recommendation, direct next action, minimal explanation.

## DataXquad Default Rule — Prefer Lark Default Tasks for Internal Execution

For DataXquad's active internal operating system, **Lark default Tasks are the system of record for execution**. Use them for live task ownership, follow-up, status, and KR-linked execution work.

Use this Base-backed skill only when one of these is true:
- the user explicitly asks to use the legacy Task Tracker Base
- you are maintaining historical Base records
- the workflow depends on fields that exist only in the Base layer

Do **not** default to the Base tracker just because it already exists. Memory/knowledge belong in GBrain/Hindsight; executable work belongs in Lark default Tasks.

See `references/lark-default-tasks-operating-rules.md` for the default-task operating model and the OKR ↔ execution split.
See `references/lark-task-okr-migration.md` when migrating legacy Base Goals / Initiatives into default Lark Task lists.

## CRM Context Handoff

### With Context (from managing-sales-pipeline / managing-partnership-pipeline)
When called from `managing-sales-pipeline` or `managing-partnership-pipeline`, a CRM record_id will be passed as context. Use it to auto-link the Task:

| Caller | Context passed | Field to fill | Field ID |
|--------|---------------|---------------|----------|
| managing-sales-pipeline | `opportunity_record_id` | Opportunity | `fldxTM0Op2` |
| managing-partnership-pipeline | `partnership_record_id` | Partnership | `flderan4Kb` |

**Rule:** If context contains a record_id, fill the corresponding DuplexLink silently — do NOT ask the user. Mention it inline: `「→ 已連結 Opportunity OP-2026-XXX」`

### Standalone Mode (no CRM context)
When invoked standalone (no CRM handoff context), both Opportunity and Partnership fields are optional. This is the common case for:
- Cron-job task review/execution (automated agent workflows)
- Direct task creation from conversation (not tied to a specific deal/partner)
- Cross-functional tasks (operations, research, etc.)

**Pattern:** If the task naturally belongs to a deal or partner, ask. If it's independent (e.g., "install skills", "audit database"), leave both fields empty.

---

## Base & Tables
- **App Token:** `MtvNbgCHXaRAaUsWXsCjnekep2g` (Sales & Ops Base)
- **Tasks:** `tblOqgxrhF6o1nUX`
- **Initiatives:** `tbl4DGbsJFmx3Mfd`
- **Goals:** `tblt9kHfcRVm3he9`

## Architecture
```
          Goal
         / | \
Initiative Opp Partnership
          \ | /
           Task
```
- **Goal** — 12–18 month business outcome. Rarely changes.
- **Initiative** — Focused internal/strategy workstream toward a Goal (not driven by a specific deal or partner relationship).
- **Opportunity** — A concrete sales deal toward a Goal.
- **Partnership** — An ongoing partner relationship toward a Goal.
- **Task** — Concrete action item. The only layer users need to input.

All three (Initiative / Opportunity / Partnership) connect directly to a Goal. They are peers, not a hierarchy.

---

## Scope guard — Base tracker vs Lark default Tasks

This skill manages the **DataXquad Lark Base task tracker**.

If the user explicitly wants to create or manage work in **Lark default Tasks / Task Lists** instead of Base:
- do **not** use this Base workflow
- route to the `lark-task` workflow instead
- keep tasks as structural execution data, and keep memory / knowledge in GBrain or Hindsight

## Output style

When confirming task intake:
- keep the confirmation short and highly scannable
- summarize the result instead of explaining every field choice
- add detail only when ambiguity or risk requires it

## Phase 1 — Triage

Read the full message. Extract **every distinct action item** mentioned.
A single message may contain 3–5 tasks across different people and Business Lines.

For each extracted task, identify:
- What needs to be done (task name)
- Who is responsible (default: the person speaking)
- Any deadline or urgency signal
- Business Line + keyword signals for Initiative matching

Present parse back silently — do NOT ask for confirmation unless genuinely ambiguous.
Save all tasks, then confirm in one summary at the end.

---

## Phase 2 — Initiative & Goal Auto-Assignment

Every task **must** be linked to an Initiative and Goal. Never leave blank.

### Match Logic (references/initiative-logic.md)
| Confidence | Action |
|------------|--------|
| >80% | Link silently, mention inline: "→ 歸入 [Initiative]" |
| Ambiguous | Ask once: "歸入 [X] 還是 [Y]？" |
| No match | Propose new Initiative, wait for confirmation, then create |

### Goal Record IDs
| Business Line | Goal Record ID |
|---------------|----------------|
| BusyCow | `recvk50RBz2xk5` |
| GeoKernel | `recvk50S1aUBia` |
| AquaOptima | `recvk50SoAHGfD` |
| DataXquad | `recvk50SSQ0qSD` |

---

## Phase 3 — Save to Lark

### Tasks Table Fields

> ⚠️ **CRITICAL**: Always write fields using **field names as keys**, NOT field IDs.
> Field IDs change. Using field IDs returns error 1254045 FieldNameNotFound.
>
> **For record updates:** Use `--record-id <recXXX>` parameter, NOT a field called "Record ID".
> Record ID is metadata, not a table field. Passing it as a JSON key returns error 1254045.

| Field Name (use as key) | Field ID (ref only) | Type | Notes |
|-------------------------|---------------------|------|-------|
| Title | fld2Z0Yi15 | Text (primary) | Format: `[TAG] action description` (field name is "Title" NOT "Task Name") |
| Done | fldEBSzJLw | Checkbox | `true` = completed, `false` = pending |
| Deadline | fldDIaKjCR | DateTime | ms timestamp UTC+8 |
| Business Line | fldDvd3nth | SingleSelect | DataXquad / GeoKernel / AquaOptima / TRACI / Distify / BusyCow |
| Responsible Person | fldbU06WCv | User | `[{"id": "open_id"}]` + user_id_type: open_id |
| Priority | fld0kpXg4L | SingleSelect | 🔴 High / 🟡 Medium / 🟢 Low |
| Description | fldp3pHhSW | Text | |
| 📋 Initiatives-Tasks | fldqeHI96Y | DuplexLink → Initiatives | `["recXXX"]` — plain array of strings. Field name key is `"📋 Initiatives-Tasks"` (with emoji) |

### New Fields (observed schema as of 2026-06)
| Field | Field ID | Type | Notes |
|-------|----------|------|-------|
| Related Deal | fldxTM0Op2 | DuplexLink → Deal | Optional — current live field name is `Related Deal` |
| Related Partnership | flderan4Kb | DuplexLink → Partnership | Optional — current live field name is `Related Partnership` |
| Agent Advice | fldXvVWDRd | Text | Present in current live schema |
| Output Link | fldjiF87Cu | Url | Present in current live schema |

> 2026-06 schema note: the live Tasks table currently exposes 11 fields only. Legacy references in this skill to `Opportunity`, `Partnership`, `Agent Status`, `執行日誌`, `Depends On`, or `Handoff Context` are not present in the observed live schema and should be treated as future/alternate-schema notes, not assumptions for write operations.

### Team IDs
| Person | Open ID |
|--------|---------|
| Hunter | `ou_f1117d10f3560d86cf7c99ce0a156be1` |
| Kevin | `ou_9ba57313a31d3033aad77865df63cb3f` |

### Save order (if new Initiative needed)
1. Create Initiative in `tblp4JYCAFs9TLlk` → get record_id
2. Create Task(s) linked to new Initiative

---

## Dispatcher Context Rule

When reading tasks to dispatch to an Agent worker, **always fetch Goal + Initiative context** — not just the task itself. A worker that only sees the task name lacks business context to make good decisions.

Fetch sequence:
1. Read Task record → get `📋 Initiatives-Tasks` link field → get Initiative record_id
2. Read Initiative record → get `Goal` link field → get Goal record_id + Goal name
3. Bundle all three levels into the worker prompt

**Context hierarchy:**
```
Goal: {goal_name} — {goal_description}     ← "why this matters strategically"
Initiative: {initiative_name}               ← "which workstream this belongs to"
Task: {task_name} + {description}           ← "exactly what to do"
```

Without Goal + Initiative, workers produce generic outputs. With them, workers produce context-appropriate deliverables.

---

After saving all tasks, output one summary table:

```
✅ 已記錄 N 個任務：

| Task | Initiative | Responsible | Deadline | Priority |
|------|-----------|-------------|----------|----------|
| ... | ...       | ...         | ...      | ...      |
```

---

## Updating Tasks
- Search by Task Name if no record ID
- To mark done: set `Done = true`
- After marking Done → ask if there's a next action
- **Cron-mode execution:** See `references/cron-task-execution.md` for the full pattern including Filter → Update → Execute → Report loop

## Pitfalls
- **CRITICAL: Always use field NAMES as keys, never field IDs.** Field IDs change when tables are rebuilt/migrated. Using field IDs returns error 1254045 FieldNameNotFound. Confirmed working pattern: `{"Task Name": "...", "Business Line": "BusyCow", ...}`
- **CRITICAL: Record ID is metadata, NOT a table field.** When updating an existing task, pass the record ID via `--record-id <recXXX>` parameter, NOT as a JSON field `{"Record ID": "..."}`. Using "Record ID" as a field key returns error 1254045 FieldNameNotFound.
- User field MUST be array: `[{"id": "..."}]` + param `user_id_type: open_id`
- DuplexLink (e.g. `📋 Initiatives-Tasks`) = plain array of strings: `["recXXX"]` — NOT `{"link_record_ids": [...]}`
- Related Deal / Related Partnership DuplexLink fields MUST use the current live field names (`Related Deal`, `Related Partnership`), not legacy names like `Opportunity`
- Deadline = ms timestamp UTC+8 — use timestamp helper below
- **Deadline format by tool**: when using `lark-base +record-upsert` (CLI), pass as string `"YYYY-MM-DD HH:mm:ss"`. Ms timestamp is for the MCP-based `mcp_lark_bitable_v1_appTableRecord_create` tool only.
- **`lark-base +record-upsert` does NOT accept `--user-id-type` flag** — only MCP tool has this param. Pass user array directly in JSON body: `[{"id": "ou_xxx"}]`; CLI infers ID type automatically.
- Default Priority = 🟡 Medium if not specified
- Default Done = false (unchecked) for new tasks
- To clear a Deadline, pass `null`: `{"Deadline": null}`
- Lark MCP has NO delete record tool. Direct API delete returns 403 (app missing `bitable:record:delete` scope). Mark unwanted records `Done: true` as the only available workaround unless the Lark app scope is updated.

## Timestamp (UTC+8)
```python
from datetime import datetime, timezone, timedelta
tz = timezone(timedelta(hours=8))
ms = int(datetime(year, month, day, tzinfo=tz).timestamp() * 1000)
```
