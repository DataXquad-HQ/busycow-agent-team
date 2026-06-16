---
name: twenty-crm
description: Query and mutate data in Twenty CRM (the DataXquad CRM system) — read pipeline, update records, create leads, manage contacts.
triggers:
  - "CRM"
  - "pipeline"
  - "opportunity"
  - "partnership"
  - "lead"
  - "prospect"
  - "contact in CRM"
  - "twenty"
  - "update stage"
  - "log interaction"
---

# Twenty CRM Skill

## When to Use

Load this skill whenever another skill or workflow needs to query or mutate data in Twenty CRM. This is the reference layer for all CRM API calls.

---

## Cross-Cutting Rules (apply to ALL CRM skills)

- **Always use "opportunity" not "deal"** — the CRM object is called `opportunities`. Never write "deal" or "deals" in any content, skill, or message. `dealType` is a field name — leave it as-is, but refer to the object itself as "opportunity".
- **Never hardcode team member names** in skill logic, cron prompts, or message drafts. Use "the Sales Rep", "the team", "our BD team".
- **CRM links in human-facing messages always use external URL** — `https://sales.dataxquad.com/objects/[type]/[UUID]`. Never expose `localhost:3001` in Lark messages or notifications.
- **Two-channel delivery pattern** — cron jobs with both a human-facing notification AND an ops log must: (1) push the human notification mid-run via `mcp_lark_im_v1_message_create`, (2) let Hermes auto-deliver the ops log via cron `deliver` to `[System] Backend Report`. Never set cron `deliver` to the human sales channel.

---

## Overview

Twenty CRM runs locally at `http://localhost:3001`. Never use an external URL.

- **API key**: stored in `.env` as `TWENTY_API_KEY`
- **Metadata endpoint**: `POST http://localhost:3001/metadata` — schema introspection only
- **Data endpoint**: `POST http://localhost:3001/graphql` — all reads and writes

## Auth Header Pattern

**Critical — token redaction affects ALL tool surfaces:**
- `write_file` content — any `Bearer <token>` pattern masked
- `terminal << 'HEREDOC'` — same masking
- `execute_code` Python sandbox — token-shaped string literals cause `SyntaxError: unterminated string literal`

**Only safe pattern:** write scripts to disk with `write_file` (loading token from `.env` at runtime, never inline), then run with `terminal python3 /path/to/script.py`. Never pass the token inline in any of the above contexts.

Load token at runtime and build the header by joining a list:

```python
def load_tok():
    with open("/mnt/disks/data/hermes/profiles/leo/.env") as f:
        for line in f:
            line = line.strip()
            if "TWENTY_API_KEY" in line and "=" in line:
                return line.split("=", 1)[1]
    return None

tok = load_tok()

def gql(query, endpoint="http://localhost:3001/graphql"):
    parts = ["Authorization", "Bearer", tok]
    hdr = ": ".join([parts[0], " ".join(parts[1:])])
    resp = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "-H", hdr,
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"query": query}),
         endpoint],
        capture_output=True, text=True
    )
    return json.loads(resp.stdout)
```

Always write scripts to `/mnt/disks/data/hermes/profiles/leo/workspace/` and run with `python3`.

## Core Objects

| Object | Query | Fields |
|---|---|---|
| **Person** | `people`, `person` | name{firstName,lastName}, emails{primaryEmail}, phones, jobTitle, company, status, source, decisionRole, country, preferredChannel, lastContactDate, notes, remarks, meetContext, contactHandle, leadTier |
| **Company** | `companies`, `company` | name, domainName{primaryLinkUrl}, employees, city, linkedinLink |
| **Opportunity** | `opportunities`, `opportunity` | name, stage, businessLine, dealType, healthCheck, priority, amount{amountMicros,currencyCode}, closeDate, nextFollowUpDate, nextActionSummary, currentStatusSummary, overview, company, pointOfContact, owner |
| **Partnership** | `partnerships`, `partnership` | name, stage, status, partnerType, startDate, endDate, currentStatusSummary, nextActionSummary, partnershipOverview, primaryContact, company |
| **Task** | `tasks` | title, status, dueAt, body, taskTargets |
| **Note** | `notes` | title, body, noteTargets |

## Opportunity Stages
`NEW` → `SCREENING` → `MEETING` → `PROPOSAL` → `CUSTOMER`

## Key Enums

