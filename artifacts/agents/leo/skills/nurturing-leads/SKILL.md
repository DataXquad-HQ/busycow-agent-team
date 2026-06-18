---
name: nurturing-leads
description: >
  C4 Lead Nurturing — keep warm with NURTURE and OPPORTUNITY tier Leads by
  sending personalised, context-driven messages at least once a month. Drafts
  are stored in the OutreachMessage CRM object (status=DRAFT), reviewed by a
  human in the Lark review channel, then sent via OpenMail after approval.
  Sent messages are logged as Engagements. Never hardcodes individual user names.
triggers:
  - "nurture"
  - "keep warm"
  - "follow up with leads"
  - "send nurturing email"
  - "monthly nurturing"
  - "check in with"
  - "reach out to"
  - "draft a message for"
  - "幫我寫封信給"
  - "跟進一下"
  - "lead nurturing"
  - "C4"
  - "who needs nurturing"
  - "overdue leads"
---

# Lead Nurturing Skill

## When to Use

Use when running the monthly nurturing cycle — either via the daily cron scanner (Flow A) or the message sender cron (Flow B). Also use when a human asks to draft or send a nurturing message to a specific Lead.

## Purpose

Keep {{COMPANY_NAME}} top-of-mind with Leads who aren't yet in an active opportunity.
The goal is **trust and cadence** — they should think of us when an opportunity arises.

**Cadence:** At least once per month per active Lead (NURTURE or OPPORTUNITY tier).
**Method:** Personalised, contextual messages — never generic blasts.
**Channel:** Email via OpenMail (`{{AGENT_EMAIL}}`), with human review before sending.

> ⚠️ Never reference specific team members by name (Hunter, Kevin, etc.) in skill logic,
> cron prompts, or message drafts. Use "the team", "our BD team", or "our team" instead.

---

## Leo's Email Identity

Every outbound email from Leo must use this signature:

```
Leo
Business Development Lead | {{COMPANY_NAME}}
AI-Powered Digital Employee

📧 {{AGENT_EMAIL}}
🌐 {{COMPANY_URL}}

--
Hi, I'm Leo — an AI-powered Business Development agent at {{COMPANY_NAME}}.
Feel free to reply directly to this email; I read every response.
If you'd prefer to speak with a human member of our team at any point,
just say so and we'll have someone get back to you right away.
```

Leo identifies as an AI digital employee — transparent, professional, not hidden.
The disclaimer reassures recipients they can reply freely and escalate to a human if needed.

---

## CRM Objects Used

### OutreachMessage (custom object)
Stores drafts and scheduled messages. Lifecycle: DRAFT → SCHEDULED → SENT / CANCELLED.

| Field | Type | Notes |
|---|---|---|
| `name` | TEXT | Auto-set to subject line |
| `subject` | TEXT | Email subject |
| `body` | RICH_TEXT | Draft content — use `body: { markdown: "..." }` |
| `context` | TEXT | Leo's notes: why now, what context used |
| `status` | SELECT | DRAFT / SCHEDULED / SENT / CANCELLED |
| `messageType` | SELECT | NURTURING / COLD_OUTREACH |
| `sendMethod` | SELECT | AUTO / MANUAL |
| `channel` | SELECT | EMAIL / WHATSAPP / LINE |
| `scheduledAt` | DATETIME | When to send |
| `sentAt` | DATETIME | When actually sent |
| `recipientId` | Person relation | Who it's addressed to |

