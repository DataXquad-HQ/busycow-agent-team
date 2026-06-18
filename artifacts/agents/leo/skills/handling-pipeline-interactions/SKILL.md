---
name: handling-pipeline-interactions
description: >
  C4/C5 pipeline interaction handling — how Leo processes any update from the Sales Rep
  about an Opportunity or Partnership. Covers: extracting engagement data, clarifying
  before writing to CRM, creating tasks, report-back tasks for planned meetings,
  and silence-based health detection. Load this skill whenever the Sales Rep mentions
  a meeting, call, demo, or any contact with a prospect/partner.
triggers:
  - "log interaction"
  - "we had a meeting"
  - "I talked to"
  - "我剛跟"
  - "meeting scheduled"
  - "demo arranged"
  - "update on opportunity"
  - "update on partnership"
  - "跟進"
  - "開會"
  - "demo"
  - "call with"
  - "engagement"
  - "C4"
  - "C5"
---

# Pipeline Interaction Skill

## When to Use

Use whenever the Sales Rep mentions a completed or upcoming interaction with a Prospect, Lead, or Partner — meeting, call, demo, email exchange. This skill orchestrates the full pipeline interaction flow: logging past engagements, creating report-back tasks for future meetings, and detecting silence-based health signals.

## Architecture Notes (confirmed 2026-06-15)

### C4 and C5 are the same capability
Opportunity (C4) and Partnership (C5) use identical flows — same skill, two objects.
The only differences:
- Object type: `opportunity` vs `partnership`
- TaskTarget field: `targetOpportunityId` vs `targetPartnershipId`
- Silence thresholds: **7 days** (Opportunity) vs **14 days** (Partnership) → `AT_RISK`
- End state: CUSTOMER vs Signed Partner (then hands to Partner Success Agent)

### Memory layers (two systems, different roles)
- **GBrain** = structured, permanent 档案室 per company/opportunity. Timeline entries, facts, currentStatusSummary. Read via slug before engaging with an opportunity.
- **Hindsight** = fast semantic recall for warm-up context before acting. Query:「這個案子上次的重點是什麼」. Both must be updated after every logged engagement — not optional.
- Primary Hindsight bank for this skill: `{{ORG_PREFIX}}-pipeline` (C5/C6 work).

### Capability numbering (v13.0, updated 2026-06-15)
C1 = Lead Capture (human-assisted onboarding from networking/events/referrals — no cold email)
C2 = Outbound Prospecting (Leo-driven: source lists, cold email sequences, reply → Lead)
C3 = Account Intelligence (enrich Prospects shallowly, Leads deeply)
C4 = Lead Nurturing (follow-up, re-engage, inbox monitoring)
C5 = Progressing Pipeline (Opportunity + Partnership combined, was C4)
C6 = Pipeline Health Monitoring (daily surfacing, stall detection, weekly review — was C5)

This skill covers C5. The sending-daily-pipeline-reminder and pipeline health work is C6.

---

## Core Design Principles

### Engagement = Past tense only
An Engagement record is an **immutable log of something that already happened**.
Never create an Engagement for a future/planned interaction.
Fields that matter most:
- `outcome` — what was the result / what did we learn?
- `nextAction` — what is the single next step to advance this opportunity?
- `engagementNote` / Note — detailed narrative of what happened

### Task = All future obligations
**Everything that still needs to be done is a Task** — including "waiting for client".
A "Waiting for client" situation = a Task to follow up and ask.
No engagement status needed. Task covers all forward-looking obligations.

### Delivery channel
All confirmations, clarifications, and daily briefings go to:
**Lark group `[DX] Sales Daily Update`** (`{{SALES_DAILY_UPDATE_CHANNEL_ID}}`)

---

## Flow A — Sales Rep Reports a Past Interaction

**Trigger:** Sales Rep says "I just talked to X", "we had a meeting", "剛跟XXX談過", etc.

### Step 1 — Extract from what the Rep said
From the Rep's message, pull out:
- Who they spoke to (person + company)
- When it happened
- What was discussed / what happened
- Any outcome or conclusion reached
- Any next steps mentioned

### Step 2 — Clarify before writing (ask ONE targeted question)
Don't fire a questionnaire. Identify the **single most critical missing piece** and ask just that.

Priority of what to clarify:
1. **Outcome** — if unclear: "這次談的結論是什麼？有沒有達成什麼共識？"
2. **Next action** — if unclear: "下一步是什麼？誰要做什麼？"
3. **Attendees** — if unclear and relevant (e.g. stakeholder meetings): "這次有哪些人出席？"

If outcome AND next action are both clear from what the Rep said → skip clarification, go straight to Step 3.

