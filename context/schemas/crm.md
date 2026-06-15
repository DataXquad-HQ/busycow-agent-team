# CRM Schema — Twenty

Object definitions for the DataXquad / GeoKernel CRM layer, powered by [Twenty](https://twenty.com) (self-hosted, `localhost:3001`).

> **圖例：** `sys` = 系統內建，無法修改 · `app` = Twenty 預設內建 · `cus` = 自定義欄位

---

## 📦 COMPANY（Twenty object: `company`）

### 🔧 System

| Field Name | Label | Type |
|---|---|---|
| `id` | Id | UUID |
| `createdAt` | Creation date | DATE_TIME |
| `updatedAt` | Last update | DATE_TIME |
| `deletedAt` | Deleted at | DATE_TIME |
| `createdBy` | Created by | ACTOR |
| `updatedBy` | Updated by | ACTOR |
| `position` | Position | POSITION |
| `searchVector` | Search vector | TS_VECTOR |

### 📦 App

| Field Name | Label | Type | Direction |
|---|---|---|---|
| `name` | Company Name | TEXT | |
| `domainName` | Website | LINKS | |
| `address` | HQ Address | ADDRESS | |
| `annualRevenue` | Annual Revenue | CURRENCY | |
| `linkedinLink` | Company Linkedin | LINKS | |
| `accountOwner` | Account Owner | RELATION | M:1 |
| `people` | People | RELATION | 1:M |
| `opportunities` | Opportunities | RELATION | 1:M |
| `noteTargets` | Notes | RELATION | 1:M |
| `taskTargets` | Tasks | RELATION | 1:M |
| `attachments` | Attachments | RELATION | 1:M |
| `timelineActivities` | Timeline Activities | RELATION | 1:M |

### ✏️ Custom

| Field Name | Label | Type | Options / Direction |
|---|---|---|---|
| `accountType` | Status | SELECT | `PROSPECT` `LEAD` `CLIENT` `PARTNER` `OPT_OUT` |
| `country` | Country | SELECT | `TAIWAN` `MALAYSIA` `INDONESIA` `THAILAND` `SINGAPORE` `VIETNAM` `OTHER` |
| `industry` | Industry | MULTI_SELECT | `GOVERNMENT` `WATER_UTILITIES` |
| `companyOverview` | Company Overview | TEXT | |
| `enrichmentOverview` | Enrichment Overview | TEXT | |
| `registeredNameEn` | Registered Name (EN) | TEXT | |
| `registeredNameCh` | Registered Name (CH) | TEXT | |
| `companyEmail` | Company Email | EMAILS | |
| `companyPhone` | Company Phone | PHONES | |
| `lastContactDate` | Last Contact Date | DATE_TIME | |
| `lastEnrichedDate` | Last Enriched Date | DATE_TIME | |
| `partnerships` | Partnerships | RELATION | 1:M |
| `engagements` | Engagements | RELATION | 1:M |

---

## 👤 PERSON（Twenty object: `person`）

### 🔧 System

| Field Name | Label | Type |
|---|---|---|
| `id` | Id | UUID |
| `createdAt` | Creation date | DATE_TIME |
| `updatedAt` | Last update | DATE_TIME |
| `deletedAt` | Deleted at | DATE_TIME |
| `createdBy` | Created by | ACTOR |
| `updatedBy` | Updated by | ACTOR |
| `avatarUrl` | Avatar | TEXT |
| `avatarFile` | Avatar File | FILES |
| `position` | Position | POSITION |
| `searchVector` | Search vector | TS_VECTOR |

### 📦 App

| Field Name | Label | Type | Direction |
|---|---|---|---|
| `name` | Name | FULL_NAME | |
| `emails` | Emails | EMAILS | |
| `phones` | Phones | PHONES | |
| `jobTitle` | Job Title | TEXT | |
| `linkedinLink` | Linkedin | LINKS | |
| `company` | Company | RELATION | M:1 |
| `pointOfContactForOpportunities` | Primary Contact For | RELATION | 1:M |
| `noteTargets` | Notes | RELATION | 1:M |
| `taskTargets` | Tasks | RELATION | 1:M |
| `attachments` | Attachments | RELATION | 1:M |
| `messageParticipants` | Message Participants | RELATION | 1:M |
| `calendarEventParticipants` | Calendar Event Participants | RELATION | 1:M |
| `timelineActivities` | Events | RELATION | 1:M |

### ✏️ Custom

| Field Name | Label | Type | Options / Direction |
|---|---|---|---|
| `status` | Status | SELECT | `PROSPECT` `LEAD` `CLIENT` `PARTNER` `OPT_OUT` |
| `country` | Country | SELECT | `TAIWAN` `HONG_KONG` `CHINA` `MALAYSIA` `THAILAND` `INDONESIA` `JAPAN` |
| `preferredChannel` | Preferred Channel | SELECT | `EMAIL` `WHATSAPP` `LINE` `PHONE` |
| `decisionRole` | Decision Role | SELECT | `BUYER` `USER` `INFLUENCER` `BLOCKER` `CHAMPION` |
| `source` | Source | SELECT | `REFERRAL` `EVENT` `PARTNER` `NETWORK` `INBOUND_WEB` `OUTBOUND_MAYA` |
| `department` | Department | TEXT | |
| `remarks` | Remarks | TEXT | |
| `lastContactDate` | Last Contact Date | DATE_TIME | |
| `primaryContactForPartnerships` | Primary Contact For Partnerships | RELATION | 1:M |
| `relatedPartnership` | Related Partnership | RELATION | M:1 |
| `engagementsAttended` | Engagements Attended | RELATION | M:1 |
| `involvingOpportunities` | Involving Opportunities | RELATION | M:1 |

---

## 🎯 OPPORTUNITY（Twenty object: `opportunity`）

### 🔧 System

`id` · `createdAt` · `updatedAt` · `deletedAt` · `createdBy` · `updatedBy` · `position` · `searchVector`

### 📦 App

| Field Name | Label | Type | Direction |
|---|---|---|---|
| `name` | Name | TEXT | |
| `amount` | Expected Amount | CURRENCY | |
| `closeDate` | Expected Close date | DATE_TIME | |
| `stage` | Stage | SELECT | `D1` `D2` `D3` `D4` `S1` `S2` `CLOSED_WON` `CLOSED_LOST` |
| `company` | Company | RELATION | M:1 |
| `owner` | Owner | RELATION | M:1 |
| `pointOfContact` | Primary Contact | RELATION | M:1 |
| `noteTargets` | Notes | RELATION | 1:M |
| `taskTargets` | Tasks | RELATION | 1:M |
| `attachments` | Attachments | RELATION | 1:M |
| `timelineActivities` | Timeline Activities | RELATION | 1:M |

### ✏️ Custom

| Field Name | Label | Type | Options / Direction |
|---|---|---|---|
| `primaryContact` | Primary Contact | TEXT | 主要聯絡人（文字備注用） |
| `priority` | Priority | SELECT | `VERY_HIGH` `HIGH` `MEDIUM` `LOW` |
| `dealType` | Deal Type | SELECT | `DIRECT` `PARTNERSHIP` `INVESTMENT` |
| `healthCheck` | Health Check | SELECT | `ON_TRACK` `NEEDS_FOLLOWUP` `AWAITING` `AT_RISK` |
| `probability` | Probability % | NUMBER | |
| `overview` | Overview | TEXT | |
| `currentStatusSummary` | Current Status Summary | TEXT | |
| `nextActionSummary` | Next Action Summary | TEXT | |
| `lastUpdateDate` | Last Contact Date | DATE_TIME | |
| `nextFollowUpDate` | Next Follow-up Date | DATE_TIME | |
| `engagements` | Engagements | RELATION | 1:M |
| `otherContacts` | Other Contacts | RELATION | 1:M → Person |

---

## 🤝 PARTNERSHIP（Twenty object: `partnership`）

### 🔧 System

`id` · `createdAt` · `updatedAt` · `deletedAt` · `createdBy` · `updatedBy` · `position` · `searchVector`

### 📦 App

| Field Name | Label | Type |
|---|---|---|
| `name` | Name | TEXT |

### ✏️ Custom

| Field Name | Label | Type | Options / Direction |
|---|---|---|---|
| `stage` | Stage | SELECT | `PROSPECT` `QUALIFYING` `AGREEMENT` `ACTIVE` `INACTIVE` |
| `status` | Status | SELECT | `ACTIVE` `NEEDS_FOLLOWUP` `DORMANT` `INACTIVE` |
| `partnerType` | Type | SELECT | `RESELLER` `INTEGRATOR` `TECHNOLOGY` `REFERRAL` |
| `partnershipOverview` | Partnership Overview | TEXT | |
| `currentStatusSummary` | Current Status Summary | TEXT | |
| `nextActionSummary` | Next Action Summary | TEXT | |
| `startDate` | Start Date | DATE_TIME | |
| `endDate` | End Date | DATE_TIME | |
| `lastUpdateDate` | Last Contact Date | DATE_TIME | |
| `docLink` | Doc Link | LINKS | |
| `company` | Company | RELATION | M:1 |
| `owner` | Owner | RELATION | M:1 |
| `primaryContact` | Primary Contact | RELATION | M:1 → Person |
| `relatedPeople` | Related People | RELATION | 1:M → Person |
| `engagements` | Engagements | RELATION | 1:M |
| `tasks` | Tasks | RELATION | 1:M |
| `notes` | Notes | RELATION | 1:M |
| `attachments` | Attachments | RELATION | 1:M |
| `timelineActivities` | Timeline Activities | RELATION | 1:M |

---

## 💬 ENGAGEMENT（Twenty object: `engagement`）

### 🔧 System

`id` · `createdAt` · `updatedAt` · `deletedAt` · `createdBy` · `updatedBy` · `position` · `searchVector`

### 📦 App

| Field Name | Label | Type |
|---|---|---|
| `name` | Name | TEXT |

### ✏️ Custom

| Field Name | Label | Type | Options / Direction |
|---|---|---|---|
| `engagementType` | Type | SELECT | `PHONE` `INPERSON` `ONLINE` `MESSAGING` `DEMO` `EMAIL` `EVENT` |
| `engagementStatus` | Status | SELECT | `PLANNED` `COMPLETED` |
| `channel` | Channel | SELECT | `EMAIL` `WHATSAPP` `LINE` `PHONE` `IN_PERSON` `ZOOM` `TEAMS` |
| `engagementDate` | Date | DATE_TIME | |
| `engagementNote` | Engagement Note | RICH_TEXT | |
| `nextAction` | Next Action | TEXT | |
| `outcome` | Outcome | TEXT | |
| `company` | Company | RELATION | M:1 |
| `opportunity` | Opportunity | RELATION | M:1 (optional) |
| `partnership` | Partnership | RELATION | M:1 (optional) |
| `clientAttendees` | Client Attendees | RELATION | 1:M → Person |
| `ourTeam` | Our Team | RELATION | 1:M → WorkspaceMember |
| `noteTargets` | Note Targets | RELATION | 1:M |
| `taskTargets` | Task Targets | RELATION | 1:M |
| `attachments` | Attachments | RELATION | 1:M |
| `timelineActivities` | Timeline Activities | RELATION | 1:M |

---

## ✅ TASK（Twenty object: `task`）

### 🔧 System

`id` · `createdAt` · `updatedAt` · `deletedAt` · `createdBy` · `updatedBy` · `position` · `searchVector`

### 📦 App

| Field Name | Label | Type | Options / Direction |
|---|---|---|---|
| `title` | Title | TEXT | |
| `status` | Status | SELECT | `TODO` `IN_PROGRESS` `DONE` |
| `dueAt` | Deadline | DATE_TIME | |
| `bodyV2` | Description | RICH_TEXT | |
| `assignee` | Assignee | RELATION | M:1 → WorkspaceMember |
| `taskTargets` | Relations | RELATION | 1:M |
| `attachments` | Attachments | RELATION | 1:M |
| `timelineActivities` | Timeline Activities | RELATION | 1:M |

### ✏️ Custom

| Field Name | Label | Type | Options / Direction |
|---|---|---|---|
| `taskPriority` | Priority | SELECT | `HIGH` `MEDIUM` `LOW` |
| `agentAdvice` | Agent Advice | RICH_TEXT | |
| `taskResults` | Task Results | RICH_TEXT | |
| `partnership` | Partnership | RELATION | M:1 (optional) |
| `opportunity` | Opportunity | RELATION | M:1 (optional) |

---

## 關係總覽

```
Company ──┬── People          (1:M)
          ├── Opportunities   (1:M)
          ├── Partnerships    (1:M)
          └── Engagements     (1:M)

Opportunity ──┬── Engagements     (1:M)
              └── Other Contacts  (1:M → Person)

Partnership ──┬── Engagements     (1:M)
              ├── Tasks           (1:M)
              ├── Primary Contact (M:1 → Person)
              └── Related People  (1:M → Person)

Engagement ──┬── Company          (M:1)
             ├── Opportunity      (M:1, optional)
             ├── Partnership      (M:1, optional)
             ├── Client Attendees (1:M → Person)
             └── Our Team         (1:M → WorkspaceMember)

Task ──┬── Opportunity  (M:1, optional)
       └── Partnership  (M:1, optional)
```

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-12 | Replaced `accountStatus` (HOT/WARM/COLD) + `accountType` (MULTI_SELECT) with unified `accountType` SELECT: `PROSPECT` `LEAD` `CLIENT` `PARTNER` `OPT_OUT`. Updated Person `status` to match. |
| 2026-06-11 | Initial full schema — Company, Contact, Deal, Partnership, Engagement, Task |
| 2026-06-11 | Rename standard objects to business terms: Company→Account, Person→Contact, Opportunity→Deal |
| 2026-06-11 | Full rewrite to canonical format with System / App / Custom sections per object |
