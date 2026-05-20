# BusyCow Playbooks

**Production-grade AI agent skills and setup guides for Hermes Agent.**

This repo packages everything needed to replicate a fully operational AI agent system — from initial stack setup to specialized business playbooks. Each playbook is self-contained and installable via a single URL.

---

## Stack

**Hermes Agent** (AI framework) + **Lark/Feishu** (data + comms) + **GBrain** (knowledge graph)

---

## Installation Order

```
Step 1: setup/SETUP.md         → SOUL.md + Memory skeleton
Step 2: core/SETUP.md          → Skills registry base + 12 core skills
Step 3: playbooks/X/SETUP.md   → Business-specific skills (pick what you need)
```

---

## Setup

| Path | What it does |
|---|---|
| [`setup/SETUP.md`](setup/SETUP.md) | Initial agent identity, memory skeleton, and SOUL.md |

---

## Core Playbook

Foundation skills every workspace needs. **Install this before any business playbook.**

| Skill | What it does |
|---|---|
| `hermes-agent` | Complete guide to Hermes Agent — setup, config, spawning agents, troubleshooting |
| `managing-skills` | Create, update, delete skills and sync to Skills Registry |
| `managing-cron-jobs` | Schedule, update, and remove Hermes cron jobs |
| `maintaining-gbrain` | Run GBrain nightly dream maintenance cycle |
| `maintaining-memory` | Framework for deciding what goes in Memory vs Skills vs GBrain |
| `capturing-to-gbrain` | Save valuable conversation knowledge to GBrain |
| `google-workspace` | Gmail, Calendar, Drive, Sheets, Docs via `gws` CLI |
| `himalaya` | CLI email client — list, read, send, search via IMAP/SMTP |
| `numpy-financial` | Financial calculations — NPV, IRR, DCF, PMT, loan amortisation |
| `native-mcp` | Connect MCP servers to Hermes — auto-discover and register tools |
| `mcporter` | CLI tool to call MCP servers ad-hoc |
| `lark-mcp-setup` | Set up lark-mcp as a native MCP server in Hermes config |

→ [`core/SETUP.md`](core/SETUP.md)

---

## Business Playbooks

### Sales
CRM management, pipeline tracking, lead enrichment, quotation generation, partner management.

| Skill | What it does |
|---|---|
| `capturing-sales-intel` | Add new contacts and companies to CRM |
| `enriching-leads` | Web-enrich new accounts with description, website, industry |
| `managing-sales-pipeline` | Create and update sales opportunities — stage, notes, follow-ups |
| `managing-partnership-pipeline` | Track partner prospects through agreement to active |
| `reviewing-sales-pipeline` | Pull pipeline status briefing — deals, invoices, forecast |
| `logging-sales-activities` | Log meeting notes and call summaries to CRM |
| `generating-quotations` | Generate quotation PDF from CRM data, upload to Drive |

→ [`playbooks/sales/SETUP.md`](playbooks/sales/SETUP.md)

---

### Internal Ops
Task tracking, daily briefings, weekly audits, and prioritisation.

| Skill | What it does |
|---|---|
| `managing-tasks` | Create and update tasks in the Task Tracker — auto-triage multi-task dumps |
| `reviewing-tasks` | Query tasks with Goal-first prioritisation — standup, weekly view |
| `planning-next-actions` | Score active tasks and recommend top 3–5 actions with reasoning |
| `generating-task-briefing` | Generate daily task briefing message (Mon–Fri, format varies by day) |
| `auditing-tasks` | Weekly audit — orphan tasks, stale initiatives, grouping recommendations |

→ [`playbooks/internal-ops/SETUP.md`](playbooks/internal-ops/SETUP.md)

---

### Knowledge Ops
GBrain enrichment, knowledge extraction, team intelligence, and memory sync.

| Skill | What it does |
|---|---|
| `building-gbrain-knowledge-graph` | Enrich GBrain when brain score is low — entity pages, links, health check |
| `extracting-lark-to-gbrain` | Pull Lark group chat messages and extract knowledge into GBrain |
| `extracting-notion-pages` | Extract content from private Notion pages via API |
| `syncing-brain-memory` | Sync GBrain vault and Hermes memory files to GitHub |
| `managing-team-knowledge` | Log team decisions, track RACI ownership, detect Bus Factor risks |

