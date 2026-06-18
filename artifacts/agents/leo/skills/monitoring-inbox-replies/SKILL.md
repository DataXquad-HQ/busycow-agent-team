---
name: monitoring-inbox-replies
description: >
  C4 Inbox Monitor — poll Leo's OpenMail inbox for inbound replies, match
  them to CRM contacts, log Engagements, update lastContactDate, write
  Hindsight memory, and notify the sales review channel so a human can
  follow up. Runs daily via cron or on manual trigger.
triggers:
  - "check inbox"
  - "any replies?"
  - "inbox monitor"
  - "有沒有人回信"
  - "收到回信了嗎"
  - "monitor email replies"
  - "C4 inbox"
---

# Inbox Monitor Skill

## When to Use

Use when checking Leo's OpenMail inbox for inbound replies to outreach emails. Runs automatically via daily cron, or trigger manually with 'check inbox' / '有沒有人回信'. Do not use for sending emails — that is handled by nurturing-leads.

## Purpose

Detect inbound replies to Leo's outreach emails, record them as Engagements
in CRM, update memory layers, and notify the sales team so they can respond.

A reply is a signal — it means the Lead is engaging. Human decides how to reply.

---

## When to Use

- **Cron:** runs automatically once daily at 02:00 UTC
- **Human trigger:** "check inbox", "有沒有人回信", "any replies?" — manual on-demand check
- **Do not use** for sending emails — that is `nurturing-leads` Flow B

---

## Credentials & IDs

| Item | Value |
|---|---|
| OpenMail token | `{{OPENMAIL_API_KEY}}` |
| Leo inbox ID | `{{OPENMAIL_INBOX_ID}}` |
| Leo address | `{{AGENT_EMAIL}}` |
| CRM base URL (API) | `http://localhost:3001/graphql` |
| CRM base URL (human links) | `{{CRM_EXTERNAL_URL}}` |

---

## Flow — Inbox Monitor

### Step 1 — Fetch unread inbound threads

```python
import requests

token = "{{OPENMAIL_API_KEY}}"
inbox_id = "{{OPENMAIL_INBOX_ID}}"
headers = {"Authorization": f"Bearer {token}"}

resp = requests.get(
    f"https://api.openmail.sh/v1/inboxes/{inbox_id}/threads?is_read=false",
    headers=headers
)
threads = resp.json()["data"]
```

Filter: only threads where the **latest message** is `direction: inbound`.
(A thread can be unread because Leo sent — ignore those. We only care about
threads where the contact wrote back.)

To get messages in a thread:
```python
resp = requests.get(
    f"https://api.openmail.sh/v1/threads/{thread_id}/messages",
    headers=headers
)
messages = resp.json()["data"]

# Check if latest message is inbound
latest = sorted(messages, key=lambda m: m["createdAt"])[-1]
if latest["direction"] != "inbound":
    continue  # skip — not a reply
```

### Step 1b — De-duplicate: skip already-processed threads

Before processing any thread, check CRM for an existing Engagement that references this thread_id.

**Important:** `engagementNote` is a `RichTextFilterInput` — it does NOT support `like`/`contains` string filters. Use the `outcome` field instead (which is a `StringFilter` and also contains the thread reply content), or search by `name` which contains the company and date:

```graphql
{
  engagements(filter: {
    outcome: { like: "%[first 8 chars of thread_id]%" }
  }) {
    edges { node { id } }
  }
}
```

Alternatively, store the thread_id in the `outcome` field explicitly (e.g. prefix with `Thread:`) so it's reliably searchable. If a match exists → skip this thread entirely (already logged). This prevents duplicate Engagements when threads were read and processed manually (e.g. during debugging or first-run bootstrapping).

### Step 2 — Match sender to CRM Person

Extract `fromAddr` from the latest inbound message. Parse the email address:
```python
import re
match = re.search(r'[\w.+-]+@[\w.-]+', latest["fromAddr"])
sender_email = match.group(0) if match else None
```

