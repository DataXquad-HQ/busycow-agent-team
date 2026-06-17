# Infrastructure Spec

> This document explains the infrastructure stack behind the BusyCow agent system —
> what we use, why we chose it, and how each piece fits together.
> Audience: humans. This is not instructions for an agent.

---

## Philosophy: The Agent as a Digital Employee

We treat each agent the way you would treat a new hire who is growing into a senior employee.

A person grows along three dimensions:

| Dimension | What it means | Agent equivalent |
|---|---|---|
| **Capability** | Skills they have + their role understanding + autonomy | Skills + SOUL.md + Cron jobs |
| **Context** | The information they can access to do their job | Structured data + Memory + Knowledge |
| **Access** | The tools and systems they are authorised to use | Credentials + Toolsets |

An agent starts with a defined role and basic skills. Over time, more skills are added, knowledge documents are written, and memory accumulates from real interactions. The agent becomes more useful not because we change its model, but because its context and capability grow.

This is the core design principle behind everything that follows.

---

## Core Framework: Hermes

**What it is:** Hermes is our agent runtime — the framework that runs every agent, manages their memory, handles tool calls, and schedules autonomous work.

**Why we use it:**
- Single framework for all agents — consistent behaviour, shared tooling
- Per-profile isolation — each agent has its own identity, credentials, skills, and cron jobs
- Native MCP support — connects directly to GBrain, Lark, and other tools without custom glue code
- Built-in skill system — encapsulates reusable logic in a structured, maintainable format

**How we use it:**
- One Hermes profile per agent (`hermes profile create [agent-name]`)
- Each profile contains: `SOUL.md`, `skills/`, `.env`, `cron/`
- Agents are packaged in `busycow-agent-package` (GitHub) for distribution to new organisations

**Agent profiles are the unit of distribution.** When we deploy BusyCow for a new client, we install Hermes and apply the agent profiles from the package.

---

## Context Layer 1: Knowledge Base (GitHub Repo)

**What it is:** A private GitHub repository containing all human-authored knowledge documents in Markdown.

**Why we use it:**
- Version controlled — every change is tracked, full history available via `git log`
- Human-readable and human-writable — Iris writes here after key decisions; founders can edit directly
- Single source of truth for knowledge — agents never write here, only Iris

**How we use it:**
- Structured into folders: `knowledge-base/company/`, `knowledge-base/sales/`, `knowledge-base/products/`, `knowledge-base/market/`, `decisions/`, `systems/`
- Documents follow a standard format with a Changelog section
- Content flows into GBrain via daily sync — agents never read GitHub directly

**The knowledge base is Layer 1 of the knowledge stack.** Humans write conclusions here. Agents read via GBrain.

---

## Context Layer 2: GBrain (Facts & Knowledge)

**What it is:** A semantic knowledge graph that indexes all knowledge base content and structures it for agent queries. Bundled with Hermes.

**Why we use it:**
- Agents cannot efficiently read raw Markdown files at runtime — GBrain makes content queryable
- Goes beyond plain RAG: adds entity graph (people, companies, relationships), timeline entries, and structured fact extraction
- Hybrid search (vector + keyword + graph traversal) returns more precise results than embeddings alone

**How we use it:**
- Knowledge base repo is registered as a GBrain source and synced daily
- Agents query via `mcp_gbrain_query()` or `mcp_gbrain_get_page(slug=...)`
- Iris writes new entities (`put_page`), extracts facts (`extract_facts`), and logs milestones (`add_timeline_entry`) after key conversations
- GBrain is the agent's answer to "what is true about the world right now"

**GBrain is Layer 2 — the queryable index over Layer 1.**

---

## Context Layer 3: Hindsight (Contextual Memory)

**What it is:** A self-hosted semantic memory store for episodic, interaction-level memory. Separate from GBrain.

**Why we use it:**
- GBrain stores facts and knowledge — Hindsight stores what *happened*
- Enables agents to recall "what did we discuss last time with this company" — something knowledge base documents never capture
- Bank-based architecture allows clean separation between shared pipeline memory, per-agent working memory, and per-human profiles

**How we use it:**
- Three bank types (see `02-knowledge-and-memory-spec.md` for details):
  - `[org]-pipeline` — shared interaction history across all opportunities
  - `[org]-agent-[name]` — each agent's private working memory
  - `[org]-human-[name]` — each human's communication style and priorities
- Agents write to Hindsight after every meaningful interaction (`log-engagement` skill)
- Agents recall from Hindsight before handling any opportunity

**Hindsight is Layer 3 — the memory of what happened, not what is true.**

---

## Structural Data: Third-Party Tools

Beyond the three context layers, agents read from and write to structured databases for operational data. These are not memory systems — they are the source of truth for live business objects.

| Tool | What it stores | Why this tool |
|---|---|---|
| **Twenty CRM** | Opportunities, Leads, Contacts, Companies, Tasks | Open-source, self-hosted, GraphQL API — full control, no per-seat cost |
| **Lark Base** | Internal task tracker, OKRs, operational tables | Already used by the team for communication — reduces context switching |

**The distinction:** CRM holds *what the pipeline looks like now*. Hindsight holds *the story of how it got there*.

---

## Agent Capability Framework

Every agent is defined by a spec document (see `00-agent-spec-template.md`) covering:

```
Capabilities    → what the agent does, grouped for human understanding
Skills          → the actual executable logic (one skill = one trigger situation)
Knowledge       → what knowledge base documents must exist before the agent is useful
Memory          → which Hindsight banks the agent reads and writes
Credentials     → what third-party accounts must be set up
Cron jobs       → what runs automatically and on what schedule
```

**Capabilities are for humans.** They group related skills into named buckets so stakeholders can understand what an agent does without reading code. They do not exist in the agent's runtime — only skills do.

**Skills are for agents.** Each skill is a Markdown file with step-by-step instructions, tool calls, and pitfalls. Skills are loaded on demand when the agent encounters the relevant trigger situation.

---

## How It All Connects

```
Human writes to knowledge base
      ↓
GitHub repo (versioned source of truth)
      ↓ daily sync
GBrain (semantic index + entity graph)
      ↑                    ↑
Iris writes              Agent queries
new entities             at runtime
      
Agent interacts with humans / CRM
      ↓
Hindsight (episodic memory per bank)
      ↑
Agent recalls before next interaction

Agent executes tasks
      ↓
Twenty CRM (structured pipeline data)
Lark (human-facing output)
```
