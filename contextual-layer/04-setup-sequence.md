# Contextual Layer Setup Sequence

Use this to set up the contextual layer before activating agents.

## Outcome

At the end of setup, the target org should have:
- a defined source-of-truth split
- a GBrain repo layout
- a Hindsight bank plan
- a router/governance model
- verification questions that prove the layer is understood

## Step 1 — Define the truth split

Complete the source-of-truth mapping for:
- current operational state
- canonical knowledge
- evidence
- episodic memory
- draft workspace context
- chat coordination

Use:
- `../artifacts/infrastructure/contextual-layer/source-of-truth-matrix.md`

## Step 2 — Set up GBrain structure

Create or confirm the knowledge-base repo shape:

```text
[org]-gbrain/
├── core/
├── evidence/
└── review/
```

Minimum areas to define:
- `core/company/`
- `core/strategy/`
- `core/agents/`
- `core/decisions/`
- `evidence/customers/`
- `evidence/partners/`
- `review/`

Use:
- `../artifacts/infrastructure/contextual-layer/gbrain-source-layout.md`

## Step 3 — Set up Hindsight banks

Minimum recommended banks:
- `[org]-global`
- `[org]-internal`
- `[org]-agent-iris`
- `[org]-agent-<specialist>` as needed
- `[org]-human-<founder>` as needed

Add domain banks only when there is a clear use case.

Use:
- `../artifacts/infrastructure/contextual-layer/hindsight-bank-plan.md`

## Step 4 — Define memory-sharing rules

Document:
- which banks are private
- which banks are shared
- who can write to shared banks
- which items must go to evidence or canonical instead of memory

Use:
- `02-memory-sharing-model.md`

## Step 5 — Define router and review behavior

Document:
- read order
- write destinations
- review-required cases
- approval owner
- logging path for promotions and publish actions

Use:
- `03-router-model.md`
- `../artifacts/infrastructure/contextual-layer/router-and-governance.md`

## Step 6 — Align Iris first

Before installing specialist agents, make sure Iris can correctly explain:
1. where founder decisions go
2. where soft conversational nuance goes
3. where task owner / deadline / status goes
4. whether chat is a coordination layer or a truth layer
5. what must go through review before becoming canonical

Use:
- `../artifacts/infrastructure/contextual-layer/existing-install-alignment-checklist.md`
- `../playbooks/agents/align-existing-iris-contextual-layer.md`

## Step 7 — Wire recurring routines

Minimum routines:
- GBrain maintenance / sync
- context health check
- session → Hindsight ingest
- weekly memory / governance review

Do not copy every possible routine on day one.
Only wire the minimum routines needed to keep context healthy.

## Verification checklist

The contextual layer is ready only when all are true:
- the org can name the system of record for live state
- the org can distinguish evidence from canonical knowledge
- the org can distinguish personal memory from shared memory
- the org has a review path for policy promotion
- Iris answers the acceptance questions correctly
- the installer can point to the repo locations for setup, router, and memory rules