```graphql
# Create a draft
mutation {
  createOutreachMessage(data: {
    name: "[Subject line]"
    subject: "[Subject line]"
    body: { markdown: "Hi [Name],\\n\\n[body]\\n\\n[signature]" }  # OutreachMessage uses `body`, not `bodyV2`
    context: "30 days since last contact. Sharing blog post on water utilities."
    status: DRAFT
    messageType: NURTURING
    sendMethod: AUTO
    channel: EMAIL
    scheduledAt: "2026-06-16T04:00:00Z"
    recipientId: "PERSON_UUID"
  }) { id name }
}

# Update to SCHEDULED (after human approval)
mutation {
  updateOutreachMessage(id: "MSG_UUID", data: {
    status: SCHEDULED
  }) { id status }
}

# Update to SENT (after send)
mutation {
  updateOutreachMessage(id: "MSG_UUID", data: {
    status: SENT
    sentAt: "2026-06-16T04:00:00Z"
  }) { id status }
}
```

---

## Flow A — Cron A: Lead Nurturing Scanner (runs daily morning)

### Step 1 — Find overdue leads

```graphql
{
  people(filter: { leadTier: { in: [NURTURE, OPPORTUNITY] } }) {
    edges { node {
      id
      name { firstName lastName }
      emails { primaryEmail }
      preferredChannel
      contactHandle
      leadTier
      lastContactDate
      meetContext
      notes
      company { id name }
    }}
  }
}
```

Filter in code: keep only where `lastContactDate` is null OR > 30 days ago.
Also exclude people who already have a DRAFT or SCHEDULED OutreachMessage:

```graphql
{
  outreachMessages(filter: {
    status: { in: [DRAFT, SCHEDULED] }
  }) {
    edges { node { recipientId } }
  }
}
```

Skip anyone already in the pending queue.

### Step 2 — For each overdue lead, recall context

```python
# Hindsight
POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories/recall
{"query": "[Company] [Person] — background, last interaction, topics", "top_k": 5}

# GBrain
mcp_gbrain_get_page(slug="companies/[company-slug]", fuzzy=True)
```

### Step 3 — Research fresh content

#### DX Blog (always check)
```python
web_extract(urls=["{{COMPANY_BLOG_URL}}"])
```
Look for posts in last 60 days relevant to this lead's industry. If found: reference naturally.

#### Lead's latest news (OPPORTUNITY tier)
```python
web_search(query="[Company name] news 2026", limit=5)
```
Look for: funding, product launch, expansion, leadership change.

### Step 4 — Draft the message

**Message types:**
| Type | When | Tone |
|---|---|---|
| Check-in | No specific news, just cadence | Warm, brief (3–4 sentences) |
| Content share | Relevant DX blog post | Value-led |
| News reference | Lead's company had notable news | Attentive |

**Subject line rules — specific > generic:**
- ✅ "Thought of you after our AquaOptima post" 
- ✅ "Saw [Company]'s expansion news — congrats"
- ❌ "Just checking in" / "Hope you're well" / "Following up"

**Draft format:**
```
Subject: [Specific, references something real]

Hi [First name],

[Opening — specific reference to how you met or last interaction]

[Middle — value: blog post / insight / their news / relevant question]

[Close — soft, no hard ask]

Best,
Leo
Business Development Lead | {{COMPANY_NAME}}
AI-Powered Digital Employee

📧 {{AGENT_EMAIL}}
🌐 {{COMPANY_URL}}

--
Leo is an AI-powered member of the {{COMPANY_NAME}} BD team.
All outreach is reviewed by our human team before sending.
```

### Step 5 — Store draft in CRM

```graphql
mutation {
  createOutreachMessage(data: {
    name: "[subject]"
    subject: "[subject]"
    body: { markdown: "[full email body]" }
    context: "[why now + what context used]"
    status: DRAFT
    messageType: NURTURING
    sendMethod: AUTO
    channel: EMAIL
    scheduledAt: "[today or tomorrow 09:00 local]"
    recipientId: "[PERSON_UUID]"
  }) { id }
}
```

### Step 6 — Notify review channel

**Two separate outputs — different channels, different audiences.**

#### 6a — Sales review notification (keep it short)

Post to `[Sales] Nurturing Outreach Review` (`{{OUTREACH_REVIEW_CHANNEL_ID}}`).
**Show only the draft + a simple action prompt. No run stats, no flags, no debug info.**

