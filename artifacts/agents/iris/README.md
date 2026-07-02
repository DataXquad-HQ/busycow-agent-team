# Iris Agent Package

This is the packaged Iris artifact set.

## What is included
- `SOUL.md`
- `SETUP.md`
- `skills/`
- `workspace/`

## What Iris currently covers
- operations, team, and task coordination
- infrastructure and context health checks
- context, memory, and knowledge management
- packaged workspace harness for runbooks, schemas, examples, and validation scripts

## Expected recurring workflows
These are the routines the installer should wire after setup:
- GBrain Dream + Memory Sync
- Nightly knowledge-base sync
- Daily Session → Hindsight Ingest
- Daily Context Health Check
- Weekly Memory & Governance Review

## Existing-install rule
If Iris already exists in the target workspace, do not rebuild the profile or workspace by default.
Instead, align the live Iris operating contract to the contextual-layer model using:
- `playbooks/agents/align-existing-iris-contextual-layer.md`
- `artifacts/infrastructure/contextual-layer/existing-install-alignment-checklist.md`

## Install rule
Use `SETUP.md` first.
Then use `workspace/README.md` for the packaged operating harness.

## Optional legacy/source-specific skills
The packaged Iris skill set may still contain source-specific or migration-era skills.
Do not wire them by default unless the target org actively uses that source or workflow.
