---
name: log-engagement
description: >
  Log a completed interaction (meeting, call, email, demo) into Twenty CRM as an
  Engagement record linked to a Person, and optionally to an Opportunity or
  Partnership. Updates opportunity fields and creates follow-up Tasks when an opportunity is
  involved. Works at three levels: Person-only (Lead Nurturing), opportunity-level
  (Opportunity / Partnership progressing).
triggers:
  - "log this interaction"
  - "update the opportunity"
  - "we had a meeting with"
  - "talked to the client"
  - "just got off a call"
  - "update opportunity"
  - "update partnership"
  - "開完會了"
  - "剛跟他們通過電話"
  - "跟進"
  - "log engagement"
  - "sent an email to"
  - "發了信給"
version: "2.0"
author: DataXquad/Leo
---

# Log Engagement

## When to Use

Use when a Sales Rep reports a completed interaction — meeting, call, email, or demo — and the engagement needs to be recorded in CRM. Covers three levels: Person-only (lead nurturing contact), Opportunity-level (active sales opportunity), and Partnership-level (partner relationship).

> An Engagement is a completed, factual record of something that happened.
> It either exists (happened) or it doesn't — no status, no pending states.
> **Confirm before writing. Never go straight to CRM.**

---

## Purpose

Convert a Sales Rep's raw update into structured CRM records. Works at three levels:

| Level | When | Links to |
|---|---|---|
| **Person-only** | Nurturing email sent, casual check-in, no active opportunity | Person + Company |
| **Opportunity (Opportunity)** | Meeting, call, demo tied to an active Opportunity | Person + Company + Opportunity |
| **Opportunity (Partnership)** | Interaction tied to an active Partnership | Person + Company + Partnership |

Opportunity and Partnership are always **optional**. Person is always **required**.

For each level, create an **Engagement** record (not a Note) — Engagement is the correct CRM object for interactions. Notes are for free-form annotations only.

---

## The Two Objects

Same flow. Different silence thresholds.

| Object | Parent | Silence threshold | End state |
|---|---|---|---|
| Opportunity | C4 | 7 days → `AT_RISK` | CUSTOMER |
| Partnership | C5 | 14 days → `AT_RISK` | Signed Partner |

---

## Step-by-Step Flow

### Step 0 — Recall Context (before doing anything)

Before extracting or writing anything, recall what Leo already knows about this opportunity:

```
POST /v1/default/banks/dx-pipeline/memories/recall
{"query": "[Company name] opportunity — background, blockers, last interaction", "top_k": 5}
```

Also recall Hunter's current priorities if this is a sensitive or high-stakes opportunity:
```
POST /v1/default/banks/dx-human-hunter/memories/recall
{"query": "priorities and communication style", "top_k": 3}
```

Use what you recall to:
- Frame your extraction questions better
- Surface relevant context when confirming with Hunter
- Spot if the new update contradicts or changes something previously noted

---

### Step 1 — Extract

From the raw input, extract:
- **What happened** — narrative summary
- **Outcome / decision / signal** — what was the result
- **Agreed next action** — if any; who owns it, by when
- **New intel** — budget signals, decision-maker revealed, competitor mentioned, timeline shift

### Step 2 — Confirm

Present extracted summary to Sales Rep:

> 「這樣記對嗎？
> **互動類型：** [Meeting / Call / Email / Demo / …]
> **日期：** [date]
> **結果：** [outcome]
> **下一步：** [next action — owner + deadline]
> **補充說明：** [narrative context]
>
> 有什麼要補充或修正的？」

**Do NOT write to CRM until confirmed (or Sales Rep explicitly skips).**

### Step 3 — Write Engagement record

Create an **Engagement** object (not a Note) linked to the Person, and optionally to Opportunity or Partnership.

```graphql
mutation {
  createEngagement(data: {
    name: "[Type] — [Company] — [date]"
    engagementType: EMAIL          # PHONE | INPERSON | ONLINE | MESSAGING | DEMO | EMAIL | EVENT
    engagementStatus: COMPLETED
    engagementDate: "2026-06-15T00:00:00Z"
    outcome: "[what happened / result]"
    nextAction: "[single next step]"
    engagementNote: { markdown: "**Outcome:** ...\n\n**Context:** ..." }
    companyId: "COMPANY_UUID"
    clientAttendeesId: "PERSON_UUID"      # always set — Person is required
    opportunityId: "OPP_UUID"             # optional — only if active Opportunity
    # partnershipId: "PART_UUID"          # optional — only if active Partnership
  }) { id name }
}
```