Single draft:
```
✉️ 1 封草稿待審查 — [Date]

**[Person Name]** — [Company]
主旨：[subject line]
CRM：{{CRM_EXTERNAL_URL}}/objects/outreachMessages/[UUID]

回覆 **OK** 發送，或直接在 CRM 將 status 改為 SCHEDULED。
```

Multiple drafts:
```
✉️ [N] 封草稿待審查 — [Date]

1. **[Person Name]** — [Company] | {{CRM_EXTERNAL_URL}}/objects/outreachMessages/[UUID]
2. **[Person Name]** — [Company] | {{CRM_EXTERNAL_URL}}/objects/outreachMessages/[UUID]

回覆 OK 全部發送，或指定哪幾封（e.g. "1 and 3 OK"）。
也可直接在 CRM 將 status 改為 SCHEDULED。
```

**Rules:**
- No run stats in this channel
- No flags/warnings in this channel
- No full draft body — just subject + CRM link
- CRM links always use `{{CRM_EXTERNAL_URL}}` (NOT localhost:3001)

#### 6b — Ops log (full detail)

Post the full run report to `[System] Backend Report` (`{{SYSTEM_BACKEND_CHANNEL_ID}}`).
Include everything: run stats, drafts created, flags, warnings, memory updates, errors.

```
📬 **Lead Nurturing Scanner — [Date]**

**Run Summary**
- Scanned: [N] leads
- Drafts created: [N]
- Skipped (already pending): [N]
- No action needed: [N]

**Drafts Created**
- [Person], [Company] — OutreachMessage ID: [UUID]

**Flags**
- ⚠️ [any warnings — ICP missing, blog not live, etc.]

**Memory**
- ✅ Hindsight updated
```

---

## Flow B — Cron B: Message Sender (runs daily midday)

### Step 1 — Find overdue DRAFT messages
```graphql
{
  outreachMessages(filter: {
    status: { eq: DRAFT }
  }) {
    edges { node {
      id subject scheduledAt
      recipient { id name { firstName lastName } emails { primaryEmail } }
    }}
  }
}
```
Filter: `scheduledAt` < now (overdue and still DRAFT = not approved yet).

**Action:** Re-notify review channel:
```
⚠️ **Overdue Draft — [Person], [Company]**
Scheduled for [date] — still awaiting approval.
Reply OK to send, or CANCEL to discard.
```

### Step 2 — Find SCHEDULED messages due now
```graphql
{
  outreachMessages(filter: {
    status: { eq: SCHEDULED }
  }) {
    edges { node {
      id name subject scheduledAt sendMethod
      body { markdown }
      recipient { id name { firstName lastName } emails { primaryEmail } companyId }
    }}
  }
}
```
Filter: `scheduledAt` <= now.

### Step 3 — Send via OpenMail

```python
import uuid, requests

headers = {
    "Authorization": "Bearer {{OPENMAIL_API_KEY}}",
    "Content-Type": "application/json",
    "Idempotency-Key": str(uuid.uuid4())  # REQUIRED
}

payload = {
    "from": "{{AGENT_EMAIL}}",
    "to": ["recipient@company.com"],
    "subject": "[subject]",
    "text": "[plain text body]",
}

INBOX_ID = "{{OPENMAIL_INBOX_ID}}"  # {{AGENT_EMAIL}}
resp = requests.post(f"https://api.openmail.sh/v1/inboxes/{INBOX_ID}/send", headers=headers, json=payload)
# Note: `to` must be a string (not array). `body` is the field name (not `text`).
# Correct payload: {"to": "email@addr", "subject": "...", "body": "..."}
```

> ⚠️ `Idempotency-Key` is mandatory — prevents duplicate sends on retry.

### Step 4 — Post-send: update CRM + log Engagement

