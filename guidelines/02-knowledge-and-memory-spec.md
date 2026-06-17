# Knowledge & Memory Guideline

> This document covers two things:
> **Architecture** — how the knowledge and memory layers work (for humans to understand).
> **Setup** — what needs to be configured before agents go live.
>
> Iris owns the knowledge base. Agents never write here directly.

---

## Architecture: How Information Flows

### Knowledge Flow Diagram

```
External World (people, email, web research)
         │
         ▼
    Agent / Iris receives or produces something
         │
    ┌────┴──────────────────────────┐
    ▼                               ▼
Hindsight                      Twenty CRM
"what happened"                "pipeline status"
— interaction records,         — structured objects:
  blockers, reasoning,           Opportunities, People,
  Sales Rep's read               Companies, Tasks
    │
    │ distilled into conclusions
    ▼
Knowledge Base / GitHub
"what is true now"
— ICP, strategy, product docs (per business line)
— versioned, human-readable
    │
    │ daily sync
    ▼
GBrain
"semantic index + timeline graph"
— agents query here at runtime
— vector search + entity relationships
    │
    ▼
Agent queries → executes task → outputs to Lark / CRM / Hindsight
```

### Rule of Thumb

| Question | Go to |
|---|---|
| What happened last time with this company? | Hindsight `[org]-pipeline` |
| What is our ICP / strategy for a specific BL? | GBrain (`business-lines/[bl-name]/icp`) |
| What stage is this opportunity at? | Twenty CRM |
| Who is this person / company, and who knows them? | GBrain `companies/` or `people/` |
| What did the Sales Rep say their priorities are? | Hindsight `[org]-human-[name]` |

---

## Architecture: Data Input, Extraction, Query & Output

### Input — How data enters the system

| Source | Trigger | Destination | Who writes |
|---|---|---|---|
| Interaction / conversation | End of every Leo session | Hindsight `[org]-pipeline` bank | Leo (`log-engagement` skill) |
| New company or contact | Encountered for the first time | GBrain `companies/` or `people/` | Iris (`capturing-to-gbrain`) |
| Key decision or conclusion | After a significant decision | Knowledge base `decisions/` → GBrain | Iris |
| BL strategy / ICP update | After strategy changes | Knowledge base `business-lines/[bl-name]/` → GBrain | Iris |
| Market research / intel | After research is complete | Knowledge base `business-lines/[bl-name]/market.md` → GBrain | Iris |
| CRM update | Every pipeline stage change | Twenty CRM | Leo (`twenty-crm` skill) |
| Human communication patterns | Observed over time | Hindsight `[org]-human-[name]` bank | Iris |

### Extraction — How raw content becomes queryable

| What gets extracted | Method | Result |
|---|---|---|
| Knowledge base markdown → semantic chunks | `gbrain sync` (daily cron) | GBrain vector index |
| Structured facts from conversation | `mcp_gbrain_extract_facts` | GBrain facts table |
| Key milestones | `mcp_gbrain_add_timeline_entry` | GBrain entity timeline |

### Query — How agents retrieve context before acting

| What the agent needs to know | Where to query | Method |
|---|---|---|
| Last interaction with a company | Hindsight `[org]-pipeline` | `POST /recall {"query": "[Company] last interaction"}` |
| ICP for a specific BL | GBrain | `mcp_gbrain_get_page(slug="business-lines/[bl-name]/icp")` |
| GTM strategy for a specific BL | GBrain | `mcp_gbrain_get_page(slug="business-lines/[bl-name]/gtm")` |
| Company background + relationships | GBrain | `mcp_gbrain_query("[company name] background")` |
| Current opportunity stage | Twenty CRM | `twenty-crm` skill GraphQL |
| Sales Rep's communication style | Hindsight `[org]-human-[name]` | `POST /recall {"query": "communication style priorities"}` |

### Output — Where results go

| Output | Destination | Trigger |
|---|---|---|
| Daily pipeline reminder | Lark `[Sales] Daily Update` | Daily cron |
| Outreach draft (pending human review) | Lark `[Sales] Nurturing Review` | Lead nurturing skill |
| Cron ops log | Lark `[System] Backend Report` | Every cron run |
| Pipeline stage update | Twenty CRM | Every stage change |
| Interaction record | Hindsight `[org]-pipeline` | After every engagement |
| New milestone | GBrain timeline | After significant event |

---

## Architecture: Document Versioning

Wiki documents change over time (ICP evolves, strategy shifts). Use git for version history — do not create archive folders. Git handles it.

Every knowledge base document must include a Changelog section so agents understand *why* something changed, not just *what* changed:

```markdown
**Last Updated:** YYYY-MM-DD
**Version:** N

## Changelog
| Date | Change | Reason |
|---|---|---|
| YYYY-MM-DD | | |
```

