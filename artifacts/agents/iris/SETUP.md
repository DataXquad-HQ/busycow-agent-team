# SETUP — Iris

## Overview

| Step | Type | What it installs or configures |
|---|---|---|
| 1 | artifact copy | `SOUL.md` |
| 2 | artifact copy | `skills/` |
| 3 | artifact copy | `workspace/` harness |
| 4 | verification | confirm key skills and workspace files exist |
| 5 | runtime review | confirm contextual-layer routine expectations from the Iris spec |

## Existing install shortcut

If the target org already has a live Iris profile, workspace, and GBrain source, do not repeat the full copy flow by default.
Use:
- `playbooks/agents/align-existing-iris-contextual-layer.md`
- `artifacts/infrastructure/contextual-layer/existing-install-alignment-checklist.md`

The shortcut path is for bringing a live Iris into contextual-layer parity rather than reinstalling the agent package.

## Step 1 — Copy `SOUL.md`

Copy:
- `artifacts/agents/iris/SOUL.md`

into the active Iris runtime profile.

## Step 2 — Copy the Iris skills layer

Copy the full directory:
- `artifacts/agents/iris/skills/`

This package carries both:
- Iris-specific governance skills
- packaged copies of the shared skills Iris depends on for current non-financial scope

## Step 3 — Copy the workspace harness

Copy the full directory:
- `artifacts/agents/iris/workspace/`

Target install path:
- `{{HERMES_INSTALL_ROOT}}/workspaces/iris/`

This workspace contains:
- operating instructions
- runbooks
- examples
- templates
- schemas
- evaluators
- lightweight validation and bridge scripts

## Step 4 — Verify key files exist

Required minimum checks:
- `artifacts/agents/iris/skills/checking-context-health/SKILL.md`
- `artifacts/agents/iris/skills/capturing-to-gbrain/SKILL.md`
- `artifacts/agents/iris/workspace/AGENTS.md`
- `artifacts/agents/iris/workspace/runbooks/first-real-operating-loop.md`
- `artifacts/agents/iris/workspace/scripts/validate_runtime_output.py`

## Step 5 — Review packaged operating expectations

Open:
- `artifacts/agents/iris/README.md`

Cron definitions are not stored as directly importable jobs here.
Use the Iris package README and the workspace harness as the source of truth for which routines Iris should run.

At minimum, confirm the runtime has these workflows:
- GBrain Dream + Memory Sync
- `{{GBRAIN_SOURCE_ID}}` Nightly Sync
- Daily Session → Hindsight Ingest
- Daily Context Health Check
- Weekly Memory & Governance Review

## Placeholder reference

| Placeholder | Meaning |
|---|---|
| `{{HERMES_INSTALL_ROOT}}` | Hermes install root on the target machine |
| `{{GBRAIN_REPO_ROOT}}` | checked-out knowledge-base repository path |
| `{{GBRAIN_SOURCE_ID}}` | source ID used by the local GBrain runtime |
| `{{LARK_USER_OPEN_ID}}` | user open ID for Lark task examples |

## Verify everything

Iris is considered installed at the artifact layer when:
1. `SOUL.md` is present in the target profile
2. the packaged skill folders exist in the Iris runtime
3. the packaged workspace directory has been copied into the target workspace path
4. the Iris skill README matches the actual folders present
5. the runtime can load at least one C1, one C2, and one C3 skill successfully

## Next step after setup

Open `artifacts/agents/iris/workspace/README.md`, then run the packaged validation examples and wire the routines listed in `artifacts/agents/iris/README.md`.
