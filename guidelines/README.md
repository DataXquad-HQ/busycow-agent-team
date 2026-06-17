# BusyCow Agent Framework — Specs

This folder contains the human-readable design specifications for the BusyCow agent framework. These are the "manual" — they explain how the system is designed and why, so clients understand what they're deploying.

## Reading Order

| File | What it covers |
|---|---|
| `01-infrastructure-spec.md` | Infrastructure requirements — servers, tools, credentials needed before go-live |
| `02-knowledge-and-memory-spec.md` | How information flows through the system — Knowledge Base, GBrain, Hindsight |
| `03-gbrain-and-hindsight-spec.md` | GBrain entity types, relationship types, Hindsight bank design, and how the two work together |
| `04-agent-spec-template.md` | Template for designing a new agent — the hiring brief + build mapping |

## Deployed Agents

The [`deployed-agents/`](deployed-agents/) folder contains the design specs for every agent that has been built and deployed. These are the human-readable "hiring briefs" — why each agent exists, what it does, and how it maps to build artifacts.

| Agent | Spec | Status |
|---|---|---|
| Iris — Chief of Staff | [iris-spec.md](deployed-agents/iris-spec.md) | ✅ Deployed |
| Leo — BD Lead Agent | [leo-spec.md](deployed-agents/leo-spec.md) | ✅ Deployed (C2 pending) |

## Who This Is For

**Clients** — read before deployment to understand what you're setting up and why.
**Implementers** — follow during setup to configure each layer correctly.
**Agents** — these specs are the authoritative design reference. If SOUL.md says one thing and a spec says another, flag it to Iris.

## Relationship to Setup Files

Specs (`specs/`) explain the design.
Setup files (`knowledge-base-setup/`, `agent-teams/`, `SETUP.md`) are the hands-on configuration work.

Read specs first. Then do setup.
