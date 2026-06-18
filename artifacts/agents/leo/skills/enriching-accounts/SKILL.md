---
name: enriching-accounts
description: >
  C3 Account Intelligence — enrich company and contact context for Leads in CRM.
  Two modes: Level 1 (triggered after new Lead is created — foundational company
  profile) and Level 2 (monthly automated update — news, blog, recent developments).
  Skips PASSERBY contacts. Writes to CRM, Hindsight {{ORG_PREFIX}}-pipeline, and GBrain.
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

Monthly cron `deliver` → `[System] Backend Report` (`{{SYSTEM_BACKEND_CHANNEL_ID}}`).
If significant findings affect active opportunities, push a brief alert to `[Sales] Daily Update` (`{{SALES_DAILY_UPDATE_CHANNEL_ID}}`) mid-run.

**CRM links in Lark messages always use:** `{{CRM_EXTERNAL_URL}}/objects/[type]/[UUID]`
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
- ICP fit assessment (check `internal/business-lines/[BL]/icp` if exists)

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

**Hindsight — {{ORG_PREFIX}}-pipeline (if OPPORTUNITY tier) or {{ORG_PREFIX}}-global (company intel):**
```
POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories
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
  slug="external/entities/companies/[company-slug]",
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
  slug="external/entities/companies/[company-slug]",
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

**Hindsight — {{ORG_PREFIX}}-pipeline:**
```
POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories
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
  slug="external/entities/companies/[company-slug]",
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
mcp_gbrain_get_page(slug="internal/business-lines/[BL]/icp")           # ICP definition
mcp_gbrain_get_page(slug="internal/business-lines/[BL]/strategy") # Sales strategy
mcp_gbrain_get_page(slug="internal/business-lines/[BL]/product")   # Relevant product wiki
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
- ✅ Hindsight: {{ORG_PREFIX}}-pipeline memory stored
- ✅ GBrain: [company-slug] page updated + timeline entry added

[⚠️ No ICP document found — fit assessed from opportunity history. Consider building `internal/business-lines/[BL]/icp`.]
```

---

## Partner Entity Enrichment (No Contact Person in CRM)

When enriching a **partner company** that has no individual contact person yet:
- Run Level 1 (foundational profile) regardless — the company record needs context
- Skip Person-level enrichment entirely — don't look up individuals if no one is in CRM
- In `enrichmentOverview`, note: "Partner company — no contact person captured yet"
- Write Hindsight to `{{ORG_PREFIX}}-pipeline` (not `{{ORG_PREFIX}}-global`) if the partner is linked to an active opportunity/GeoKernel pipeline
- Set GBrain slug under `external/entities/external/entities/companies/[slug]` (not `external/entities/companies/[slug]`) for external entities

**Activation gate pattern:** When a partner's engagement is gated on a product milestone
(e.g. "will promote once AI features are confirmed working"), capture the gate explicitly in:
- CRM `currentStatusSummary`
- CRM `nextActionSummary` (what needs to happen to unblock)
- Hindsight memory tags (tag with the gate condition, e.g. `ai-feature-gate`)
- GBrain facts table in the company page

---

## Quality Bar

Before writing to CRM, Hindsight, or GBrain:
- DX fit assessment (business line + use case) based on explicit product knowledge or confirmed opportunity patterns — not a guess from the company name alone?
- ICP fit rating (strong/moderate/weak) traceable to specific ICP criteria (industry, size, geography, problem)? If ICP document is missing, label clearly as "Estimated from opportunity history — no ICP document"?
- News items from Level 2 pass the significance filter — are they "would the Sales Rep want to know this before their next call?" level? Noise excluded?
- `enrichmentOverview` in CRM is an update or improvement of existing content — not an overwrite of more detailed prior data with something shorter?
- `lastEnrichedDate` is set — otherwise next monthly cron will redundantly re-run within the same month?
- Any finding that changes the DX opportunity assessment is flagged for the Sales Rep — not silently stored in Hindsight only?

If any check fails, revise before writing.

## Fallback Behavior

- **If web search returns thin or no results**: try `web_extract` on the company homepage directly; if that also fails, note "Web research returned no results for [Company] on [date]" in the CRM `enrichmentOverview` and Hindsight. Do not fabricate findings.
- **If GBrain is unreachable**: write to CRM and Hindsight only; skip the GBrain page update and timeline entry; note the gap — "GBrain update skipped (unavailable)." The CRM `enrichmentOverview` is the fallback record.
- **If Hindsight is unreachable**: write to CRM and GBrain only; note the gap in the output report. The CRM remains the primary record.
- **If the GBrain ICP page (`internal/business-lines/[BL]/icp` or `internal/business-lines/[bl]/icp`) is missing**: proceed using known opportunity patterns to infer fit; label the assessment as "⚠️ No ICP document — fit estimated from opportunity history"; flag the missing page in the output.
- **If CRM `enrichmentOverview` or `companyOverview` already contains richer detail than the new web research**: do not overwrite with shorter content; append as a new section labelled "[Date] update: [finding]".
- **If `lastEnrichedDate` is missing on the company record** (field not set yet): treat as never enriched — proceed with full Level 1 enrichment.

## Pitfalls

- **Always check leadTier before running** — query the company's linked people and confirm at least one is NURTURE or OPPORTUNITY. If all are PASSERBY, skip entirely.
- **Don't overwrite good existing data** — before updating `companyOverview`, read the current value. If it's already detailed, append/improve rather than replace.
- **lastEnrichedDate is the freshness gate** — always set it after enrichment. Monthly cron uses it to avoid redundant re-runs.
- **Web search quality varies** — if web_search returns thin results, try web_extract on the company homepage directly. LinkedIn pages often have the clearest company descriptions.
- **GBrain slug naming** — use lowercase hyphenated company name: `external/entities/companies/acme-corp`, not `companies/Acme Corp`. Fuzzy match on get_page helps if slug is unknown.
- **Hindsight bank choice** — OPPORTUNITY companies → `{{ORG_PREFIX}}-pipeline`. General company intel with no active opportunity → `{{ORG_PREFIX}}-global`.
- **Level 2 significance filter is important** — don't flood Hindsight with noise. If in doubt, ask: "would the Sales Rep want to know this before their next call with this company?" If no, skip.
- **Monthly cron dedup** — check `lastEnrichedDate` to avoid running twice in one month. Threshold: 25 days (not 30, to handle calendar variation).
