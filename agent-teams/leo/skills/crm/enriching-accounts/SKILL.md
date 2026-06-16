---
name: enriching-accounts
description: >
  C3 Account Intelligence — enrich company and contact context for Leads in CRM.
  Two modes: Level 1 (triggered after new Lead is created — foundational company
  profile) and Level 2 (monthly automated update — news, blog, recent developments).
  Skips PASSERBY contacts. Writes to CRM, Hindsight dx-pipeline, and GBrain.
triggers:
  - "enrich"
  - "account intelligence"
  - "公司資料"
  - "補資料"
  - "研究一下"
  - "background on"
  - "tell me about this company"
  - "幫我查"
  - "company intel"
  - "enrichment"
  - "account update"
  - "monthly update"
  - "C3"
---

# Account Intelligence Skill

## Purpose

Keep our understanding of accounts and contacts continuously updated.
The more comprehensive data we have, the more value we can extract through analysis
and the better we can customise each engagement.

**Two modes, one skill:**
- **Level 1 — Foundational Enrich**: triggered after a new Lead is created. Builds the base profile.
- **Level 2 — Monthly Update**: automated monthly run. Keeps intelligence fresh with news and developments.

**Scope:**
- Enrich at **company level** (primary) + person LinkedIn background (secondary)
- Skip `leadTier = PASSERBY` — not worth the cost
- Run on `NURTURE` and `OPPORTUNITY` tier contacts

---

## Cron Delivery

Monthly cron `deliver` → `[System] Backend Report` (`oc_8c3706de744958173c700d995ccfd4ef`).
If significant findings affect active opportunities, push a brief alert to `[Sales] Daily Update` (`oc_a5e03bcb6026a81a5a330b53c4e90575`) mid-run.

**CRM links in Lark messages always use:** `https://sales.dataxquad.com/objects/[type]/[UUID]`
Never use `localhost:3001` in any human-facing output.

---

## When to Run Which Level

| Trigger | Level | Scope |
|---|---|---|
| New Lead just created (manual trigger by the Sales Rep) | Level 1 | Single company |
| Sales Rep asks「幫我查一下 [company]」| Level 1 | Single company |
| Monthly cron (auto) | Level 2 | All active companies with NURTURE/OPPORTUNITY people |
| the Sales Rep asks for latest news on a company | Level 2 | Single company |

---

## Level 1 — Foundational Enrich

### Goal
Build the base company profile so Leo has enough context to personalise outreach,
prepare for meetings, and make scouting decisions.

### Sources to check (in order)
1. Company website (homepage + About page)
2. Company LinkedIn page
3. Google News — last 3 months, 2–3 headlines max

### What to extract

**Company profile:**
- Full company name (registered if different from brand name)
- Website URL
- Business description — what do they do, who do they serve
- Industry / sector
- Company size (headcount range)
- Geography — HQ + key markets
- Key products or services

**Relevance to DX:**
- Which DX business line(s) could this company use?
- What's the most likely pain point or use case?
- ICP fit assessment (check `wiki/dx-icp` if exists)

**Key contacts (from CRM):**
- For each Person linked to this company with leadTier ≠ PASSERBY:
  - Confirm/update job title
  - Note seniority and decision role if inferable

### What to write

**CRM — Company:**
```graphql
mutation {
  updateCompany(id: "COMPANY_UUID", data: {
    domainName: { primaryLinkUrl: "https://company.com", primaryLinkLabel: "company.com" }
    companyOverview: "[2–3 sentence plain description of what the company does]"
    enrichmentOverview: "[DX relevance: which business line, likely use case, ICP fit]"
    industry: INDUSTRY_ENUM
    lastEnrichedDate: "2026-06-15T00:00:00Z"
  }) { id name }
}
```

**Hindsight — dx-pipeline (if OPPORTUNITY tier) or dx-global (company intel):**
```
POST http://localhost:8888/v1/default/banks/dx-pipeline/memories
{
  "items": [{
    "content": "[Company] — L1 enrich [date]. [Business description]. DX fit: [business line + use case]. Key contacts: [names/roles]. Source: [website/LinkedIn].",
    "tags": ["enrich", "level1", "[company-slug]", "account-intelligence"]
  }]
}
```

**GBrain — company page:**
```python
# Update or create company page
mcp_gbrain_put_page(
  slug="companies/[company-slug]",
  content="""---
type: company
name: [Company Name]
website: [URL]
industry: [industry]
size: [headcount range]
hq: [city, country]
---

# [Company Name]

[Business description — 2–3 sentences]

## DX Relevance
[Which business line, why, likely use case]

## Key Contacts
[List people in CRM linked to this company]
"""
)

# Timeline entry
mcp_gbrain_add_timeline_entry(
  slug="companies/[company-slug]",
  date="[YYYY-MM-DD]",
  summary="L1 enrich completed",
  detail="Foundational profile built. DX fit: [business line]."
)
```

---

## Level 2 — Monthly Update

### Goal
Keep intel fresh. Catch major developments before they become missed opportunities:
new funding, product launches, leadership changes, expansions, pain points surfacing publicly.

### Sources to check (in order)
1. Company blog / news page (if exists)
2. Google News — company name, last 30 days
3. LinkedIn company page — recent posts
4. (If OPPORTUNITY tier) — any updates on key contacts (LinkedIn activity)

