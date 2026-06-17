# Agent Design Spec — Leo

> **Status:** ✅ Deployed (C2 Outbound Prospecting pending)
> **Last Updated:** 2026-06-17
> **Build artifacts:** `~/.hermes/profiles/leo/SOUL.md`, `~/.hermes/profiles/leo/skills/`

---

## Part 1 — Core Need & Positioning

### 1a. Why This Agent Exists

The company needs to grow revenue across multiple business lines simultaneously. Humans cannot personally manage every prospect, follow up on every lead, and monitor every deal — the cognitive load is too high and the speed too slow.

Leo exists to be the attention the sales rep buys back. Every prospect gets contacted. Every lead gets followed up. Every deal gets monitored. The human focuses on relationships and decisions; Leo handles the engine underneath. Without Leo, deals go quiet, leads go cold, and pipeline visibility is zero.

---

### 1b. Role & Goal

| Field | Value |
|---|---|
| **Name** | Leo |
| **Title** | BD Lead Agent |
| **One-line goal** | No prospect left un-emailed. No lead going quiet. No deal stalling without a recovery plan. |
| **The number it owns** | Partner count × Pipeline value × Conversion rate |
| **Primary human contact** | Human (BD decisions, outreach approval) |

---

### 1c. Team Positioning

| | Role | What flows |
|---|---|---|
| **Receives from** | Human | Source lists, outreach approval, deal context, strategy direction |
| **Receives from** | Growth Agent | Inbound leads (enter CRM as LEAD) |
| **Hands off to** | Human | Drafted outreach (for approval before send), deal recommendations, daily reminders |
| **Does NOT own** | Inbound lead gen (Growth Agent), post-sign customer success (Customer Success Agent), final deal sign-off (Human) |

---

## Part 2 — Context & Data Layer

### 2a. What Leo Needs to Know

| What Leo needs to know | Source | How it reads it |
|---|---|---|
| ICP for each BL | GBrain vault | Direct file: `internal/business-lines/[bl]/icp.md` |
| Sales strategy per BL | GBrain vault | Direct file: `internal/business-lines/[bl]/strategy.md` |
| Product overview per BL | GBrain vault | Direct file: `internal/business-lines/[bl]/product.md` |
| GTM motion per BL | GBrain vault | Direct file: `internal/business-lines/[bl]/gtm.md` |
| Company background | GBrain vault | Direct file: `internal/company/overview.md` |
| External company facts + relationships | GBrain MCP | `mcp_gbrain_get_page("external/entities/companies/[slug]")` |
| People at target company | GBrain MCP | `mcp_gbrain_traverse_graph("external/entities/companies/[slug]", link_type="works_at")` |
| Recent interactions with a deal | Hindsight | `[org]-pipeline` bank recall |
| Human communication preferences | Hindsight | `[org]-human-[name]` bank |

**GBrain content that must exist before Leo is fully useful:**

| Document | Slug | Status |
|---|---|---|
| BL ICP | `internal/business-lines/[bl]/icp.md` | ✅ File exists — needs content |
| BL strategy | `internal/business-lines/[bl]/strategy.md` | ✅ File exists — needs content |
| BL product | `internal/business-lines/[bl]/product.md` | ✅ File exists — needs content |
| BL GTM | `internal/business-lines/[bl]/gtm.md` | ✅ File exists — needs content |

---

### 2b. Capabilities

| # | Capability | What it means | Skills | Status |
|---|---|---|---|---|
| C1 | Lead Capture | Onboard contacts from humans or events into CRM; scout and prioritise raw prospect lists | `capturing-leads`, `prospect-scouting` | ✅ Built |
| C2 | Outbound Prospecting | Run cold email sequences for qualified prospects from first contact to reply | *(to build)* | 🔧 Pending |
| C3 | Account Intelligence | Enrich prospect/lead context before outreach or meetings; monthly refresh for active accounts | `enriching-accounts` | ✅ Built |
| C4 | Lead Nurturing | Draft monthly personalised follow-ups; monitor inbox for inbound replies; send approved emails | `nurturing-leads`, `monitoring-inbox-replies` | ✅ Built |
| C5 | Pipeline Progressing | Log every interaction; surface daily tasks to human; provide deal advice on demand | `log-engagement`, `handling-pipeline-interactions`, `creating-report-back-tasks`, `advising-on-tasks`, `sending-daily-pipeline-reminder` | ✅ Built |
| C6 | Pipeline Health Monitoring | Weekly pipeline coverage check; monthly strategy and memory freshness review | `checking-pipeline-health`, `checking-pipeline-strategy`, `ingesting-sales-strategy` | ✅ Built (needs BL docs) |

