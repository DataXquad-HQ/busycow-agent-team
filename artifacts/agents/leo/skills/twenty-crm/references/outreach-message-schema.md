# OutreachMessage — Full Schema Reference
*Created: 2026-06-15*

## Object Identity
- **nameSingular:** `outreachMessage`
- **namePlural:** `outreachMessages`
- **Object metadata ID:** `68c20f74-28b7-4768-af61-ad7b54fc279c`
- **Purpose:** Stores outreach drafts (nurturing, cold outreach) with lifecycle state. Separate from Engagement (which is the immutable sent-interaction log).

## Fields

| Field | Type | Values / Notes |
|---|---|---|
| `name` | TEXT | Auto-set to subject line |
| `subject` | TEXT | Email subject |
| `bodyV2` | RICH_TEXT | Use `{ markdown: "..." }` — NOT `body` |
| `context` | TEXT | Leo's notes: why now, context used |
| `status` | SELECT | `DRAFT` / `SCHEDULED` / `SENT` / `CANCELLED` |
| `messageType` | SELECT | `NURTURING` / `COLD_OUTREACH` |
| `sendMethod` | SELECT | `AUTO` / `MANUAL` |
| `channel` | SELECT | `EMAIL` / `WHATSAPP` / `LINE` |
| `scheduledAt` | DATE_TIME | When to send |
| `sentAt` | DATE_TIME | When actually sent |
| `recipientId` | ID → Person | MANY_TO_ONE relation |

## Lifecycle
```
DRAFT → SCHEDULED → SENT
              └──→ CANCELLED
```
- **DRAFT**: Leo created it, awaiting human approval
- **SCHEDULED**: Human approved (via CRM or Lark reply), Sender cron will pick it up
- **SENT**: Email dispatched via OpenMail, Engagement created
- **CANCELLED**: Discarded without sending

## GraphQL Patterns

### Create a draft
```graphql
mutation {
  createOutreachMessage(data: {
    name: "[Subject line]"
    subject: "[Subject line]"
    bodyV2: { markdown: "Hi [Name],\n\n[body]\n\n[signature]" }
    context: "[why now + context used]"
    status: DRAFT
    messageType: NURTURING
    sendMethod: AUTO
    channel: EMAIL
    scheduledAt: "2026-06-16T01:00:00Z"
    recipientId: "PERSON_UUID"
  }) { id name status }
}
```

### Query pending drafts
```graphql
{
  outreachMessages(filter: { status: { in: [DRAFT, SCHEDULED] } }) {
    edges { node {
      id name subject status scheduledAt
      recipient { id name { firstName lastName } emails { primaryEmail } }
    }}
  }
}
```

### Update to SCHEDULED (after approval)
```graphql
mutation {
  updateOutreachMessage(id: "MSG_UUID", data: { status: SCHEDULED }) { id status }
}
```

### Update to SENT
```graphql
mutation {
  updateOutreachMessage(id: "MSG_UUID", data: {
    status: SENT
    sentAt: "2026-06-16T04:00:00Z"
  }) { id status }
}
```

## CRM Link (external)
Always use: `{{CRM_EXTERNAL_URL}}/objects/outreachMessages/[UUID]`
Never use: `http://localhost:3001/objects/outreachMessages/[UUID]`
