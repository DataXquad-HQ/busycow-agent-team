# Router Model

This document explains how the contextual router should decide where reads and writes go.

## Purpose

The router exists to stop agents from guessing where context should live.
It should make routing deterministic enough that:
- current-state truth stays in systems of record
- memory stays useful but bounded
- canonical knowledge changes are governed
- evidence trails are preserved

## Two router jobs

1. **Read routing** — where should the agent look first?
2. **Write routing** — where should new information be stored?

## Read-routing model

### Default order
1. explicit human instruction
2. structured state / system of record
3. GBrain canonical
4. approved decision record
5. workspace operating docs
6. Hindsight personal or shared memory
7. inference

### Read-routing questions

| User need | First read target | Why |
|---|---|---|
| current owner / stage / deadline | structured system | live state belongs there |
| operating rule / approved decision | GBrain canonical | durable approved truth |
| what happened / why | GBrain evidence | preserves source trail |
| soft relationship nuance | Hindsight | useful soft context, not canonical |
| current draft / work-in-progress | workspace | active working material |

## Write-routing model

### Direct-write destinations
These are usually safe without review when properly sourced:
- workspace drafts
- GBrain evidence
- personal Hindsight bank
- structured systems of record

### Review-first destinations
These should usually go through review or staged promotion first:
- GBrain canonical changes
- source-of-truth policy changes
- cross-agent behavior policy
- shared patterns that look like org-wide rules
- memory items that would affect governance or authority boundaries

## Minimum event fields

A write event should usually capture:
- `event_id`
- `occurred_at`
- `agent_id`
- `summary`
- `source_system`
- `source_ref` when available
- `entities` when relevant
- `volatility`
- `confidence`
- `needs_review` when promotion is possible

## Router decision heuristics

| Signal | Route tendency |
|---|---|
| current status / owner / deadline / stage | structured system |
| what happened in a meeting or conversation | evidence |
| recent working nuance for one role | personal memory |
| repeated soft pattern for multiple agents | shared memory or review |
| durable policy / framework / official process | review then canonical |
| still-being-tested draft | workspace |

## Governance checks before promotion

Before something becomes canonical, ask:
1. Is there a real source?
2. Is this durable beyond the current session?
3. Does it affect more than one agent or one task?
4. Would a wrong write create operating confusion?
5. Does a human approval owner need to sign off?

If the answer is yes to the governance questions, route through review.

## Example routing cases

### Case 1 — founder decides a new operating rule
- capture evidence of the decision
- stage the rule for review if needed
- publish to GBrain canonical once approved

### Case 2 — Leo learns a soft relationship preference
- write to Leo personal bank or a governed shared pipeline bank
- do not treat it as org policy

### Case 3 — task deadline changes
- update the task system
- optionally capture evidence or handoff note
- do not store the deadline only in memory

### Case 4 — repeated pattern suggests a new workflow rule
- capture examples in evidence
- stage a review item
- promote only after governance review

## Failure rule

If the router is unavailable, fall back conservatively:
- current state → structured system
- event trail → evidence
- soft role memory → personal bank
- policy candidate → review queue or draft, not canonical
- uncertain draft → workspace