### Step 3 — Confirm before writing
Present a structured summary for the Rep to approve:

```
📋 確認以下資訊存入 CRM：

**互動紀錄 (Engagement)**
- 對象：[Company] — [Person(s)]
- 日期：[date]
- 形式：[call / meeting / demo / messaging]
- Outcome：[what happened / conclusion]
- Next Action：[single next step]

**Note（詳細紀錄）**
[narrative summary]

**Tasks 要建立：**
- [ ] [Task 1 — owner, due date]
- [ ] [Task 2 — owner, due date]

確認後我就存進去，有需要修改嗎？
```

### Step 4 — Write to CRM (after confirmation)
1. Create/update Engagement record linked to the Opportunity or Partnership
2. Create Note linked to the same record
3. Update Opportunity/Partnership:
   - `currentStatusSummary` — updated one-para narrative
   - `nextActionSummary` — single line, what needs to happen next
   - `lastUpdateDate` — today
   - `healthCheck` — reassess based on new info
   - `nextFollowUpDate` — if known
4. Create all identified Tasks (see Task creation rules below)
5. Update GBrain company/opportunity page with new intel

---

## Flow B — Sales Rep Mentions a Future Meeting

**Trigger:** "我下週三要跟XXX開會", "demo arranged for 6/16", "scheduled a call", etc.

