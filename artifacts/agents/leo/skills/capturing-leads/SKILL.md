---
name: capturing-leads
description: >
  C1 Lead Capture — help the Sales Rep onboard new contacts from events, networking,
  and referrals into CRM as Leads. Handles both text descriptions and business
  card photos (native vision). Always asks about Opportunity/Partnership potential.
  Writes to CRM + Hindsight contextual memory.
triggers:
  - "剛認識了"
  - "名片"
  - "business card"
  - "幫我記錄"
  - "新聯絡人"
  - "活動認識"
  - "朋友介紹"
  - "referral"
  - "lead capture"
  - "put into CRM"
  - "存進來"
  - "展覽"
  - "event"
  - "networking"
---

# Lead Capture Skill

## Purpose

Help the Sales Rep onboard new contacts from events, networking, and referrals into CRM.
This is **C1 — the human-assisted onboarding path**. No cold email. No sequences.
These people have already been met — they enter CRM directly as `LEAD`.

The most important job: **pull everything the Sales Rep knows out of their head and into the right memory layers.**

Leo's mandatory question for every contact: **「有沒有 Opportunity 或 Partnership 要建？」**
No contact should leave Lead Capture without Leo asking this.

**This skill also covers partner capture** — when a company is not a lead but a known partner
(reseller, referral agent, angel investor, channel partner), the same 3-layer write applies:
CRM (Company + Person + Partnership) + GBrain entity page + Hindsight {{ORG_PREFIX}}-pipeline memory.
Partners skip the Lead Tier logic but still need full context written to all three layers.

---

## Two Input Modes

### Mode A — Text / Verbal Description
The Sales Rep describes the person in natural language (Chinese or English).
Leo extracts structured data, asks targeted clarifying questions, then writes.

### Mode B — Business Card Photo
The Sales Rep shares a photo. Leo reads it natively (no OCR tool needed — use model vision).
Extract: name, title, company, email, phone, any social handles visible.
Then proceed exactly as Mode A for the contextual questions.

---

## Information to Capture

### Tier 1 — Core (always required)
| Field | CRM Location | Notes |
|---|---|---|
| Name | Person.name | First + last |
| Company | Company | Create if doesn't exist |
| Job title | Person.jobTitle | |
| Email | Person.emails.primaryEmail | |
| Phone | Person.phones | |
| How we met | Person.meetContext | Event name / who introduced / occasion |
| Source type | Person.source | EVENT / REFERRAL / NETWORK / PARTNER |
| Lead Tier | Person.leadTier | PASSERBY / NURTURE / OPPORTUNITY |

### Tier 2 — Contact & Relationship (ask if not volunteered)
| Field | CRM Location | Notes |
|---|---|---|
| Preferred channel | Person.preferredChannel | LINE / WhatsApp / EMAIL etc |
| Contact handle | Person.contactHandle | LINE ID, WhatsApp number, WeChat ID |
| Country | Person.country | |
| Department | Person.department | |
| Decision role | Person.decisionRole | If relevant to an opportunity |

### Tier 3 — Contextual Memory (goes to Hindsight, not CRM fields)
These go into `{{ORG_PREFIX}}-pipeline` (if opportunity) or `{{ORG_PREFIX}}-global` (company intel):
- What did you talk about at first meeting?
- What's your read on this person — worth pursuing?
- How does their company/role connect to DX's products?
- Suggested follow-up angle or approach
- Any mutual connections or warm context

---

## Conversation Flow

### Step 1 — Extract from what the Sales Rep said
From the Sales Rep's message or photo, pull out everything already given.
Show your work immediately: present what you extracted so the Sales Rep only corrects/adds.

### Step 2 — Ask ONE targeted question
Identify the single most critical missing piece. Priority order:
1. **Lead Tier** — if not clear: 「這個人你怎麼看？過客、先存著、還是有案子要談？」
2. **Meet context** — if not stated: 「你們是在哪認識的？什麼活動或誰介紹的？」
3. **Opportunity/Partnership** — ALWAYS ask this if leadTier = NURTURE or OPPORTUNITY:
   「有沒有 Opportunity 或 Partnership 的機會要建起來？」
