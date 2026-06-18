---
name: twenty-crm
description: >
  Use when any agent needs to read, write, configure, or query Twenty CRM.
  Covers authentication, GraphQL CRUD, schema introspection, custom objects/fields,
  and common pitfalls. Load this skill before writing any Twenty API code.
  Works across all Hermes profiles — ALWAYS call http://localhost:3001 (never
  Tailscale IP or Cloudflare external URL — those are browser-only).
triggers:
  - "twenty crm"
  - "twenty api"
  - "crm query"
  - "crm write"
  - "twenty graphql"
  - "read from twenty"
  - "write to twenty"
  - "twenty schema"
  - "twenty object"
  - "twenty field"
version: "1.0"
author: BusyCow
---

# Twenty CRM — Universal Access Skill

## References

This shared skill is intentionally generic. Any deployment-specific IDs or credentials should be kept outside the package and injected during installation.

---

## ⚠️ Access Rule (ALL agents, ALL profiles)

**Always use the internal VM endpoint:**

| Purpose | URL |
|---------|-----|
| Data CRUD | `http://localhost:3001/graphql` |
| Schema / metadata | `http://localhost:3001/metadata` |
| Health check | `http://localhost:3001/healthz` |
| MCP server | `http://localhost:3001/mcp` |
| REST API | `http://localhost:3001/api` |

**Never use** external browser-access URLs in agent code. Use the internal localhost endpoint for all agent operations.

---

## Authentication

### API Key (preferred for agents)

API keys are long-lived JWTs. Store in a file — never interpolate in shell:

```bash
echo "<paste API key token here>" > /tmp/twenty_token.txt
```

```python
TOKEN = open('/tmp/twenty_token.txt').read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
```

Get/regenerate via UI: **Settings → API & Webhooks → API Keys → Generate API Key**

> ⚠️ `/tmp` is cleared on VM restart. Regenerate token at start of each agent session.

### Token Refresh Flow (when token expires / UNAUTHENTICATED error)

```python
import requests

BASE = "http://localhost:3001/metadata"

def gql(query, token=None, url=BASE):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return requests.post(url, json={"query": query}, headers=h).json()

# Step 1: get loginToken
r1 = gql('mutation { getLoginTokenFromCredentials(email: "{{TWENTY_ADMIN_EMAIL}}", password: "{{TWENTY_ADMIN_PASSWORD}}", origin: "http://localhost:3001") { loginToken { token } } }')
login_token = r1["data"]["getLoginTokenFromCredentials"]["loginToken"]["token"]

# Step 2: exchange → accessToken
# IMPORTANT: field is "accessOrWorkspaceAgnosticToken", NOT "accessToken"
r2 = gql(f'mutation {{ getAuthTokensFromLoginToken(loginToken: "{login_token}", origin: "http://localhost:3001") {{ tokens {{ accessOrWorkspaceAgnosticToken {{ token }} refreshToken {{ token }} }} }} }}')
access_token = r2["data"]["getAuthTokensFromLoginToken"]["tokens"]["accessOrWorkspaceAgnosticToken"]["token"]

# Step 3: generate API key token
API_KEY_ID = "{{TWENTY_API_KEY_ID}}"
r3 = gql(f'mutation {{ generateApiKeyToken(apiKeyId: "{API_KEY_ID}", expiresAt: "2027-01-01T00:00:00Z") {{ token }} }}', access_token)
api_token = r3["data"]["generateApiKeyToken"]["token"]

with open("/tmp/twenty_token.txt", "w") as f:
    f.write(api_token)
print("Token ready.")
```

**Pitfalls:**
- `getLoginTokenFromCredentials` and `getAuthTokensFromLoginToken` both require `origin` param
- `accessOrWorkspaceAgnosticToken` — NOT `accessToken`
- `generateApiKeyToken` requires the **accessToken** from step 2, not loginToken
- All three mutations go to `/metadata`, not `/graphql`

**Deployment placeholders:**
- Admin email: `{{TWENTY_ADMIN_EMAIL}}`
- Admin password: `{{TWENTY_ADMIN_PASSWORD}}`
- API Key ID: `{{TWENTY_API_KEY_ID}}`
- Workspace ID: `{{TWENTY_WORKSPACE_ID}}`

---

## Python Helper (copy-paste baseline)

```python
import requests, json

TOKEN = open('/tmp/twenty_token.txt').read().strip()
GQL  = "http://localhost:3001/graphql"
META = "http://localhost:3001/metadata"

def gql(query, url=GQL, variables=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    d = r.json()
    if d.get("errors"):
        print("GraphQL errors:", json.dumps(d["errors"], indent=2))
    return d
```

---

## Reading Data (CRUD — /graphql)

### List records

