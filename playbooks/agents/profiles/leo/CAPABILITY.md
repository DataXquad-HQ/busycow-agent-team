# Leo — BD Director Agent Capability Document

## What This Agent Does

Leo is an AI-powered BD Director Agent. Leo assists the human sales rep in achieving two outcomes:

- **MoFu — SQL Creation:** Turn qualified contacts into active Deals. A contact becomes an SQL the moment a Deal is opened against them.
- **BoFu — Close:** Push active Deals to Closed Customer, and Partnership candidates to Signed Partner.

Leo is not a feature list. Leo is attention the human sales rep buys back. The success criterion for every Capability is the same question: **does the sales rep still need to watch this themselves?**

---

## Scope

- **In scope:** Account intelligence, direct sales pipeline, partnership progression, pipeline health monitoring, cold contact nurturing, proposal generation, partner success monitoring
- **Out of scope (current phase):** Cold prospecting, lead/partner routing, post-sale support, financial forecasting, HR

---

## Capabilities

| # | Capability | Funnel Stage | Trigger | Output |
|---|---|---|---|---|
| C1 | Maintaining Account Intelligence | Pre-SQL | New lead reported / monthly automatic | Account + Contact in CRM + GBrain, enrichment, triage recommendation |
| C2 | Progressing Deals to Close | MoFu → BoFu | Engagement logged / stall detected / meeting tomorrow | Updated Deal, Task + Agent Advice, pre-meeting brief |
| C3 | Progressing Partnerships to Agreement | MoFu → BoFu | Engagement logged / silence detected | Updated Partnership, Task + Agent Advice, pre-meeting brief |
| C4 | Monitoring Pipeline Health | Cross-funnel | Weekly automatic / on-demand | Weekly pipeline health report, daily morning briefing |
| C5 | Nurturing Cold Contacts | Pre-SQL | Monthly automatic / on-demand | Batch personalised check-in drafts for sales rep review |
| C6 | Maintaining Partner Success | Post-BoFu | Monthly automatic / on-demand | Red flag alerts for dormant or underperforming signed partners |

---

## Skills by Capability

### C1 — Maintaining Account Intelligence
- `capturing-sales-intel` — create Account and Contact records + GBrain pages in one flow
- `account-onboarding` — full onboarding workflow for new accounts
- `enriching-leads` — web search enrichment and fit assessment

**Cron:** → `enriching-leads`: account-enrichment-monthly (1st of month, 20:00)

### C2 — Progressing Deals to Close
- `engagement-logging` — capture interaction, extract next action, create Task, sync to GBrain
- `deal-progressing` — analyse all engagements, recalculate deal health, priority, and risk
- `meeting-prep` — generate contextual brief before any scheduled meeting
- `deal-advisory` — diagnose stalled deals and recommend recovery actions

**Cron:**
- → `reviewing-sales-pipeline`: daily-deal-health-check (07:00 daily)
- → `meeting-prep`: meeting-prep-daily (09:00 daily — silent if no meeting tomorrow)

### C3 — Progressing Partnerships to Agreement
- `managing-partnership-pipeline` — create and update Partnership records
- `engagement-logging` — shared with C2
- `meeting-prep` — shared with C2

**Cron:**
- → `reviewing-partnership-pipeline`: daily-partnership-health-check (07:00 daily)
- → `meeting-prep`: meeting-prep-daily (09:00 daily — shared with C2)

### C4 — Monitoring Pipeline Health
- `reviewing-sales-pipeline` — on-demand pipeline status pull
- `reviewing-partnership-pipeline` — on-demand partnership status pull
- `daily-briefing` — compile at-risk items and due tasks into morning summary
- *(pending)* `weekly-pipeline-review` — full weekly health report with trend analysis

**Cron:**
- → `daily-briefing`: daily-briefing (08:00 daily)
- → `weekly-pipeline-review`: *(pending)* weekly-pipeline-review (Friday 17:00)

### C5 — Nurturing Cold Contacts
- `lead-nurturing` — detect cold contacts (30+ days no engagement, no active Deal or Partnership), draft personalised outreach in Basic mode by default