```graphql
# Mark message SENT
mutation {
  updateOutreachMessage(id: "MSG_UUID", data: {
    status: SENT
    sentAt: "[ISO now]"
  }) { id }
}

# Update Person.lastContactDate
mutation {
  updatePerson(id: "PERSON_UUID", data: {
    lastContactDate: "[ISO now]"
  }) { id }
}

# Create Engagement (immutable interaction log)
mutation {
  createEngagement(data: {
    name: "Nurturing Email — [Company] — [date]"
    engagementType: EMAIL
    engagementStatus: COMPLETED
    engagementDate: "[ISO now]"
    outcome: "Nurturing email sent. [Brief content summary]."
    nextAction: "Follow up if no reply in 30 days"
    engagementNote: { markdown: "**Type:** Nurturing\n\n**Subject:** [subject]\n\n**Content summary:** [what was shared]" }
    companyId: "[COMPANY_UUID]"
    clientAttendeesId: "[PERSON_UUID]"
  }) { id }
}
```

Then write to Hindsight:
```
POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories
{
  "items": [{
    "content": "[Company] / [Person] — Nurturing email sent [date]. Subject: [subject]. Content: [what was shared]. Next touch: ~30 days.",
    "tags": ["nurture", "[company-slug]", "email", "lead-nurturing"]
  }]
}
```

---

## Blog Access

{{COMPANY_NAME}} blog: `{{COMPANY_BLOG_URL}}` (Ghost CMS)

```python
# Fetch recent posts
web_extract(urls=["{{COMPANY_BLOG_URL}}"])
# Look for: title, excerpt, URL, publish date
# Select posts < 60 days old that match lead's industry
```

---

## Lark Channels

| Channel | chat_id | What goes here |
|---|---|---|
| `[Sales] Nurturing Outreach Review` | `{{OUTREACH_REVIEW_CHANNEL_ID}}` | Draft notifications only — short format, subject + CRM link |
| `[System] Backend Report` | `{{SYSTEM_BACKEND_CHANNEL_ID}}` | Full ops log from cron runs — stats, flags, errors |

**The review channel must stay short.** Sales team reads it to approve drafts, not to audit system health. One glance, one action. No run stats, no flags, no debug output in that channel.

Cron `deliver` is always set to `[System] Backend Report`. The review notification is a separate in-run push to the sales channel.

---

## Lark Review Channel

**Chat ID:** `{{OUTREACH_REVIEW_CHANNEL_ID}}`
**Name:** `[Sales] Nurturing Outreach Review`
**Purpose:** Human review of all outreach drafts before sending.

Human responds:
- **OK** → update OutreachMessage status to SCHEDULED (Sender cron picks it up)
- **[edited text]** → Leo updates the draft body, then sets SCHEDULED
- **CANCEL** → set status to CANCELLED

---

## Quality Bar

Before storing a draft OutreachMessage (Flow A) or sending a message (Flow B):

**Draft quality (Flow A):**
- Subject line is specific — references something real (event, DX blog post, company news, prior meeting) — not a generic "just checking in"?
- Opening line references a concrete, verifiable detail (how they met, a recent company event) — not invented?
- Any blog post or news reference is confirmed to exist (web_extract verified it) — not assumed from memory?
- No team member names appear in the draft — only "the team", "our BD team", "{{COMPANY_NAME}}"?
- AI disclaimer block is included in full — not shortened or paraphrased?
- If context from Hindsight was used: labelled as "Based on prior interaction context…" not presented as confirmed current fact?

**Send quality (Flow B):**
- Message being sent has `status: SCHEDULED` — confirmed human-approved — not DRAFT?
- `Idempotency-Key` is a fresh UUID — not reused from a prior send?
- Recipient email address verified from CRM (not assumed from memory)?

If any check fails, do not send — fix the issue or escalate to review channel.

## Fallback Behavior

