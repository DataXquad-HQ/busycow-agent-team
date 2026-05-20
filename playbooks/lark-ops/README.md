# Lark Ops Playbook

Skills for building and managing Lark/Feishu Bitable databases, documents, and automations — the operational data layer for your AI agent.

## Skills

| Skill | What it does |
|---|---|
| `lark-bitable-schema-setup` | Create Bitable apps, tables, and fields via API from scratch |
| `lark-docx-writer` | Create structured Lark Docs with headings, bullets, and paragraphs programmatically |
| `reading-lark-files` | Download and read files (xlsx, pdf, docx) shared via Lark file links |
| `feishu-lark-bitable-calendar-sync` | Sync Bitable task records to personal Lark Calendar events |
| `tracking-financials` | Manage financial forecast and actuals in a Lark Bitable tracker |

## Prerequisites

- **Core playbook installed**
- **Lark MCP configured** — see `core/skills/lark-mcp-setup.md`
- **Lark App with permissions**: `bitable:app`, `docx:document`, `drive:file`, `calendar:calendar`
- Create your Lark App at: https://open.larksuite.com/app

## Use Cases

- **CRM / task database** — build and manage structured Bitable tables your agent reads/writes
- **Document generation** — agent creates formatted Lark Docs from data (reports, proposals)
- **Calendar sync** — task deadlines automatically appear in personal calendar
- **Financial tracking** — revenue, expenses, and cashflow in Bitable with agent updates