Query CRM for Person with this email:
```graphql
{
  people(filter: {
    emails: { primaryEmail: { eq: "sender@company.com" } }
  }) {
    edges { node {
      id
      name { firstName lastName }
      emails { primaryEmail }
      leadTier
      lastContactDate
      company { id name }
    }}
  }
}
```

**If no CRM match found:**
- Still log to `[System] Backend Report` — unknown sender replied
- Do NOT create a new Person automatically — flag for human review
- Format: `⚠️ Unknown sender replied: [email] — subject: [subject]. Not in CRM. Manual action needed.`

### Step 3 — Extract reply content

```python
reply_body = latest["bodyText"] or ""

# Strip quoted original message (lines starting with ">")
lines = reply_body.split("\n")
clean_lines = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith(">"):
        break  # stop at quoted section
    clean_lines.append(line)
reply_clean = "\n".join(clean_lines).strip()
```

Also capture:
- `subject` — from thread
- `reply_date` — `latest["createdAt"]`
- `thread_id` — for reference

### Step 4 — Log Engagement in CRM

```graphql
mutation {
  createEngagement(data: {
    name: "Inbound Reply — [Company] — [date]"
    engagementType: EMAIL
    engagementStatus: COMPLETED
    engagementDate: "[reply_date ISO]"
    outcome: "Inbound reply received. Content: [first 200 chars of reply_clean]"
    nextAction: "Human to review and respond"
    engagementNote: { markdown: "**Type:** Inbound Reply\n\n**Subject:** [subject]\n\n**Reply:**\n[reply_clean]\n\n**Thread ID:** [thread_id]" }
    companyId: "[COMPANY_UUID]"
    clientAttendeesId: "[PERSON_UUID]"
  }) { id }
}
```

### Step 5 — Update Person.lastContactDate

```graphql
mutation {
  updatePerson(id: "[PERSON_UUID]", data: {
    lastContactDate: "[reply_date ISO]"
  }) { id }
}
```

### Step 6 — Write Hindsight memory

```python
import requests

payload = {
    "items": [{
        "content": f"[Company] / [Person] — Inbound reply received [date]. Subject: [subject]. Reply: [reply_clean first 300 chars]. Needs human follow-up.",
        "tags": ["inbound-reply", "[company-slug]", "email", "lead-nurturing"]
    }]
}
requests.post(
    "http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories",
    json=payload
)
```

### Step 7 — Analyse reply intent & create CRM Task

> This step was confirmed in production (2026-06-16). Intent classification drives Task creation automatically.

Read the clean reply and classify the intent:

| Intent | Examples | Task to create |
|---|---|---|
| **Wants human contact** | 「可以認識真人嗎」「能跟你們的人聊聊嗎」 | "Respond to [Person] — wants to speak with a human" |
| **Has a question** | 「你們有做X嗎」「價格怎麼算」 | "Reply to [Person]'s question: [question summary]" |
| **Wants a meeting** | 「可以安排個call嗎」「有空聊聊嗎」 | "Schedule a call with [Person] — [Company]" |
| **Positive / interested** | 「很有興趣」「請多介紹」 | "Follow up with [Person] — expressed interest" |
| **Neutral / acknowledge** | 「收到了」「謝謝」 | "Follow up with [Person] — acknowledged outreach" |
| **Negative / not interested** | 「不需要」「暫時不考慮」 | No task — flag for human to consider OPT_OUT |

Create a CRM Task for all intents **except negative**:

```graphql
mutation {
  createTask(data: {
    title: "[Task title based on intent]"
    bodyV2: { markdown: "**Reply received from:** [Person], [Company]\n\n**Their message:**\n[reply_clean]\n\n**Suggested action:** [what Leo recommends based on intent]\n\nCRM: {{CRM_EXTERNAL_URL}}/objects/people/[PERSON_UUID]" }
    status: TODO
    dueAt: "[tomorrow ISO date, 09:00 local = 01:00 UTC]"
    assigneeId: "[Sales Rep user ID from CRM]"
  }) { id }
}
```

