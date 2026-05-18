---
name: managing-partnership-pipeline
description: >
  Use when there is any update on a Partnership — new partner prospect, stage change,
  partner meeting, follow-up, or contract trigger. Handles both creating new Partnerships
  and updating existing ones. Use when user says "跟夥伴聊了", "partnership 有進展",
  "partner update", "有個新合作夥伴", or dumps a block of partner updates.
  For NEW contacts/companies → also run capturing-sales-intel.
triggers:
  - "partnership update"
  - "partner stage"
  - "跟夥伴聊了"
  - "partner progress"
  - "partnership 有進展"
  - "update partner"
  - "有個新合作夥伴"
  - "新的 partner"
version: "2.0"
author: BusyCow
---

# Managing Partnership Pipeline

## What Is a Partnership?
A company with a formal/semi-formal relationship — reseller, tech partner, referral, channel.
Partner = the organisation. Individuals → Contacts table, linked via Accounts.

## Base
- **App Token:** stored in Memory as "Sales CRM Base"
- **Partnership:** `{{PARTNERSHIP_TABLE_ID}}`
- **Activities:** `{{ACTIVITIES_TABLE_ID}}`

See `references/partnership-schema.md` and `references/activities-schema.md` for all field IDs.

---

## Stage Flow
```
Prospect → Qualifying → Agreement → Active
                                  → On Hold / Inactive
```

| Stage | Meaning |
|-------|---------|
| Prospect | Initial identification, first contact |
| Qualifying | Both sides evaluating fit |
| Agreement | Negotiating terms, contract being drafted |
| Active | Signed, collaboration in progress |
| On Hold | Temporarily paused |
| Inactive | Relationship ended |

## Known Partners (as of May 2026)
| ID | Name | Notes |
|----|------|-------|
| P001 | HKRFID | Reseller HK — Active |
| P002 | AICities | Reseller HK — Stanley (CEO) |
| P003 | Onnet | Reseller MY — awaiting agreement |
| P004 | AI Edge | Reseller HK — Richard Chan |
| P005 | VoiceBot | Reseller HK |
| P006 | HeadWorker Technical Consultant | Tech partner HK |
| P007 | Cassandra | TBD |
| P008 | Daniel (Onnet) | Legacy person record |

**Next ID: P009**

---

## Phase 1 — Triage the Update

User input is often a multi-entity dump. Before doing anything:

1. Read the full message carefully
2. Identify every distinct partner mentioned
3. For each entity, classify:
   - Existing partnership (update) or new prospect (create)?
   - Did stage change?
   - Is there a concrete signal or commitment?
   - Is there a next action implied?
   - Did this partner bring a new Opportunity? → flag for `managing-sales-pipeline`

Present your parse back to the user:
> "我看到 2 個夥伴更新：[A] — [B]。我先處理這兩個，有沒有遺漏？"

---

## Phase 2 — For Each Entity: Probe Gaps

Do NOT run through a fixed checklist. Extract what's in the message, ask only for what's missing.

**Must have before logging an activity:**
- Who was spoken to (contact name + company)
- How (電話 / WhatsApp/LINE / 線上會議 / 實體拜訪 / Demo / 訊息)
- What happened (1-line summary)
- Partner response / reaction

**Must have before updating stage:**
- What concrete signal triggered the stage change?

**Must have before creating a new Partnership:**
- Partner company name (must exist in Accounts — if not, flag for `capturing-sales-intel`)
- Type: Reseller / Tech Partner / Referral / OEM / Other
- Country / region
- Initial stage (default: Prospect)

**Good probing examples:**
> "對方有沒有明確表態？還是還在觀望？"
> "Stage 要推到 Qualifying 嗎？"
> "這個夥伴有帶來具體商機嗎？"
> "下一步誰負責，什麼時候之前？"

---

## Phase 3 — Log Activity

For every interaction, create an Activity record.

```
Summary format: "[Type] [Contact] @ [Partner] — [one-line outcome]"
Example: "線上會議 Stanley @ AICities — 討論 MapKing 客戶導入，待確認時間"
```

Activity fields to set:
- Summary, Date (ms timestamp), Type (match exact option)
- Account (DuplexLink to Accounts record)
- Client Response
- Stage Advanced? (true/false)
- Next Action
- Partnership (DuplexLink to Partnership record)

---

## Phase 4 — Update / Create Partnership

**If existing partnership:**
- Update Stage if changed
- Append new status to Description field (running narrative log)
- Only update fields where there's new information

**If new partnership:**
- Check Accounts table for existing company — if not found: "這家公司還沒在 CRM 裡，要一起建嗎？" → `capturing-sales-intel`
- Generate ID: P + zero-padded 3 digits (check current highest, next is P009)
- Set: Name, Account (DuplexLink), Stage, Description

---

## Phase 5 — Push Next Steps

After logging, ALWAYS push for concrete next actions. Never just record and stop.

For each entity, ask:
1. **下一步是什麼？** 誰負責，什麼時候之前？→ if actionable, create task via `managing-tasks`
2. **Stage 對嗎？** 要推進還是退回？
3. **有沒有要起草合約？** Stage → Agreement 時觸發
4. **這個夥伴有帶來具體商機嗎？** → if yes, create Opportunity via `managing-sales-pipeline`

---

## Pitfalls
- P008 is a legacy person record — new partnerships must always be companies
- Never create duplicate — search by name before creating
- Activity Type must match exact SingleSelect: 電話 / 實體拜訪 / 線上會議 / WhatsApp/LINE / Demo / 訊息
- DuplexLink = `{"link_record_ids": ["recXXX"]}` — need actual record_id
- Date = millisecond timestamp (UTC+8)
- Stage field ID: `fldu8TVcvX` (added May 2026)
- Always update Description when stage changes — it's the running narrative
