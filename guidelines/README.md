# BusyCow Agent Framework — Specs

This folder contains the human-readable design specifications for the BusyCow agent framework. These are the "manual" — they explain how the system is designed and why, so clients understand what they're deploying.

## Reading Order

| File | What it covers |
|---|---|
| `00-agent-spec-template.md` | Template for writing an agent spec — use this when designing a new agent |
| `01-infrastructure-spec.md` | Infrastructure requirements — servers, tools, credentials needed before go-live |
| `02-knowledge-and-memory-spec.md` | How information flows through the system — Wiki, GBrain, Hindsight, CRM |

## Who This Is For

**Clients** — read before deployment to understand what you're setting up and why.
**Implementers** — follow during setup to configure each layer correctly.
**Agents** — these specs are the authoritative design reference. If SOUL.md says one thing and a spec says another, flag it to Iris.

## Relationship to Setup Files

Specs (`specs/`) explain the design.
Setup files (`wiki-setup/`, `agent-teams/`, `SETUP.md`) are the hands-on configuration work.

Read specs first. Then do setup.