**Opportunity:**
- `businessLine`: BUSYCOW, GEOKERNEL, AQUAOPTIMA, TRACI, DISTIFY, DATAXQUAD
- `dealType`: DIRECT, PARTNERLED
- `healthCheck`: ON_TRACK, NEEDS_FOLLOWUP, AWAITING_RESPONSE, AT_RISK
- `priority`: HIGH, MEDIUM, LOW

**Person:**
- `status`: (check schema — e.g. PROSPECT, LEAD, etc.)
- `source`: (check schema)
- `decisionRole`: (check schema)
- `country`: (check schema)
- `preferredChannel`: (check schema)

**Partnership:**
- `stage`: (check schema)
- `status`: (check schema)
- `partnerType`: (check schema)

To check any enum values: `{ __type(name: "EnumName") { enumValues { name } } }` via /graphql

## Common Queries

### List all opportunities with stage
```graphql
{ opportunities(first: 50) { edges { node {
    id name stage businessLine dealType healthCheck priority
    nextFollowUpDate nextActionSummary currentStatusSummary
    amount { amountMicros currencyCode }
    company { name }
    pointOfContact { name { firstName lastName } }
} } } }
```

### Get a single opportunity by ID
```graphql
{ opportunity(id: "UUID") { id name stage ... } }
```

### List all partnerships
```graphql
{ partnerships(first: 50) { edges { node {
    id name stage status partnerType
    currentStatusSummary nextActionSummary
    company { name }
    primaryContact { name { firstName lastName } }
} } } }
```

### List all people
```graphql
{ people(first: 50) { edges { node {
    id name { firstName lastName }
    emails { primaryEmail }
    jobTitle company { name }
    status source lastContactDate
} } } }
```

### Filter by field
```graphql
{ opportunities(filter: { stage: { eq: NEW } }) { edges { node { id name } } } }
```

## Common Mutations

### Update opportunity stage
```graphql
mutation {
  updateOpportunity(id: "UUID", data: { stage: SCREENING }) {
    id stage
  }
}
```

### Update opportunity fields
```graphql
mutation {
  updateOpportunity(id: "UUID", data: {
    nextFollowUpDate: "2026-06-20T00:00:00Z"
    nextActionSummary: "Follow up re proposal"
    healthCheck: ON_TRACK
    priority: HIGH
  }) {
    id name stage
  }
}
```

### Create a person
```graphql
mutation {
  createPerson(data: {
    name: { firstName: "John", lastName: "Doe" }
    emails: { primaryEmail: "john@example.com" }
    jobTitle: "CEO"
    companyId: "COMPANY_UUID"
  }) {
    id name { firstName lastName }
  }
}
```

### Create a company
```graphql
mutation {
  createCompany(data: {
    name: "Acme Corp"
    domainName: { primaryLinkUrl: "https://acme.com", primaryLinkLabel: "acme.com" }
    city: "Hong Kong"
  }) {
    id name
  }
}
```

### Create an opportunity
```graphql
mutation {
  createOpportunity(data: {
    name: "Opportunity name"
    stage: NEW
    businessLine: BUSYCOW
    companyId: "COMPANY_UUID"
    pointOfContactId: "PERSON_UUID"
    overview: "Initial context"
  }) {
    id name stage
  }
}
```

### Create a note on an opportunity
```graphql
mutation {
  createNote(data: {
    title: "Note title"
    body: "Content of the note"
    noteTargets: {
      createMany: {
        data: [{ opportunityId: "OPP_UUID" }]
      }
    }
  }) {
    id title
  }
}
```

## OutreachMessage Custom Object (created 2026-06-15)

Custom object for storing outreach drafts. Separate from Engagement (which is immutable interaction log).

```graphql
{
  outreachMessages(filter: { status: { eq: DRAFT } }) {
    edges { node {
      id name subject status messageType sendMethod channel
      scheduledAt sentAt
      bodyV2 { markdown }
      context
      recipient { id name { firstName lastName } emails { primaryEmail } }
    }}
  }
}
```

Create:
```graphql
mutation {
  createOutreachMessage(data: {
    name: "[subject]"
    subject: "[subject]"
    bodyV2: { markdown: "[body]" }
    context: "[why now]"
    status: DRAFT          # DRAFT | SCHEDULED | SENT | CANCELLED
    messageType: NURTURING # NURTURING | COLD_OUTREACH
    sendMethod: AUTO       # AUTO | MANUAL
    channel: EMAIL
    scheduledAt: "2026-06-16T04:00:00Z"
    recipientId: "PERSON_UUID"
  }) { id }
}
```

