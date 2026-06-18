# CRM Write Patterns — Verified Field Names

Verified live against Twenty CRM GraphQL API 2026-06-14.
These correct field names were discovered during live production use.

---

## TaskTarget — link a Task to a record

```graphql
mutation {
  createTaskTarget(data: {
    taskId: "TASK_UUID"
    targetOpportunityId: "OPP_UUID"      # ← NOT opportunityId
    # also: targetPartnershipId, targetPersonId, targetCompanyId, targetEngagementId
  }) { id }
}
```

## NoteTarget — link a Note to a record

```graphql
mutation {
  createNoteTarget(data: {
    noteId: "NOTE_UUID"
    targetOpportunityId: "OPP_UUID"      # ← NOT opportunityId
    # also: targetPartnershipId, targetPersonId, targetCompanyId, targetEngagementId
  }) { id }
}
```

## Note — create with body

```graphql
mutation CreateNote($data: NoteCreateInput!) {
  createNote(data: $data) { id title }
}
# variables:
{
  "data": {
    "title": "Note title",
    "bodyV2": { "markdown": "**Content** in markdown" }   # ← NOT body, NOT bodyV2: { blocks: [...] }
  }
}
```

## Task — create with body

```graphql
mutation {
  createTask(data: {
    title: "[報回] Company — date 後補紀錄"
    status: TODO
    dueAt: "2026-06-16T15:00:00Z"
    bodyV2: { markdown: "Context + agent advice here" }   # ← NOT body
  }) { id title }
}
```

## Opportunity — single record lookup

```graphql
# ❌ WRONG — throws "Argument not allowed: id"
{ opportunity(id: "UUID") { id name } }

# ✅ CORRECT
{ opportunities(filter: { id: { eq: "UUID" } }) {
    edges { node { id name stage } }
} }
```

## Opportunity — update with amount

```graphql
mutation {
  updateOpportunity(id: "OPP_UUID", data: {
    amount: { amountMicros: "300000000000", currencyCode: "TWD" }
    # amountMicros = value × 1,000,000 (e.g. TWD 300,000 = 300_000 × 1_000_000 = 300_000_000_000)
    nextFollowUpDate: "2026-06-16T00:00:00Z"
    nextActionSummary: "One-line next action"
    healthCheck: AT_RISK   # enum without quotes
  }) { id name amount { amountMicros currencyCode } }
}
```

---

## Full write sequence — log interaction for an Opportunity

```python
OPP_ID = "..."
COMPANY_ID = "..."

# 1. Update opportunity fields
gql(f"""mutation {{
  updateOpportunity(id: "{OPP_ID}", data: {{
    currentStatusSummary: "..."
    nextActionSummary: "..."
    healthCheck: ON_TRACK
    nextFollowUpDate: "2026-06-23T00:00:00Z"
    lastUpdateDate: "2026-06-14T00:00:00Z"
  }}) {{ id }}
}}""")

# 2. Create task (use variables to avoid escaping issues with markdown body)
task_result = gql("""mutation CreateTask($data: TaskCreateInput!) {
  createTask(data: $data) { id }
}""", variables={"data": {
    "title": "[跟進] Company — follow up on proposal",
    "status": "TODO",
    "dueAt": "2026-06-17T12:00:00Z",
    "bodyV2": {"markdown": "**Context:** ...\n**Goal:** ...\n**Approach:** ..."}
}})
task_id = task_result["data"]["createTask"]["id"]

# 3. Link task to opportunity
gql(f"""mutation {{
  createTaskTarget(data: {{
    taskId: "{task_id}"
    targetOpportunityId: "{OPP_ID}"
  }}) {{ id }}
}}""")

# 4. Create note
note_result = gql("""mutation CreateNote($data: NoteCreateInput!) {
  createNote(data: $data) { id }
}""", variables={"data": {
    "title": "Interaction summary title",
    "bodyV2": {"markdown": "**Outcome:** ...\n\n**Next action:** ...\n\n**Context:** ..."}
}})
note_id = note_result["data"]["createNote"]["id"]

# 5. Link note to opportunity
gql(f"""mutation {{
  createNoteTarget(data: {{
    noteId: "{note_id}"
    targetOpportunityId: "{OPP_ID}"
  }}) {{ id }}
}}""")
```
