# Setup Contextual Layer

## Goal
Install the shared context system that agents will read from and write to.

## Design pack
Read this first if the installer needs the full framework in one place:
- `../../contextual-layer/README.md`
- `../../contextual-layer/01-context-types.md`
- `../../contextual-layer/02-memory-sharing-model.md`
- `../../contextual-layer/03-router-model.md`
- `../../contextual-layer/04-setup-sequence.md`

## Required artifacts
- `artifacts/infrastructure/contextual-layer/README.md`
- `artifacts/infrastructure/contextual-layer/runtime-architecture.md`
- `artifacts/infrastructure/contextual-layer/router-and-governance.md`
- `artifacts/infrastructure/contextual-layer/gbrain-source-layout.md`
- `artifacts/infrastructure/contextual-layer/hindsight-bank-plan.md`
- `artifacts/infrastructure/contextual-layer/source-of-truth-matrix.md`

## Steps
1. Set up or confirm the knowledge base / GBrain source repo.
2. Set up or confirm the Hindsight service and the required bank naming convention.
3. Record which system owns each truth class using `source-of-truth-matrix.md`.
4. Confirm the installer understands the split:
   - canonical knowledge
   - evidence
   - episodic memory
   - structured operational state
   - workspace drafts
5. If GBrain or Hindsight integrations require additional steps, continue into:
   - `playbooks/integrations/gbrain/README.md`
   - `playbooks/integrations/hindsight/README.md`

## Stop conditions
Stop and report if:
- no knowledge-base repo path is available
- no Hindsight endpoint is available and no substitute is approved
- current-state ownership is unclear between CRM, task system, and memory

## Verify
- the target org has a named knowledge-base repo location
- the target org has a Hindsight endpoint or an accepted temporary gap
- the source-of-truth split is documented before any agent install starts
