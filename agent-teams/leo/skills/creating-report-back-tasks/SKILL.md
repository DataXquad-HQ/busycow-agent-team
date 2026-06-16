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
  - "report back task"
  - "next week's meeting"
  - "call tomorrow"
  - "arranged a demo"
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

> "Report-Back Task created:
> 📅 **[Log Interaction] CompanyName — Call on June 17**
> Message me after the call with what happened and I'll log it for you."

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