### What to do
1. Acknowledge the scheduled interaction
2. Ask clarifying questions about what would make the interaction successful (optional, only if there's prep work to do)
3. Create a **Report-Back Task** immediately

### Report-Back Task format
```
Title:    [報回] [Company] — [type] [date] 後補紀錄
Due:      EOD of the meeting day
Body:     「會議後請回來跟 Leo 說：發生了什麼、outcome 是什麼、下一步是什麼。」
          + relevant context: what the goals of the meeting are, who's attending, what to watch for
Linked:   → Opportunity or Partnership record
```

This task appears in the daily briefing on the meeting day and the day after,
ensuring the Rep doesn't forget to report back.

### Clarifying questions for planned meetings (only ask if prep work needed)
- Who is attending? (especially decision-makers / stakeholders)
- What is the goal of this meeting?
- Is there any prep Leo should help with? (deck, cost comparison, demo script)

---

## Flow C — Silence Detection (Automatic)

**Trigger:** Daily health check cron, or Rep asks "what needs attention?"

### Rules
| Silence duration | Action |
|---|---|
| Opportunity: 7+ days no new Engagement | Flag `healthCheck = NEEDS_FOLLOWUP`, create stall Task |
| Opportunity: 14+ days | Flag `healthCheck = AT_RISK`, create urgent stall Task |
| Partnership: 14+ days no new Engagement | Flag `healthCheck = NEEDS_FOLLOWUP`, create stall Task |
| Partnership: 21+ days | Flag `healthCheck = AT_RISK` |

### Stall Task format
```
Title:    [跟進] [Opportunity/Partnership name] — X 天沒有互動紀錄
Body:     「上次互動：[date]。目前狀態：[currentStatusSummary]。
           請確認進展，或更新下一步。」
Agent advice: [specific suggestion based on last known status]
```

---

## Task Creation Rules

Every Task Leo creates must have:
- **Title** — clear, actionable (starts with a verb or bracketed type tag)
- **Due date** — always set one; if uncertain use +3 days as default
- **Body** — context + agent advice ("here's how to approach this", "key points to cover", "relevant docs at X")
- **Linked record** — always link to the Opportunity or Partnership

### Task type prefixes
| Prefix | When to use |
|---|---|
| `[報回]` | Report-back task after a planned meeting — Rep must come back and log what happened |
| `[跟進]` | Follow-up with client / waiting for response |
| `[準備]` | Prep work before a meeting (deck, proposal, research) |
| `[發送]` | Send a document, email, or proposal |
| `[STALL]` | Silence-detected stall alert |
| `[決策]` | Internal decision needed before proceeding |

---

## Clarification Style Rules

- **Ask ONE question at a time.** Never send a bulleted questionnaire.
- **Lead with what you already extracted.** Show your work so the Rep only corrects/adds, not re-explains.
- **Be direct.** "這次談的結論是什麼？" not "Could you please elaborate on the outcome of your discussion?"
- **If you have enough to write — write.** Offer the draft and let the Rep correct it rather than asking upfront.

---

## CRM Write Sequence (reference)

```python
# 1. Create Engagement
mutation {
  createEngagement(data: {
    name: "[Title summary]"
    engagementType: ONLINE   # or INPERSON / PHONE / DEMO / MESSAGING
    engagementDate: "2026-06-16T00:00:00Z"
    outcome: "..."
    nextAction: "..."
    engagementNote: { markdown: "..." }    # detailed narrative
    companyId: "COMPANY_UUID"
    # opportunityId or partnershipId via relation
  }) { id }
}

# 2. Update Opportunity
mutation {
  updateOpportunity(id: "OPP_UUID", data: {
    currentStatusSummary: "..."
    nextActionSummary: "..."
    lastUpdateDate: "2026-06-16T00:00:00Z"
    healthCheck: ON_TRACK    # or NEEDS_FOLLOWUP / AWAITING_RESPONSE / AT_RISK
    nextFollowUpDate: "2026-06-23T00:00:00Z"
  }) { id }
}

# 3. Create Task
mutation {
  createTask(data: {
    title: "[跟進] ..."
    status: TODO
    dueAt: "2026-06-19T12:00:00Z"
    body: "Context + agent advice"
    # link via taskTargets
  }) { id }
}
```

See `twenty-crm` skill for full auth + query patterns.

---

## Quality Bar

Before presenting the CRM write confirmation to the Sales Rep (Step 3 in Flow A):
- The structured summary shows extracted facts (what was said/done) and Leo's interpretation (healthCheck judgment, stage suggestion) in separate lines — not blended into a single narrative?
- `healthCheck` value comes from applying the judgment table to the new information — not inferred from the prior value alone?
- Every Task has a due date — no open-ended tasks with no timeline?
- Any stage advancement recommendation cites the specific criterion met (e.g. "SCREENING → MEETING because meeting completed") — not stated as obvious?
- Report-Back Task (Flow B) created immediately on mention of a future meeting — not deferred to after the meeting?
- No team member names appear in Task bodies, Notes, or Lark notifications?

If any check fails, revise before presenting the confirmation summary.

## Fallback Behavior

- **If CRM is unreachable**: do not attempt to write; present the structured summary as a text block the Sales Rep can reference; offer to retry when CRM is back; do not lose the Sales Rep's update.
- **If GBrain is unreachable**: skip `add_timeline_entry` and `extract_facts`; log this in the session summary; CRM is the primary record — GBrain is supplementary.
- **If Hindsight `{{ORG_PREFIX}}-pipeline` is unreachable**: skip the Hindsight write; note it in the session reply; the CRM Engagement is the authoritative record.
- **If the linked Opportunity or Partnership cannot be found in CRM** (search returns empty): ask the Sales Rep to confirm company name or provide the CRM ID; do not create an unlinked Engagement floating with no parent.
- **If multiple Opportunities match the company name**: present the list with stage and currentStatusSummary for each; ask the Sales Rep to confirm which one — never guess.
- **If the Sales Rep's update is too sparse to extract outcome + next action**: ask ONE targeted question (see Step 2 priority order) — do not write to CRM with unknown outcome or no next action.

## Pitfalls

- **Don't query opportunity by name with `like` filter** — partial name matches often return empty. List all and filter in Python, or use `filter: { id: { eq: "UUID" } }`.
- **Single-record lookup uses filter, not id argument** — `opportunity(id: ...)` throws "Argument not allowed: id". Use `opportunities(filter: { id: { eq: "..." } })` instead.
- **Never create an Engagement for a future event** — use a Report-Back Task instead.
- **Engagement has no status field** — it's a past-tense record. All forward-looking state lives in Tasks and Opportunity/Partnership fields.
- **Always link Tasks to the Opportunity or Partnership** — unlinked tasks are invisible in the pipeline context.
- **bodyV2 not body** — Task and Note body field is `bodyV2: { markdown: "..." }`. `body` does not exist. `bodyV2: { blocks: [...] }` also fails. Verified 2026-06-14.
- **NoteTarget / TaskTarget field naming** — field is `targetOpportunityId` / `targetPartnershipId`, NOT `opportunityId`. Same pattern for both.
- **GBrain update is not optional** — after every logged engagement: `add_timeline_entry` + `extract_facts` if new intel. Then Hindsight retain with opportunity context summary.
- **`engagementNote` is RichText** — use `engagementNote: { markdown: "..." }`, NOT a plain string. Same pattern as `bodyV2` on Task/Note.
- **Engagement Person link field** — `clientAttendeesId` (NOT `personId`, NOT `attendeeId`). Always set this; it's required for Person-only engagements (e.g. Lead Nurturing emails).
- **OutreachMessage ≠ Engagement** — OutreachMessage is a mutable draft (DRAFT→SCHEDULED→SENT lifecycle). Engagement is the immutable log created AFTER something is sent. Never use Engagement as a draft holder.