4. **Contact handle** — if preferredChannel is LINE/WhatsApp but no handle given

Never send a questionnaire. One question at a time.

### Step 3 — Confirm before writing
Present the full summary for the Sales Rep to approve:

```
📋 確認以下資訊存入 CRM：

**聯絡人**
- 姓名：[name]
- 公司：[company] （[existing / 新建]）
- 職稱：[title]
- 認識來源：[meetContext] — [source enum]
- 分類：[leadTier]
- 聯絡方式：[email / phone / contactHandle]

**備注（存入 Hindsight）**
[contextual summary — what was discussed, Sales Rep's read, follow-up angle]

**要建立：**
- [ ] Opportunity: [name] — [stage] （或：無）
- [ ] Partnership: [name] （或：無）
- [ ] Task: [follow-up action if any]

確認後我就存進去，有需要修改嗎？
```

### Step 4 — Write (after confirmation)

Execute in order:
1. Create or find Company
2. Create Person linked to Company
3. If Opportunity → create Opportunity (stage: NEW) linked to Person + Company
4. If Partnership → create Partnership linked to Person + Company
5. Write Hindsight memory ({{ORG_PREFIX}}-pipeline if opportunity, {{ORG_PREFIX}}-global if company intel)
6. Write GBrain timeline entry on company page
7. Create follow-up Task if needed (leadTier = NURTURE or OPPORTUNITY)

**For partners (not leads):** same 3-layer write — CRM (Company + Person + Partnership) + GBrain entity page + Hindsight. Skip Lead Tier logic. Write a full GBrain entity page (`external/entities/companies/[slug]`) for the company and (`external/entities/people/[slug]`) for the key contact. See `references/gbrain-entity-write-patterns.md` for templates.

---

## CRM Write Patterns

### Find or create Company
```graphql
# Search first
{ companies(filter: { name: { like: "%CompanyName%" } }) {
    edges { node { id name } }
} }

# If not found, create
mutation {
  createCompany(data: {
    name: "Company Name"
    domainName: { primaryLinkUrl: "https://company.com", primaryLinkLabel: "company.com" }
    city: "Taipei"
    status: LEAD
  }) { id name }
}
```

### Create Person
```graphql
mutation {
  createPerson(data: {
    name: { firstName: "John", lastName: "Doe" }
    emails: { primaryEmail: "john@example.com" }
    phones: { primaryPhoneNumber: "+886-912-345-678", primaryPhoneCountryCode: "+886" }
    jobTitle: "CEO"
    companyId: "COMPANY_UUID"
    status: LEAD
    source: EVENT
    meetContext: "Computex 2026 — Day 1 booth visit"
    contactHandle: "LINE: @johndoe"
    preferredChannel: LINE
    leadTier: NURTURE
    country: TAIWAN
    notes: "First meeting summary goes here"
  }) { id name { firstName lastName } }
}
```

### Create Opportunity (if applicable)
```graphql
mutation {
  createOpportunity(data: {
    name: "Company — Product Opportunity"
    stage: NEW
    businessLine: BUSYCOW
    dealType: DIRECT
    companyId: "COMPANY_UUID"
    pointOfContactId: "PERSON_UUID"
    overview: "Initial context from first meeting"
    currentStatusSummary: "Met at Computex. Expressed interest in X. Next: schedule demo."
    nextActionSummary: "Schedule intro demo call"
    priority: MEDIUM
    healthCheck: ON_TRACK
  }) { id name stage }
}
```

### Create follow-up Task
```graphql
mutation {
  createTask(data: {
    title: "[跟進] Company — first follow-up after Computex"
    status: TODO
    dueAt: "2026-06-20T12:00:00Z"
    bodyV2: { markdown: "Met at Computex 2026. Context: [summary]. Suggested approach: [angle]." }
  }) { id }
}
# Then link via taskTarget
mutation {
  createTaskTarget(data: {
    taskId: "TASK_UUID"
    targetPersonId: "PERSON_UUID"
  }) { id }
}
```

---

## Memory Write Patterns

### Hindsight — opportunity or nurture context
```
POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories
{
  "items": [{
    "content": "[Company] / [Person] — Met at [event], [date]. [What was discussed]. Sales Rep's read: [assessment]. Potential angle: [product/approach]. Next: [action].",
    "tags": ["lead", "[company-slug]", "[leadTier]", "lead-capture"]
  }]
}
```

