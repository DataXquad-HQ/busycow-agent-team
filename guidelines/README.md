# Hermes AI Colleague Package Guidelines

This folder contains the human-readable design specifications for the Hermes AI colleague package.

Guidelines explain the architecture, operating model, and deployment philosophy. They are for humans who need to understand what this package installs and why it is structured this way.

If Default Hermes needs to perform setup or migration work, use `../playbooks/`.
If a file should be copied or adapted into a live runtime, use `../artifacts/`.

---

## Reading Order

| File | What it covers |
|---|---|
| `00-package-model.md` | What this package is, the three rollout phases, and the repository contract |
| `01-infrastructure-spec.md` | Core runtime architecture after a base Hermes install exists |
| `02-knowledge-and-memory-spec.md` | Context Layer rules for GBrain, Hindsight, structured state, and workspace context |
| `03-gbrain-and-hindsight-spec.md` | Deeper GBrain and Hindsight model; should be updated to match the current Context Layer policy before being treated as canonical |
| `04-agent-spec-template.md` | Human-facing template for designing a new AI colleague |
| `05-mandatory-skills.md` | Cross-agent skill requirements and installation expectations |

---

## Design Stack

Every AI colleague should be designed through seven layers:

1. Identity Layer
2. Context Layer
3. Capability Layer
4. Authority Layer
5. Autonomy Layer
6. Evaluation Layer
7. Governance Layer

Do not start by writing a long prompt. Start by defining the colleague's role, context, authority, evaluation, and runtime artifacts.

---

## Context Layer Default

The default context architecture is:

1. GBrain canonical knowledge
2. GBrain evidence and source material
3. Hindsight personal and shared/domain memory
4. Structured operational state
5. Agent workspace context

These are complementary layers, not substitutes.

---

## Reference Docs

| File | What it covers |
|---|---|
| `reference/architecture-overview.md` | Overall system and agent-team architecture |
| `reference/agent-capability-doc-standard.md` | Standard for agent capability documentation |
| `reference/shared-skill-model.md` | Shared canonical skills, selective installs, and agent-local skill governance |
| `reference/repo-structure-migration-map.md` | Old-path to new-path migration map for the package |

---

## Deployed Agents

The `deployed-agents/` folder contains design specs for agents that have been built or prepared for deployment.

These are human-readable role and operating specs. Runtime assets should live under `../artifacts/agents/`.

---

## Relationship to Other Layers

| Layer | Purpose |
|---|---|
| `guidelines/` | why the system is designed this way |
| `playbooks/` | how Default Hermes performs setup, migration, and verification |
| `artifacts/` | the actual files that get installed or copied |

Keep rationale, instructions, and runtime assets separate so another team can both understand the package and let Hermes execute it safely.