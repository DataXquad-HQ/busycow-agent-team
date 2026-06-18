# CRM Schema — Twenty

Object definitions for the CRM layer, powered by [Twenty](https://twenty.com) (self-hosted).

> **Legend:** `app` = Twenty built-in · `cus` = custom field
>
> **Last verified:** 2026-06-15 via GraphQL introspection

Replace `{{CRM_URL}}` with your Twenty instance URL (default: `http://localhost:3001`).

---

## GraphQL Endpoints

| Endpoint | Purpose |
|---|---|
| `POST {{CRM_URL}}/graphql` | Data CRUD |
| `POST {{CRM_URL}}/metadata` | Schema introspection only |

Auth: `Authorization: Bearer {{TWENTY_API_KEY}}`

> ⚠️ `/api` returns 404 — always use `/graphql` for data.

---

## COMPANY

### App fields

| Field | Type |
|---|---|
| `name` | TEXT |
| `domainName` | LINKS |
| `address` | ADDRESS |
| `annualRevenue` | CURRENCY |
| `linkedinLink` | LINKS |
| `accountOwner` | RELATION M:1 → WorkspaceMember |
| `people` | RELATION 1:M → Person |
| `opportunities` | RELATION 1:M → Opportunity |
| `noteTargets` | RELATION 1:M |
| `taskTargets` | RELATION 1:M |

### Custom fields

| Field | Type | Options / Notes |
|---|---|---|
| `accountType` | SELECT | `PROSPECT` `LEAD` `CLIENT` `PARTNER` `OPT_OUT` |
| `country` | SELECT | Configure to match your target markets |
| `industry` | MULTI_SELECT | Configure to match your target industries |
| `companyOverview` | TEXT | |
| `enrichmentOverview` | TEXT | |
| `lastContactDate` | DATE_TIME | |
| `lastEnrichedDate` | DATE_TIME | |
| `partnerships` | RELATION 1:M → Partnership | |
| `engagements` | RELATION 1:M → Engagement | |

---

## PERSON

### App fields

| Field | Type |
|---|---|
| `name` | FULL_NAME |
| `emails` | EMAILS |
| `phones` | PHONES |
| `jobTitle` | TEXT |
| `linkedinLink` | LINKS |
| `company` | RELATION M:1 → Company |

### Custom fields

| Field | Type | Options / Notes |
|---|---|---|
| `status` | SELECT | `PROSPECT` `LEAD` `CLIENT_PARTNER` |
| `leadTier` | SELECT | `PASSERBY` `NURTURE` `OPPORTUNITY` — outreach priority tier |
| `country` | SELECT | Configure to match your target markets |
| `preferredChannel` | SELECT | `EMAIL` `WHATSAPP` `LINE` `PHONE` `LINKEDIN` `WECHAT` |
| `decisionRole` | SELECT | `DECISION_MAKER` `CHAMPION` `INFLUENCER` `END_USER` `GATEKEEPER` |
| `source` | SELECT | `REFERRAL` `EVENT` `PARTNER` `NETWORK` `INBOUND_WEB` `OUTBOUND` |
| `department` | TEXT | |
| `notes` | TEXT | Free-form notes |
| `remarks` | TEXT | |
| `meetContext` | TEXT | Where/how we met — event name, who introduced |
| `contactHandle` | TEXT | e.g. `LINE: @johndoe`, `WhatsApp: +1-xxx` |
| `lastContactDate` | DATE_TIME | |
| `relatedPartnerships` | RELATION M:1 → Partnership | |
| `primaryPartnerships` | RELATION 1:M → Partnership | |
| `engagementsAttended` | RELATION M:1 → Engagement | |
| `involvingOpportunities` | RELATION M:1 → Opportunity | |

---

## OPPORTUNITY

### App fields

| Field | Type | Options |
|---|---|---|
| `name` | TEXT | |
| `amount` | CURRENCY | |
| `closeDate` | DATE_TIME | |
| `stage` | SELECT | `NEW` `SCREENING` `MEETING` `PROPOSAL` `CUSTOMER` |
| `company` | RELATION M:1 → Company | |
| `owner` | RELATION M:1 → WorkspaceMember | |
| `pointOfContact` | RELATION M:1 → Person | |

### Custom fields

| Field | Type | Options / Notes |
|---|---|---|
| `businessLine` | SELECT | `{{YOUR_PRODUCT_LINES}}` — configure to match your products/services |
| `dealType` | SELECT | `DIRECT` `PARTNERLED` |
| `healthCheck` | SELECT | `ON_TRACK` `NEEDS_FOLLOWUP` `AWAITING_RESPONSE` `AT_RISK` |
| `priority` | SELECT | `HIGH` `MEDIUM` `LOW` |
| `probability` | NUMBER | |
| `expectedValue` | CURRENCY | |
| `dealId` | TEXT | External reference ID |
| `overview` | TEXT | |
| `currentStatusSummary` | TEXT | |
| `nextActionSummary` | TEXT | |
| `nextFollowUpDate` | DATE_TIME | |
| `docLink` | LINKS | |
| `primaryContact` | TEXT | Text annotation — name of primary contact |
| `relevantContacts` | RELATION 1:M → Person | |
| `otherContacts` | RELATION 1:M → Person | |
| `engagements` | RELATION 1:M → Engagement | |

---

## PARTNERSHIP

### App fields

| Field | Type |
|---|---|
| `name` | TEXT |

### Custom fields

| Field | Type | Options |
|---|---|---|
| `stage` | SELECT | `PROSPECT` `QUALIFYING` `AGREEMENT` `ACTIVE` `INACTIVE` |
| `status` | SELECT | `ACTIVE` `NEEDS_FOLLOWUP` `DORMANT` `INACTIVE` |
| `partnerType` | SELECT | `RESELLER` `INTEGRATOR` `TECHNOLOGY` `REFERRAL` |
| `partnershipOverview` | TEXT | |
| `currentStatusSummary` | TEXT | |
| `nextActionSummary` | TEXT | |
| `startDate` | DATE_TIME | |
| `endDate` | DATE_TIME | |
| `lastUpdateDate` | DATE_TIME | |
| `docLink` | LINKS | |
| `company` | RELATION M:1 → Company | |
| `owner` | RELATION M:1 → WorkspaceMember | |
| `primaryContact` | RELATION M:1 → Person | |
| `relatedPeople` | RELATION 1:M → Person | |
| `engagements` | RELATION 1:M → Engagement | |
| `tasks` | RELATION 1:M → Task | |

---

## ENGAGEMENT

Custom object — immutable log of a completed interaction. Create one per meeting, call, email, or demo that actually happened.

| Field | Type | Options / Notes |
|---|---|---|
| `name` | TEXT | Auto-generated or descriptive label |
| `engagementType` | SELECT | `PHONE` `INPERSON` `ONLINE` `MESSAGING` `DEMO` `EMAIL` `EVENT` |
| `engagementStatus` | SELECT | `PLANNED` `COMPLETED` |
| `channel` | SELECT | `EMAIL` `WHATSAPP` `LINE` `PHONE` `IN_PERSON` `ZOOM` `TEAMS` |
| `engagementDate` | DATE_TIME | |
| `engagementNote` | RICH_TEXT | Use `{ markdown: "..." }` — not a plain string |
| `outcome` | TEXT | |
| `nextAction` | TEXT | |
| `clientAttendeesId` | ID → Person | **Field name is `clientAttendeesId`, NOT `personId`** |
| `companyId` | ID → Company | |
| `opportunityId` | ID → Opportunity | Optional |
| `partnershipId` | ID → Partnership | Optional |
| `ourTeam` | RELATION 1:M → WorkspaceMember | |

---

## OUTREACH MESSAGE

Custom object — stores outreach email drafts and tracks their lifecycle before and after sending.

| Field | Type | Options / Notes |
|---|---|---|
| `name` | TEXT | Same as subject |
| `subject` | TEXT | Email subject line |
| `body` | RICH_TEXT | Use `body: { markdown: "..." }` — **not** `bodyV2` |
| `context` | TEXT | Why sending now — personalisation rationale |
| `status` | SELECT | `DRAFT` `SCHEDULED` `SENT` `CANCELLED` |
| `messageType` | SELECT | `NURTURING` `COLD_OUTREACH` |
| `sendMethod` | SELECT | `AUTO` `MANUAL` |
| `channel` | SELECT | `EMAIL` `WHATSAPP` `LINE` |
| `scheduledAt` | DATE_TIME | |
| `sentAt` | DATE_TIME | Set after send |
| `recipientId` | ID → Person | |

**Lifecycle:** `DRAFT` → `SCHEDULED` → `SENT` | `CANCELLED`

---

## TASK

### App fields

| Field | Type | Options |
|---|---|---|
| `title` | TEXT | |
| `status` | SELECT | `TODO` `IN_PROGRESS` `DONE` |
| `dueAt` | DATE_TIME | |
| `bodyV2` | RICH_TEXT | Use `bodyV2: { markdown: "..." }` |
| `assignee` | RELATION M:1 → WorkspaceMember | |

### Custom fields

| Field | Type | Options |
|---|---|---|
| `taskPriority` | SELECT | `HIGH` `MEDIUM` `LOW` |
| `agentAdvice` | RICH_TEXT | |
| `taskResults` | RICH_TEXT | |
| `partnership` | RELATION M:1 → Partnership | Optional |
| `opportunity` | RELATION M:1 → Opportunity | Optional |

> **Note:** Task relation fields use `target[Object]Id` naming: `targetOpportunityId`, `targetPersonId`, `targetCompanyId`, `targetEngagementId`. Not `opportunityId`.

---

## Relationship Map

```
Company ──┬── People          (1:M)
          ├── Opportunities   (1:M)
          ├── Partnerships    (1:M)
          └── Engagements     (1:M)

Opportunity ──┬── Engagements      (1:M)
              ├── Relevant Contacts (1:M → Person)
              └── Other Contacts    (1:M → Person)

Partnership ──┬── Engagements      (1:M)
              ├── Tasks             (1:M)
              ├── Primary Contact   (M:1 → Person)
              └── Related People    (1:M → Person)

Engagement ──┬── Company           (M:1)
             ├── Opportunity        (M:1, optional)
             ├── Partnership        (M:1, optional)
             ├── Client Attendees   (1:M → Person, via clientAttendeesId)
             └── Our Team           (1:M → WorkspaceMember)

OutreachMessage ── Recipient (M:1 → Person)

Task ──┬── Opportunity  (M:1, optional)
       └── Partnership  (M:1, optional)
```

---

## Key Pitfalls

| Symptom | Fix |
|---|---|
| `opportunity(id: "UUID")` throws "Argument not allowed: id" | Use `opportunities(filter: { id: { eq: "UUID" } })` → `edges[0].node` |
| `filter: { name: { like: "%..." } }` returns empty | List all with `first: 100`, filter in Python |
| Engagement create fails — field not found | Use `clientAttendeesId`, not `personId` |
| `Note.body` / `Task.body` not found | Rich text field is `bodyV2: { markdown: "..." }` |
| `OutreachMessage.bodyV2` not found | OutreachMessage uses `body`, not `bodyV2` |
| `engagementNote` rejected as plain string | Use `engagementNote: { markdown: "..." }` |
| Enum filter syntax error | Use bare value: `{ stage: { eq: NEW } }` — no quotes around enum |

---

## Changelog

| Date | Change |
|---|---|
| 2026-06-15 | Added OutreachMessage object; added Person fields `leadTier`, `meetContext`, `contactHandle`, `notes`; updated Person enums (status, decisionRole, source); added Opportunity fields `expectedValue`, `dealId`, `docLink`, `relevantContacts`; added pitfalls table |
| 2026-06-14 | Corrected Opportunity stages; fixed `healthCheck` enum; fixed `dealType` enum; added `businessLine` field |
| 2026-06-12 | Unified `accountType` SELECT |
| 2026-06-11 | Initial schema |
