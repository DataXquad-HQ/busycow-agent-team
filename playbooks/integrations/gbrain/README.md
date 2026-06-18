# GBrain

## What it is

GBrain is Hermes Agent's long-term knowledge graph. It is a local-first, self-hosted structured memory layer that persists across sessions.

## Role in the stack

GBrain is the **agent-queryable knowledge layer** — the distilled, structured version of everything the team knows. Agents query GBrain instead of reading raw documents.

| Use | Example |
|---|---|
| Entity facts | "What do we know about Company X?" |
| Decisions | "What did we decide about pricing?" |
| People | "Who is the contact at Partner Y?" |
| Intel | "What signals has Leo seen from this prospect?" |
| Timelines | "What has happened with this opportunity over time?" |

## How it fits with other tools

| Tool | What it stores | Query pattern |
|---|---|---|
| **GBrain** | Entity facts, decisions, relationships, intel | "What do we know about X?" |
| **Hindsight** | Episodic memory — what happened, what was said | "What happened with X?" |
| **Twenty CRM** | Live operational pipeline — opportunities, stages, contacts | "What is the current status of opportunity X?" |

These three overlap on contacts and companies but serve different query patterns. Agents write to all three at the appropriate time.

## How agents use it

**Iris** is the primary writer — she extracts facts and decisions from conversations and writes them to GBrain after every meaningful interaction.

**All agents** read GBrain when they need context before acting.

**Leo** writes opportunity context and partner intel after interactions.

Key operations:
- `mcp_gbrain_put_page` — write or update a page
- `mcp_gbrain_query` — semantic search across all knowledge
- `mcp_gbrain_extract_facts` — extract structured facts from conversation text
- `mcp_gbrain_add_timeline_entry` — log an event to an entity's timeline

## Page structure

```
companies/     ← company profiles
people/        ← contact profiles
decisions/     ← strategic and operational decisions (YYYY-MM-DD-topic)
analysis/      ← market intel, research
concepts/      ← frameworks and principles
```

## Setup

```bash
hermes setup gbrain
gbrain init
gbrain sync
```

GBrain vault lives at `~/brain/` (git-backed). All knowledge pages are markdown with YAML frontmatter.
