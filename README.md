# Hermes AI Colleague Package

A reusable package for installing a Hermes-native AI colleague operating system into another team's environment.

This repository is meant to be read by two audiences:

- **Humans** who need to understand the architecture, operating model, and rollout assumptions.
- **Default Hermes** running inside the target environment after a base VM and base Hermes install already exist.

The package is not a single prompt, not only a knowledge base, and not only a collection of skills. It is an installable operating architecture for AI colleagues: role-owning Hermes profiles with context, capabilities, authority, autonomy, evaluation, and governance.

---

## Rollout Model

A target team usually adopts this package in three phases.

```text
Phase 0: Human bootstrap
  - create VM or host
  - install base Hermes
  - provide repository access and required credentials

Phase 1: Core AI colleague infrastructure
  - configure Hermes runtime defaults
  - configure GBrain, Hindsight, structured systems, workspace roots
  - configure tool policies, logging, audit, and approval gateway assumptions

Phase 2: AI colleague installation
  - create one Hermes profile per role-owning colleague
  - install SOUL.md, AGENTS.md, workspace docs, skills, cron templates, and memory policy
  - verify context routing, authority rules, evaluation, and safe tool access
```

The intended bootstrap flow is:

```text
Human creates VM and installs base Hermes
Default Hermes reads this repo
Default Hermes follows SETUP.md
Default Hermes installs core stack first
Default Hermes installs selected AI colleagues from artifacts/
```

---

## Repository Layers

```text
busycow-agent-package/
├── guidelines/   # human-readable architecture and design specs
├── playbooks/    # agent-readable operational runbooks
├── artifacts/    # installable or copyable runtime assets
├── README.md
└── SETUP.md      # entrypoint for humans and Default Hermes
```

### `guidelines/`

Human-readable specifications. Use this layer to understand why the system is designed this way and how to reason about new AI colleagues.

### `playbooks/`

Agent-readable runbooks. Use this layer when an already-running Hermes agent needs to install, upgrade, verify, or repair the system.

### `artifacts/`

Concrete runtime assets. Use this layer for files that get copied, adapted, or installed into live Hermes profiles, agent workspaces, GBrain sources, Hindsight configuration, structured systems, or deployment directories.

---

## Reading Paths

### Human evaluator or operator

1. `guidelines/README.md`
2. `guidelines/00-package-model.md`
3. `guidelines/01-infrastructure-spec.md`
4. `guidelines/02-knowledge-and-memory-spec.md`
5. `guidelines/04-agent-spec-template.md`

### Default Hermes performing setup

1. `SETUP.md`
2. `playbooks/README.md`
3. `playbooks/bootstrap/install-core-stack.md`
4. `playbooks/bootstrap/install-agent-package.md`
5. relevant integration playbooks under `playbooks/integrations/`
6. selected runtime assets under `artifacts/`

---

## Core Architecture

Every AI colleague should be designed through seven layers:

1. Identity Layer
2. Context Layer
3. Capability Layer
4. Authority Layer
5. Autonomy Layer
6. Evaluation Layer
7. Governance Layer

The Context Layer is deliberately split into five responsibilities:

| Layer | Purpose |
|---|---|
| GBrain canonical | approved, durable, reviewable company truth |
| GBrain evidence | traceable source material and evidence pages |
| Hindsight | experiential memory, corrections, recent signals, learned patterns |
| Structured operational state | CRM, Plane, approvals, workflow state, logs, evaluations |
| Agent workspace | role-local operating docs, drafts, queues, notes, and current work |

Do not collapse these into one memory system.

---

## Current Stack Assumptions

| System | Role |
|---|---|
| Hermes Agent | runtime container for each AI colleague profile |
| GBrain | canonical knowledge and evidence-backed company brain |
| Hindsight | hot semantic memory for personal and shared/domain experience |
| Structured systems | source of truth for operational state and approval state |
| Lark / Feishu | workspace communication and human-facing delivery |
| GitHub | package distribution and versioned design/build artifacts |

---

## Core Rule

Human reads `guidelines/`, Default Hermes runs `playbooks/`, live systems install `artifacts/`.

A good package should let another team start with a base Hermes install, then progressively install the shared infrastructure and each role-owning AI colleague without guessing the architecture.