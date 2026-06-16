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
- Direct task creation from conversation (not tied to a specific opportunity/partner)
- Cross-functional tasks (operations, research, etc.)

**Pattern:** If the task naturally belongs to a opportunity or partner, ask. If it's independent (e.g., "install skills", "audit database"), leave both fields empty.

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
- **Initiative** — Focused internal/strategy workstream toward a Goal (not driven by a specific opportunity or partner relationship).
- **Opportunity** — A concrete sales opportunity toward a Goal.
- **Partnership** — An ongoing partner relationship toward a Goal.
- **Task** — Concrete action item. The only layer users need to input.

All three (Initiative / Opportunity / Partnership) connect directly to a Goal. They are peers, not a hierarchy.

---

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

### New Fields (added May 2026)
| Field | Field ID | Type | Notes |
|-------|----------|------|-------|
| Opportunity | fldxTM0Op2 | DuplexLink → Opportunity | Optional — use field name "Opportunity" (NOT field ID) when writing |
| Partnership | flderan4Kb | DuplexLink → Partnership | Optional — use field name "Partnership" (NOT field ID) when writing |

### Dependency Field (added Jun 2026)
| Field Name | Field ID | Type | Notes |
|---|---|---|---|
| `Depends On` | `fldXS8Mheq` | DuplexLink → self (tblOqgxrhF6o1nUX) | List predecessor tasks; agent poller skips this task until all are Done=true. Back-field: `📋 Tasks-Depends On` (fldKmD5nzT) |

Use when a task must wait for another: fill `Depends On` with the predecessor task's record ID. The daily poller checks this field before executing.

### Dispatcher Fields (added May 2026 — Multi-Agent system)
| Field Name | Field ID | Type | Notes |
|---|---|---|---|
| `Agent Status` | fldRjvAxAV | SingleSelect | ⏳ Queued / 🤖 In Progress / 👀 Review / ✅ Accepted / 🔄 Retry |
| `Output Link` | fldjiF87Cu | Url | URL of output artifact (Google Doc, Sheet, file) |
| `執行日誌` | fldpmHTf10 | Text | Agent execution log — milestones, decisions, errors |
| `Depends On` | fldXS8Mheq | DuplexLink (self) | Linked tasks that must be Done before this task can run |
| `Handoff Context` | fldNuQ2YVY | Text | Auto-injected by upstream agent: Output Link + 執行日誌 summary from all Depends On tasks. Agent must read this before executing. |

## Data Transit Pattern (decided 2026-06-01)
- **In-task (short-lived):** `/tmp/` local files, discarded after task ends
- **Cross-agent handoff:** Google Drive file + `Output Link` field as URL index; injected into downstream `Handoff Context`
- **Long-term storage:** GBrain (knowledge/intel) or Google Drive (human-readable docs)
- **No Plane/Jira needed** — `Depends On` + `Handoff Context` covers dependency and data transit within Lark Bitable

See `devops/building-multi-agent-dispatcher` skill for full Dispatcher architecture.

> ⚠️ Pitfall: These DuplexLink fields MUST be written using their **field names** ("Opportunity", "Partnership"),
> not field IDs. Using field IDs returns error 1254045 FieldNameNotFound.

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
- Opportunity / Partnership DuplexLink fields MUST use field name (not ID): `"Opportunity": ["recXXX"]`
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
