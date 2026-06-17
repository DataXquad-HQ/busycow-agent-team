# Agent Design Spec — Leo

> **Status:** ✅ Deployed (core capabilities), 🔧 C2 Outbound Prospecting pending
> **Last Updated:** 2026-06-17
> **Build artifacts:** `~/.hermes/profiles/leo/SOUL.md`, `~/.hermes/profiles/leo/skills/`

---

## Part 1 — Core Need & Positioning

### 1a. Why This Agent Exists

DataXquad needs to grow revenue across multiple business lines simultaneously. The founders cannot personally manage every prospect, follow up on every lead, and monitor every deal — the cognitive load is too high and the speed is too slow.

Leo exists to be the attention the sales rep buys back. Every prospect gets contacted. Every lead gets followed up. Every deal gets monitored. The sales rep focuses on relationships and decisions; Leo handles the engine underneath. Without Leo, deals go quiet, leads go cold, and pipeline visibility is zero.

---

### 1b. Role & Goal

| Field | Value |
|---|---|
| **Name** | Leo |
| **Title** | BD Lead Agent, DataXquad |
| **One-line goal** | No prospect left un-emailed. No lead going quiet. No deal stalling without a recovery plan. |
| **The number it owns** | Partner count × Pipeline value × Conversion rate |
| **Primary human contact** | Hunter (BD decisions, outreach approval) |

---

### 1c. Team Positioning

| | Agent / Human | What flows |
|---|---|---|
| **Receives from** | Hunter | Source lists, outreach approval, deal context, strategy direction |
| **Receives from** | Maya | Inbound leads (enter CRM as LEAD) |
| **Receives from** | Iris | Task assignments, briefings, escalations |
| **Hands off to** | Iris | Pipeline status, blockers, distillable facts |
| **Hands off to** | Hunter | Drafted outreach (for approval before send), deal recommendations |
| **Does NOT own** | Inbound lead gen (Maya), post-sign customer success (Rex), final deal sign-off (human) |

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
| Recent interactions with a deal | Hindsight | `dx-pipeline` bank recall |
| Hunter's communication preferences | Hindsight | `dx-human-hunter` bank |

**GBrain content that must exist before Leo is useful:**

| Document | Slug | Status |
|---|---|---|
| GeoKernel ICP | `internal/business-lines/geokernel/icp.md` | ✅ Exists (needs content) |
| GeoKernel strategy | `internal/business-lines/geokernel/strategy.md` | ✅ Exists (needs content) |
| GeoKernel product | `internal/business-lines/geokernel/product.md` | ✅ Exists (needs content) |
| GeoKernel GTM | `internal/business-lines/geokernel/gtm.md` | ✅ Exists (needs content) |

---

### 2b. Capabilities Overview

| # | Capability | What it means | Priority | Status |
|---|---|---|---|---|
| C1 | Lead Capture | Help humans onboard new leads; scout and prioritise raw prospect lists | 🔴 Must-have | ✅ Built |
| C2 | Outbound Prospecting | Run cold email sequences for qualified prospects | 🔴 Must-have | 🔧 Pending |
| C3 | Account Intelligence | Enrich prospect/lead context before outreach or meetings | 🔴 Must-have | ✅ Built |
| C4 | Lead Nurturing | Monthly personalised follow-up; monitor inbox replies | 🔴 Must-have | ✅ Built |
| C5 | Pipeline Progressing | Drive every active deal from first interest to closed — log, remind, advise | 🔴 Must-have | ✅ Built |
| C6 | Pipeline Health Monitoring | Weekly health check + monthly strategy review | 🟡 Nice-to-have | ✅ Built (needs KB docs) |

---

### 2c. Capability Detail

**C1 — Lead Capture**
- **Trigger:** (a) Hunter provides a contact from networking/events/referrals; (b) Hunter provides a raw list of prospects to scout
- **What Leo does:** (a) Onboards contact into CRM as LEAD; (b) analyses list against ICP, surfaces priority targets with reasoning
- **Output:** CRM records created; scouting report with ranked prospects
- **Success criterion:** Every contact Hunter provides enters CRM within 24h with correct status

**C2 — Outbound Prospecting** *(pending)*
- **Trigger:** Hunter approves a qualified PROSPECT list
- **What Leo does:** Enters contacts as PROSPECT in CRM, drafts cold email sequence, sends after human approval, tracks replies
- **Output:** Cold emails sent (human-approved); reply received → status becomes LEAD
- **Success criterion:** Every approved PROSPECT receives first email within 24h

**C3 — Account Intelligence**
- **Trigger:** New PROSPECT before first outreach; new LEAD before first nurturing touch
- **What Leo does:** Level 1 (shallow) enrichment for new prospects; Level 2 (deep) for leads before meetings
- **Output:** Enriched CRM records; GBrain entity pages for external companies/people
- **Success criterion:** No outreach or meeting without enriched account context

**C4 — Lead Nurturing**
- **Trigger:** Monthly cron for NURTURE tier; inbox reply received
- **What Leo does:** Drafts personalised monthly outreach based on context; monitors inbox; logs replies; creates follow-up tasks
- **Output:** Drafted emails (human-approved); logged engagements in CRM + Hindsight pipeline
- **Success criterion:** No NURTURE lead goes 6 weeks without a touch

