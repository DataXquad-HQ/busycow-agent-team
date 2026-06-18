# BusyCow Agent Package

A reusable package for deploying a production-grade AI agent operating system inside a company.

This repo is designed for **two audiences**:
- **Humans** who need to understand the architecture and deployment model
- **Agents** that will execute setup, rollout, migration, and verification work after a base Hermes install already exists

---

## Repository Model

This repo now has **three core layers**:

```text
busycow-agent-package/
├── guidelines/   ← human-readable specs
├── playbooks/    ← agent-readable operational instructions
├── artifacts/    ← actual installable / copyable assets
├── README.md
└── SETUP.md      ← entrypoint that routes you into playbooks/
```

### 1. `guidelines/`
Human-readable specifications.
Use this layer to understand **why** the system is designed this way.

### 2. `playbooks/`
Agent-readable runbooks.
Use this layer to tell an already-running Hermes agent **how** to install, upgrade, verify, or repair the system.

### 3. `artifacts/`
Concrete deployable files.
Use this layer for the actual SOULs, skills, cron templates, schemas, and knowledge-base templates that get copied into a live install.

---

## Reading Paths

### If you are a human evaluator / operator
Start here:
1. `guidelines/README.md`
2. `guidelines/01-infrastructure-spec.md`
3. `guidelines/02-knowledge-and-memory-spec.md`
4. `guidelines/deployed-agents/`

### If you are an agent performing setup or migration
Start here:
1. `playbooks/README.md`
2. `playbooks/bootstrap/install-core-stack.md`
3. the relevant files under `playbooks/`
4. copy or apply the needed files from `artifacts/`

---

## Top-Level Directories

| Directory | Audience | Purpose |
|---|---|---|
| `guidelines/` | Human | Architecture, specs, deployment model, agent specs |
| `playbooks/` | Agent | Operational setup, rollout, migration, verification instructions |
| `artifacts/` | Agent / Installer | Files that get installed or copied into a live system |

---

## Current Stack

| Tool | Role |
|---|---|
| Hermes Agent | Agent runtime |
| GBrain | Knowledge graph and durable context |
| Hindsight | Episodic memory |
| Twenty CRM | Structured pipeline data |
| Lark / Feishu | Workspace communication and docs |

---

## Core Rule

**Human reads guidelines, agent runs playbooks, system installs artifacts.**
