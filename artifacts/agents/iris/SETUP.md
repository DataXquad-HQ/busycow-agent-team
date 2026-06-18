# SETUP — Iris

## What this installs

This setup installs the DataXquad-use Iris artifact layer:
- `SOUL.md`
- the Iris skill layer under `artifacts/agents/iris/skills/`
- the reference scenario coverage document
- the cron expectations documented in the Iris spec

---

## Steps

### 1. Copy SOUL.md
Copy:
- `artifacts/agents/iris/SOUL.md`

to the active Iris profile / runtime location.

### 2. Copy the Iris skills directory
Copy the full directory:
- `artifacts/agents/iris/skills/`

This includes:
- Iris-specific governance skills
- packaged copies of the shared skills Iris depends on for C1 / C2 / C3

### 3. Verify the key Iris-local skills exist
Required minimum package-local checks:
- `capturing-operating-changes/SKILL.md`
- `openmail/SKILL.md`
- `managing-tasks/SKILL.md`
- `checking-context-health/SKILL.md`
- `capturing-to-gbrain/SKILL.md`

### 4. Review cron expectations
Cron definitions are not stored as directly importable jobs here.
Use `guidelines/deployed-agents/iris-spec.md` as the source of truth for which jobs Iris should run.

At minimum, confirm the runtime has these workflows:
- Daily Lark → GBrain Extraction
- GBrain Dream + Memory Sync
- dx-gbrain Nightly Sync
- Daily Session → Hindsight Ingest
- Daily Context Health Check
- Daily Ops Briefing

### 5. Read the scenario coverage file
Open:
- `artifacts/agents/iris/skills/references/runtime-scenario-coverage.md`

This tells you which workflows are already proven vs only specified.

---

## Verify

Iris is considered installed at the artifact layer when:
1. `SOUL.md` is present
2. the packaged skill folders exist in the Iris runtime
3. the Iris package skill README matches the actual folders present
4. the runtime can load at least one C1, one C2, and one C3 skill successfully

---

## Current scope note

This package currently targets:
- Iris handling her own Chief-of-Staff operating workflows
- non-financial scope only
- no requirement yet to manage other agents' behavior directly
