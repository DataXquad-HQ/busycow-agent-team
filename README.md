# Hermes AI Colleague Package

This repo is a **Hermes-first installation package** for deploying an AI colleague system into a new environment.

The package is organized around **two setup classes**:

1. **Infrastructure setup**
   - Hermes runtime
   - contextual layer
   - collaboration layer
   - governance and verification
2. **Agent setup**
   - one installable package per agent
   - profile identity, skills, workspace, routines, and verification

## Start Here

### If you are human
Read only these first:
1. `README.md`
2. `guidelines/README.md`
3. `guidelines/agents.md`
4. `contextual-layer/README.md` if you are designing or reviewing the context stack

### If you are the installer agent
Run in this order:
1. `artifacts/infrastructure/hermes/installer-agent-mission.md`
2. `SETUP.md`
3. `contextual-layer/README.md`
4. `playbooks/infrastructure/README.md`
5. `playbooks/infrastructure/01-setup-hermes-runtime.md`
6. `playbooks/infrastructure/02-setup-contextual-layer.md`
7. `playbooks/infrastructure/03-setup-collaboration-and-governance.md`
8. `playbooks/infrastructure/04-verify-infrastructure.md`
9. `playbooks/agents/README.md`
10. `playbooks/agents/install-iris.md` or another agent playbook

## Repo Shape

```text
hermes-ai-colleague-package/
├── guidelines/                 # minimal human-facing orientation
├── contextual-layer/           # dedicated contextual-layer reference pack
├── playbooks/
│   ├── infrastructure/         # agent-readable infrastructure setup
│   ├── agents/                 # agent-readable agent installation flows
│   └── integrations/           # per-system integration details
├── artifacts/
│   ├── infrastructure/         # concrete infrastructure templates / conventions
│   ├── agents/                 # concrete agent packages
│   ├── shared-skills/
│   ├── schemas/
│   └── knowledge-base-templates/
├── README.md
└── SETUP.md
```

## Core Install Principle

- `guidelines/` tells a human **what is in the package**.
- `contextual-layer/` gives a single entrypoint for the context framework, memory model, router, and setup sequence.
- `playbooks/infrastructure/` tells an installer agent **how to build the shared stack**.
- `playbooks/agents/` tells an installer agent **how to install a specific agent**.
- `artifacts/infrastructure/` and `artifacts/agents/` contain **the actual files to copy or adapt**.

## Currently packaged

- shared infrastructure setup
- contextual layer setup
- collaboration and governance setup
- Iris agent package