To get the assignee ID (Sales Rep):
```graphql
{
  workspaceMembers {
    edges { node { id name { firstName lastName } } }
  }
}
```
Pick the human Sales Rep (not Leo/bot accounts).

**For negative intent:** Do NOT create a task automatically. Flag in the Lark notification so the human can decide whether to OPT_OUT.

### Step 8 — Notify sales review channel

Post to `[Sales] Nurturing Outreach Review` (`{{OUTREACH_REVIEW_CHANNEL_ID}}`):
Single reply:
```
📩 收到回信！— [Date]

**[Person Name]** — [Company]
主旨：Re: [subject]

> [reply_clean — first 300 chars, truncate with "…" if longer]

📋 已建立 Task：[task title]
CRM 聯絡人：{{CRM_EXTERNAL_URL}}/objects/people/[PERSON_UUID]
CRM 互動記錄：{{CRM_EXTERNAL_URL}}/objects/engagements/[ENGAGEMENT_UUID]
```

Negative intent (no task created):
```
📩 收到回信 — [Date]

**[Person Name]** — [Company]
主旨：Re: [subject]

> [reply_clean]

⚠️ 對方表示不感興趣。是否要標記為 OPT_OUT？請人工確認。
```

Multiple replies in one run:
```
📩 [N] 封新回信 — [Date]

1. **[Person]** — [Company]
   > [reply preview 80 chars…]
   📋 Task：[task title]
   CRM：{{CRM_EXTERNAL_URL}}/objects/people/[UUID]

2. **[Person]** — [Company]
   > [reply preview 80 chars…]
   📋 Task：[task title]
   CRM：{{CRM_EXTERNAL_URL}}/objects/people/[UUID]
```

### Step 9 — Mark thread as read

```python
requests.patch(
    f"https://api.openmail.sh/v1/threads/{thread_id}",
    headers={**headers, "Content-Type": "application/json"},
    json={"is_read": True}
)
```

**Only mark as read AFTER:**
- Engagement created ✅
- lastContactDate updated ✅
- Hindsight written ✅
- CRM Task created (if applicable) ✅
- Lark notification sent ✅

If any step fails — do NOT mark as read. The thread stays unread so the next
cron run will retry it.

---

## Ops Log (Backend Report)

Post full run report to `[System] Backend Report` (`{{SYSTEM_BACKEND_CHANNEL_ID}}`):

```
📬 Inbox Monitor — [Date] [Time]

**Run Summary**
- Unread threads checked: [N]
- Inbound replies found: [N]
- Unknown senders: [N]
- Skipped (outbound only): [N]

**Processed**
- [Person], [Company] — Engagement ID: [UUID] ✅

**Unknown Senders**
- ⚠️ [email] replied — not in CRM

**Errors**
- [any failures]
```

If nothing to report (zero unread threads): post nothing to either channel.
Stay silent when there's nothing to say.

---

## Lark Channels

| Channel | chat_id | What goes here |
|---|---|---|
| `[Sales] Nurturing Outreach Review` | `{{OUTREACH_REVIEW_CHANNEL_ID}}` | Reply notifications — short, actionable |
| `[System] Backend Report` | `{{SYSTEM_BACKEND_CHANNEL_ID}}` | Full ops log |

---

## Reference Files

- `references/openmail-api-notes.md` — confirmed OpenMail API behaviours: mark-read endpoint, inbound filtering, reply body cleanup. Load when debugging inbox issues.

## Quality Bar

Before logging an Engagement or creating a Task:
- Reply direction confirmed as `inbound` on the latest message — not an outbound thread being reprocessed?
- Quoted text stripped — Engagement `outcome` field contains only the new reply text, not the full email chain?
- Sender email matched to a CRM Person — not assumed from name or subject line alone?
- Intent classification based on actual reply content — not inferred from subject line only?
- Thread de-duplication check run — no existing Engagement with this thread_id already logged?
- CRM Task body includes the verbatim reply excerpt (first 200 chars) so the sales team has full context without opening CRM?
- CRM links in Lark notification use `{{CRM_EXTERNAL_URL}}` — not `localhost`?

