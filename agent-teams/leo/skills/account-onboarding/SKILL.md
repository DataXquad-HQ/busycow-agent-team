---
name: account-onboarding
description: >
  Use when the sales rep tells Leo about a new person they met — at an event,
  through an introduction, or inbound contact. Leo extracts what's known, asks
  one question to fill the most critical gap, then creates Company + Person
  records in Twenty CRM and triggers first enrichment.
  Use when user says "我認識了一個人", "met someone at the event",
  "新聯絡人", "add to CRM", or describes a new person/company they encountered.
triggers:
  - "met someone"
  - "new contact"
  - "我認識了一個人"
  - "新聯絡人"
  - "剛遇到"
  - "event contact"
  - "add to CRM"
  - "加進 CRM"
  - "onboard"
version: "4.0"
author: Leo (BD Director Agent)
---

# Account Onboarding

## Purpose

When the sales rep tells Leo about a person they met, Leo's job is to:
1. Extract everything useful from what the sales rep says
2. Ask **one targeted question** if a critical gap exists — never a questionnaire
3. Create Company + Person records in Twenty CRM
4. Run first enrichment on the company
5. Confirm the relationship type (Opportunity / Partnership / Connection)

**When to use:**
- Sales rep met someone at an event, through an introduction, or inbound contact
- Sales rep describes a new person/company in passing — even informally
- `capturing-sales-intel` identifies a new company to add

**Not triggered by:** website form submissions (those are not qualified until personally validated).

---

## CRM Reference

**Twenty CRM:** `http://localhost:3001` (always localhost — never external URL)
**GraphQL endpoint:** `http://localhost:3001/graphql`

**CRM terminology:**
| Term | Twenty object |
|---|---|
| Company | `company` |
| Person | `person` |
| Opportunity | `opportunity` |

---

## Phase 1: Extract from What the Sales Rep Said

Parse the sales rep's message for any of:

| Field | What to look for |
|---|---|
| Person's name | First name + last name |
| Person's title / role | What they do |
| Company name | English or Chinese |
| Company website / domain | If mentioned |
| Industry / what the company does | Any description |
| Country / location | Where they're based |
| How they met | Event, intro, inbound, referral |
| Relationship type hint | Are they a potential customer, partner, or just a connection? |
| Next action hint | Did the sales rep say anything like "follow up", "send proposal", "just staying in touch"? |

Map to these **critical fields** (must have before creating records):
- **Person name** — first name minimum
- **Company name** — required to create Company record
- **Something about what they do** — for enrichment and fit assessment

If all three are present: proceed to Phase 2.

If a critical field is missing: ask **one question** targeting the biggest gap:
- Missing company: "他是哪家公司的？"
- Missing company context: "這家公司主要做什麼？"
- Missing name: "這個人叫什麼名字？"

Do not ask multiple questions at once. Never run a checklist.

---

## Phase 2: Check for Existing Records

Before creating, check if Company already exists in Twenty:

```graphql
query {
  companies(filter: { name: { like: "%{company_name}%" } }) {
    edges { node { id name domainName { primaryLinkUrl } } }
  }
}
```

If found → tell the sales rep: "這家公司已經在 CRM 裡了（{name}）。幫你新增這個人到這間公司。" → skip Company creation, go to Person creation.

---

## Phase 3: Create Company Record

```graphql
mutation {
  createCompany(data: {
    name: "{company_name}"
    domainName: { primaryLinkUrl: "{website_or_empty}", primaryLinkLabel: "" }
    accountStatus: "COLD"
    accountType: ["{type}"]
    country: "{country}"
    industry: ["{industry}"]
    companyOverview: "{brief_description_from_sales_rep}"
    registeredNameEn: "{registered_name_en_if_known}"
    registeredNameCh: "{registered_name_ch_if_known}"
  }) {
    id
    name
  }
}
```

**accountType** — infer from context:
- They might buy from us → `PROSPECT`
- They could resell/partner with us → `PARTNER`
- Not clear yet → `PROSPECT` (default, can update later)

