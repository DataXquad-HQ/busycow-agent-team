# Lark Default Tasks Operating Rules — [Org]

Use this when the user wants to run [Org] on **Lark default Tasks**, not on a custom Base.

## Core split
- **OKR list** stores Objectives and KRs.
- **Execution list** stores live tasks that someone must actually do.
- Knowledge/memory stay in GBrain/Hindsight.
- Do not use Tasks as a memory dump.

## Recommended structure

### List 1 — OKR
Store only:
- Objective
- KR
- milestone-like outcome targets

Do **not** put day-to-day execution tasks here.

### List 2 — Execution
Store only executable work:
- action item
- owner
- status
- next step
- due date if real
- linkage back to Objective / KR

## Linking execution back to OKR
Preferred pattern:
1. Add custom field `Objective` (single_select)
2. Add custom field `KR` (single_select)
3. Each execution task must map to one KR

This prevents blind activity and keeps review tied to outcomes.

## Sections vs subtasks

### Sections
Use sections for workstreams or directions, for example:
- Package
- Iris
- Maya
- Websites
- [Portfolio Company] rollout
- Governance

### Subtasks
Use subtasks only to break one execution task into smaller execution steps.
Do **not** use subtasks to represent the OKR hierarchy itself.

Bad pattern:
- KR as parent task
- execution tasks as subtasks

Better pattern:
- KR stays in the OKR list
- execution task lives in Execution list
- subtasks split the execution task only when needed

## Naming rules
- KR should read like an outcome.
- Execution task should read like a verb + object.
- If a due date is fake or aspirational, omit it and use priority instead.

## Review rule for Iris
When reviewing the execution list, ask:
- Does every task map to a KR?
- Is there any KR with no execution tasks?
- Is there any task with no owner / no next step?
- Are we doing tasks that do not move an active KR?
