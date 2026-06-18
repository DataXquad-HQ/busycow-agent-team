# Third-Party Tools

Every tool the BusyCow agent stack depends on — what it does, how agents use it, who hosts it, and whether it is required or optional.

---

## Tool Registry

| Tool | Role | Hosting | Required? |
|---|---|---|---|
| [Hermes Agent](#hermes-agent) | Agent runtime — skills, cron, memory, tool access | Self-hosted (VM) | ✅ Required |
| [Twenty CRM](#twenty-crm) | Pipeline data — opportunities, contacts, companies, engagements | Self-hosted (Docker) | ✅ Required |
| [Hindsight](#hindsight) | Episodic memory — interaction context, soft signals, per-opportunity recall | Self-hosted (Docker) | ✅ Required |
| [GBrain](#gbrain) | Knowledge graph — entity facts, decisions, company timelines | Self-hosted (Node) | ✅ Required |
| [OpenMail](#openmail) | Outbound/inbound email — outreach sending, reply detection, thread management | Cloud (SaaS) | ✅ Required for Leo |
| [GitHub](#github) | Internal wiki — sales strategy, ICP, product docs, agent package distribution | Cloud (SaaS) | ✅ Required |
| [Tavily](#tavily) | Web search — company research, news, enrichment | Cloud (API) | ✅ Required for Leo |
| [Anthropic Claude](#anthropic-claude) | LLM backbone — reasoning, drafting, classification | Cloud (API) | ✅ Required |
| [Lark / Feishu](#lark--feishu) | Workspace IM — message delivery, task tracking, doc management | Cloud (SaaS) | ⚙️ Optional (China/SEA deployments) |

---

## Hermes Agent

**Hosting:** Self-hosted on VM  
**Default port:** `8787` (web UI), `9119` (dashboard)  
**What it is:** The agent runtime. Runs all agent sessions, skill loading, cron scheduling, memory read/write, and tool dispatch.

Agents are Hermes profiles (`~/.hermes/profiles/<agent-name>/`). Each profile has its own:
- `SOUL.md` — identity and operating instructions
- `skills/` — loaded skill library
- `cron/jobs.json` — scheduled jobs
- `.env` — per-agent credentials

**Docs:** https://hermes-agent.nousresearch.com/docs

---

## Twenty CRM

**Hosting:** Self-hosted (Docker Compose)  
**Default internal URL:** `http://localhost:3001`  
**External URL (human-facing links):** `{{CRM_EXTERNAL_URL}}`  
**What it is:** Source of truth for all structured pipeline data — Opportunities, Partnerships, People, Companies, Engagements, Tasks, OutreachMessages.

Agents access via GraphQL:
- Data CRUD: `POST /graphql`
- Schema introspection: `POST /metadata`

Auth: `Authorization: Bearer {{TWENTY_API_KEY}}`

**Schema reference:** `artifacts/schemas/crm.md`  
**Setup:** `playbooks/integrations/twenty-crm/SETUP.md`

---

## Hindsight

**Hosting:** Self-hosted (Docker)  
**Default port:** `8888` (API), `9999` (UI)  
**What it is:** Semantic memory layer. Stores contextual, narrative, and opportunity-level memory that doesn't fit structured CRM fields — what was said, why a deal stalled, how a contact responded, Hunter's read on a situation.

Agents write and recall via REST:
```
POST /v1/default/banks/{bank}/memories        # store
POST /v1/default/banks/{bank}/memories/recall # retrieve
```

**Memory banks used by Leo:**

| Bank | Purpose |
|---|---|
| `{{ORG_PREFIX}}-pipeline` | Per-opportunity context — primary bank for C5/C6 |
| `{{ORG_PREFIX}}-global` | Company-level facts approved across the team |
| `{{ORG_PREFIX}}-agent-leo` | Leo's private short-term working memory |
| `{{ORG_PREFIX}}-internal` | Cross-agent handoffs and operational decisions |
| `{{ORG_PREFIX}}-human-sales-rep` | Sales Rep's priorities and communication style (read-only) |
| `{{ORG_PREFIX}}-human-manager` | Manager's priorities and communication style (read-only) |

**Docs:** `playbooks/integrations/hindsight/README.md`

---

## GBrain

**Hosting:** Self-hosted (Node.js)  
**Access:** Via MCP tools (`mcp_gbrain_*`) loaded in Hermes  
**What it is:** Structured knowledge graph. Stores entity facts (companies, people, decisions), relationship links, and timelines. Complements Hindsight — GBrain is for facts and relationships; Hindsight is for context and narrative.

Agents use GBrain for:
- Timeline entries after engagements (`mcp_gbrain_add_timeline_entry`)
- Relationship context — who knows whom (`mcp_gbrain_traverse_graph`)
- Product and ICP knowledge pages (`mcp_gbrain_get_page`)
- Extracting new facts from conversations (`mcp_gbrain_extract_facts`)

**Docs:** `playbooks/integrations/gbrain/README.md`

---

## OpenMail

**Hosting:** Cloud (SaaS) — [openmail.sh](https://openmail.sh)  
**Base URL:** `https://api.openmail.sh/v1`  
**What it is:** Dedicated email infrastructure for agent-driven outreach. Each agent gets its own inbox address. Supports send, receive, threading, and webhook/polling for inbound reply detection.

Leo's inbox: `{{AGENT_EMAIL}}` (inbox ID: `{{OPENMAIL_INBOX_ID}}`)

Key API actions:
| Action | Endpoint |
|---|---|
| Send email | `POST /v1/messages` — requires `Idempotency-Key` header |
| List threads | `GET /v1/inboxes/{id}/threads` |
| Get messages | `GET /v1/threads/{id}/messages` |
| Mark as read | `PATCH /v1/threads/{id}` |

Auth: `Authorization: Bearer {{OPENMAIL_TOKEN}}`

**Skill reference:** `artifacts/agents/leo/skills/openmail/SKILL.md`

---

## GitHub

**Hosting:** Cloud (SaaS) — [github.com](https://github.com)
**What it is:** Version-controlled storage for the internal wiki and agent package. Leo reads company knowledge pages (sales strategy, ICP, product docs) that live in the internal wiki repo. Iris writes to the wiki after key decisions; Leo pulls via GBrain sync.

**What Leo uses it for:**
- Reading the internal wiki (`{{INTERNAL_WIKI_REPO}}`) — sales strategy, ICP, product context
- Reading the agent package repo (`{{AGENT_PACKAGE_REPO}}`) — skill updates, context schemas
- Pushing knowledge page updates when instructed

**Auth:** SSH key configured on the VM. The same key is used by all agents on the same machine.

**Setup:**
```bash
# Generate SSH key (if not already present)
ssh-keygen -t ed25519 -C "agents@{{YOUR_DOMAIN}}" -f ~/.ssh/github_agents

# Add public key to GitHub account
cat ~/.ssh/github_agents.pub
# → paste into GitHub Settings → SSH and GPG keys

# Add to SSH config
cat >> ~/.ssh/config << 'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/github_agents
  IdentitiesOnly yes
EOF

# Verify
ssh -T git@github.com
```

**Skill reference:** `artifacts/agents/leo/skills/github-core-repos/SKILL.md`

---

## Tavily

**Hosting:** Cloud (API) — [tavily.com](https://tavily.com)
**What it is:** Web search API optimised for AI agents — returns clean, structured results without scraping overhead. Leo calls it via Hermes's built-in `web_search` tool, which routes to Tavily when `TAVILY_API_KEY` is configured.

**What Leo uses it for:**

| Skill | How Tavily is used |
|---|---|
| `enriching-accounts` | Search company news, website, LinkedIn for L1/L2 enrichment |
| `prospect-scouting` | Research companies on a target list before cold outreach |
| `checking-pipeline-health` | Search for context on stalled or at-risk opportunities |
| `checking-pipeline-strategy` | Search for market signals and competitor activity |

**Important:** Leo's skills call `web_search` generically — the actual provider is determined by Hermes config. Set `TAVILY_API_KEY` in Leo's `.env` and configure Tavily as the search provider in `config.yaml` to activate it.

**Auth:** `TAVILY_API_KEY` in Leo's `.env`

**Get an API key:** [app.tavily.com](https://app.tavily.com) → Dashboard → API Keys

---

## Anthropic Claude

**Hosting:** Cloud (API) — [anthropic.com](https://www.anthropic.com)  
**What it is:** The LLM powering all agent reasoning, drafting, classification, and decision-making. Hermes dispatches every agent session to Claude via the Anthropic API.

**Configured in:** Hermes `config.yaml` under `models.default`  
**Auth:** `ANTHROPIC_API_KEY` in Hermes `.env`

Recommended model tier for production: `claude-sonnet-4` or later. Use `claude-haiku-4` for high-frequency cron tasks to reduce cost.

---

## Lark / Feishu

**Hosting:** Cloud (SaaS) — [larksuite.com](https://www.larksuite.com) / [feishu.cn](https://www.feishu.cn)  
**What it is:** Workspace IM, task board, doc management, and calendar. Used as the human-facing delivery channel — agents push notifications, reminders, and reports to Lark channels.

**When to use:** This tool is most relevant for teams already using Lark/Feishu (common in China, Southeast Asia, and Taiwan). Teams using Slack, Teams, or other IM platforms should substitute with the equivalent messaging integration.

**Package default:** bind `lark-cli` to the same app as Hermes, then run it in `default-as=bot` and `strict-mode=off`. Treat `lark-cli` as a required operator surface, not an optional extra.

**Delivery channels Leo uses:**

| Channel | Purpose |
|---|---|
| `{{SALES_DAILY_UPDATE_CHANNEL_ID}}` | Pipeline reminders and human-facing notifications |
| `{{OUTREACH_REVIEW_CHANNEL_ID}}` | Outreach drafts pending human review |
| `{{SYSTEM_BACKEND_CHANNEL_ID}}` | Ops logs and cron execution reports (internal) |

**Docs:** `playbooks/integrations/lark/README.md`