### What to look for
- Funding rounds or M&A activity
- New product launches or pivots
- Leadership changes (new CxO, department heads)
- Geographic expansion
- Public pain points (layoffs, operational issues, complaints)
- Awards, certifications, tenders won
- Any mention of competitors or relevant technology

### Significance filter
Not everything needs to be written. Only log if:
- **Significant**: funding, acquisition, major launch, leadership change → write to Hindsight + GBrain timeline
- **Interesting**: minor news, blog post about a relevant topic → write brief note to Hindsight only
- **Noise**: PR fluff, award mentions with no substance → skip

### What to write

**CRM — Company:**
```graphql
mutation {
  updateCompany(id: "COMPANY_UUID", data: {
    lastEnrichedDate: "2026-06-15T00:00:00Z"
    enrichmentOverview: "[Updated DX relevance note if changed]"
  }) { id name }
}
```

**Hindsight — dx-pipeline:**
```
POST http://localhost:8888/v1/default/banks/dx-pipeline/memories
{
  "items": [{
    "content": "[Company] — L2 update [date]. [Summary of significant finding]. Implication for DX: [so what]. Source: [URL].",
    "tags": ["enrich", "level2", "[company-slug]", "account-intelligence", "[month-year]"]
  }]
}
```

**GBrain — timeline entry (significant findings only):**
```python
mcp_gbrain_add_timeline_entry(
  slug="companies/[company-slug]",
  date="[YYYY-MM-DD]",
  summary="[One-line milestone — e.g. 'Raised Series B $20M']",
  detail="[Brief detail + DX implication]",
  source="[URL]"
)
```

---

## Monthly Cron Scope

When running as monthly automation, the cron:
1. Lists all companies in CRM that have at least one person with `leadTier` = NURTURE or OPPORTUNITY
2. For each company, runs Level 2 update
3. Delivers a summary report to Lark `[DX] Sales Daily Update`

### Getting the target company list
```graphql
{
  people(filter: { leadTier: { in: [NURTURE, OPPORTUNITY] } }) {
    edges { node {
      company { id name lastEnrichedDate }
      leadTier
    }}
  }
}
```

Deduplicate by company ID. Skip if `lastEnrichedDate` is within last 25 days (already updated this month).

### Monthly summary report format
```
📊 **Account Intelligence — Monthly Update**
[Month Year]

**Updated: [N] companies**

🔴 Significant findings:
- [Company]: [one-line finding]
- [Company]: [one-line finding]

🟡 Minor updates:
- [Company]: [brief note]

⚪ No changes: [Company], [Company], ...

Total active accounts monitored: [N]
```

---

## Enrichment Depth by Lead Tier

| leadTier | Level 1 | Level 2 (monthly) | Notes |
|---|---|---|---|
| PASSERBY | ❌ Skip | ❌ Skip | Not worth the cost |
| NURTURE | ✅ Run | ✅ Run | Standard depth |
| OPPORTUNITY | ✅ Run | ✅ Run | Full depth — also check key contacts |

---

## Knowledge Context to Load First

Before assessing DX fit for any company, check:
```python
mcp_gbrain_get_page(slug="wiki/dx-icp")           # ICP definition
mcp_gbrain_get_page(slug="wiki/dx-sales-strategy") # Sales strategy
mcp_gbrain_get_page(slug="wiki/products/[line]")   # Relevant product wiki
```
If pages don't exist: continue, infer from known opportunity patterns, flag ⚠️ in output.

---

## Output to Sales Rep (manual trigger)

When triggered manually, always show the Sales Rep a summary of what was found and written:

```
🔍 **Account Intelligence — [Company Name]**
Level [1/2] | [Date]

**Company Profile**
[2–3 sentence overview]

**DX Fit**
Business line: [line]
Use case: [description]
ICP fit: [strong / moderate / weak / unknown — no ICP doc]

**Key Findings** (Level 2 only)
- [Finding 1]
- [Finding 2]

**Written to:**
- ✅ CRM: companyOverview + enrichmentOverview updated
- ✅ Hindsight: dx-pipeline memory stored
- ✅ GBrain: [company-slug] page updated + timeline entry added

[⚠️ No ICP document found — fit assessed from opportunity history. Consider building `wiki/dx-icp`.]
```

---

## Pitfalls

- **Always check leadTier before running** — query the company's linked people and confirm at least one is NURTURE or OPPORTUNITY. If all are PASSERBY, skip entirely.
- **Don't overwrite good existing data** — before updating `companyOverview`, read the current value. If it's already detailed, append/improve rather than replace.
- **lastEnrichedDate is the freshness gate** — always set it after enrichment. Monthly cron uses it to avoid redundant re-runs.
- **Web search quality varies** — if web_search returns thin results, try web_extract on the company homepage directly. LinkedIn pages often have the clearest company descriptions.
- **GBrain slug naming** — use lowercase hyphenated company name: `companies/acme-corp`, not `companies/Acme Corp`. Fuzzy match on get_page helps if slug is unknown.
- **Hindsight bank choice** — OPPORTUNITY companies → `dx-pipeline`. General company intel with no active opportunity → `dx-global`.
- **Level 2 significance filter is important** — don't flood Hindsight with noise. If in doubt, ask: "would the Sales Rep want to know this before their next call with this company?" If no, skip.
- **Monthly cron dedup** — check `lastEnrichedDate` to avoid running twice in one month. Threshold: 25 days (not 30, to handle calendar variation).
