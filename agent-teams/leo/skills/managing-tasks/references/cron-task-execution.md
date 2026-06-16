# Cron-Mode Task Execution Pattern

## When This Applies
- Running as scheduled cron job (no interactive user present)
- Fetching agent-specific tasks via Worker Type field
- Executing tasks autonomously and updating status
- Writing results back to Lark Base without confirmation loops

## Pattern Overview

```
Query → Filter by Worker Type → Update Status → Execute → Report → Mark Done
```

## Query & Filter

Use `lark-cli base +record-list` to fetch all tasks:

```bash
lark-cli base +record-list \
  --base-token <base_token> \
  --table-id tblOqgxrhF6o1nUX \
  --limit 100 \
  --as bot
```

Filter in-memory for:
- `Worker Type` = `"<agent_name>"` (e.g., "Leo", "Maya", "Quinn", "Rex")
- `Done` = `false` (pending/incomplete tasks only)

## Update Workflow

### 1. Mark "In Progress"
Before executing, set task status to "In Progress":

```bash
lark-cli base +record-upsert \
  --base-token <base_token> \
  --table-id tblOqgxrhF6o1nUX \
  --record-id <recXXX> \
  --json '{"Done": false, "Task Status": "In Progress"}'
```

### 2. Execute Task

Parse `Task Name` and `Description` fields. Execute according to task type:
- Installation tasks: verify symlinks, check files
- Data operations: query/update Lark or external systems
- Analysis tasks: compute and report results
- Sync tasks: pull/push data between systems

### 3. Record Execution Result

Append execution log to `Execution Log` field (append mode, do NOT overwrite):

```bash
lark-cli base +record-upsert \
  --base-token <base_token> \
  --table-id tblOqgxrhF6o1nUX \
  --record-id <recXXX> \
  --json '{
    "Done": true,
    "Task Status": "Done",
    "執行日誌": "✓ TASK_NAME completed on 2026-06-01\nDetails: ...\n"
  }'
```

### 4. Handle Blocking

If task cannot complete:

```bash
lark-cli base +record-upsert \
  --base-token <base_token> \
  --table-id tblOqgxrhF6o1nUX \
  --record-id <recXXX> \
  --json '{
    "Done": false,
    "Task Status": "Blocked",
    "執行日誌": "⚠️ Blocked: [reason]\nAction: [what needs to happen]\n"
  }'
```

## Cron Output Behavior

- **If tasks found & executed:** Output full summary table with Task Name, Status, Responsible Person, Deadline
- **If no pending tasks:** Output `"<Agent> online — no pending tasks today."`
- **Do NOT use send_message:** Cron system auto-delivers final response to configured destination
- **Silent mode:** If genuinely nothing to report, respond with exactly `[SILENT]` (no other text)

## Field Mappings (Task Table)

| Display Name | Actual Field Name | Type | Notes |
|---|---|---|---|
| Task | Task Name | Text | Primary identifier |
| Done | Done | Checkbox | true = completed, false = pending |
| Task Status | Task Status | SingleSelect | "Pending", "In Progress", "Done", "Blocked" |
| Responsible Person | Responsible Person | User | Array: `[{"id": "ou_xxx"}]` |
| Worker Type | Worker Type | SingleSelect | "Leo", "Maya", "Quinn", "Rex", etc. |
| Execution Log | 執行日誌 | Text | Append-only log of execution results |

## Error Handling

### Common Issues

1. **Auth missing** — `missing required scope(s): base:record:read`
   - Already fixed in this context: bot identity fallback
   - Cron should use `--as bot` for unattended access

2. **Record not found** — `record_id` is stale or typo
   - Verify record exists with `+record-get` before updating
   - Log the error to `執行日誌` and mark status "Blocked"

3. **Field name wrong** — error 1254045 FieldNameNotFound
   - ALWAYS use field NAMES, NOT field IDs (e.g., "Done", NOT "fldEBSzJLw")
   - Verify field names match actual table structure with `+field-list`

### Safe Retry Pattern

For transient failures (network, rate limit):
- Retry up to 2 times with 1-second delay
- If still fails, mark status "Blocked" and note error
- Do NOT loop indefinitely in cron context

## Session Record Example

From 2026-06-01 execution:

```
Task: [LEO] Install Role-Specific Skills
Record ID: recvldbLa0E5Yl
Worker Type: Leo
Status: Pending → In Progress → Done

Execution:
✓ ALL SKILLS VERIFIED (2026-06-01)
  - managing-sales-pipeline ✓
  - managing-partnership-pipeline ✓
  - generating-quotations ✓
  - generating-invoices ✓
  - reviewing-sales-pipeline ✓
  - capturing-sales-intel ✓
```

## Notes for Future Sessions

- Cron mode has NO user interaction — all decisions must be deterministic
- Agent identity (Worker Type) drives which tasks to process
- Execution logs accumulate — each run appends, never overwrites
- If a task requires user confirmation, mark it "Blocked" and note why
- Multi-agent pattern: each agent checks for tasks with matching Worker Type
