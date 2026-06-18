---
name: creating-report-back-tasks
description: >
  When a future meeting, call, or demo is mentioned, immediately create a
  Report-Back Task in Twenty CRM so Leo can detect if the interaction was
  never logged. The mechanism by which Leo tracks "planned but never reported"
  interactions. Used in C4 (Opportunity) and C5 (Partnership) flows.
triggers:
  - "we have a meeting on"
  - "call scheduled for"
  - "demo next week"
  - "meeting tomorrow"
  - "I'll be talking to them on"
  - "create report back task"
  - "報回 task"
  - "下週有個 meeting"
  - "明天有通電話"
  - "安排了一個 demo"
version: "1.0"
author: {{COMPANY_NAME}}/Leo
---

# Create Report-Back Task

> When a Sales Rep mentions a future meeting, call, or demo — Leo immediately
> creates a Report-Back Task. This is the mechanism by which Leo detects
> "the meeting was planned but never reported."

---

## Purpose

When Hunter mentions a planned future interaction, Leo:
1. Creates a **Report-Back Task** due on the meeting date EOD
2. Links it to the relevant Opportunity or Partnership in Twenty CRM
3. After the due date, if no new Engagement (Note) exists → Task appears overdue → surfaces in daily briefing

This closes the loop: if the Task goes overdue, either the meeting didn't happen, or it wasn't logged. Either way, Leo flags it.

---

## Trigger Signals

Create a Report-Back Task whenever the Sales Rep mentions:
- A scheduled meeting / call / demo
- A planned follow-up conversation
- "I'm meeting them on [date]"
- "We have a call next [weekday]"
- Any future interaction with a named company or person

Leo should do this **proactively** — even if the Sales Rep doesn't explicitly ask.

---

## Task Format

```
Title:  [Log Interaction] [Company] — [interaction type] on [date]
Status: TODO
Due:    [meeting date] EOD (23:59 local time, or use 15:00 UTC as proxy)
Owner:  [Sales Rep]
Priority: Medium
```

**Body (agent advice):**
```
📌 Context: [Company] [interaction type] scheduled for [date].
   This task is a reminder to report back to Leo after the meeting so the
   interaction gets logged in CRM.

🎯 Goal: Report back to Leo with what happened — outcome, decisions, next steps.
   Leo will then create the Engagement record and any follow-up Tasks.

💡 Suggested: After the meeting, just message Leo with a quick update.
   Even a one-liner is enough to start — Leo will ask clarifying questions.
```

---

## Step-by-Step

### Step 1 — Identify

Extract from what the Sales Rep said:
- **Company name** (look up in CRM if needed)
- **Interaction type** — Meeting / Call / Demo / Contract Review / etc.
- **Date** — confirm if ambiguous (e.g. "next Tuesday" → resolve to exact date)
- **Linked record** — which Opportunity or Partnership does this relate to?

### Step 2 — Look Up Parent Record

Find the active Opportunity or Partnership for this company:

```graphql
{
  opportunities(filter: {
    name: { like: "%CompanyName%" }
    stage: { notIn: [CUSTOMER] }
  }) {
    edges { node { id name stage currentStatusSummary } }
  }
}
```

Or for Partnership:
```graphql
{
  partnerships(filter: {
    name: { like: "%CompanyName%" }
  }) {
    edges { node { id name stage } }
  }
}
```

> If multiple records found, ask Sales Rep to confirm which one.

### Step 3 — Create the Task

```graphql
mutation CreateTask($data: TaskCreateInput!) {
  createTask(data: $data) { id }
}
# variables:
{
  "data": {
    "title": "[Log Interaction] CompanyName — Call on 2026-06-17",
    "status": "TODO",
    "dueAt": "2026-06-17T15:00:00Z",
    "bodyV2": {
      "markdown": "📌 **Context:** CompanyName call scheduled for 2026-06-17.\nThis task is a reminder to report back to Leo after the call so the interaction gets logged in CRM.\n\n🎯 **Goal:** Report back to Leo with outcome, decisions, and next steps.\n\n💡 **Suggested:** After the call, message Leo with a quick update — even a one-liner is fine."
    }
  }
}
```

