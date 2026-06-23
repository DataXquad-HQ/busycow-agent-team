# Hermes AI Colleague System Package

This repository is a reusable package for showing, installing, and extending a Hermes-native AI colleague system.

It has two jobs:

1. **Human demo and architecture guide**: help people understand what the system contains, how the architecture works, and which AI colleagues are designed or packaged.
2. **Default Hermes install package**: give a base Hermes agent enough structured playbooks and artifacts to install the core infrastructure and selected AI colleagues in a target environment.

This package is not a prompt library. It is an operating package for AI colleagues: role-owning Hermes profiles with context, workspace, tools, authority, routines, evaluation, and governance.

---

## System Architecture

The package is organized around four infrastructure layers.

| Layer | Purpose | Current V1 focus |
|---|---|---|
| **Contextual Layer** | What agents know, remember, retrieve, and treat as truth | GBrain canonical, GBrain evidence, Hindsight, structured systems |
| **AI Colleague Agent Layer** | The role-owning AI colleagues themselves | one Hermes profile per durable colleague |
| **Workspace & Collaboration Layer** | Where humans and agents interact and where working context lives | Lark/Feishu first; Slack can be added later |
| **Operations & Governance Layer** | How installs, routines, approvals, logs, evaluation, and audit work | playbooks, authority files, logs, approval rules |

These layers should stay separate. GBrain is not the workspace. Hindsight is not the source of operational truth. Lark is not the runtime. Hermes profiles are not the whole knowledge base.

---

## Adoption Flow

A target team normally adopts this package in three phases.

```text
Phase 0: Human bootstrap
  - create VM or host
  - install base Hermes
  - provide repository access and required credentials

Phase 1: Core infrastructure install
  - configure Contextual Layer assumptions
  - configure workspace and collaboration layer
  - configure governance, logging, approvals, and tool policies

Phase 2: AI colleague install
  - create one Hermes profile per role-owning colleague
  - install profile, workspace, skills, memory policy, routines, and evaluation policy
  - verify context routing, authority, and activation criteria
```

The intended execution path is:

```text
Human creates VM and installs base Hermes
Default Hermes reads this repo
Default Hermes follows SETUP.md
Default Hermes installs core infrastructure first
Default Hermes installs selected AI colleagues from artifacts/
```

---

## Repository Layers

```text
hermes-ai-colleague-package/
├── guidelines/   # human-readable architecture, design docs, and catalog
├── playbooks/    # agent-readable install, migration, and verification runbooks
├── artifacts/    # installable runtime assets and templates
├── README.md
└── SETUP.md      # entrypoint for humans and Default Hermes
```

| Folder | Audience | Purpose |
|---|---|---|
| `guidelines/` | Humans | Explain the system architecture, design model, and AI colleague catalog |
| `playbooks/` | Default Hermes / installers | Tell an agent what to do, in what order, and when to stop |
| `artifacts/` | Installers and runtime builders | Provide files that can be copied or adapted into live systems |

---

## Human Reading Path

Start here if you are evaluating the package or learning the architecture:

1. `guidelines/README.md`
2. `guidelines/00-system-architecture.md`
3. `guidelines/01-infrastructure-spec.md`
4. `guidelines/02-contextual-layer-spec.md`
5. `guidelines/04-ai-colleague-design-spec-template.md`
6. `guidelines/06-ai-colleague-catalog.md`

---

## Default Hermes Install Path

Start here if base Hermes is already installed and this package should be applied to an environment:

1. `SETUP.md`
2. `playbooks/README.md`
3. `playbooks/bootstrap/install-core-infrastructure.md`
4. `playbooks/bootstrap/install-ai-colleague.md`
5. relevant integration playbooks under `playbooks/integrations/`
6. selected runtime files under `artifacts/`

---

## Core Context Rule

Use the right system for the right kind of context:

| Context type | System of record |
|---|---|
| approved durable knowledge | GBrain canonical |
| evidence and source material | GBrain evidence |
| experiential memory and learned patterns | Hindsight |
| owner, stage, approval, deadline, workflow state | structured operational systems |
| drafts, queues, notes, current working docs | agent workspace |

Do not collapse these into one memory system.

---

## V1 Workspace Position

This version is **Lark/Feishu-first** for the Workspace & Collaboration Layer.

Slack is a valid future collaboration surface, but this package should not claim Slack support until Slack artifacts, playbooks, credentials, and verification steps exist.

---

## Core Rule

Human reads `guidelines/`. Default Hermes runs `playbooks/`. Live systems install `artifacts/`.

A usable package must work both as a demo for humans and as a real installation package for an already-running base Hermes environment.