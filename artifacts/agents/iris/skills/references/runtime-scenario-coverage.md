# Iris Runtime Scenario Coverage

## Purpose

This file tracks whether Iris is merely specified, or is actually proven in runtime for the work she personally needs to handle now.

Current scope:
- focus on Iris herself
- do not assume she needs to manage other agents' behavior in this phase
- financial analysis excluded for now

---

## Scenario Matrix

| Scenario | Expected Iris behavior | Current status | Notes |
|---|---|---|---|
| Founder changes operating rule | capture decision, update active state, update Hindsight, update task layer if needed | partial | `capturing-operating-changes` exists; needs repeated real use |
| Rebuild OKR from current company state | read company docs, rewrite objectives/KRs, re-map tasks | proven | done with real DataXquad data |
| Stale initiative cleanup | distinguish archive vs active, close/hide stale state | proven | done with real Lark task data |
| Daily ops briefing | summarize task + cron + context health | partly proven | cron exists and runs; output quality still needs repeated review |
| Weekly operating review | identify blockers, ownership gaps, objective drift | not fully proven | workflow is possible but not yet repeated enough |
| Knowledge system health check | verify GBrain / Hindsight / cron / disk / sync health | proven | executed with real runtime tools |
| Founder preference capture | ensure style / preference goes into hot memory correctly | partly proven | session-ingest pipeline works, but deliberate capture workflow still needs repetition |
| Package publication | update artifacts, commit, push package repo cleanly | partly proven | package workflow exists; Iris artifact completion is being built now |
| Infra incident triage | surface problem, classify urgency, preserve log, route for action | partly proven | health inspection exists; escalation handling still needs more runtime reps |

---

## What “good enough” looks like

Iris should be considered operationally credible for the current phase when she can repeatedly do all of the following:

1. convert founder decisions into durable state changes
2. keep current-state docs and decision-history docs distinct
3. maintain a live task / OKR layer that matches company reality
4. detect stale operational structure and archive it cleanly
5. notice context / infra degradation before founders have to ask
6. package her own operating layer into reproducible artifacts

Until then, the agent is useful but not fully matured.
