# Agent Runtime Artifact Standard
**Version: 2.0 | Status: Canonical**

This document defines the standard structure for the **runtime artifact layer** of an agent package inside this repo.

Use it when deciding what belongs under:

```text
artifacts/agents/<agent>/
```

This is not a human-facing hiring brief.
Human-readable agent specs belong in:

```text
guidelines/deployed-agents/
```

---

## Purpose

The runtime artifact layer contains the files that are actually installed, copied, or referenced during a live deployment.
It answers:
- which files define the agent at runtime
- which files are copied into Hermes profiles
- which assets support that runtime

---

## Canonical Structure

```text
artifacts/agents/<agent>/
├── SOUL.md
├── SETUP.md
├── cron/
│   ├── README.md
│   └── jobs.json
└── skills/
    ├── README.md
    └── <skill-name>/
        ├── SKILL.md
        ├── references/
        ├── scripts/
        └── templates/
```

### Required files

| File | Purpose |
|---|---|
| `SOUL.md` | Runtime identity, role, boundaries, communication style, knowledge sources |
| `SETUP.md` | Agent-specific installation instructions |
| `skills/` | Runtime skills copied into Hermes profile skill directories |

### Optional files

| File | Purpose |
|---|---|
| `cron/README.md` | Human/operator explanation of the cron set |
| `cron/jobs.json` | Reference cron templates |
| skill `references/` | Supporting material loaded only when needed |
| skill `scripts/` | Deterministic helper scripts |
| skill `templates/` | Output templates or text scaffolds |

---

## What Does NOT Belong Here

Do **not** place these in `artifacts/agents/<agent>/`:

| Wrong content | Correct location |
|---|---|
| Human-readable architecture spec for the agent | `guidelines/deployed-agents/` |
| Company-wide system design rationale | `guidelines/` |
| Generic rollout instructions for multiple agents | `playbooks/` |
| Shared schemas | `artifacts/schemas/` |
| Knowledge-base starter content for client repos | `artifacts/knowledge-base-templates/` |
| Canonical shared skills for multiple profiles | `artifacts/shared-skills/` |

---

## SOUL.md Standard

Every runtime SOUL should contain at least:
- identity / role
- capabilities or operating scope
- authority and boundaries
- communication style
- knowledge sources
- tools relied on
- delivery or escalation rules if relevant

SOUL.md is the runtime truth for the agent.

---

## Skills Standard

Each skill under `artifacts/agents/<agent>/skills/` must be a **directory**, not a flat markdown file.

Correct:

```text
skills/log-engagement/SKILL.md
skills/log-engagement/references/crm-write-patterns.md
```

Incorrect:

```text
skills/log-engagement.md
```

If the same skill is intended for multiple agents, the canonical shared copy belongs in:

```text
artifacts/shared-skills/<skill-name>/
```

A profile-local copy may still also exist under a specific agent when needed for runtime packaging.

---

## Setup Standard

`SETUP.md` inside an agent artifact folder should tell an agent or operator how to install that specific agent.
It should assume the broader core stack is either already installed or handled by a playbook.

A good agent `SETUP.md` includes:
- prerequisites
- profile creation
- SOUL placement
- skill installation
- cron setup if applicable
- verification steps

---

## Quality Bar

Before calling an agent artifact folder clean:
- every file inside it is actually used for runtime installation, copy, or verification
- no human-only design essays are mixed into the folder
- no stale files like `CAPABILITIES.md`, `CONTEXT.md`, or `BUILD-LIST.md` remain unless a current playbook explicitly uses them
- skill directories are real directories with `SKILL.md`
- shared-vs-agent-local ownership is clear

---

## Pitfalls

- Do not confuse runtime artifacts with design specs
- Do not leave old parallel document systems (`CAPABILITIES.md`, `CONTEXT.md`) beside SOUL unless they are still actively part of the install model
- Do not package flat skill markdown files when the runtime expects skill directories
- Do not put canonical shared skills only inside one agent folder — use `artifacts/shared-skills/`
- Do not rely on this layer to explain architecture; that belongs in `guidelines/`