If any check fails, do not mark the thread as read — leave it unread for retry.

## Fallback Behavior

- **If OpenMail is unreachable**: post to Backend Report: "OpenMail unavailable — inbox could not be polled. Retrying next scheduled run." Do not silently skip.
- **If CRM is unreachable**: inbox can be read, but do not create Engagements or Tasks; log reply to Backend Report only; do not mark thread as read (leaves it for retry when CRM is back).
- **If Hindsight `{{ORG_PREFIX}}-pipeline` is unreachable**: skip the Hindsight write; log the gap in Backend Report; proceed with CRM Engagement creation — Hindsight is supplementary, not blocking.
- **If sender email does not match any CRM Person**: do NOT auto-create a person; flag in Backend Report as "Unknown sender: [email] — manual action needed"; post the reply preview to Backend Report so a human can act.
- **If Lark `[Sales] Nurturing Outreach Review` message fails**: log the failure in Backend Report; the Engagement and Task are already created — the ops log is the fallback record.
- **If intent classification is ambiguous** (reply is too short or language unclear): default to "Neutral / acknowledge" intent — create a follow-up task rather than doing nothing.

## Pitfalls

- **`is_read` not `isRead`** — OpenMail PATCH body uses snake_case: `{"is_read": true}`. camelCase returns 400. PUT returns 404 — only PATCH works.
- **Filter direction carefully** — unread threads include ones Leo sent. Always check `latest["direction"] == "inbound"` before processing.
- **Mark as read only after all steps succeed** — if CRM write or Lark notify fails, leave thread unread so next run retries.
- **CRM links always external** — `{{CRM_EXTERNAL_URL}}/objects/[type]/[UUID]`. Never use `localhost:3001` in Lark messages.
- **Don't auto-create unknown senders** — flag for human review. Spam or cold replies should not pollute CRM.
- **Strip quoted text from reply** — the meaningful content is the new text only, not the quoted original message. Stop at the first line starting with `>`.
- **Silent when nothing to do** — if zero unread inbound replies, post nothing to either channel.
- **TWENTY_API_KEY auth** — load from env: `[k for k in open('/path/.env').read().splitlines() if k.startswith('TWENTY_API_KEY')][0].split('=',1)[1]`
- **API calls can inadvertently mark threads read** — calling `GET /v1/threads/{id}/messages` may cause the thread's `isRead` to flip on the server side. If a reply was processed manually (e.g. during debugging), check CRM for an existing Engagement before creating a duplicate. The cron should de-duplicate by checking: does an Engagement already exist with this thread_id in its note?
- **`is_read=false` may return zero even when replies exist** — if threads were read by a prior API call or manual processing, poll all threads and filter by `direction: inbound` + absence of existing Engagement instead of relying solely on `is_read=false`.
- **`engagementNote` is RichTextFilterInput — not searchable with `like`** — do NOT use `engagementNote: { like: "..." }` in dup-check queries; it will fail with a NoneType error. Use the `outcome` field (StringFilter) instead, which also records the reply content and is string-searchable.
- **Task body field is `bodyV2`** — TaskCreateInput uses `bodyV2: { markdown: "..." }`, not `body`. Using `body` returns `BAD_USER_INPUT`.
- **Lark auth via FEISHU_APP_ID/FEISHU_APP_SECRET** — get a tenant_access_token by POST to `https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal` with `{"app_id": ..., "app_secret": ...}`. There is no pre-issued bearer token for Lark.
- **Escalation signal** — if reply content contains phrases like "speak with a real person", "真人", "human", flag in the Lark notification with `⚡ 對方要求與真人聯繫` so the sales rep prioritises it.