**Bulk write** — multiple memories in one call (always preferred over separate calls):
```
POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories
{
  "items": [
    { "content": "...", "tags": ["..."] },
    { "content": "...", "tags": ["..."] }
  ]
}
```

### GBrain — company timeline entry
```python
mcp_gbrain_add_timeline_entry(
  slug="companies/[company-slug]",
  date="[YYYY-MM-DD]",
  summary="First contact — met at [event]",
  detail="[Person name], [title]. [Brief context of conversation]."
)
```

### GBrain — extract facts if significant intel
```python
mcp_gbrain_extract_facts(
  turn_text="[Company] is a [description]. They are interested in [topic]. Key contact: [name], [role]."
)
```

---

## Lead Tier Decision Guide

| Signal | Lead Tier |
|---|---|
| Just exchanged cards, no real conversation | PASSERBY |
| Good conversation, interesting person/company, no immediate opportunity | NURTURE |
| Mentioned a specific problem we can solve, or asked about pricing/demo | OPPORTUNITY |
| Clear partnership discussion (reseller, integration, referral) | OPPORTUNITY → also create Partnership |

**PASSERBY**: Still create Person in CRM. No Hindsight memory needed. No task.
**NURTURE**: Person + Company + Hindsight memory + follow-up task (due +2 weeks).
**OPPORTUNITY**: Person + Company + Opportunity/Partnership + full Hindsight + task (due +3 days).

---

## Partner Capture (vs Lead Capture)

When the Sales Rep is capturing a **partner** (reseller, referral agent, distributor, OEM) rather than a lead:

1. **Do NOT create a Person with `status: LEAD`** — create with `status: LEAD` still for the contact person, but the primary record is a **Partnership** object, not an Opportunity.
2. **Look up existing Company first** — partners are often already in CRM (may have a stub record with an incomplete name like "SkyDyn" instead of full legal name). Always search before creating.
3. **Partnership fields to populate:**
   - `partnerType`: RESELLER / INTEGRATOR / TECHNOLOGY / REFERRAL
   - `stage`: PROSPECT → QUALIFYING → AGREEMENT → ACTIVE → INACTIVE
   - `status`: ACTIVE / NEEDS_FOLLOWUP / DORMANT / INACTIVE
   - `partnershipOverview`: full context of the relationship
   - `currentStatusSummary`: what's happening right now
   - `nextActionSummary`: clear next step
   - `companyId`: link to company (this link is a separate mutation if not set at creation)
4. **GBrain entity page** — create `external/entities/companies/[slug]` with operating brand, legal name, what they do, and relationship context.
5. **Hindsight** — write to `{{ORG_PREFIX}}-pipeline` with partner role, gate conditions, and CRM IDs.

**Company name cleanup pattern:** If an existing stub has a partial name (e.g. "SkyDyn"), update it to the full legal name + operating brand in the same mutation that enriches other fields.



When the Sales Rep is entering multiple contacts after an event:
- Process one at a time, but keep momentum — don't ask too many questions per person
- For PASSERBY contacts: just confirm name/company/source, write immediately, no clarification needed
- For NURTURE/OPPORTUNITY: go through full flow
- After all contacts done: summarize what was created

---

## Partner Company Capture (No Contact Person Yet)

Sometimes the user describes a **partner company** without naming a specific contact person.
This happens when the relationship is established at the company level first (e.g. exclusive reseller
agreement signed, but no individual contact in CRM yet).

**Do not skip capture just because there's no person.** Follow this reduced flow:

1. **Create or update the Company** — name, domain, city/country if known
2. **Create or update the Partnership** — link to company, set: `stage`, `status`, `partnerType`,
   `partnershipOverview`, `currentStatusSummary`, `nextActionSummary`
3. **Write Hindsight** (`{{ORG_PREFIX}}-pipeline`) — capture relationship context, CRM IDs, activation gate if any
4. **Write GBrain** — `external/entities/companies/[slug]` page + timeline entry + `partner_of` link
5. **Flag in CRM** — set `currentStatusSummary` to note "No contact person captured yet"
6. When a contact person is later identified, create the Person and link via `primaryContact` on the Partnership

