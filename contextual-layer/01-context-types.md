# Context Types

This document defines the context classes used by the AI colleague system.

## Core rule

Do not collapse all context into one store.
Different context types have different authority, lifetime, and sharing rules.

## Context taxonomy

| Context type | What it is | Default system | Authority | Typical examples |
|---|---|---|---|---|
| Chat coordination | conversational coordination and temporary discussion | chat / IM | low | "please handle this next", quick clarifications, routing messages |
| Structured operational state | the live current state of work | CRM, task system, calendar, approval system, other system of record | highest for current status | owner, stage, deadline, approval state, task status |
| Canonical knowledge | approved durable truth that should stay true across sessions | GBrain `core/` | high | company rules, operating model, approved strategy, ratified decisions |
| Evidence | durable source trail for what happened | GBrain `evidence/` | medium | meeting notes, customer evidence, partner evidence, incident trail |
| Review candidates | staged items not yet approved as canonical | GBrain `review/` or review queue | pending | policy candidates, promoted patterns, unresolved conflicts |
| Episodic memory | recent and role-scoped working memory | Hindsight personal or shared banks | soft | recent conversations, soft nuance, operating patterns, role memory |
| Workspace context | draft and working material | workspace files / local harness | temporary | drafts, runbooks, scratch analysis, validation outputs |
| Inference | model interpretation not yet grounded in a source | nowhere by default | lowest | guessed intent, unverified synthesis |

## Non-negotiable rules

1. **Chat is not durable truth.**
   - Chat can trigger work.
   - Chat does not become canonical by itself.

2. **Current state lives in structured systems.**
   - If the question is "what is true right now?", read the system of record first.
   - Memory and notes may explain the state, but should not override it.

3. **Canonical knowledge must be approved.**
   - Durable policy or org truth belongs in GBrain `core/`.
   - Promotion into canonical should be governed.

4. **Evidence explains what happened.**
   - Evidence is not automatically policy.
   - It is the durable source trail behind later decisions.

5. **Memory is contextual, not authoritative.**
   - Hindsight helps continuity.
   - It should not own live status or official policy.

6. **Workspace is for active work, not truth publication.**
   - Drafts and harness files can guide work.
   - They should not silently become canonical.

## Retrieval order

When the agent needs truth, use this priority:
1. explicit human instruction
2. structured current-state system
3. canonical knowledge
4. approved decision record
5. workspace operating docs
6. episodic memory
7. inference

## Quick routing examples

| Question or event | First destination |
|---|---|
| "Who owns this task now?" | structured operational state |
| "What decision did the founder approve?" | GBrain canonical or decision record |
| "What happened in yesterday's customer call?" | GBrain evidence |
| "What soft nuance should Leo remember about this lead?" | Hindsight personal or shared bank |
| "What draft operating note are we still testing?" | workspace |
| "This looks like a new permanent rule" | review queue first, then canonical if approved |