→ [`playbooks/knowledge-ops/SETUP.md`](playbooks/knowledge-ops/SETUP.md)

---

### Lark Ops
Build and manage Lark/Feishu databases, documents, calendar sync, and financial tracking.

| Skill | What it does |
|---|---|
| `lark-bitable-schema-setup` | Create Bitable apps, tables, and fields via API |
| `lark-docx-writer` | Create structured Lark Docs programmatically |
| `reading-lark-files` | Download and read files shared via Lark links |
| `feishu-lark-bitable-calendar-sync` | Sync Bitable tasks to personal Lark Calendar |
| `tracking-financials` | Manage financial forecast and actuals in Lark Bitable |

→ [`playbooks/lark-ops/SETUP.md`](playbooks/lark-ops/SETUP.md)

---

### Content
Documents, presentations, diagrams, blog posts, PDF editing, and multimedia.

| Skill | What it does |
|---|---|
| `writing-blog-post` | Write structured blog posts from briefings |
| `marp-pitch-deck` | Build pitch decks using Marp markdown → PDF/PPTX |
| `excalidraw` | Create hand-drawn style diagrams in Excalidraw format |
| `powerpoint` | Create, edit, parse .pptx files |
| `ocr-and-documents` | Extract text from PDFs and scanned documents |
| `nano-pdf` | Edit PDFs with natural-language instructions |
| `youtube-content` | Fetch YouTube transcripts and transform into structured content |

→ [`playbooks/content/SETUP.md`](playbooks/content/SETUP.md)

---

### Finance
Financial modeling, investor forecasts, Google Sheets models, and invoice generation.

| Skill | What it does |
|---|---|
| `building-investor-financial-model` | Investor-grade financial forecast — multi-scenario Python model + Google Sheets |
| `gsheets-formula-model` | Live formula-driven Google Sheets model with scenario switcher |
| `generating-invoices` | Generate invoices from CRM data, fill Doc template, export PDF |

→ [`playbooks/finance/SETUP.md`](playbooks/finance/SETUP.md)

---

### AI Automation
Multi-agent systems, autonomous pipelines, AI vision, speech recognition, and event-driven automation.

| Skill | What it does |
|---|---|
| `hermes-cron-scheduling` | Scheduling conventions and time-window philosophy for Hermes cron jobs |
| `hermes-profile-management` | Manage profiles — inspect, move cron jobs, reset auth/state |
| `webhook-subscriptions` | Event-driven webhooks so external services trigger your agent |
| `running-strategic-council` | Multi-agent council to pressure-test business goals before acting |
| `crewai-claude-code-writer` | Wire Claude Code CLI as builder agent inside CrewAI — solves max_iter exhaustion |
| `crewai-openhands-deploy` | Deploy CrewAI + OpenHands self-hosted AI dev stack via Docker |
| `ai-pipeline-feasibility-study` | Validate AI vision pipelines end-to-end without physical hardware |
| `facility-inspection-ai-playbook` | AI inspection playbook for patrol robots (YOLO-World + VLM + ticketing) |
| `whisper` | Speech recognition — transcription, translation, 99 languages |
| `graphify` | Build visual knowledge graphs from any documents, code, or notes |

→ [`playbooks/ai-automation/SETUP.md`](playbooks/ai-automation/SETUP.md)

---

## Quick Start (full install)

```bash
# 1. Initial setup
curl -fsSL https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/setup/SETUP.md \
  | hermes "Follow these setup instructions exactly"

# 2. Core skills
curl -fsSL https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/SETUP.md \
  | hermes "Follow these setup instructions exactly"

# 3. Pick your playbooks
curl -fsSL https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/sales/SETUP.md \
  | hermes "Follow these setup instructions exactly"
```

---

## Publisher

**BusyCow** — AI systems for operators who move fast.
https://github.com/DataXquad-HQ/busycow-playbooks