Save the returned `id` as `company_id`.

---

## Phase 4: Create Person Record

```graphql
mutation {
  createPerson(data: {
    name: { firstName: "{first}", lastName: "{last}" }
    jobTitle: "{title_if_known}"
    emails: { primaryEmail: "{email_if_known}" }
    phones: { primaryPhoneNumber: "{phone_if_known}" }
    companyId: "{company_id}"
    source: "{source}"
  }) {
    id
    name { firstName lastName }
  }
}
```

**source** — map from how they met:
| How they met | source value |
|---|---|
| Event / conference / exhibition | `EVENT` |
| Introduction / referral from someone | `REFERRAL` |
| They reached out to us | `INBOUND_WEB` |
| Partner introduced them | `PARTNER` |
| Maya's outbound | `OUTBOUND_MAYA` |

Save the returned `id` as `person_id`.

---

## Phase 5: First Enrichment

After records are created, immediately run `enriching-leads` skill:
- Input: company name, company domain (if known), Twenty company `id`
- Enrichment web-searches the domain, extracts: company overview, size estimate, industry, key facts
- Writes findings to Twenty CRM company notes (not back to user for confirmation at this stage — C1 is about speed of capture)

If no domain is known, use company name as search term.

---

## Phase 6: Create GBrain Page

```python
mcp_gbrain_put_page(
    slug=f"companies/{company_slug}",
    content="""---
type: company
title: {Company Name}
website: {website}
---

## Overview

{description_from_sales_rep_and_enrichment}

## How We Met

{how_met} — {date}

## Key People

- {person_name}, {title}

## Timeline

## Recent Insights
"""
)
```

Slug format: `companies/{slugified-name}` — e.g. "Acme Corp" → `companies/acme-corp`

---

## Phase 7: Confirm Relationship Type

Present a brief summary to the sales rep and confirm how to classify this person:

```
✅ 已加入 CRM：

公司：{Company Name}
聯絡人：{Person Name}，{Title}
類型：{accountType}
第一次認識：{how_met}

這個人目前定位為：
- **Opportunity** — 有主動銷售機會，開 Opportunity 追蹤
- **Partnership** — 潛在合作夥伴，開 Partnership 追蹤
- **Connection** — 先建立關係，暫時觀望

你希望怎麼分類？
```

Based on the sales rep's answer:
- **Opportunity** → create Opportunity record linked to this person and company
- **Partnership** → create Partnership record
- **Connection** → no additional record needed; person is in CRM and GBrain, Leo will include them in monthly C5 nurture run

---

## Verification Checklist

- [ ] Company not duplicated in Twenty before creating
- [ ] Company record created — got `id` back
- [ ] `accountStatus` = COLD (default)
- [ ] Person record created and linked to Company
- [ ] `source` field set on Person
- [ ] Enrichment triggered — company notes populated
- [ ] GBrain page created at `companies/{slug}`
- [ ] Relationship type confirmed by sales rep
- [ ] Opportunity or Partnership record created if applicable

---

## Pitfalls

1. **Always use localhost** — never the external Cloudflare URL.

2. **Never ask more than one question** — if multiple fields are missing, ask for the most critical one. More will surface naturally.

3. **`accountType` is MULTI_SELECT** — must be an array: `["PROSPECT"]` not `"PROSPECT"`.

4. **`industry` is MULTI_SELECT** — same: `["GOVERNMENT"]`.

5. **`domainName` format** — Twenty uses `{ primaryLinkUrl: "https://...", primaryLinkLabel: "" }`. If no website known, pass `{ primaryLinkUrl: "", primaryLinkLabel: "" }`.

6. **accountStatus options** — only `HOT`, `WARM`, `COLD` are valid. Default to `COLD`.

7. **Enrich even with minimal info** — if only the company name is known, still run enrichment. A domain search often turns up a website and overview.

8. **Person `source` must match enum** — valid values: `REFERRAL`, `EVENT`, `PARTNER`, `INBOUND_WEB`, `OUTBOUND_MAYA`.
