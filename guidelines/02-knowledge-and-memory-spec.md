# Knowledge & Memory Spec

> This document covers two things:
> **Architecture** — how the knowledge and memory layers work (for humans to understand).
> **Setup** — what needs to be configured before agents go live.
>
> Iris owns this wiki. Agents never write here directly.

**Last Updated:** 2026-06-17
**Version:** 2

## Changelog
| Date | Change | Reason |
|---|---|---|
| 2026-06-17 | Restructured wiki to multi-business-line model; updated GBrain slug convention | DataXquad operates multiple BLs — single-entity structure was insufficient |

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
Wiki / GitHub
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
| What happened last time with this company? | Hindsight `dx-pipeline` |
| What is our ICP / strategy for GeoKernel? | GBrain (`business-lines/geokernel/icp`) |
| What stage is this opportunity at? | Twenty CRM |
| Who is this person / company, and who knows them? | GBrain `companies/` or `people/` |
| What did the Sales Rep say their priorities are? | Hindsight `dx-human-[name]` |

---

## Architecture: Data Input, Extraction, Query & Output

### Input — How data enters the system

| Source | Trigger | Destination | Who writes |
|---|---|---|---|
| Interaction / conversation | End of every Leo session | Hindsight `dx-pipeline` bank | Leo (`log-engagement` skill) |
| New company or contact | Encountered for the first time | GBrain `companies/` or `people/` | Iris (`capturing-to-gbrain`) |
| Key decision or conclusion | After a significant decision | Wiki `decisions/` → GBrain | Iris |
| BL strategy / ICP update | After strategy changes | Wiki `business-lines/[bl]/` → GBrain | Iris |
| Market research / intel | After research is complete | Wiki `business-lines/[bl]/market.md` → GBrain | Iris |
| CRM update | Every pipeline stage change | Twenty CRM | Leo (`twenty-crm` skill) |
| Human communication patterns | Observed over time | Hindsight `dx-human-[name]` bank | Iris |

### Extraction — How raw content becomes queryable

| What gets extracted | Method | Result |
|---|---|---|
| Wiki markdown → semantic chunks | `gbrain sync` (daily cron) | GBrain vector index |
| Structured facts from conversation | `mcp_gbrain_extract_facts` | GBrain facts table |
| Key milestones | `mcp_gbrain_add_timeline_entry` | GBrain entity timeline |

### Query — How agents retrieve context before acting

| What the agent needs to know | Where to query | Method |
|---|---|---|
| Last interaction with a company | Hindsight `dx-pipeline` | `POST /recall {"query": "[Company] last interaction"}` |
| ICP for a specific BL | GBrain | `mcp_gbrain_get_page(slug="business-lines/[bl]/icp")` |
| GTM strategy for a specific BL | GBrain | `mcp_gbrain_get_page(slug="business-lines/[bl]/gtm")` |
| Company background + relationships | GBrain | `mcp_gbrain_query("[company name] background")` |
| Current opportunity stage | Twenty CRM | `twenty-crm` skill GraphQL |
| Sales Rep's communication style | Hindsight `dx-human-[name]` | `POST /recall {"query": "communication style priorities"}` |

### Output — Where results go

| Output | Destination | Trigger |
|---|---|---|
| Daily pipeline reminder | Lark `[Sales] Daily Update` | Daily cron |
| Outreach draft (pending human review) | Lark `[Sales] Nurturing Review` | Lead nurturing skill |
| Cron ops log | Lark `[System] Backend Report` | Every cron run |
| Pipeline stage update | Twenty CRM | Every stage change |
| Interaction record | Hindsight `dx-pipeline` | After every engagement |
| New milestone | GBrain timeline | After significant event |

---

## Architecture: Document Versioning

Wiki documents change over time (ICP evolves, strategy shifts). Use git for version history — do not create archive folders. Git handles it.