**Do NOT create a placeholder Person record** — empty person records pollute the CRM.
Better to leave the person slot empty and flag it in the partnership status summary.

---

## Quality Bar

Before presenting the confirmation summary (Step 3):
- `leadTier` is explicitly set and the decision rationale stated (e.g. "NURTURE because good conversation, no immediate opportunity") — not defaulted silently?
- `meetContext` is descriptive (event name + how introduced) — not just "event" or "referral"?
- Hindsight `context` field content (what was discussed, Sales Rep's read) is based on what the Sales Rep actually said — not embellished or expanded with Leo's assumptions?
- The question "有沒有 Opportunity 或 Partnership 要建？" was asked (or the answer was already clear from context) before proceeding?
- No CRM duplicate check skipped — company search always performed before creating a new Company record?
- For NURTURE/OPPORTUNITY: follow-up Task due date is set (not left open)?
- No team member names in Hindsight memory content — "the Sales Rep" or "our team" throughout?

If any check fails, fix before writing to CRM.

## Fallback Behavior

- **If CRM is unreachable**: present the confirmation summary as a structured text block; do not attempt CRM writes; offer to retry when CRM is back. Do not lose the Sales Rep's context — store it in Hindsight as a draft entry tagged "pending-crm-write".
- **If Hindsight is unreachable**: write to CRM first (primary record); note "Hindsight write failed" in the session reply; the CRM `Person.notes` and `meetContext` fields are the fallback record.
- **If GBrain is unreachable**: skip `add_timeline_entry` and `extract_facts`; note the gap; CRM + Hindsight are sufficient for lead capture.
- **If the company already exists in CRM with a partial/stub name** (e.g. "SkyDyn" instead of "SkyDynamic Co."): update the existing record rather than creating a duplicate — always confirm with the Sales Rep if name match is uncertain.
- **If `mcp_gbrain_extract_facts` returns an embedding dimension error**: skip GBrain extract; log the intel in Hindsight instead; note the GBrain failure in the session reply.
- **If the business card photo is unreadable** (blurry, poor lighting): ask the Sales Rep to type the key fields (name, company, email) — do not guess OCR results.

## Pitfalls

- **Always ask about Opportunity/Partnership** — never skip this for NURTURE or OPPORTUNITY tier contacts. This is the most important question in Lead Capture.
- **For multi-entity brain dumps** — load `references/founder-brain-dump-pattern.md` before writing anything. Audit CRM first, write in dependency order, batch via Python script for 5+ mutations.
- **Company deduplication** — always search before creating. Use `like "%name%"` search, then confirm with the Sales Rep if unsure. Stub records with partial names (e.g. "SkyDyn", "AICities") may already exist — update them rather than creating duplicates.
- **Person.notes vs Hindsight** — short factual notes (e.g. "speaks Mandarin only") go in `Person.notes`. Contextual narrative (what was discussed, Sales Rep's read) goes in Hindsight.
- **PASSERBY still gets a CRM record** — just no Hindsight memory and no task.
- **Don't ask more than one question at a time** — even in bulk mode, one question per contact.
- **leadTier drives everything downstream** — C3 Account Intelligence uses it to decide enrich depth. Set it carefully.
- **meetContext is freetext** — write naturally: "Computex 2026 Day 1 — introduced by Kevin" not just "Computex".
- **taskTarget link is separate mutation** — create Task first, then create TaskTarget linking to Person/Opportunity.
- **Company name search with `like` can miss** — if `like "%name%"` returns nothing, try listing all companies and filtering in Python.
- **Never hardcode team member names** — use "the Sales Rep", "our team", "the team" in all skill logic and Hindsight entries.
- **Partners skip Lead Tier but still get 3-layer write** — CRM Partnership + GBrain entity page + Hindsight {{ORG_PREFIX}}-pipeline. See `references/gbrain-entity-write-patterns.md` for the full template.
- **Bulk Hindsight writes** — when capturing multiple entities in one session, batch all memories into one POST with multiple items in the `items` array. Do not fire separate POSTs per entity.