- **If CRM is unreachable**: cannot query overdue leads or OutreachMessage queue — abort the run; post to Backend Report: "CRM unavailable — nurturing scanner could not run. No drafts created."
- **If Hindsight `{{ORG_PREFIX}}-pipeline` returns no context for a lead**: proceed with web research only; note in the `context` field of the OutreachMessage: "No prior interaction history in Hindsight."
- **If GBrain company page is missing**: proceed without it; note absence in draft context field; do not block draft creation.
- **If {{COMPANY_NAME}} blog (`{{COMPANY_BLOG_URL}}`) is unreachable**: skip blog reference; use lead's company news or a general check-in format instead. Do not fabricate a blog post.
- **If OpenMail is unreachable** (Flow B): do not mark OutreachMessage as SENT; leave status as SCHEDULED; post to Backend Report with error detail so next run can retry.
- **If lead's email address is missing from CRM**: skip that lead; flag in Backend Report: "[Person] — no email address in CRM, cannot draft."
- Do not silently skip a lead — every skipped lead must appear in the Backend Report ops log with the reason.

## Pitfalls

- **Never hardcode team member names** in skill logic, cron prompts, or message drafts. Use "Human", "Sales Rep", "our team", "the BD team". This applies across all skills.
- **Email disclaimer is mandatory — never omit it.** Every outbound email must end with the full AI-agent disclaimer block (see "Leo's Email Identity" section). This reassures recipients they can reply freely and escalate to a human. Do not shorten or paraphrase it. WhatsApp/LINE messages do NOT need this disclaimer — email only.
- **`approvals.cron_mode` must be set to `approve`** — without this, all terminal/execute_code calls in cron sessions are BLOCKED (no user present to approve). Run: `hermes --profile leo config set approvals.cron_mode approve`. See `references/cron-approval-config.md`.
- **CRM API calls use localhost** — `http://localhost:3001/graphql` for all CRM reads/writes (fast, no external traffic). But **CRM links shown to humans always use the external URL**: `{{CRM_EXTERNAL_URL}}/objects/[type]/[UUID]`. Never expose localhost URLs in Lark messages.
- **Two delivery channels, two audiences** — `[Sales] Nurturing Outreach Review` gets only the draft notification (short, actionable). `[System] Backend Report` gets the full ops log (stats, flags, errors). Never mix them.

- **Never auto-send without SCHEDULED status** — DRAFT means not approved. Only SCHEDULED messages get sent by Cron B.
- **Cron session ≠ interactive session** — tools like `execute_code` and `terminal` may behave differently or get blocked in an interactive session vs. a cron session. When testing the nurturing flow interactively, use `terminal` directly for Hindsight calls rather than `execute_code`. The cron runs cleanly in its own isolated session with `["web", "terminal", "file"]` toolset.
- **OpenMail send endpoint is `POST /v1/inboxes/{inbox_id}/send`** — NOT `/v1/messages`. Inbox ID for {{AGENT_EMAIL}}: `{{OPENMAIL_INBOX_ID}}`. Payload: `to` is a string (not array), body field is `body` (not `text`). Confirmed 2026-06-15.
- **Never reference team members by name** in drafts or skill logic. Use "our team", "{{COMPANY_NAME}}'s BD team".
- **Skip PASSERBY tier entirely** — never draft nurturing for PASSERBY leads.
- **Skip leads already in pending queue** — check for existing DRAFT/SCHEDULED messages before drafting a new one.
- **lastContactDate drives the 30-day check** — always update it after a SENT message.
- **Engagement is immutable** — create it only after the email is actually sent. Never create a PLANNED engagement for a future message; that's what OutreachMessage is for.
- **`body` not `bodyV2`** — OutreachMessage body field is `body: { markdown: "..." }` (RichText). The `bodyV2` alias does NOT exist on this custom object. Confirmed via schema introspection 2026-06-15.
- **Don't force blog mentions** — only reference DX blog if genuinely relevant. Forced references are worse than none.
