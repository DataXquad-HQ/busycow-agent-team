# Hermes Agent

## What it is

Hermes Agent is the AI agent runtime that powers the entire BusyCow stack. Each agent in the team runs as a separate Hermes profile.

Homepage: https://hermes-agent.nousresearch.com

## Role in the stack

Hermes provides the execution environment for every agent — it handles the LLM loop, tool execution, memory, skills, cron jobs, and platform connections.

## Key concepts

| Concept | What it is |
|---|---|
| **Profile** | A named agent identity with its own SOUL.md, memory, skills, cron jobs, and credentials |
| **SOUL.md** | The agent's system prompt — defines role, behaviour, authority, boundaries |
| **Skill** | A SKILL.md file that teaches the agent how to do a specific repeatable task |
| **Cron** | Scheduled jobs that run autonomously without user interaction |
| **MCP server** | External tool integrations (Lark, GBrain, etc.) loaded as structured tool sets |

## Profile structure

```
~/.hermes/                          ← Iris (default profile)
    config.yaml
    SOUL.md
    MEMORY.md
    USER.md
    skills/
    cron/
    profiles/
        leo/                        ← Leo profile
            config.yaml
            SOUL.md
            MEMORY.md
            skills/
            cron/
        maya/
        rex/
        steve/
```

## Agent independence

Each profile is fully self-contained:
- Its own `config.yaml` (model, MCP servers, credentials)
- Its own `SOUL.md` (identity and role)
- Its own `skills/` directory (real files, no symlinks to other profiles)
- Its own cron jobs
- Its own Lark bot credentials

Deleting one profile has zero impact on any other.

## Setup

```bash
pip install hermes-agent
hermes setup
```

To create a new agent profile:
```bash
hermes profile create <name>
```

Full docs: https://hermes-agent.nousresearch.com/docs
