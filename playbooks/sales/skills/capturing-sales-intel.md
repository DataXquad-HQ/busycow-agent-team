---
name: capturing-sales-intel
description: >
  Use when user mentions a NEW person or NEW company that doesn't yet exist in
  the CRM — e.g. "認識了一個人", "有家新公司", "加進去", "新聯絡人", "add to CRM".
  Scope: Account + Contact creation ONLY.
  For new Opportunities → use managing-sales-pipeline.
  For new Partnerships → use managing-partnership-pipeline.
triggers:
  - "新客戶"
  - "新聯絡人"
  - "認識了"
  - "有家公司"
  - "幫我記一下這個人"
  - "加進去"
  - "加 CRM"
  - "有人介紹"
  - "潛在客戶"
version: "2.0"
author: BusyCow
---

# Capturing Sales Intel

## Scope
**Only creates:** Account (company) and/or Contact (person).
- New Opportunity → hand off to `managing-sales-pipeline`
- New Partnership → hand off to `managing-partnership-pipeline`

## Base
- **App Token:** stored in Memory as "Sales CRM Base"
- **Accounts:** `{{ACCOUNTS_TABLE_ID}}`
- **Contacts:** `{{CONTACTS_TABLE_ID}}`

---

## Phase 1 — Classify

From context, identify what needs to be created. Can be both simultaneously.

| Signal | Create |
|--------|--------|
| Person name + company/role mentioned | Contact |
| Company/organisation mentioned | Account |
| Both | Account first, then Contact linked to it |

If unclear: "這是新的聯絡人、新的公司，還是兩個都要加？"

---

## Phase 2 — Probe Gaps

Do NOT ask all questions upfront. Extract what's already in the message, then ask only for what's missing.

### Account — Must Have Before Saving
- Company full name
- Country (Taiwan / Hong Kong / Malaysia / other)
- Client type (Direct 直客 / Reseller / Partner / End User)

### Account — Ask If Not Mentioned
- Short name / alias
- Industry
- Which Business Line (BusyCow / GeoKernel / AquaOptima / TRACI)
- How did we find them / who introduced (來源)
- Billing entity (SG - DataXquad Pte. / TW - ATA Limited)
  → Overseas (HK/SG/MY) = SG; Taiwan or GeoKernel/TRACI = TW

### Contact — Must Have Before Saving
- Full name
- Company they work at
- Role / title

### Contact — Ask If Not Mentioned
- Phone / WhatsApp
- Email
- Decision role: Buyer / User / Influencer / Blocker / Champion
- Preferred channel
- How we met / who introduced

**Probing style:** conversational, not interrogation. Group related questions.
> "他在公司是什麼角色？有決策權嗎？怎麼認識的？"

---

## Phase 3 — Duplicate Check

Before creating, always search first:
```
mcp_lark_bitable_v1_appTableRecord_search
  filter: field_name="Client Name" / "Contact Name", operator="is", value="[name]"
```
If found → update existing record, do NOT create duplicate.

---

## Phase 4 — Save to Lark

### Save order (if creating both)
1. Create Account → capture `record_id`
2. Create Contact, link to Account via DuplexLink

See `references/accounts-schema.md` and `references/contacts-schema.md` for field IDs and types.

### DuplexLink format
```json
{"link_record_ids": ["recXXX"]}
```

---

## Phase 5 — Confirm + Hand Off

```
✅ 已記錄：
- 公司：[Company Name] ([Country], [Type])
- 聯絡人：[Name] — [Role]
```

Then ask:
- "有沒有相關的業務機會要一起建？" → `managing-sales-pipeline`
- "這是合作夥伴性質的嗎？" → `managing-partnership-pipeline`

---

## Pitfalls
- SingleSelect options must match exactly — check schema before writing
- MultiSelect = array of strings: `["BusyCow", "GeoKernel"]`
- Phone = plain string with country code: `"+852 9123 4567"`
- DuplexLink needs actual `record_id` from prior search/create
- Never save Account without Country + Type — these drive billing and reporting
