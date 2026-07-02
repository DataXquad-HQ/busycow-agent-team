# Contextual Layer

This folder is the dedicated package reference for the **contextual layer**.

Use it when you need the full picture for:
- how context is split into different truth classes
- how agents use personal memory vs shared memory vs canonical knowledge
- how the router decides where a read or write should go
- how to set up the contextual layer before activating agents

## What this folder is

This is a **cross-cutting reference pack**.
It does **not** replace the package structure:
- `playbooks/` still holds the executable setup flow
- `artifacts/` still holds the installable templates and conventions
- `guidelines/` still stays minimal

This folder exists so a human or installer agent can find the contextual-layer design in one place.

## Read in this order

1. `01-context-types.md`
2. `02-memory-sharing-model.md`
3. `03-router-model.md`
4. `04-setup-sequence.md`

## Canonical implementation links

### Playbooks
- `../playbooks/infrastructure/02-setup-contextual-layer.md`
- `../playbooks/agents/align-existing-iris-contextual-layer.md`

### Artifacts
- `../artifacts/infrastructure/contextual-layer/runtime-architecture.md`
- `../artifacts/infrastructure/contextual-layer/router-and-governance.md`
- `../artifacts/infrastructure/contextual-layer/gbrain-source-layout.md`
- `../artifacts/infrastructure/contextual-layer/hindsight-bank-plan.md`
- `../artifacts/infrastructure/contextual-layer/source-of-truth-matrix.md`
- `../artifacts/infrastructure/contextual-layer/existing-install-alignment-checklist.md`

## Outcome

Before any agent goes live, the installer should be able to answer:
- what kind of context belongs in which layer
- which memory is private vs shared
- what must go through review before promotion
- how to verify the contextual layer is working