**Key fields:**
- `clientAttendeesId` — the Person this engagement is with (always required)
- `opportunityId` / `partnershipId` — set only when tied to an opportunity (both optional)
- `engagementType: EMAIL` — use this for nurturing emails sent via OpenMail
- `engagementNote` — rich text field, use `{ markdown: "..." }` format

> **Pitfall:** `engagementNote` is a RichText field — use `{ markdown: "..." }`, NOT a plain string.

### Step 4 — Update Opportunity / Partnership (skip if Person-only)

**Only run this step if an Opportunity or Partnership is linked.**

After confirming the engagement with the Sales Rep, Leo must **judge** the new state — not just fill fields. Apply this logic:

**healthCheck judgment:**

| Situation | Set to |
|---|---|
| New engagement just logged, clear next step agreed | `ON_TRACK` |
| Waiting on client to reply, send document, make decision | `AWAITING_RESPONSE` |
| Next step is unclear or overdue but not yet silent | `NEEDS_FOLLOWUP` |
| No engagement for 7+ days (Opp) or 14+ days (Partnership) | `AT_RISK` |

**currentStatusSummary** — rewrite from scratch based on the full picture now:
> One sentence. Present tense. What is the actual state of this opportunity today?
> Bad: "Had a call." Good: "Proposal sent 2026-06-14; waiting for CFO sign-off by June 20."

**nextActionSummary** — the single most important next thing:
> Format: [Action] — [Owner] — [Deadline]
> Example: "Follow up with CFO if no reply by June 20 — Hunter — 2026-06-20"

**Stage advancement logic:**
- `NEW → SCREENING`: first meaningful two-way contact confirmed
- `SCREENING → MEETING`: meeting scheduled or completed
- `MEETING → PROPOSAL`: proposal requested or sent
- `PROPOSAL → CUSTOMER`: contract signed / opportunity closed
- If ambiguous → Leo suggests, Sales Rep confirms before updating

```graphql
mutation {
  updateOpportunity(id: "OPP_UUID", data: {
    currentStatusSummary: "Proposal sent 2026-06-14; waiting for CFO sign-off by June 20"
    nextActionSummary: "Follow up with CFO if no reply by June 20 — Hunter — 2026-06-20"
    healthCheck: AWAITING_RESPONSE
    nextFollowUpDate: "2026-06-20T00:00:00Z"
    lastUpdateDate: "2026-06-15T00:00:00Z"
  }) { id }
}
```

### Step 5 — Create Tasks (skip if Person-only with no open actions)

If Person-only nurturing engagement: only create a Task if there's a specific follow-up action (e.g. "check back in 3 weeks"). Don't create a task just for the sake of it.

If opportunity-level: create a Task for every open action item.

```graphql
mutation CreateTask($data: TaskCreateInput!) {
  createTask(data: $data) { id }
}
# variables:
{
  "data": {
    "title": "[跟進] Company — specific action",
    "status": "TODO",
    "dueAt": "2026-06-17T12:00:00Z",
    "bodyV2": {
      "markdown": "📌 **Context:** [why this matters / what was said]\n🎯 **Goal:** [what success looks like]\n📎 **Reference:** [Engagement, GBrain page, or document]\n💡 **Suggested approach:** [how Leo recommends handling it]"
    }
  }
}
```

Then link each Task:
```graphql
mutation {
  createTaskTarget(data: {
    taskId: "TASK_UUID"
    targetOpportunityId: "OPP_UUID"       # for C4
    # targetPartnershipId: "PART_UUID"    # for C5
  }) { id }
}
```

> **Rule:** "Waiting for client response" is still a Task — never leave an open loop without a Task with a due date.

### Step 6 — Update Memory (two layers, both required)

**Layer 1 — Hindsight `dx-pipeline` (primary — always do this first):**
```
POST /v1/default/banks/dx-pipeline/memories
{"items": [{
  "content": "[Company] — [date]: [what happened]. Blocker: [if any]. Hunter's read: [if shared]. Next: [agreed action].",
  "tags": ["opportunity", "[company-slug]", "[opportunity|partnership]"]
}]}
```
This is what Leo recalls at the start of the next interaction — fast warm-up context.