```python
# Standard object (company, person, opportunity, note, task)
r = gql("{ companies { edges { node { id name } } } }")

# With filters
r = gql("""
{
  companies(filter: { name: { like: "%Acme%" } }) {
    edges { node { id name } }
  }
}
""")

# Custom object (e.g. partner, invoice, quotation)
r = gql("{ partners { edges { node { id name partnerStage } } } }")
```

### Get single record

```python
r = gql(f'{{ company(id: "{record_id}") {{ id name annualRevenue }} }}')
```

### Create record

```python
r = gql("""
mutation {
  createCompany(data: {
    name: "Acme Corp"
    domainName: { primaryLinkUrl: "acme.com", primaryLinkLabel: "Acme" }
  }) { id name }
}
""")
```

### Update record

```python
r = gql(f"""
mutation {{
  updateCompany(id: "{record_id}", data: {{
    annualRevenue: {{ amountMicros: "5000000000", currencyCode: "USD" }}
  }}) {{ id name }}
}}
""")
```

### Delete record

```python
r = gql(f'mutation {{ deleteCompany(id: "{record_id}") {{ id }} }}')
```

---

## Schema Introspection

### List all queryable objects (including standard)

```python
r = gql("{ __schema { queryType { fields { name } } } }", url=META)
all_objects = sorted([f["name"] for f in r["data"]["__schema"]["queryType"]["fields"]])
```

### List custom objects only (via /metadata)

```python
r = gql("{ objects { edges { node { id nameSingular labelSingular isSystem isCustom } } } }", url=META)
custom = [n["node"] for n in r["data"]["objects"]["edges"] if n["node"]["isCustom"]]
```

> **Important:** Standard objects (`company`, `person`, `opportunity`, `note`, `task`) do NOT appear in `/metadata` objects query. They are always queryable via `/graphql`. Use DB query to get their metadata IDs.

### Get standard object metadata IDs (from DB)

```bash
docker exec twenty-db-1 psql -U twenty -d default -c \
  "SELECT \"nameSingular\", id FROM core.\"objectMetadata\" WHERE \"nameSingular\" IN ('company','person','opportunity');"
```

**Standard object metadata IDs are deployment-specific. Query them from DB or metadata when needed.**

---

## Schema Management — Custom Objects & Fields

### Create custom object

```python
r = gql("""
mutation {
  createOneObject(input: { object: {
    nameSingular: "quotation"
    namePlural: "quotations"
    labelSingular: "Quotation"
    labelPlural: "Quotations"
    description: "Sales quotation"
    icon: "IconFileText"
  }}) { id nameSingular }
}
""", url=META)
# Note: "object:" wrapper is required — omitting it causes validation error
```

### Add field to object

```python
OBJECT_ID = "..."  # from createOneObject or DB

r = gql(f"""
mutation {{
  createOneField(input: {{ field: {{
    objectMetadataId: "{OBJECT_ID}"
    name: "quotationId"
    label: "Quotation ID"
    type: TEXT
  }} }}) {{ id name }}
}}
""", url=META)
```

**Field types:** `TEXT`, `NUMBER`, `DATE_TIME`, `BOOLEAN`, `LINKS`, `SELECT`, `MULTI_SELECT`, `CURRENCY`, `FULL_NAME`, `EMAIL`, `PHONE`, `RELATION`

### Add SELECT field (must use variables — not inline)

```python
import uuid

mutation = """
mutation CreateField($input: CreateOneFieldMetadataInput!) {
  createOneField(input: $input) { id name }
}"""

variables = {
    "input": {
        "field": {
            "objectMetadataId": OBJECT_ID,
            "name": "status",
            "label": "Status",
            "type": "SELECT",
            "options": [
                {"id": str(uuid.uuid4()), "value": "DRAFT", "label": "Draft", "color": "GRAY", "position": 0},
                {"id": str(uuid.uuid4()), "value": "ACTIVE", "label": "Active", "color": "GREEN", "position": 1},
            ]
        }
    }
}

r = gql(mutation, url=META, variables=variables)
```

**SELECT option required fields:** `id` (UUID), `value`, `label`, `color` (ALL_CAPS enum), `position` (int). Missing any → "Multiple validation errors".

**Color enum values:** `GRAY`, `BLUE`, `GREEN`, `RED`, `YELLOW`, `ORANGE`, `PURPLE`, `TURQUOISE`, `SKY`, `PINK`

### Reserved field names (will be rejected)

`currency`, `name`, `id`, `createdAt`, `updatedAt`, `deletedAt`

---

## Example Object Map

### Standard objects

| Object | Query name | Purpose |
|--------|-----------|---------|\n| Company | `companies` | Accounts — clients, prospects, partners |
| Person | `people` | Contacts |
| Opportunity | `opportunities` | Sales deals |
| Note | `notes` | Interaction logs, meeting notes |
| Task | `tasks` | Action items with due dates |