> **Pitfall:** Body field is `bodyV2: { markdown: "..." }` — NOT `body`, NOT `bodyV2: { blocks: [...] }`.

### Step 4 — Link Task to Parent Record

```graphql
mutation {
  createTaskTarget(data: {
    taskId: "TASK_UUID"
    targetOpportunityId: "OPP_UUID"       # for C4
    # targetPartnershipId: "PART_UUID"    # for C5
  }) { id }
}
```

> **Pitfall:** Field is `targetOpportunityId` / `targetPartnershipId` — NOT `opportunityId`.

### Step 5 — Confirm to Sales Rep

After creating:

> 「已幫你建好報回 Task：
> 📅 **[Log Interaction] CompanyName — Call on June 17**
> 到時候通完話跟我說一下結果，我來幫你記進去。」

---

## What Happens Next (Detection Loop)

After the due date, Leo's daily briefing checks for overdue Report-Back Tasks:

```
For each overdue Task with title starting with "[Log Interaction]":
  Check if a new Engagement (Note) exists for the linked record since the task was created
  If NO new Engagement found:
    → Flag in daily briefing: "Meeting with [Company] on [date] — interaction not yet logged"
    → Prompt Sales Rep to report back
```

This is how Leo maintains the detection loop without asking the Sales Rep to remember to report.

> **Who runs the detection loop?**
> The `sending-daily-pipeline-reminder` cron (runs every morning) is responsible for
> scanning overdue `[Log Interaction]` tasks and surfacing flags. This skill only
> creates the task — it does not perform the detection. If overdue tasks are not
> appearing in the daily briefing, check that the daily reminder cron is active and
> that it is querying tasks with `status: TODO` and `dueAt` in the past.

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
| Creating Report-Back Tasks | ✅ Autonomous — do it proactively |
| Linking Task to Opportunity / Partnership | ✅ Autonomous |
| Resolving ambiguous date ("next Tuesday") | ✅ Autonomous — confirm if uncertain |
| Selecting correct Opportunity if multiple | ⚠️ Ask Sales Rep to confirm |

---

## Fallback Behavior

- **If CRM is unreachable**: do not silently skip; inform the Sales Rep: "CRM is currently unavailable — I wasn't able to create the Report-Back Task for [Company] [date]. Please remind me when CRM is back, or create it manually." Store the pending task detail in the session reply so it isn't lost.
- **If no active Opportunity or Partnership is found for the company**: create the Task without a linked parent record; note in the Task body "No active Opportunity/Partnership found — task is unlinked"; inform the Sales Rep and ask if a new opportunity should be created.
- **If multiple Opportunities match the company** and the Sales Rep hasn't specified: present the options and ask which one to link — do not default to the first match.
- **If the meeting date is ambiguous** (e.g. "next Tuesday") and Leo is uncertain: resolve it using today's date context; if still uncertain, ask once before creating the task — a wrong due date defeats the purpose of the detection loop.

## Pitfalls

- **Create proactively.** Don't wait to be asked. If a future meeting is mentioned, create the Task immediately.
- **`bodyV2` not `body`.** Always use `bodyV2: { markdown: "..." }`.
- **`targetOpportunityId` not `opportunityId`.** Use the correct TaskTarget field.
- **Date ambiguity.** "Next Tuesday" needs to be resolved to an exact date. Confirm if you're not certain of the date.
- **Multiple matching records.** If more than one active Opportunity or Partnership matches the company, ask which one.

---

## References

- `references/crm-write-patterns.md` (in log-engagement skill) — Verified CRM field names and full write sequence
- `pipeline-design-decisions.md` — Decision 3: Report-Back Task design rationale
