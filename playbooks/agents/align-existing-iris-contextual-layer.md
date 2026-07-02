# Align an Existing Iris to the Contextual Layer

## Goal
Bring an already-installed Iris runtime into parity with the package's contextual-layer model without rebuilding the profile or workspace from scratch.

## Use this playbook when
- the target org already has an Iris profile
- the target org already has a knowledge base / GBrain source installed
- the gap is not "install Iris", but "make Iris use the same contextual-layer operating model"

## Required artifacts
- `artifacts/infrastructure/contextual-layer/README.md`
- `artifacts/infrastructure/contextual-layer/runtime-architecture.md`
- `artifacts/infrastructure/contextual-layer/source-of-truth-matrix.md`
- `artifacts/infrastructure/contextual-layer/hindsight-bank-plan.md`
- `artifacts/infrastructure/contextual-layer/gbrain-source-layout.md`
- `artifacts/infrastructure/contextual-layer/existing-install-alignment-checklist.md`
- `artifacts/agents/iris/README.md`

## Steps
1. Confirm the live Iris already exists and can load its current `SOUL.md`, skills, and workspace harness.
2. Read `artifacts/infrastructure/contextual-layer/runtime-architecture.md` and `source-of-truth-matrix.md`.
3. Update the live Iris operating contract so it explicitly knows:
   - chat is coordination, not truth
   - GBrain is durable / canonical knowledge
   - Hindsight is episodic / hot memory
   - the execution system owns task truth
   - review is required before low-authority context becomes canonical policy
4. Compare the live workspace docs against `artifacts/infrastructure/contextual-layer/existing-install-alignment-checklist.md` and patch only the missing rules.
5. Confirm the required Hindsight banks exist and follow the naming pattern in `hindsight-bank-plan.md`.
6. Confirm the live GBrain source layout matches the structure in `gbrain-source-layout.md`.
7. Confirm the live recurring routines match the minimum Iris contextual-layer set:
   - GBrain maintenance / sync
   - context health check
   - session → Hindsight ingest
   - weekly memory / governance review
8. Run the acceptance questions in the checklist and stop if Iris answers them incorrectly.

## Stop conditions
Stop and report if:
- the live Iris profile cannot be located
- the knowledge base source is unknown
- Hindsight is unavailable and no temporary substitute is approved
- the execution system is undefined, causing chat or memory to be used as task truth

## Verify
- Iris can explain the contextual split correctly
- required Hindsight banks exist
- GBrain source layout is known and routable
- minimum recurring routines are present
- acceptance questions pass before specialist agents are built