### Custom objects

| Object | Query name | Object ID | Purpose |
|--------|-----------|-----------|---------|\n| Partnership | `partnerships` | — | Partner relationship pipeline |
| Engagement | `engagements` | `{{OBJECT_ID}}` | Immutable interaction log |
| OutreachMessage | `outreachMessages` | — | Outreach email drafts/queue |
| Partner | `partners` | `{{OBJECT_ID}}` | Partnership pipeline (legacy) |
| Quotation | `quotations` | `{{OBJECT_ID}}` | Sales quotations |
| Quotation Item | `quotationItems` | `{{OBJECT_ID}}` | Quotation line items |
| Invoice | `invoices` | `{{OBJECT_ID}}` | Invoices |
| Invoice Item | `invoiceItems` | `{{OBJECT_ID}}` | Invoice line items |

### Company custom fields (example additions)

| Field | Type | Purpose |
|-------|------|---------|\n| `shortName` | TEXT | Short/common name |
| `companyType` | SELECT | Client / Prospect / Partner / Vendor |
| `source` | SELECT | How we met them |

### Person custom fields (example additions)

| Field | Type | Purpose |
|-------|------|---------|\n| `decisionRole` | SELECT | Champion / Decision Maker / Influencer / Blocker |
| `source` | SELECT | How we met them |
| `whatsapp` | TEXT | WhatsApp number |
| `notes` | TEXT | Free-form notes |
| `leadTier` | SELECT | COLD / NURTURE / OPPORTUNITY — outreach priority tier |
| `lastContactDate` | DATE_TIME | Last time we contacted this person |
| `lastEnrichedDate` | DATE_TIME | Last time account intel was refreshed |

### Opportunity fields (pipeline-specific)

| Field | Type | Values / Notes |
|-------|------|---------------|
| `stage` | SELECT | `NEW` → `SCREENING` → `MEETING` → `PROPOSAL` → `CUSTOMER` |
| `businessLine` | SELECT | Deployment-specific values such as product or business-line names |
| `dealType` | SELECT | `DIRECT`, `PARTNERLED` |
| `healthCheck` | SELECT | `ON_TRACK`, `NEEDS_FOLLOWUP`, `AWAITING_RESPONSE`, `AT_RISK` |
| `priority` | SELECT | `HIGH`, `MEDIUM`, `LOW` |
| `nextFollowUpDate` | DATE_TIME | When to follow up next |
| `nextActionSummary` | TEXT | What to do next |
| `currentStatusSummary` | TEXT | Current deal status |

### Partnership fields

| Field | Type | Notes |
|-------|------|-------|
| `stage` | SELECT | Check schema for values |
| `status` | SELECT | Check schema for values |
| `partnerType` | SELECT | Check schema for values |
| `currentStatusSummary` | TEXT | — |
| `nextActionSummary` | TEXT | — |
| `partnershipOverview` | TEXT | — |
| `primaryContact` | RELATION | Person |
| `company` | RELATION | Company |

---

## Engagement Object (Immutable Interaction Log)

Engagement = a completed interaction that actually happened. **Never create an Engagement for a draft or planned action.** Use Note for plans; use Task for follow-ups.

```graphql
mutation {
  createEngagement(data: {
    type: EMAIL                        # EMAIL | MEETING | CALL | DEMO
    status: COMPLETED
    engagementNote: { markdown: "Summary of what happened" }
    startedAt: "2026-06-16T10:00:00Z"
    clientAttendeesId: "PERSON_UUID"   # NOT personId — field is clientAttendeesId
    companyId: "COMPANY_UUID"
    opportunityId: "OPPORTUNITY_UUID"  # optional
  }) {
    id type status
  }
}
```

**After creating Engagement**, always update:
1. `person.lastContactDate` → ISO timestamp
2. Opportunity `healthCheck` / `nextFollowUpDate` / `nextActionSummary` if relevant

---

## OutreachMessage Object (Outreach Draft Queue)

Custom object for storing Leo's outreach drafts before sending.

```graphql
# Query drafts awaiting review
{
  outreachMessages(filter: { status: { eq: DRAFT } }) {
    edges { node {
      id name subject status messageType sendMethod channel
      scheduledAt sentAt
      body { markdown }
      context
      recipient { id name { firstName lastName } emails { primaryEmail } }
    }}
  }
}
```

**Status lifecycle:** `DRAFT` → `SCHEDULED` → `SENT` | `CANCELLED`