Every wiki document must include a Changelog section so agents understand *why* something changed, not just *what* changed:

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
  slug="business-lines/geokernel/icp",
  date="YYYY-MM-DD",
  summary="Updated ICP — removed SME segment",
  detail="ACV too low to justify BD effort. Refocusing on enterprise only."
)
```

---

## Setup: Wiki Folder Structure

```
dx-internal-wiki/
│
├── company/                         ← Cross-BL company layer
│   ├── overview.md                  ← Who we are, investment thesis
│   ├── team.md                      ← Core team, roles, org structure
│   └── portfolio.md                 ← All BLs at a glance
│
├── business-lines/                  ← One folder per business line
│   ├── geokernel/
│   │   ├── overview.md              ← What the product is
│   │   ├── strategy.md              ← Current direction, priority markets
│   │   ├── icp.md                   ← Ideal Customer Profile
│   │   ├── product.md               ← Features, selling points, objection handling
│   │   ├── gtm.md                   ← GTM motion: channels, sequences, pricing
│   │   └── market.md                ← Competitive landscape, industry trends
│   ├── aquaoptima/
│   │   └── (same structure)
│   ├── distify/
│   │   └── (same structure)
│   └── busycow/
│       └── (same structure)
│
├── agents/                          ← Agent role specs
├── systems/                         ← Tool usage guides (GBrain, Hindsight, CRM, Lark)
└── decisions/                       ← Cross-BL decision log
```

### What Goes in Each File

**`company/overview.md`** — Stable background. DataXquad's identity, fund structure, portfolio thesis.
**`company/team.md`** — Key people across all BLs.
**`company/portfolio.md`** — One-liner per BL: what it does, stage, key metric.

**`business-lines/[bl]/overview.md`** — What the product is, who it's for, why it exists.
**`business-lines/[bl]/strategy.md`** — Current direction, priority geographies, growth targets.
**`business-lines/[bl]/icp.md`** — Ideal customer: firmographics, pain, triggers, disqualifiers.
**`business-lines/[bl]/product.md`** — Features, value props, differentiators, objection handling.
**`business-lines/[bl]/gtm.md`** — Channels, outreach sequences, pricing, deal structure.
**`business-lines/[bl]/market.md`** — Competitors, market sizing, dynamics, positioning.

### GBrain Slug Convention

```
# Company layer
mcp_gbrain_get_page(slug="company/overview")
mcp_gbrain_get_page(slug="company/portfolio")

# Business line layer
mcp_gbrain_get_page(slug="business-lines/[bl]/icp")
mcp_gbrain_get_page(slug="business-lines/[bl]/strategy")
mcp_gbrain_get_page(slug="business-lines/[bl]/product")
mcp_gbrain_get_page(slug="business-lines/[bl]/gtm")
mcp_gbrain_get_page(slug="business-lines/[bl]/market")

# Cross-BL query (GBrain handles automatically)
mcp_gbrain_query("ICP for water infrastructure clients")
# → returns relevant chunks across all BLs
```

---

## Setup: Hindsight Banks

Three bank types. No more.

| Bank | Access | Purpose |
|---|---|---|
| `dx-pipeline` | read + write (all agents) | Shared — per-opportunity interaction history, blockers, what was said, agreed next steps. Tag each record with `business_line: [bl]` |
| `dx-agent-[name]` | read + write (that agent only) | Private — agent's working memory within a session |
| `dx-human-[name]` | read (agents), write (Iris only) | Human's communication style, priorities, observed patterns |

### Why No Per-BL Pipeline Banks

Pipeline bank stays shared across BLs. Each interaction record carries a `business_line` tag — agents filter at query time. Splitting into per-BL banks forces agents to know which bank to query before they know what they're looking for. Wrong design.

### Why Only Three Types

- `dx-pipeline` is shared — any agent touching a deal needs the same history
- `dx-agent-[name]` is private — working memory must not bleed between agents
- `dx-human-[name]` is agent read-only — agents observe, only Iris writes

### Creating Banks

Create all required banks before any agent goes live:
```
POST /v1/default/banks
{"id": "dx-pipeline", "name": "Pipeline Memory"}

POST /v1/default/banks
{"id": "dx-agent-leo", "name": "Leo Working Memory"}

POST /v1/default/banks
{"id": "dx-human-hunter", "name": "Hunter Profile"}

POST /v1/default/banks
{"id": "dx-human-kevin", "name": "Kevin Profile"}
```

### Registering Wiki as GBrain Source

```bash
gbrain sources add --id dx-internal-wiki --path /mnt/disks/data/dx-internal-wiki --federated true
gbrain sync --repo /mnt/disks/data/dx-internal-wiki
```

Daily sync cron (already configured):
```
Schedule: 0 20 * * *  (8PM UTC = 4AM Taiwan)
Job: dx-wiki-gbrain-sync
```
