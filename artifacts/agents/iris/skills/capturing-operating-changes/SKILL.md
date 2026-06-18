---
name: capturing-operating-changes
description: >
  Use when a founder or Iris makes a structural / operating decision that must
  be reflected across the company state layer — for example task-system changes,
  agent-role changes, routing-rule changes, cron/governance changes, knowledge
  architecture changes, or any operating-policy update that should not live only
  in chat. Triggers durable writes to GBrain, hot memory updates, and current-
  state document updates.
triggers:
  - "we decided"
  - "from now on"
  - "change the operating rule"
  - "update the company operating state"
  - "structural change"
  - "org change"
  - "routing rule changed"
  - "task system changed"
  - "記下這個決定"
  - "更新 operating state"
version: "1.0"
author: DataXquad / Iris
---

# Capturing Operating Changes

## When to Use

Use this when the company has made a **durable operating change** that should
change how future work is routed, remembered, or executed.

Typical examples:
- a task / OKR system is changed
- an agent role is added, removed, or marked pending
- a routing rule changes (`Lark Tasks > Base`, `Ops vs System channel rule`)
- a new governance rule is established
- a memory / knowledge architecture decision is made
- a recurring operating workflow is officially adopted

Do **not** use this for:
- temporary task progress
- one-off debugging notes
- unconfirmed ideas still under discussion

---

## Write Targets

For each change, Iris should decide which layers must be updated:

| Layer | Use when |
|---|---|
| `internal/decisions/YYYY-MM-DD-[topic].md` in GBrain | a real decision was made |
| current-state docs in GBrain (`internal/company/`, `internal/business-lines/`, `internal/agents/`, `internal/systems/`) | the decision changes the current operating truth |
| Hindsight `dx-global` | the change should affect future interpretation across sessions |
| Hindsight `dx-human-hunter` / `dx-human-kevin` | the change expresses founder preference / decision style |
| task / OKR layer | the decision changes active execution priorities |

The default pattern is usually:
1. decision log
2. current-state doc update
3. Hindsight write
4. task / OKR adjustment if execution changed

---

## Steps

### 1. Classify the change

Ask:
- **What changed?** (org / task system / routing / memory / process / policy)
- **Is this confirmed?** If not confirmed, do not write it as truth.
- **What future behavior should change because of this?**

If the answer does not change future behavior, this probably does not belong in this skill.

### 2. Identify the canonical current-state doc

Update the document that should represent the **latest active truth**.

Common targets:
- company-level operating rule → `internal/company/overview.md` or another `internal/company/` page
- BL-level strategy change → `internal/business-lines/[bl]/strategy.md`
- agent role change → `internal/agents/[agent]/role.md` or equivalent active role doc
- system architecture change → `internal/systems/[topic].md`

Do not store active truth only in a historical decision log.

### 3. Write the decision log

Create or update a decision page under:
- `internal/decisions/YYYY-MM-DD-[topic].md`

Recommended structure:
- Context
- Decision
- Why it changed
- Operational consequence
- What documents / tasks were updated because of it

### 4. Update hot memory

Write concise durable items into Hindsight:
- `dx-global` for company-wide operating truth
- `dx-human-hunter` / `dx-human-kevin` only when the change reflects founder preference, style, or decision pattern

Write one memory item per durable fact.

### 5. Update execution layer if needed

If the change affects active work:
- update OKR items
- re-map execution tasks
- close/archive stale tasks
- create new tasks for newly introduced operating work

### 6. Confirm the closure

When done, Iris should be able to answer:
- Where is the **history** of this decision?
- Where is the **current active truth** now stored?
- Which **tasks** changed because of it?
- Which **memory bank** will help future sessions recall it?

If any one of these is missing, the operating change was not fully captured.

---

## Quality Bar

Before returning output:
- Is the change clearly **confirmed**, not just discussed?
- Did I separate **historical log** from **current active state**?
- Did I update the system that will actually shape future behavior (GBrain / Hindsight / tasks), not just describe it?
- If execution changed, are task / OKR updates traceable to the decision?
- Did I avoid writing temporary progress as durable operating truth?

If any check fails, the capture is incomplete.

---

## Fallback Behavior

- If GBrain MCP write fails: write via CLI fallback or update the local vault file directly, then sync later.
- If Hindsight is unavailable: write the decision log and current-state doc first, then note the missing hot-memory sync explicitly.
- If the task system is unavailable: complete the decision + state capture first, then record that execution mapping remains outstanding.
- If the correct canonical current-state document is unclear: update the decision log, note the ambiguity, and do not silently invent a home for the truth.

Do not block the whole capture just because one layer failed.

---

## Pitfalls

- Logging the decision but not updating the current-state doc
- Updating a task board without preserving the reasoning anywhere
- Writing speculative discussion as confirmed operating truth
- Storing a founder preference only in GBrain without also updating Hindsight
- Leaving stale goals / tasks alive after the structural change has already made them obsolete
- Treating archival pages as active context