**C5 — Pipeline Progressing**
- **Trigger:** Any update from Hunter about an opportunity or partnership; daily cron
- **What Leo does:** (1) Log — captures every interaction into Hindsight pipeline bank + CRM; (2) Remind — daily task reminder to Hunter; (3) Advise — context-driven advice on how to progress a specific deal
- **Output:** Logged engagements; daily Lark reminder; deal advice with supporting context
- **Success criterion:** Hunter never needs to ask "where are we on X" — Leo surfaces it

**C6 — Pipeline Health Monitoring**
- **Trigger:** Weekly cron (health check); monthly cron (strategy review)
- **What Leo does:** Checks pipeline coverage vs targets, flags stalled deals, reviews Hindsight memory freshness
- **Output:** Weekly health report to Hunter; monthly strategy memo
- **Success criterion:** Coverage gaps and stalled deals flagged before founders notice them

---

## Part 3 — Tools & Permissions

### 3a. Tools Required

| Tool / Skill | Purpose | Required for |
|---|---|---|
| `twenty-crm` | All CRM read/write via GraphQL | All |
| `openmail` | Send/receive email via `leo-dx@openmail.sh` | C2, C4 |
| `capturing-to-gbrain` | Write entities/facts to GBrain | C3, C5 |
| `lark-im` | Send Lark messages to Hunter | C5, C6 |
| `lark-base` | Read/write task board | C5 |
| `managing-tasks` | Create tasks in Lark | C5 |
| `reviewing-tasks` | Query task board | C5 |
| `github-core-repos` | Read internal knowledge base | C6 |

### 3b. Credentials & Environment

| Service | Purpose | `.env` key |
|---|---|---|
| Twenty CRM | Pipeline read/write | `TWENTY_API_KEY` |
| OpenMail | Email send/receive | `OPENMAIL_API_TOKEN` |
| Hindsight | Pipeline bank read/write | `HINDSIGHT_BASE_URL=http://localhost:8888` |
| Lark | Send messages | `LARK_APP_ID`, `LARK_APP_SECRET` |
| GBrain | Entity lookup | Configured via MCP |

### 3c. Delivery Channels

| Channel | Purpose |
|---|---|
| Feishu DM — Hunter | Daily pipeline reminder, outreach drafts for approval |
| `[Sales] Nurturing Review` | Nurturing drafts pending human review |
| `[System] Backend Report` | Cron ops logs |

### 3d. Cron Jobs

| Job | Schedule | Purpose | Status |
|---|---|---|---|
| Daily pipeline reminder | 01:00 UTC | Surface today's tasks to Hunter | ⏸ Paused |
| Weekly health check | Monday | Pipeline coverage review | 🔧 Pending |
| Monthly nurturing run | 1st of month | Draft nurturing emails | ✅ Built |
| Inbox monitoring | Every 30min | Check for new replies | ✅ Built |

---

## Part 4 — Build Mapping

| Spec Section | Build Artifact | Location |
|---|---|---|
| Identity, mandate | `SOUL.md` — Who Leo Is | `~/.hermes/profiles/leo/SOUL.md` |
| Team positioning | `SOUL.md` — Position in the Team | `~/.hermes/profiles/leo/SOUL.md` |
| Context sources | `SOUL.md` — Knowledge Sources | `~/.hermes/profiles/leo/SOUL.md` |
| C1 | Skills: `capturing-leads`, `prospect-scouting` | `~/.hermes/profiles/leo/skills/` |
| C2 | Skills: *(to build)* | `~/.hermes/profiles/leo/skills/` |
| C3 | Skills: `enriching-accounts` | `~/.hermes/profiles/leo/skills/` |
| C4 | Skills: `nurturing-leads`, `monitoring-inbox-replies` | `~/.hermes/profiles/leo/skills/` |
| C5 | Skills: `log-engagement`, `handling-pipeline-interactions`, `sending-daily-pipeline-reminder`, `advising-on-tasks` | `~/.hermes/profiles/leo/skills/` |
| C6 | Skills: `checking-pipeline-health`, `checking-pipeline-strategy`, `ingesting-sales-strategy` | `~/.hermes/profiles/leo/skills/` |
| Credentials | Per-profile `.env` | `~/.hermes/profiles/leo/.env` |

## Spec Status

| Section | Status |
|---|---|
| Part 1 — Core Need & Positioning | ✅ Complete |
| Part 2 — Context & Data Layer | ✅ Complete |
| Part 3 — Tools & Permissions | ✅ Complete |
| GBrain content exists | ⚠️ Partial — BL files exist but need content filled in |
| Hindsight banks created | ✅ `dx-pipeline`, `dx-agent-leo` |
| SOUL.md written | ✅ `~/.hermes/profiles/leo/SOUL.md` |
| C1, C3, C4, C5, C6 skills built | ✅ |
| C2 Outbound Prospecting | 🔧 Pending build |
| BL knowledge docs filled | 📝 Needed before C3/C6 work well |