```graphql
# Create draft
mutation {
  createOutreachMessage(data: {
    name: "[subject]"
    subject: "[subject]"
    body: { markdown: "[email body]" }     # field is `body`, NOT `bodyV2`
    context: "[why sending now]"
    status: DRAFT
    messageType: NURTURING                  # NURTURING | COLD_OUTREACH
    sendMethod: AUTO                        # AUTO | MANUAL
    channel: EMAIL
    scheduledAt: "2026-06-17T04:00:00Z"
    recipientId: "PERSON_UUID"
  }) { id }
}

# Update after send
mutation {
  updateOutreachMessage(id: "MSG_UUID", data: {
    status: SENT
    sentAt: "2026-06-17T04:01:00Z"
  }) { id }
}
```

**Cross-cutting rules for outreach:**
- CRM API calls: always `http://localhost:3001/graphql`
- Human-facing CRM links: always `{{CRM_EXTERNAL_URL}}/objects/[type]/[UUID]` — never expose localhost
- Never reference team members by name in messages — use "the team" or "our BD team"

---

## Note vs Task (when to use which)

| Object | Use for |
|--------|---------|
| `note` | Information records — meeting summaries, account intel, research |
| `task` | Action items — follow-ups, deadlines, assignees |

Prefer `note` + `task` over any custom `activity` object — better UI integration (Timeline, auto-relate to company/person).

---

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| `UNAUTHENTICATED` / `Token invalid` | Token expired | Run token refresh flow above |
| `Multiple validation errors` | (a) field already exists, (b) reserved name, (c) schema cache stale | Check DB first; restart server if (c) |
| `Field "CreateOneObjectInput.object" not provided` | Missing `object:` wrapper in createOneObject | Add `input: { object: { ... } }` |
| Object not in `/metadata` objects query | Standard objects don't appear there | Use `/graphql` directly; get IDs from DB |
| SELECT options failing | Missing `id` or `position` in options | Use variables approach, include all 5 fields |
| Schema cache stale after object creation | Server needs restart | `cd /mnt/disks/data/twenty && docker compose restart twenty-server-1` |
| Filter on `/metadata` objects not working | `filter` arg not supported on metadata API | Fetch all, filter in Python |
| `opportunity(id: "UUID")` throws "Argument not allowed: id" | Single-record lookup by direct `id` arg not supported | Use `opportunities(filter: { id: { eq: "UUID" } })` → `edges[0].node` |
| `filter: { name: { like: "%partial%" } }` returns empty | Name filtering on opportunities is unreliable | List all with `first: 100`, filter by name in Python |
| Engagement create fails with "field not found: personId" | Relation field is `clientAttendeesId`, NOT `personId` | Use `clientAttendeesId: "PERSON_UUID"` |
| `Note.body` / `Task.body` missing | Rich text field is `bodyV2`, not `body` | Use `bodyV2: { markdown: "..." }` — NOT `{ blocks: [...] }` |
| `OutreachMessage.bodyV2` missing | OutreachMessage custom object uses `body`, not `bodyV2` | Use `body: { markdown: "..." }` on OutreachMessage |
| `engagementNote` rejected as plain string | `engagementNote` is RichText | Use `engagementNote: { markdown: "..." }` |
| Metadata `/objects` only returns 10 results | No cursor pagination on metadata API | Paginate with `filter: { id: { notIn: [...known_ids] } }` |
| Wrong mutation for field creation | Correct name is `createOneField`, not `createField` | Use `createOneField`; `objectMetadataId` goes inside `field {}`, not in `input {}` |
| `updateOneField` rejects `objectMetadataId` | Not valid in update input | `UpdateOneFieldMetadataInput` only accepts `id` + `update` |
| SELECT enum update loses existing options | Options array is replaced entirely | Always pass full list including existing values |
| `taskTarget` / `noteTarget` relation field wrong name | Field is `target[Object]Id`, not `[object]Id` | Use `targetOpportunityId`, `targetPersonId`, `targetCompanyId`, etc. |

### Diagnose "Multiple validation errors" properly

```python
errors = d.get("errors", [])
for e in errors:
    ext = e.get("extensions", {})
    print(json.dumps(ext.get("errors", {}), indent=2))
```

---

## Server Management

```bash
# Health check
curl -sf http://localhost:3001/healthz && echo "UP"

# Restart server (clears schema cache)
cd /mnt/disks/data/twenty && docker compose restart twenty-server-1
# Wait ~2 min for NestJS boot before retrying

# DB direct access
docker exec twenty-db-1 psql -U twenty -d default

# Check existing fields for an object
docker exec twenty-db-1 psql -U twenty -d default -c \
  "SELECT name, type FROM core.\"fieldMetadata\" WHERE \"objectMetadataId\" = '<id>' ORDER BY name;"

# Backup
docker exec twenty-db-1 pg_dump -U twenty default > backup_$(date +%Y%m%d).sql
```

---

## Official Docs

- User Guide: https://docs.twenty.com/user-guide/introduction
- Developer Docs: https://docs.twenty.com/developers/introduction
- Self-hosting: https://docs.twenty.com/developers/self-hosting/docker-compose


