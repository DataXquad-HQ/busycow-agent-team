# Knowledge Ops Playbook

Skills for managing your agent's long-term knowledge — GBrain enrichment, team intelligence, cross-platform knowledge extraction, and memory sync to GitHub.

## Skills

| Skill | What it does |
|---|---|
| `building-gbrain-knowledge-graph` | Enrich GBrain when brain score is low — create entity pages, add links, verify health |
| `extracting-lark-to-gbrain` | Pull Lark group chat messages and extract meaningful knowledge into GBrain nightly |
| `extracting-notion-pages` | Extract content from private Notion pages via API |
| `syncing-brain-memory` | Sync local GBrain vault and Hermes memory files to GitHub |
| `managing-team-knowledge` | Log team decisions, track RACI ownership, detect Bus Factor risks |

## Prerequisites

- **Core playbook installed** — GBrain running, skills registry active
- **Lark MCP configured** — for `extracting-lark-to-gbrain` (see `core/skills/lark-mcp-setup.md`)
- **GitHub repo** — for `syncing-brain-memory` (any repo the agent has push access to)
- **Notion API token** — for `extracting-notion-pages` (set in `~/.hermes/.env` as `NOTION_TOKEN`)

## Recommended Setup Order

1. Install this playbook (`SETUP.md`)
2. Run `building-gbrain-knowledge-graph` to bootstrap your brain with entity pages
3. Schedule `extracting-lark-to-gbrain` as a nightly cron (03:00 local time)
4. Schedule `syncing-brain-memory` after the nightly GBrain dream cycle
