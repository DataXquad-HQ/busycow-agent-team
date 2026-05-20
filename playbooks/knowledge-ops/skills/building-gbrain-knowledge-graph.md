---
name: building-gbrain-knowledge-graph
description: >
  Use when GBrain brain score is low (<60), orphan count is high, or user wants to
  enrich the knowledge graph with people, companies, and relationships. Covers the
  full workflow: create entity pages → add works_at / has_member links → connect
  domain pages (market, competitors, opportunities) → verify with doctor + find_orphans.
triggers:
  - "brain score low"
  - "orphan pages"
  - "gbrain graph"
  - "add people to gbrain"
  - "連結 gbrain"
  - "knowledge graph"
---

# Building the GBrain Knowledge Graph

## Purpose
GBrain brain score is driven by graph density — pages with no inbound links are "orphans"
and heavily penalise the score. This skill covers the systematic process to go from
a sparse disconnected brain (score ~45) to a connected one (score 70+).

## The Core Insight
**Links must be bidirectional to remove orphans.**
- A page is only non-orphan if something *links TO it* (inbound link).
- `person → works_at → company` alone does NOT make the person non-orphan.
- Must also add `company → has_member → person` for the person to have an inbound link.

## Step 1: Diagnose

```
mcp_gbrain_run_doctor        # check brain_score and health_score
mcp_gbrain_find_orphans      # list all orphan pages
mcp_gbrain_list_pages        # see what entity pages exist
```

Categorise orphans into buckets:
- **People** — need works_at + has_member links
- **Companies** — need subsidiary_of / has_member links
- **Market/intel** — need targets_market / part_of links
- **Competitors** — need has_competitor links from product pages
- **Opportunities** — need belongs_to + involves links
- **System pages** (hermes-memory, decisions, readme) — acceptable as orphans, skip

---

## Step 2: Build Entity Pages

### People page template
```markdown
---
title: "Full Name"
type: person
created: "YYYY-MM-DD"
tags: [role, company-slug, team]
---

# Full Name

**Role:** Title — [[company/slug]]
**Timezone:** UTC+8 (Taiwan)

## RACI Map
| Domain | RACI |
...

## Contact
- Email: name@yourcompany.com

## Affiliations
- [[company/slug]] — Role & Title
- [[busycow/dataxquad]] — Portfolio founder (if applicable)
```

### Slug conventions
- People: `people/firstname-lastname` (lowercase, hyphenated)
- Companies: `busycow/companyname` for BusyCow portfolio, `partners/name` for partners, `clients/name` for clients
- Opportunities: `opportunities/slug-YYYY`

---

## Step 3: Add Links (People ↔ Companies)

For each person, add BOTH directions:

```python
# Direction 1: person → company (person has inbound from company)
mcp_gbrain_add_link(from="people/name", link_type="works_at", to="company/slug")

# Direction 2: company → person (person gets inbound link → removes orphan status)
mcp_gbrain_add_link(from="company/slug", link_type="has_member", to="people/name")
```

**Link types used:**
| Relationship | link_type |
|---|---|
| Person works at company | `works_at` |
| Company has team member | `has_member` |
| Company is portfolio of parent | `subsidiary_of` |
| Document/analysis belongs to entity | `belongs_to` |
| Product targets a market segment | `targets_market` |
| Product has a competitor | `has_competitor` |
| Market signal is part of timeline | `part_of` |
| Opportunity involves a person | `involves` |
| Partner/reseller relationship | `partner_of` |
| Entity manages another | `managed_by` |

---

## Step 4: Connect Domain Pages

### Market pages → product pages
```
busycow/busycow → targets_market → market/hong-kong-sme
busycow/busycow → targets_market → market/sme-taiwan
busycow/aquaoptima → targets_market → market/taiwan-water-utilities  (if exists)
```

### Competitor pages → product pages
```
busycow/busycow → has_competitor → competitors/make-com
busycow/busycow → has_competitor → competitors/zapier-agents
busycow/busycow → has_competitor → competitors/salesforce
busycow/busycow → has_competitor → competitors/bytedance-coze
```

### Intel/market-signals pages
```
intel/market-signals/YYYY-MM-DD → part_of → intel/market-signals/timeline
intel/market-signals/timeline → belongs_to → busycow/busycow
```

### Opportunity pages
```
opportunities/slug → belongs_to → company/slug
opportunities/slug → involves → people/slug
```

### System/tool pages
```
busycow-task-tracker → belongs_to → busycow/dataxquad
busycow-invoice-quotation-base → belongs_to → busycow/dataxquad
busycow-intelligence-system → belongs_to → busycow/busycow
```

---

## Step 5: Verify Progress

```
mcp_gbrain_run_doctor     # health_score should be ≥95, brain_score ≥70
mcp_gbrain_find_orphans   # total_orphans should be <15
```

### Score benchmarks (51 pages)
| Brain Score | State |
|---|---|
| 45 | All pages orphan, no links |
| 55–60 | Core people linked, companies connected |
| 70–80 | Market/competitor/opportunity pages linked |
| 80+ | Content enriched (takes, timeline entries) |

---

## Pitfalls

- **`add_link` is one-directional** — GBrain does NOT auto-create reverse links. Always add both directions manually for people ↔ company relationships.
- **Brain score won't update until doctor is re-run** — call `mcp_gbrain_run_doctor` after batching links.
- **Dream/sync doesn't create graph links** — links must be added via `mcp_gbrain_add_link`, not written into markdown (auto_link is disabled for remote MCP callers).
- **System pages (hermes-memory/*, decisions/*, readme) are acceptable orphans** — do not waste time linking log/system pages.
- **Orphan count includes newly added pages** — 3 new person pages always start as orphans until bidirectional links are added.
- **Score plateau at 79** — beyond 79 requires content enrichment: facts, takes, timeline entries on entity pages, not just more links.

## BusyCow-specific entity map (as of May 2026)

### Companies
- `busycow/dataxquad` — parent company
- `busycow/aquaoptima` — water AI, Taiwan/SEA
- `busycow/busycow` — SME AI agent platform, HK/TW
- `busycow/geokernel` — emergency geospatial / drone
- `busycow/traci` — stealth portfolio company
- `projects/distify` — separate Singapore entity, robot distribution

### Core team
- `people/hunter-lin` → works_at dataxquad, busycow, distify
- `people/kevin-chan` → works_at dataxquad, busycow, aquaoptima
- `people/morris-chou` → works_at aquaoptima, dataxquad (CEO [your product])
- `people/chun-er` → works_at aquaoptima, dataxquad (CPO [your product])
- `people/deng-seng` → works_at aquaoptima, dataxquad (Lead Engineer)
