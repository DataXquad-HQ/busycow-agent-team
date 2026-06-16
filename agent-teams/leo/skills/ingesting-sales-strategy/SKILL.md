---
name: ingesting-sales-strategy
description: >
  One-time setup skill (re-run on document updates). Reads the company's
  sales-strategy.md from GitHub Wiki, extracts structured knowledge, and
  stores it into GBrain (concept pages) and Hindsight {{ORG_PREFIX}}-global (semantic
  memories). Leo reads from GBrain + Hindsight during Health Check and
  Strategy Check — never reads the source document at runtime.
triggers:
  - "ingest sales strategy"
  - "update sales strategy"
  - "load strategy document"
  - "strategy document updated"
  - "read sales strategy"
  - "update strategy document"
---

# Ingest Sales Strategy Skill

## Purpose

Read the company's `sales-strategy.md` from GitHub Wiki once, extract all
structured knowledge, and write it into the two memory layers Leo uses at
runtime. After ingest, Leo never reads the source document again until the
document is updated and ingest is re-run.

---

## Reference Files

- `templates/sales-strategy.md` — canonical document template for the company Wiki. Seven sections, fields marked required vs optional. Share this with whoever is setting up the Wiki document.

## When to Run

- **First-time setup** — when the system is first deployed
- **Document updated** — whenever `sales-strategy.md` is changed in the Wiki
- **Triggered by human** — "ingest sales strategy from [URL]"

---

## When to Use

- **First-time setup** — when the system is deployed for a new company
- **Document updated** — whenever `sales-strategy.md` changes in the Wiki
- **Human trigger:** "ingest sales strategy from [URL]", "update sales strategy", "strategy document updated"
- **Do not run** on a schedule — only on explicit human instruction or confirmed document update

---

## Inputs

| Input | How provided |
|---|---|
| Document URL | Human provides in the trigger message (GitHub Wiki raw URL) |

Example trigger:
```
"ingest sales strategy from https://raw.githubusercontent.com/[org]/[repo]/main/wiki/sales-strategy.md"
```

---

## Step 1 — Fetch the document

```python
from hermes_tools import web_extract
result = web_extract(urls=["[URL provided by human]"])
content = result["results"][0]["content"]
```

---

## Step 2 — Parse the seven sections

Extract each section by heading. Expected sections:
1. Company Overview
2. Sales Goals
3. Ideal Customer Profile (ICP)
4. Sales Strategy
5. Partnership Goals
6. Partnership Strategy
7. Pipeline Benchmarks

For each section, extract the key fields as structured data.

**Critical fields to extract:**
- `revenue_target` — total revenue target (number + currency + period)
- `revenue_period` — e.g. "FY2026", "Q3 2025"
- `new_customer_target` — number of new customers
- `typical_deal_size` — expected range
- `minimum_deal_size` — floor below which deprioritise
- `icp_industries` — list of target verticals
- `icp_company_size` — description
- `icp_geographies` — target markets
- `icp_decision_maker` — role
- `icp_pain_point` — one sentence
- `icp_green_flags` — list
- `icp_red_flags` — list
- `sales_motion` — primary motion (outbound / inbound / partner-led)
- `partner_target_count` — number of partners to sign
- `partner_types` — list
- `stage_conversion_rates` — dict {stage: rate}
- `avg_sales_cycle_days` — number
- `stall_threshold_days` — number (default 30 if not specified)

---

## Step 3 — Write to GBrain

Create or overwrite one page per concept. Use `mcp_gbrain_put_page`.

### Page: `concepts/sales-goals`
```markdown
---
type: concept
title: Sales Goals
updated: [today's date]
---

# Sales Goals

**Period:** [revenue_period]
**Revenue target:** [revenue_target]
**New customer target:** [new_customer_target]
**Typical opportunity size:** [typical_deal_size]
**Minimum opportunity size:** [minimum_deal_size]

## Breakdown by Business Line
[table or list from document, if provided]
```

### Page: `concepts/icp`
```markdown
---
type: concept
title: Ideal Customer Profile
updated: [today's date]
---

# Ideal Customer Profile

**Industries:** [icp_industries]
**Company size:** [icp_company_size]
**Geographies:** [icp_geographies]
**Decision maker:** [icp_decision_maker]
**Pain point:** [icp_pain_point]

## Green Flags
[icp_green_flags as list]

## Red Flags
[icp_red_flags as list]
```

### Page: `concepts/sales-strategy`
```markdown
---
type: concept
title: Sales Strategy
updated: [today's date]
---

# Sales Strategy

**Primary motion:** [sales_motion]

## Key Channels
[list]

## Sales Approach
[list]

## Prioritisation Rules
[list]

## What We Do NOT Do
[list]
```

