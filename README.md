# BusyCow Agent Package

A framework for deploying a production-grade AI agent team inside a company — built on [Hermes Agent](https://hermes-agent.nousresearch.com).

BusyCow is DataXquad's methodology for running AI agents as a real operating team: each agent owns a function, operates independently, and shares only data — not infrastructure.

---

## What's in this package

```
busycow-agent-package/
├── architecture/           ← How the system is designed and why
├── agent-teams/            ← Per-agent SOUL.md, skills, and capabilities
├── context/                ← Data schemas (CRM, structural data definitions)
├── third-party-tools/      ← Every tool in the stack: what it does, how we use it, setup
├── standards/              ← Doc standards and conventions
└── SETUP.md                ← Installation guide
```

---

## Core principles

**1. Each agent is independent**
No shared skills, no shared credentials, no shared infrastructure. If two agents need the same capability, duplicate it. Simplicity over elegance.

**2. Context is layered**

| Layer | What | Where |
|---|---|---|
| Human-readable docs | Policies, decisions, how we operate | GitHub knowledge base (`[org]-internal-kb`) |
| Contextual memory | Entity knowledge, episodic memory | GBrain + Hindsight |
| Structural data | Opportunities, contacts, pipeline, records | CRM and other operational systems |

**3. Agent design lives in `prompt.md`**
Each agent's identity, role, and capabilities are defined in their `SOUL.md`. That file is the agent's operating system.

**4. Credentials are not shared**
Every agent has its own API tokens and environment credentials. If a credential must be shared, duplicate it into each agent's environment separately.

---

## Agent roster

| Agent | Function |
|---|---|
| Iris | Chief of Staff — coordination, knowledge, task dispatch |
| Leo | BD Lead — outbound, pipeline, lead nurturing |
| Maya | GTM — inbound, content, market intel |
| Rex | Customer Success — support, renewals |
| Steve | Software Development — code, infrastructure |

---

## Stack

| Tool | Purpose |
|---|---|
| Hermes Agent | Agent runtime |
| Lark / Feishu | Workspace — IM, task board, docs |
| GBrain | Knowledge graph — entity facts, decisions, intel |
| Hindsight | Episodic memory — what happened, what was said |
| Twenty CRM | Pipeline — opportunities, contacts, stages |

See `third-party-tools/` for setup and usage details on each.