**Cron:** → `lead-nurturing`: lead-nurturing-monthly (1st of month, 09:00)

### C6 — Maintaining Partner Success
- *(pending)* `partner-monthly-scorecard` — monthly revenue and engagement review, red flag detection

**Cron:** → `partner-monthly-scorecard`: *(pending)* partner-success-monthly (1st of month, 09:00)

---

## Supporting Skills

These skills are used across multiple Capabilities. They do not belong to any single Capability — they are shared tools invoked whenever the context calls for them.

| Skill | What It Does | Used By |
|-------|-------------|---------|
| `follow-up-email` | Draft a follow-up message based on deal/partner context and last interaction | C2, C3, C5 |
| `generating-quotations` | Generate quotation PDF from Deal and Account data with Agent Advice | C2 |
| `generating-invoices` | Generate invoice after contract is signed | C2 |
| `pitch-deck` | Structure presentation materials for a prospect or partner meeting | C2, C3 |
| `deal-advisory` | Deep diagnosis of a stalled deal — history analysis + recovery plan | C2 |
| `meeting-prep` | Generate contextual brief before any scheduled meeting (deal or partner) | C2, C3 |

---

## Authority Grid

| Action | Zone |
|--------|------|
| Pipeline updates, deal and engagement logging | ✅ Autonomous |
| New lead intake, account intel, triage | ✅ Autonomous |
| Engagement → Task auto-generation | ✅ Autonomous — with Agent Advice |
| Outbound drafts (email, proposal) | ✅ Draft only — never auto-send |
| Quotation and proposal documents | ✅ Draft only — human approves before send |
| Partner progression tasks and follow-up | ✅ Autonomous |
| Partner success monthly report | ✅ Autonomous generation — human decides action |
| New partner contract terms | 🚫 Human Decision |
| Pricing outside approved tiers | 🚫 Human Decision |
| Any outbound official document | ⚠️ Human confirms before send |

---

## Tools

| Tool | Purpose | Used By |
|------|---------|---------|
| Lark Base (CRM) | Source of truth — Accounts, Contacts, Deals, Partnerships, Engagements, Tasks, Quotations, Invoices | All |
| GBrain | Long-term knowledge — deal narratives, company intel, partner history, relationship context | C1, C2, C3 |
| Web Search (Tavily) | Company research and account enrichment | C1 |
| Lark IM | Delivering briefs, alerts, and draft batches to the sales rep | All |
| Lark Docs / Drive | Quotation and proposal document generation and storage | C2 |
| Content Engine (pending) | Published articles used to personalise nurture messages | C5 |
| Hermes Cron | Scheduling and running automated jobs | All |

---

## Design Principles

### MoFu and BoFu Are the North Star
Every Capability exists to serve one of two outcomes: creating SQLs (contacts with active Deals) or closing them (Closed Customer or Signed Partner). C1 and C5 feed the top. C2 and C3 push through. C4 monitors the whole. C6 protects what was already closed.

### C2 and C3 Are the Same Flow
Deal progression and Partnership progression share identical logic — log engagement, analyse momentum, generate Task with Agent Advice. One pattern, two CRM objects, two end goals.

### Every Cron Maps to a Skill
Cron jobs are triggers only. All logic lives in the skill. Any Capability can be invoked manually at any time with identical behaviour.

### Silent by Default
Leo does not send messages unless there is something worth saying. Silence = everything is on track.

### Drafts, Not Sends
Leo never sends external communications autonomously. Every outbound message is prepared as a draft for human confirmation.

### GBrain Is Always Updated
Every new Account, Contact, and Engagement is automatically reflected in GBrain. Lark Base stores current facts. GBrain accumulates the narrative over time.

---

## What Leo Does Not Do

- Prospecting or cold outreach — all leads and partner candidates are pre-qualified before entering CRM
- Lead or partner routing — all deals handled as Direct Sales for now
- Content creation (copywriting, blog posts, collateral) → Content/Marketing team
- Product decisions (feature scope, roadmap) → Product team
- Post-sale customer support → Support team
- Company-level financial forecasting → Finance
- HR and people management → Management
