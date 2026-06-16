# Twenty CRM — Live Schema Snapshot
*Verified: 2026-06-15 via GraphQL introspection against localhost:3001*
*Updated: 2026-06-15 — added Person fields for C1 Lead Capture*

## GraphQL Endpoints (confirmed working)
- `POST /graphql` — data CRUD ✅
- `POST /metadata` — schema introspection ✅
- `POST /api` — **404, does not exist** ❌

## Object Counts (at time of snapshot)
- People: 16
- Companies: 18
- Opportunities: 14
- Partnerships: 9
- Tasks: 0
- Notes: 0

## Opportunity Stage Enum (OpportunityStageEnum)
`NEW` → `SCREENING` → `MEETING` → `PROPOSAL` → `CUSTOMER`

## Key Custom Enums

### OpportunityBusinessLineEnum
`BUSYCOW` | `GEOKERNEL` | `AQUAOPTIMA` | `TRACI` | `DISTIFY` | `DATAXQUAD`

### OpportunityDealTypeEnum
`DIRECT` | `PARTNERLED`

### OpportunityHealthCheckEnum
`ON_TRACK` | `NEEDS_FOLLOWUP` | `AWAITING_RESPONSE` | `AT_RISK`

### OpportunityPriorityEnum
`HIGH` | `MEDIUM` | `LOW`

### PersonStatusEnum
`PROSPECT` | `LEAD` | `CLIENT_PARTNER`

### PersonCountryEnum
`TAIWAN` | `HONG_KONG` | `CHINA` | `MALAYSIA` | `JAPAN` | `SINGAPORE` | `OTHER`

### PersonSourceEnum
`OUTBOUND_MAYA` | `INBOUND_WEB` | `REFERRAL` | `EVENT` | `PARTNER` | `NETWORK`

### PersonDecisionRoleEnum
`DECISION_MAKER` | `CHAMPION` | `INFLUENCER` | `END_USER` | `GATEKEEPER`

### PersonPreferredChannelEnum
`WHATSAPP` | `EMAIL` | `PHONE` | `LINKEDIN` | `LINE` | `WECHAT`

### PersonLeadTierEnum (new 2026-06-15)
`PASSERBY` | `NURTURE` | `OPPORTUNITY`

## Opportunity Custom Fields (confirmed via introspection)
```
businessLine          OpportunityBusinessLineEnum
dealType              OpportunityDealTypeEnum
healthCheck           OpportunityHealthCheckEnum
priority              OpportunityPriorityEnum
nextFollowUpDate      DateTime
nextActionSummary     String
currentStatusSummary  String
overview              String
probability           Float
expectedValue         Currency
dealId                String
docLink               Links
primaryContact        String   (text annotation, not relation)
relevantContacts      Person   (relation)
otherContacts         Person   (relation)
```

## Partnership Custom Fields (confirmed via introspection)
```
stage                 PartnershipStageEnum
status                PartnershipStatusEnum
partnerType           PartnershipPartnerTypeEnum
startDate             DateTime
endDate               DateTime
lastUpdateDate        DateTime
currentStatusSummary  String
nextActionSummary     String
partnershipOverview   String
docLink               Links
primaryContact        Person   (M:1 relation)
relatedPeople         Person   (1:M relation)
company               Company  (M:1 relation)
```

## Person Custom Fields (confirmed via introspection)
```
status               PersonStatusEnum
country              PersonCountryEnum
decisionRole         PersonDecisionRoleEnum
source               PersonSourceEnum        (OUTBOUND_MAYA|INBOUND_WEB|REFERRAL|EVENT|PARTNER|NETWORK)
preferredChannel     PersonPreferredChannelEnum
department           String
notes                String
remarks              String
lastContactDate      DateTime
meetContext          String   (NEW 2026-06-15 — where/how we met: event name, who introduced)
contactHandle        String   (NEW 2026-06-15 — e.g. LINE: @johndoe, WhatsApp: +886-xxx)
leadTier             PersonLeadTierEnum  (NEW 2026-06-15 — PASSERBY|NURTURE|OPPORTUNITY)
relatedPartnerships  Partnership  (M:1)
primaryPartnerships  Partnership  (1:M)
engagementsAttended  Engagement
involvingOpportunities Opportunity
relevantDeals        Opportunity
```

## Engagement Custom Fields (confirmed via introspection 2026-06-15)
```
engagementType    EngagementEngagementTypeEnum  (PHONE|INPERSON|ONLINE|MESSAGING|DEMO|EMAIL|EVENT)
engagementStatus  EngagementEngagementStatusEnum (PLANNED|COMPLETED)
channel           EngagementChannelEnum  (EMAIL|WHATSAPP|LINE|PHONE|IN_PERSON|ZOOM|TEAMS)
engagementDate    DateTime
engagementNote    RichText   → use { markdown: "..." } NOT a plain string
outcome           String
nextAction        String
name              String
clientAttendeesId ID → Person  (the person this engagement is with — NOT personId)
companyId         ID → Company
opportunityId     ID → Opportunity  (optional)
partnershipId     ID → Partnership  (optional)
```

## OutreachMessage Custom Object (created 2026-06-15)
Object metadata ID: `68c20f74-28b7-4768-af61-ad7b54fc279c`
See `references/outreach-message-schema.md` for full field list and GraphQL patterns.
```
status        SELECT  DRAFT|SCHEDULED|SENT|CANCELLED
messageType   SELECT  NURTURING|COLD_OUTREACH
sendMethod    SELECT  AUTO|MANUAL
channel       SELECT  EMAIL|WHATSAPP|LINE
subject       TEXT
body          RICH_TEXT  → bodyV2: { markdown: "..." }
context       TEXT
scheduledAt   DATE_TIME
sentAt        DATE_TIME
recipientId   → Person (MANY_TO_ONE)
```
The `structural-data/crm/schema` page in Hindsight previously had these errors — now corrected:
- Opportunity stages were `D1/D2/D3/D4/S1/S2/CLOSED_WON/CLOSED_LOST` (old/wrong)
- `healthCheck` had `AWAITING` — actual is `AWAITING_RESPONSE`
- `dealType` had `PARTNERSHIP` and `INVESTMENT` options — actual is `PARTNERLED`
- `businessLine` field was missing entirely
- `priority` had `VERY_HIGH` option — actual is just `HIGH/MEDIUM/LOW`
