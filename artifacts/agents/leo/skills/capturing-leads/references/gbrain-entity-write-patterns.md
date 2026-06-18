# GBrain Entity Write Patterns
*Verified via session 2026-06-17 — partner and contact capture*

Use `mcp_gbrain_put_page` to create external entity pages for companies and people.
Always pair with a timeline entry and Hindsight memory write.

---

## Company Page Template

```markdown
---
type: company
title: [Legal Name] ([Local Script if applicable])
aliases:
  - [Common name]
  - [Brand name if different]
country: [Country]
website: https://[domain]
status: active-partner | lead | prospect
tags:
  - [business-line]
  - [country]
  - [role: partner / reseller / referral-agent / investor]
---

# [Legal Name]

**Operating brand:** [if different from legal name]
**Website:** [URL]
**Legal name:** [Full legal name in local script]
**Country:** [Country]
**CRM Company ID:** [UUID]

---

## What They Do

[2–4 sentences: core business, services, market position]

---

## Relationship with {{COMPANY_NAME}}

**Role:** [Exclusive reseller / Channel partner / Referral agent / Angel investor / etc.]
**Status:** [QUALIFYING / ACTIVE / PENDING — with reason]
**Relevant business lines:** [GeoKernel / BusyCow / Distify / etc.]

[Context paragraph: how the relationship works, what they bring, what we bring]

---

## Active Opportunities

[List any CRM opportunities linked to this company, with stage and next action]

---

## Facts

[Optional — use facts fence if there are structured claims worth tracking over time]
```

**Slug pattern:** `external/entities/companies/[kebab-name-country-suffix-if-needed]`
Examples: `external/entities/companies/sky-dynamics-tw`, `external/entities/companies/taiwan-water-corporation`

---

## Person Page Template

```markdown
---
type: person
title: [Full Name]
aliases:
  - [Name variant]
country: [Country]
linkedin: https://www.linkedin.com/in/[handle]/
tags:
  - [role: angel-investor / partner / key-relationship]
  - [business-line]
---

# [Full Name]

**Title:** [Job title / Role]
**Location:** [City, Country]
**LinkedIn:** [URL]
**CRM Person ID:** [UUID]

---

## Who They Are

[2–3 sentences: background, expertise, why they matter to {{COMPANY_NAME}}]

---

## Their Companies

| Company | Role | Relevance to {{COMPANY_NAME}} |
|---|---|---|
| [Company] | [Title] | [Why it matters] |

---

## Active Opportunities via This Person

[List CRM opportunities where this person is the point of contact]

---

## Relationship Notes

[Context: how introduced, alignment of incentives, communication style, key things to know]
```

**Slug pattern:** `external/entities/people/[firstname-lastname-kebab]`
Examples: `external/entities/people/stanley-ng`, `external/entities/people/ho-li-wei`

---

## Timeline Entry (always add after writing a new entity page)

```python
mcp_gbrain_add_timeline_entry(
    slug="external/entities/companies/[slug]",
    date="YYYY-MM-DD",
    summary="[One-line milestone — e.g. 'Role upgraded to exclusive Taiwan reseller']",
    detail="[Richer context — what changed, why, what's next]",
    source="Hunter (direct, YYYY-MM-DD session)"
)
```

---

## Graph Link (add when relationship type is clear)

```python
mcp_gbrain_add_link(
    from_="external/entities/companies/[company-slug]",
    to="internal/business-lines/[bl]/gtm",
    link_type="partner_of",   # or: reseller_of, investor_in, channel_for
    link_source="manual",
    context="[one-line description of the relationship]"
)
```

---

## Hindsight Write ({{ORG_PREFIX}}-pipeline — always pair with GBrain write)

```python
POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories
{
  "items": [{
    "content": "[Company] / [Person] — [Role]. [Context]. [Current status]. [Next action]. CRM IDs: Company [UUID], Person [UUID], Partnership [UUID].",
    "tags": ["[company-slug]", "[role]", "[business-line]", "partner"]
  }]
}
```

**Bulk write pattern** — multiple memories in one call (saves tokens, atomic):
```python
{
  "items": [
    { "content": "...", "tags": ["..."] },
    { "content": "...", "tags": ["..."] },
    { "content": "...", "tags": ["..."] }
  ]
}
```

---

## Pitfalls

- **Always search CRM before creating a new company** — stub records like "SkyDyn" or "AICities" may already exist under partial names. Update the stub rather than creating a duplicate.
- **GBrain write-through** — `mcp_gbrain_put_page` with `write_through: true` writes both to the GBrain DB AND to the physical file at `[GBRAIN_VAULT]/external/entities/[path].md`. Both happen automatically — no separate file write needed.
- **Slug naming** — use kebab-case, append country suffix only when disambiguation is needed (e.g. two companies with same name in different markets).
- **Partner ≠ Lead** — partners skip `leadTier` and the PASSERBY/NURTURE/OPPORTUNITY classification. They go straight to Partnership object in CRM. But they still get full GBrain + Hindsight treatment.
- **Person page is optional for very minor contacts** — only create a GBrain person page if the individual is a key contact (decision maker, long-term relationship, angel investor). For a passing referral, CRM Person record + Hindsight mention is enough.