**Layer 2 — GBrain (structural, permanent record):**
- `mcp_gbrain_add_timeline_entry` on the company page — date + one-line milestone
- `mcp_gbrain_extract_facts` if significant new intel: budget signal, decision-maker revealed, competitor named, structural blocker, timeline shift

**What counts as significant intel for GBrain extract_facts:**
- A named decision-maker revealed for the first time
- A budget number or timeline stated explicitly
- A competitor mentioned by name
- A blocker that is structural (not just a scheduling delay)

Both layers are non-negotiable. Hindsight = fast recall next session. GBrain = permanent depth.

---

## Single-Record Lookup (Pitfall)

```graphql
# ❌ WRONG — throws "Argument not allowed: id"
{ opportunity(id: "UUID") { id name } }

# ✅ CORRECT
{ opportunities(filter: { id: { eq: "UUID" } }) {
    edges { node { id name stage } }
} }
```

---

## Authority

| Action | Zone |
|---|---|
| Creating Engagements | ✅ Autonomous — after Sales Rep confirms |
| Updating Opportunity / Partnership record | ✅ Autonomous — after confirmation |
| Creating Tasks | ✅ Autonomous |
| Suggesting stage advancement | ✅ Leo suggests |
| Confirming stage advancement (ambiguous) | ⚠️ Ask Sales Rep |
| Closing / abandoning an opportunity | 🚫 Human decision only |
| Contract terms or pricing exceptions | 🚫 Human decision only |
| Sending any external communication | 🚫 Requires confirmation before send |

---

## Pitfalls

- **Recall first.** Always recall `dx-pipeline` before extracting. Don't ask the Sales Rep what Hindsight already knows.
- **Confirm before writing.** Extract → confirm → write. Never go straight to CRM.
- **Engagements are immutable.** Never update or delete. Add a new one if a correction is needed.
- **"Waiting for client" is still a Task.** Every open loop needs a Task with a due date.
- **Both memory layers required.** Hindsight `dx-pipeline` first, then GBrain. Neither alone is sufficient.
- **`clientAttendeesId` is the Person link** — NOT `personId`, NOT `attendeeId`. This is the field that links an Engagement to a Person. Always set it.
- **`engagementNote` is RichText** — use `engagementNote: { markdown: "..." }` NOT a plain string. Same pattern as `bodyV2` on Task/Note.
- **`opportunityId` and `partnershipId` are both optional** — confirmed via schema. Person-only engagements are fully supported without either.
- **Engagement `channel` vs `engagementType`** — both exist. `engagementType` = broad category (EMAIL, PHONE, INPERSON…). `channel` = specific platform (ZOOM, TEAMS, WHATSAPP…). Set both when relevant.
- **`bodyV2` not `body`.** Always use `bodyV2: { markdown: "..." }` for Notes and Tasks.
- **Single-record lookup.** Use `opportunities(filter: { id: { eq: "UUID" } })` not `opportunity(id: "UUID")`.
- **Attendees not in CRM yet.** If meeting attendees (e.g. Rae, Julia) don't exist as People records, set `clientAttendeesId` to the primary known contact for the opportunity, and list the actual attendees by name in `engagementNote`. Do NOT block the engagement write waiting for new People records to be created. Flag in your reply that those contacts should be added to CRM.
- **`mcp_gbrain_extract_facts` embedding dimension error.** If extract_facts returns `"expected 1536 dimensions, not 768"`, the GBrain source was indexed with a different embedding model. Graceful fallback: the intel is already in Hindsight `dx-pipeline` — log the facts there and note the GBrain failure in your reply. Do not retry extract_facts in a loop.

---

## References

- `references/crm-write-patterns.md` — Verified CRM field names and full write sequence
- `references/pipeline-design-decisions.md` — Design rationale
- `references/hindsight-api-patterns.md` — Hindsight bank creation (PUT not POST), recall/retain patterns, bank design decisions
- `references/openmail-api-patterns.md` — OpenMail send/receive API (temporarily here; move to email/outreach skill when C1 is built)
- `references/vikings-stakeholder-map.md` — The Vikings org structure: known contacts, shareholder blocker, Rae/Julia attendance history