### Page: `concepts/partnership-goals`
```markdown
---
type: concept
title: Partnership Goals
updated: [today's date]
---

# Partnership Goals

**Period:** [revenue_period]
**Target signed partners:** [partner_target_count]
**Partner types:** [partner_types]
**Target geographies:** [list]
**Revenue through partners (target):** [value]
```

### Page: `concepts/partnership-strategy`
```markdown
---
type: concept
title: Partnership Strategy
updated: [today's date]
---

# Partnership Strategy

## What Makes a Good Partner
[list]

## Partner Engagement Model
[description]

## Prioritisation Rules
[list]
```

### Page: `concepts/pipeline-benchmarks`
```markdown
---
type: concept
title: Pipeline Benchmarks
updated: [today's date]
---

# Pipeline Benchmarks

## Stage Conversion Rates
| Stage | Conversion Rate |
|---|---|
| NEW → SCREENING | [rate] |
| SCREENING → MEETING | [rate] |
| MEETING → PROPOSAL | [rate] |
| PROPOSAL → CUSTOMER | [rate] |

**Average sales cycle:** [avg_sales_cycle_days] days
**Stall threshold:** [stall_threshold_days] days without activity

*Source: [historical data / CRM-calculated / industry benchmark — note which]*
```

---

## Step 4 — Write to Hindsight {{ORG_PREFIX}}-global

Write one semantic memory item per section. Use natural language — these
are what Leo recalls with fuzzy queries during Health Check.

```python
import requests

items = [
    {
        "content": f"[Company] revenue target for [period] is [revenue_target]. New customer target: [N]. Typical opportunity size: [range]. Minimum: [floor].",
        "tags": ["strategy", "goals", "revenue-target"]
    },
    {
        "content": f"ICP: [icp_industries]. Target company size: [icp_company_size]. Geography: [icp_geographies]. Decision maker: [icp_decision_maker]. Pain point: [icp_pain_point]. Green flags: [list]. Red flags: [list].",
        "tags": ["strategy", "icp", "target-customer"]
    },
    {
        "content": f"Sales motion is [sales_motion]. Key channels: [list]. Prioritisation: [rules]. Do not: [list].",
        "tags": ["strategy", "sales-motion", "approach"]
    },
    {
        "content": f"Partnership goal for [period]: [partner_target_count] signed partners of type [partner_types]. Target [revenue_pct]% of revenue through partners.",
        "tags": ["strategy", "partnership", "goals"]
    },
    {
        "content": f"Good partner criteria: [list]. Engagement model: [description]. Prioritise: [rule].",
        "tags": ["strategy", "partnership", "criteria"]
    },
    {
        "content": f"Pipeline benchmarks: NEW→SCREENING [r]%, SCREENING→MEETING [r]%, MEETING→PROPOSAL [r]%, PROPOSAL→CUSTOMER [r]%. Avg cycle [N] days. Stall threshold [N] days.",
        "tags": ["strategy", "benchmarks", "conversion-rates"]
    }
]

requests.post(
    "http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-global/memories",
    json={"items": items}
)
```

---

## Step 5 — Confirm ingest to human

Report back:
```
✅ Sales Strategy ingested — [date]

**GBrain pages written:**
- concepts/sales-goals
- concepts/icp
- concepts/sales-strategy
- concepts/partnership-goals
- concepts/partnership-strategy
- concepts/pipeline-benchmarks

**Hindsight {{ORG_PREFIX}}-global:** 6 memory items stored

**Key values extracted:**
- Revenue target: [value] ([period])
- New customer target: [N]
- Stall threshold: [N] days
- Benchmarks: [PROPOSAL→CUSTOMER rate]% close rate

Leo is ready to run Pipeline Health Check and Strategy Check.
```

If any section is missing from the document, flag it:
```
⚠️ Missing sections: [list]
These sections are required for full Health Check functionality.
Ask the document owner to fill them in and re-run ingest.
```

---

## Pitfalls

- **Re-run = overwrite** — `mcp_gbrain_put_page` overwrites existing pages. This is correct behaviour on re-ingest.
- **If benchmarks are blank** — store stall threshold as 30 days (default) and note that conversion rates will be calculated from CRM data after 6+ months.
- **{{ORG_PREFIX}}-global is for company-wide decisions only** — do not store opportunity-specific or person-specific data here.
- **Never use "deal"** — always use "opportunity" in all stored content, matching the CRM object name.