Update status after send:
```graphql
mutation {
  updateOutreachMessage(id: "MSG_UUID", data: {
    status: SENT
    sentAt: "[ISO now]"
  }) { id }
}
```

## Schema Introspection Reference

To explore what fields an object has:
```graphql
# via /graphql
{ __type(name: "Opportunity") { fields { name type { name kind } } } }

# or via /metadata for custom objects
{ objects { edges { node { nameSingular fields { edges { node { name label type } } } } } } }
```

To add a new custom field to an existing object, use the metadata API (POST /metadata).

**Step 1 — find the object's metadata ID:**
```python
# The metadata /objects query returns 10 at a time with NO pagination support (no `first`, no `after`).
# Use `notIn` filter to page through manually:
result = meta('{ objects { edges { node { id nameSingular } } } }')
# If target not in first 10, exclude known IDs:
known_ids_json = json.dumps([...list of IDs already seen...])
result2 = meta(f'{{ objects(filter: {{ id: {{ notIn: {known_ids_json} }} }}) {{ edges {{ node {{ id nameSingular }} }} }} }}')
```

Known object IDs (verified 2026-06-15):
- `person`: `5ae439de-e1d6-40f1-846b-a4b482ad665a`
- `company`: `b77d396f-68cf-4ba4-a4ba-c423eed3a922`
- `opportunity`: `61788876-89f8-4ac5-be6d-3d2fb7111b3c`
- `partnership`: `7ef607fd-6b4d-4b87-ab96-60393f06af33`
- `engagement`: `5de654a0-96b3-484a-b80e-b35b5b276a6d`
- `task`: `a0ef39a6-8619-4ab7-a6ce-db4b85a33c81`

**Step 2 — create the field (correct mutation is `createOneField`, NOT `createField`):**
```python
# objectMetadataId goes INSIDE the field block, not in the outer input
mutation = {
    "query": """
mutation CreateField($input: CreateOneFieldMetadataInput!) {
  createOneField(input: $input) { id name label type }
}
""",
    "variables": {
        "input": {
            "field": {
                "type": "TEXT",           # or SELECT, DATE_TIME, etc.
                "name": "myField",
                "label": "My Field",
                "description": "Description",
                "objectMetadataId": "OBJECT_UUID"   # ← inside field, not input
            }
        }
    }
}
# For SELECT fields, pass options as a list in variables (not inline GQL literals):
# "options": [{"value": "VAL", "label": "Label", "color": "gray", "position": 0}, ...]
```

**Step 3 — update a field's options (e.g. add enum value):**
```python
# First find the field ID — /metadata fields query also caps at 10, filter by isCustom:
# { fields(filter: { objectMetadataId: { eq: "OBJ_ID" }, isCustom: { is: true } }) { ... } }
# Use notIn on id to page through if > 10 custom fields.
# BooleanFieldComparison uses `is`/`isNot`, not `eq`.

# Update mutation — objectMetadataId is NOT in UpdateOneFieldMetadataInput, only id + update:
mutation = {
    "query": """
mutation UpdateField($input: UpdateOneFieldMetadataInput!) {
  updateOneField(input: $input) { id name options }
}
""",
    "variables": {
        "input": {
            "id": "FIELD_UUID",
            "update": {
                "options": [...full options list including new values...]
            }
        }
    }
}
# IMPORTANT: pass the FULL options list, not just the new one. It replaces, not appends.
```

## Reference Files

- `references/live-schema-snapshot.md` — verified enum values, field list, object counts, and schema divergence notes from 2026-06-15 introspection
- `references/metadata-api-patterns.md` — how to add custom fields/objects/enums via the metadata API; pagination workarounds; known object metadata IDs
- `references/outreach-message-schema.md` — OutreachMessage custom object: full field list, lifecycle, and GraphQL patterns
- `scripts/twenty_query_template.py` — copy-paste baseline script with safe token loading and gql() helper; copy to workspace/ and run with `python3`
- `scripts/add_person_field.py` — working template for adding a custom field to Person via metadata API; edit constants and run
- `scripts/find_object_fields.py` — paginate through all custom fields on any object; handles the 10-item metadata API cap

## Pitfalls

