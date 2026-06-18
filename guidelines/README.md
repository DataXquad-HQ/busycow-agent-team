# BusyCow Agent Framework — Guidelines

This folder contains the **human-readable design specifications** for the BusyCow agent framework.
These documents explain the architecture, operating model, and deployment philosophy.

## This layer is for humans

Guidelines answer:
- What is this system?
- Why is it structured this way?
- What does each agent own?
- How should a deployment be reasoned about?

If you need the agent to actually perform setup or migration work, go to `../playbooks/`.
If you need the concrete files that get installed, go to `../artifacts/`.

---

## Reading Order

| File | What it covers |
|---|---|
| `01-infrastructure-spec.md` | Infrastructure requirements — servers, tools, credentials needed before go-live |
| `02-knowledge-and-memory-spec.md` | How information flows through the system — knowledge base, GBrain, Hindsight |
| `03-gbrain-and-hindsight-spec.md` | GBrain entity types, relationship types, Hindsight bank design |
| `04-agent-spec-template.md` | Template for designing a new agent |
| `05-mandatory-skills.md` | Cross-agent skill requirements |

## Reference Docs

| File | What it covers |
|---|---|
| `reference/architecture-overview.md` | Overall system and agent-team architecture |
| `reference/agent-capability-doc-standard.md` | Standard for agent capability documentation |
| `reference/repo-structure-migration-map.md` | Old-path → new-path migration map for the package |

---

## Deployed Agents

The [`deployed-agents/`](deployed-agents/) folder contains the design specs for agents that have been built and deployed.
These are human-readable hiring briefs and operating specs — not runtime artifacts.

---

## Relationship to Other Layers

- `guidelines/` = why the system is designed this way
- `playbooks/` = how an agent performs setup / migration / verification
- `artifacts/` = the actual files that get installed or copied
