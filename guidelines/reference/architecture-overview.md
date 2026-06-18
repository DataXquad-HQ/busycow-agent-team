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
**Where:** GitHub wiki (company's `[org]-knowledge-base` or equivalent)
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
| `[org]-global` | Everyone | Company identity, product facts |
| `[org]-internal` | All agents | Ops processes, tooling |
| `[org]-sales` | Leo, Maya, Rex, Iris, Humans | Pipeline context, opportunity history |
| `[org]-agent-{name}` | That agent only | Role-specific patterns |
| `[org]-human-{name}` | That human only | Personal context |

### Layer 3 — Structural data
**Where:** CRM (Twenty), task board (Lark Base), or other operational systems
**What:** Opportunities, contacts, pipeline stages, tasks, invoices — live operational records
**Schema definitions:** See `artifacts/schemas/`

## Agent Prompt Design

Each agent's identity is defined in `SOUL.md`. This file is the agent's operating system — it defines:
- Role and position in the org
- What the agent owns (metrics)
- Authority and boundaries
- How it should behave

`SOUL.md` is loaded as the system prompt at agent startup. Keep it focused — every line should affect behaviour.

---

## SOUL.md Structure — Required Sections

Every agent's SOUL.md must follow this structure. Sections in **bold** are mandatory.

| Section | What it contains |
|---|---|
| **Identity & Role** | Who the agent is, where it sits in the team, what problem it exists to solve |
| **Pipeline / Capabilities** | What the agent does end-to-end — capabilities, flows, ownership |
| **Tools** | What the agent can access, how, and what is off-limits (see format below) |
| **Knowledge Sources** | Where the agent recalls context from — GBrain slugs, Hindsight banks |
| **Data & Memory Architecture** | The three layers and which bank/object each type of data goes into |
| **Operating Rules** | Skill-first, cron-as-trigger, build-incrementally, verified-means-tested |

---

## Tools Section Format (mandatory in every SOUL.md)

The Tools section is the single authoritative declaration of what an agent can access. It must cover three things: what is always available, what is restricted in cron, and what is explicitly not available.

```markdown
## Tools

### Always Available (interactive sessions + cron)
| Tool | Endpoint / Access | Skill | Used for |
|---|---|---|---|
| Twenty CRM | `http://localhost:3001/graphql` | `twenty-crm` | All pipeline reads/writes |
| Hindsight | `http://localhost:8888` | — (direct API) | Contextual memory |
| GBrain | MCP (`mcp_gbrain_*`) | `capturing-to-gbrain` | Knowledge graph, timelines |
| Web search | Built-in tool | — | Enrichment, research |

### Cron sessions (restricted toolset: web, terminal, file)
MCP tools (GBrain, Lark) are NOT available in cron jobs. Any capability
that requires MCP must run in an interactive session or delegate via task.

### Not available to this agent
- Code execution
- Image generation
- File system writes outside `workspace/`
```

**Why this matters:**
- The agent knows exactly what it has — no guessing, no failed tool calls
- The deployer knows exactly what to enable in `config.yaml`
- The cron restriction is explicit so skills are written accordingly
- "Not available" prevents the agent from attempting tools it cannot use
