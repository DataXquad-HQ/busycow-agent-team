# Architecture Overview

## Agent Team Design

Each agent in the BusyCow team owns a function end-to-end. The team is designed so any single agent can operate independently — no agent depends on another agent to function.

```
Human (Founders)
    └── Iris (Chief of Staff)
            ├── Maya     — GTM, inbound lead gen, content
            ├── Leo      — Outbound, pipeline, lead nurturing
            ├── Rex      — Customer success, renewals
            └── Steve    — Software development, infrastructure
```

## Independence Principle

**Skills:** Every agent has its own skill set as real files in its own profile directory. If two agents need the same skill, the skill is duplicated — not symlinked or shared. This eliminates dependency chains and makes each agent fully portable.

**Credentials:** Every agent has its own API tokens and environment variables. No shared credential pools. If a service credential needs to be used by multiple agents, it is duplicated into each agent's `.env` separately.

**Infrastructure:** Each agent profile is self-contained under `~/.hermes/profiles/<name>/`. Deleting one agent has zero impact on any other.

## Context Layers

Agents operate on three types of context. Each type has a designated home.

### Layer 1 — Human-readable documentation
**Where:** GitHub wiki (company's `dx-internal-wiki` or equivalent)
**What:** Company policies, how we operate, decisions and rationale, agent role definitions
**Who writes:** Iris (after key conversations and decisions)
**Who reads:** Humans directly; agents read via GBrain (Iris keeps it synced)

### Layer 2 — Contextual memory
**Where:** GBrain (structured knowledge graph) + Hindsight (episodic memory)
**What:**
- GBrain: entity facts, decisions, intel, relationships — "what do we know about X"
- Hindsight: interaction history, soft signals, call notes — "what happened with X"

**Bank structure for Hindsight:**

| Bank | Access | Content |
|---|---|---|
| `dx-global` | Everyone | Company identity, product facts |
| `dx-internal` | All agents | Ops processes, tooling |
| `dx-sales` | Leo, Maya, Rex, Iris, Humans | Pipeline context, deal history |
| `dx-agent-{name}` | That agent only | Role-specific patterns |
| `dx-human-{name}` | That human only | Personal context |

### Layer 3 — Structural data
**Where:** CRM (Twenty), task board (Lark Base), or other operational systems
**What:** Deals, contacts, pipeline stages, tasks, invoices — live operational records
**Schema definitions:** See `context/schemas/`

## Agent Prompt Design

Each agent's identity is defined in `SOUL.md`. This file is the agent's operating system — it defines:
- Role and position in the org
- What the agent owns (metrics)
- Authority and boundaries
- How it should behave

`SOUL.md` is loaded as the system prompt at agent startup. Keep it focused — every line should affect behaviour.
