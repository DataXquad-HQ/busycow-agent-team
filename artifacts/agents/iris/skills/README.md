# Skills — Iris

## Purpose

This folder contains the **Iris runtime skill layer** for [Org] use.

The goal is simple:
- Iris should not rely only on the shared Hermes skill registry
- the package should explicitly carry the skills Iris is expected to use
- the package should make it obvious which parts of the Iris spec are already backed by real skill artifacts

---

## Package-local Iris skills currently present

### Iris-specific governance skills
| Skill | Purpose |
|---|---|
| `capturing-operating-changes` | capture structural / operating decisions across GBrain, Hindsight, and the task layer |
| `openmail` | read Leo's inbox for outreach / pipeline monitoring when Iris needs visibility |

### Packaged capability skills copied into Iris
These are included here so Iris is package-complete for [Org] use, even when they also exist in the shared Hermes skill layer.

#### C1 — Operations, Team & Agent Management
- `managing-tasks`
- `reviewing-tasks`
- `planning-next-actions`
- `generating-task-briefing`
- `generating-daily-ops-briefing`

#### C2 — Infrastructure Management
- `checking-context-health`
- `managing-cron-jobs`
- `packaging-to-github`
- `managing-skills`

#### C3 — Context, Memory & Knowledge Management
- `extracting-lark-to-gbrain`
- `ingesting-sessions-to-hindsight`
- `capturing-to-gbrain`
- `maintaining-gbrain`
- `syncing-brain-memory`
- `managing-team-knowledge`

---

## Tool dependencies that are NOT package-local skills
These are still part of Iris's operating surface, but they are tool / integration dependencies rather than Iris-local skill folders in this package.

- `lark-im`
- `lark-base`

---

## Coverage against iris-spec.md

| Spec area | Status |
|---|---|
| C1 capability skills | packaged |
| C2 capability skills | packaged |
| C3 capability skills | packaged |
| C4 Financial Analysis | intentionally not built yet |
| Iris-specific structural decision capture | packaged |
| Scenario coverage doc | packaged in `references/runtime-scenario-coverage.md` |

---

## What this means practically

Iris is no longer just:
- a SOUL.md
- plus a reference spec
- plus an assumption that shared skills exist somewhere else

Iris now has an explicit package skill layer that covers the active non-financial scope in the spec.

---

## Notes

- These skills are packaged for **[Org] use first**.
- Some skills are shared/generic in origin, but are copied here so Iris is self-contained in the package.
- `runtime-scenario-coverage.md` tracks which workflows are already proven in real runtime versus only specified.