- The `/api` REST endpoint returns 404 — always use `/graphql` for data
- The `/metadata` endpoint is only for schema introspection, not data queries
- When filtering enums, use the value without quotes: `{ stage: { eq: NEW } }` not `{ stage: { eq: "NEW" } }`
- Amount is stored as `amountMicros` (millionths of currency unit) — divide by 1,000,000 for display
- The `partnership` and `opportunity` single-record queries by ID can return null if the record was soft-deleted
- When writing scripts: always load the token from env at runtime; never hardcode or pass via string interpolation in write_file (gets redacted)
- Build auth header as: `parts = ["Authorization", "Bearer", tok]; hdr = ": ".join([parts[0], " ".join(parts[1:])])`
- **`opportunity(id: "UUID")` throws "Argument not allowed: id"** — single-record lookup by direct id arg is not supported. Use `opportunities(filter: { id: { eq: "UUID" } })` and take `edges[0].node`
- **`taskTarget` and `noteTarget` link field is `targetOpportunityId`**, not `opportunityId`. Full set: `targetOpportunityId`, `targetPartnershipId`, `targetPersonId`, `targetCompanyId`, `targetEngagementId`
- **`Note.body` does not exist** — the rich text field is `bodyV2`. Use `bodyV2: { markdown: "..." }`. Do NOT pass `{ blocks: [...] }` — that throws "Invalid subfield 'blocks'". The `markdown` subfield is the reliable path
- **`Note.body` vs `bodyV2`**: same pattern applies to `Task` — body field is `bodyV2: { markdown: "..." }` not `body: "..."`
- **`engagementNote` is a RichText field** — use `{ markdown: "..." }` NOT a plain string
- **`clientAttendeesId` not `personId`** — Engagement's person relation field is `clientAttendeesId`
- **Metadata API `/objects` caps at 10, no cursor** — paginate using `filter: { id: { notIn: [...known_ids] } }`. See `references/metadata-api-patterns.md` for known object IDs
- **Metadata `createOneField` not `createField`** — mutation name changed; `objectMetadataId` goes inside `field` not in `input`
- **`UpdateOneFieldMetadataInput` does NOT have `objectMetadataId`** — only `id` + `update` are valid
- **OutreachMessage body field is `body`, NOT `bodyV2`** — the custom object uses `body: { markdown: "..." }` (RichText). `bodyV2` does not exist on this object. Confirmed via introspection 2026-06-15.
- **CRM links for humans use external URL** — `https://sales.dataxquad.com/objects/[type]/[UUID]`, never `localhost:3001`
- Best pattern: write full script to `/mnt/disks/data/hermes/profiles/leo/workspace/`, run with `terminal python3 /path/script.py`
- **`opportunity(id: "...")` throws "Argument not allowed: id"** — single-record lookup does NOT accept `id` as a direct argument. Use `opportunities(filter: { id: { eq: "UUID" } }) { edges { node { ... } } }` and take `edges[0]`
- **`filter: { name: { like: "%partial%" } }` on opportunities is unreliable** — often returns empty even when records exist. Safer: list all with `opportunities(first: 100)` and filter by name in Python. Same applies to other objects.

## Metadata API Pitfalls (field/schema mutations)

- **Wrong mutation name** — it is `createOneField`, NOT `createField`. The error "Did you mean createOneField?" is the hint.
- **`objectMetadataId` placement** — goes INSIDE the `field` block, NOT in the outer `input`. `CreateOneFieldMetadataInput` only has one field: `field`.
- **`updateOneField` input shape** — `UpdateOneFieldMetadataInput` only has `id` + `update`. No `objectMetadataId` at the top level.
- **`objects` query caps at 10, no pagination** — `first` and `after` are not supported. Use `notIn` filter with already-seen IDs to surface the rest. Person object is NOT in the first 10 — it is at position 19+.
- **`fields` query also caps at 10** — same pattern: use `notIn` on id to page through. Filter by `isCustom: { is: true }` (BooleanFieldComparison uses `is`/`isNot`, not `eq`).
- **`object(id).fields` also caps at 10** — `first` argument not supported on nested fields either. Use top-level `fields(filter: { objectMetadataId: { eq: "..." } })` instead.
- **SELECT field options must be a full replacement** — `updateOneField` replaces the options array entirely. Always pass the complete list including existing values when adding a new enum option.
- **`FieldFilter` only supports**: `id`, `isCustom`, `isActive`, `isSystem`, `isUIReadOnly`, `objectMetadataId` — no `name` filter. To find a specific field by name, fetch all and filter in Python.
