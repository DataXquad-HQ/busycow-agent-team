# Existing Iris Alignment Checklist

Use this when Iris already exists in a target workspace and the job is to align its contextual-layer behavior rather than create a fresh profile.

## Minimum operating contract

Iris must explicitly know:
- chat is a coordination layer, not durable truth
- GBrain holds durable and canonical knowledge
- Hindsight holds episodic, role-scoped, and recent memory
- the execution system holds task truth
- review is required before low-authority context becomes canonical policy

## Minimum Hindsight banks

- `[org]-agent-iris`
- `[org]-global`
- `[org]-internal`
- `[org]-human-<founder>`

Add specialist or domain banks only after live usage justifies them.

## Minimum GBrain areas

- `core/company/`
- `core/product/`
- `core/market/`
- `core/sales/`
- `core/decisions/`
- `core/agents/`
- `evidence/customers/`
- `evidence/partners/`
- `evidence/product/`

## Minimum recurring routines

- GBrain maintenance / sync
- context health check
- session → Hindsight ingest
- weekly memory / governance review

Do not copy optional org-specific routines until the target org actually needs them.

## Acceptance questions

Iris should answer all 5 correctly before specialist agents are built:

1. Where does a founder decision go?
2. Where does soft conversational nuance go?
3. Where does task owner / deadline / status go?
4. Is chat a coordination layer or a truth layer?
5. What must go through review before becoming canonical?

## Go / no-go rule

- **Go** when Iris answers all 5 correctly and the minimum routines are present.
- **No-go** when Iris confuses chat, memory, task truth, or canonical knowledge.