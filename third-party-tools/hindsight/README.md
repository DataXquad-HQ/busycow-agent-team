# Hindsight

## What it is

Hindsight is the episodic memory layer. It stores what happened — interaction history, soft signals, call notes, and conversational context that doesn't fit in a structured knowledge graph.

## Role in the stack

Hindsight answers: *"What happened with X?"*
GBrain answers: *"What do we know about X?"*

Use Hindsight when the value is in the event or the conversation, not just the fact.

## Bank structure

Banks define who reads and writes a given pool of memory. The boundary is access pattern — not topic.

| Bank | Readers | Writers | Content |
|---|---|---|---|
| `dx-global` | Everyone | Iris | Company identity, product facts |
| `dx-internal` | All agents | Iris | Ops processes, tooling conventions |
| `dx-sales` | Leo, Maya, Rex, Iris, Humans | Leo, Iris | Opportunities, deal context, what was promised, partner interactions |
| `dx-agent-{name}` | That agent only | That agent | Role-specific patterns, learnings |
| `dx-human-{name}` | That human only | Iris + that human | Personal context, preferences |

**Principle: shared context → shared bank. Private behaviour → private bank.**

## How agents use it

Agents write to Hindsight after meaningful interactions — calls, emails, deal updates, customer issues.

Agents read from Hindsight when they need interaction history before acting — e.g. Leo checks `dx-sales` before drafting a follow-up to understand what was last said.

## What does NOT go in Hindsight

| Content | Goes here instead |
|---|---|
| Structured pipeline data | Twenty CRM |
| Entity facts and decisions | GBrain |
| Procedural SOPs | Skills |
| Company policies | dx-internal-wiki |

## Setup

Hindsight runs as a self-hosted service on the VM.

```
Ports: 8888 (API), 9999 (admin)
Path:  /mnt/disks/data/hindsight/
API:   /v1/default/banks/{bank_id}/memories
```

Create banks via the Hindsight admin UI or API before agents attempt to write to them.