After a significant update, also add a GBrain timeline entry:
```
mcp_gbrain_add_timeline_entry(
  slug="business-lines/[bl-name]/icp",
  date="YYYY-MM-DD",
  summary="Updated ICP — removed SME segment",
  detail="ACV too low to justify BD effort. Refocusing on enterprise only."
)
```

---

## Setup: Knowledge Base Folder Structure

```
[org]-internal-kb/
│
├── company/                         ← Cross-BL company layer
│   ├── overview.md                  ← Who you are, what you do
│   ├── team.md                      ← Core team, roles, org structure
│   └── portfolio.md                 ← All BLs at a glance
│
├── business-lines/                  ← One folder per business line
│   ├── [bl-name]/
│   │   ├── overview.md              ← What the product is
│   │   ├── strategy.md              ← Current direction, priority markets
│   │   ├── icp.md                   ← Ideal Customer Profile
│   │   ├── product.md               ← Features, selling points, objection handling
│   │   ├── gtm.md                   ← GTM motion: channels, sequences, pricing
│   │   └── market.md                ← Competitive landscape, industry trends
│   └── [bl-name]/
│       └── (same structure)
│
├── agents/                          ← Agent role specs
├── systems/                         ← Tool usage guides (GBrain, Hindsight, CRM, Lark)
└── decisions/                       ← Cross-BL decision log
```

### What Goes in Each File

**`company/overview.md`** — Stable background. Company identity, founding story, what you do.
**`company/team.md`** — Key people across all BLs.
**`company/portfolio.md`** — One-liner per BL: what it does, stage, key metric.

**`business-lines/[bl-name]/overview.md`** — What the product is, who it's for, why it exists.
**`business-lines/[bl-name]/strategy.md`** — Current direction, priority geographies, growth targets.
**`business-lines/[bl-name]/icp.md`** — Ideal customer: firmographics, pain, triggers, disqualifiers.
**`business-lines/[bl-name]/product.md`** — Features, value props, differentiators, objection handling.
**`business-lines/[bl-name]/gtm.md`** — Channels, outreach sequences, pricing, deal structure.
**`business-lines/[bl-name]/market.md`** — Competitors, market sizing, dynamics, positioning.

### GBrain Slug Convention

```
# Company layer
mcp_gbrain_get_page(slug="company/overview")
mcp_gbrain_get_page(slug="company/portfolio")

# Business line layer
mcp_gbrain_get_page(slug="business-lines/[bl-name]/icp")
mcp_gbrain_get_page(slug="business-lines/[bl-name]/strategy")
mcp_gbrain_get_page(slug="business-lines/[bl-name]/product")
mcp_gbrain_get_page(slug="business-lines/[bl-name]/gtm")
mcp_gbrain_get_page(slug="business-lines/[bl-name]/market")

# Cross-BL query (GBrain handles automatically)
mcp_gbrain_query("ICP for [industry] clients")
# → returns relevant chunks across all BLs
```

---

## Setup: Hindsight Banks

Three bank types. No more.

| Bank | Access | Purpose |
|---|---|---|
| `[org]-pipeline` | read + write (all agents) | Shared — per-opportunity interaction history, blockers, what was said, agreed next steps. Tag each record with `business_line: [bl-name]` |
| `[org]-agent-[name]` | read + write (that agent only) | Private — agent's working memory within a session |
| `[org]-human-[name]` | read (agents), write (Iris only) | Human's communication style, priorities, observed patterns |

### Why No Per-BL Pipeline Banks

Pipeline bank stays shared across BLs. Each interaction record carries a `business_line` tag — agents filter at query time. Splitting into per-BL banks forces agents to know which bank to query before they know what they're looking for. Wrong design.

### Why Only Three Types

- `[org]-pipeline` is shared — any agent touching a deal needs the same history
- `[org]-agent-[name]` is private — working memory must not bleed between agents
- `[org]-human-[name]` is agent read-only — agents observe, only Iris writes

### Creating Banks

Create all required banks before any agent goes live:
```
POST /v1/default/banks
{"id": "[org]-pipeline", "name": "Pipeline Memory"}

POST /v1/default/banks
{"id": "[org]-agent-leo", "name": "Leo Working Memory"}

POST /v1/default/banks
{"id": "[org]-human-[founder-1]", "name": "[Founder 1] Profile"}

POST /v1/default/banks
{"id": "[org]-human-[founder-2]", "name": "[Founder 2] Profile"}
```

### Registering Knowledge Base as GBrain Source

```bash
gbrain sources add --id [org]-internal-kb --path /path/to/kb-repo --federated true
gbrain sync --repo /path/to/kb-repo
```

Set up a daily sync cron after registration to keep GBrain in sync with knowledge base changes.