---

## Part 3 — Tools & Permissions

### 3a. Tools Required

| Tool / Skill | Purpose |
|---|---|
| `twenty-crm` | All CRM read/write via GraphQL — foundational layer for all pipeline operations |
| `openmail` | Send/receive email via agent's dedicated mailbox |
| `web` (Tavily) | Web research for account enrichment and prospect scouting |
| `capturing-to-gbrain` | Write external entities and facts to GBrain |
| `github-core-repos` | Read internal knowledge repos |
| `lark-im` | Send messages to human and Lark channels |
| `managing-tasks` | Create tasks in Lark task board |
| `reviewing-tasks` | Query and summarise task board |
| `managing-skills` | Maintain and update own skills |

### 3b. Credentials & Environment

| Service | Purpose | `.env` key |
|---|---|---|
| Anthropic | LLM inference | `ANTHROPIC_API_KEY` |
| OpenRouter | LLM fallback | `OPENROUTER_API_KEY` |
| Twenty CRM | Pipeline read/write | `TWENTY_API_KEY` |
| OpenMail | Email send/receive | Agent mailbox token |
| Feishu Bot | Lark messaging | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` |
| Hindsight | Pipeline bank read/write | `HINDSIGHT_BASE_URL` |
| Tavily | Web search for enrichment | `TAVILY_API_KEY` |
| GitHub | Read internal repos | `GITHUB_TOKEN` |

### 3c. Delivery Channels

| Channel | Purpose |
|---|---|
| `[Sales] Daily Update` | Daily pipeline reminder and task list for sales team |
| `[Sales] Nurturing Review` | Outreach drafts pending human approval before send |
| `[Sales] Pipeline and Strategy` | Weekly health check and monthly strategy reports |
| `[System] Backend Report` | Cron ops logs, errors, run stats — internal only |

### 3d. Cron Jobs

| Job | Schedule | Capability | Delivers to |
|---|---|---|---|
| Daily Pipeline Reminder | Mon–Fri 01:00 UTC | C5 | `[Sales] Daily Update` |
| Lead Nurturing Scanner | Daily 01:00 UTC | C4 — draft creation | `[Sales] Nurturing Review` + `[System] Backend Report` |
| Outreach Message Sender | Daily 04:00 UTC | C4 — send approved emails | `[System] Backend Report` |
| Inbox Monitor | Daily 02:00 UTC | C4 — inbound reply tracking | Silent if no replies; `[System] Backend Report` on activity |
| Weekly Pipeline Health Check | Monday 01:00 UTC | C6 | `[Sales] Pipeline and Strategy` |
| Monthly Pipeline Strategy Check | 1st of month 01:00 UTC | C6 | `[Sales] Pipeline and Strategy` |
| Monthly Account Intelligence Update | 1st of month 02:00 UTC | C3 | `[Sales] Daily Update` |

---

## Part 4 — Build Mapping

| Spec Section | Build Artifact | Location |
|---|---|---|
| Identity, mandate | `SOUL.md` — Who Leo Is | `~/.hermes/profiles/leo/SOUL.md` |
| Team positioning | `SOUL.md` — Position in the Team | `~/.hermes/profiles/leo/SOUL.md` |
| Context sources | `SOUL.md` — Knowledge Sources | `~/.hermes/profiles/leo/SOUL.md` |
| Capabilities + Skills | Skills directory | `~/.hermes/profiles/leo/skills/` |
| Cron jobs | Hermes cron config | `busycow-agent-package/agent-teams/leo/cron/jobs.json` |
| Credentials | Per-profile `.env` | `~/.hermes/profiles/leo/.env` |

## Spec Status

| Section | Status |
|---|---|
| Part 1 — Core Need & Positioning | ✅ Complete |
| Part 2 — Context & Data Layer | ✅ Complete |
| Part 3 — Tools & Permissions | ✅ Complete |
| GBrain BL content filled | 📝 Files exist — content needed |
| Hindsight banks | ✅ `[org]-pipeline`, `[org]-agent-leo` |
| SOUL.md | ✅ Deployed |
| C1, C3, C4, C5, C6 skills | ✅ Built |
| C2 Outbound Prospecting | 🔧 Pending build |
| All cron jobs | ✅ Configured in `jobs.json` |
