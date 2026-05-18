---
name: managing-sales-pipeline
description: >
  Use when there is any update on a Sales Opportunity — new deal, stage change,
  client meeting, follow-up, or document trigger (quote/invoice). Handles both
  creating new Opportunities and updating existing ones. Use when user says
  "跟客戶聊了", "有進展", "update stage", "deal update", "有個新機會", or dumps
  a block of sales updates. For NEW contacts/companies → also run capturing-sales-intel.
triggers:
  - "跟客戶聊了"
  - "有進展"
  - "update stage"
  - "deal update"
  - "有個新機會"
  - "opportunity update"
  - "推進"
  - "pipeline update"
version: "2.0"
author: BusyCow
---

# Managing Sales Pipeline

## Base
- **App Token:** stored in Memory as "Sales CRM Base"
- **Opportunity:** `{{OPPORTUNITIES_TABLE_ID}}`
- **Activities:** `{{ACTIVITIES_TABLE_ID}}`

See `references/opportunity-schema.md` and `references/activities-schema.md` for all field IDs.

---

## Stage Flow
```
Lead → Qualified → Proposal → Negotiation → Won / Lost
```

---

## Phase 1 — Triage the Update

User input is often a multi-entity dump. Before doing anything:

1. Read the full message carefully
2. Identify every distinct company/deal mentioned
3. For each entity, classify:
   - Existing opportunity (update) or new opportunity (create)?
   - Did stage change?
   - Is there a client signal (reaction, objection, budget, timeline)?
   - Is there a next action implied?

Present your parse back to the user:
> "我看到 3 個更新：[A] — [B] — [C]。我先處理這三個，有沒有遺漏？"

---

## Phase 2 — For Each Entity: Probe Gaps

Do NOT run through a fixed checklist. Extract what's already in the message, then ask only for what's genuinely missing.

**Must have before logging an activity:**
- Who was spoken to (contact name + company)
- How (電話 / WhatsApp/LINE / 線上會議 / 實體拜訪 / Demo / 訊息)
- What happened (1-line summary)
- Client response / reaction

**Must have before updating stage:**
- What concrete signal triggered the stage change?
- What is the new stage?

**Must have before creating a new Opportunity:**
- Client (must exist in Accounts — if not, flag for `capturing-sales-intel`)
- Description of the deal
- Business Line
- Initial stage (default: Lead)
- Owner (Hunter or Kevin)

**Good probing examples:**
> "對方的反應呢？有沒有表態預算或時間線？"
> "Stage 要推到 Qualified 嗎，還是還在 Lead？"
> "下一步誰負責，大概什麼時候要做？"

---

## Phase 3 — Log Activity

For every interaction, create an Activity record.

```
Summary format: "[Type] [Contact] @ [Company] — [one-line outcome]"
Example: "線上會議 Stanley @ MapKing — 討論 AI adoption 路徑，待內部評估"
```

Activity fields to set:
- Summary, Date (ms timestamp), Type (match exact option)
- Account (DuplexLink to Accounts record)
- Client Response
- Stage Advanced? (true/false)
- Next Action
- Opportunity (DuplexLink to Opportunity record)

---

## Phase 4 — Update / Create Opportunity

**If existing opportunity:**
- Update Stage if changed
- Update Expected Value, Expected Close Date, Notes if new info available
- Only update fields where there's new information — don't overwrite with blanks

**If new opportunity:**
- Check Accounts table for existing client — if not found, flag: "這家公司還沒在 CRM 裡，要一起建嗎？" → `capturing-sales-intel`
- Generate ID: `OPP-YYYY-[SHORTNAME]-[seq]` (check existing records for next seq)
- Set: Description, Client (DuplexLink), Stage, Business Line, Owner, Expected Value (if known)

---

## Phase 5 — Push Next Steps

After logging, ALWAYS push for concrete next actions. Never just record and stop.

For each entity, ask:
1. **下一步是什麼？** 誰負責，什麼時候之前？→ if actionable, create task via `managing-tasks`
2. **Stage 對嗎？** 要推進還是退回？
3. **需要產生文件嗎？**
   - 客戶要報價 → `generating-quotations`
   - Stage → Won / 收到付款 → `generating-invoices`

**Document trigger table:**
| Signal | Action |
|--------|--------|
| Client requests proposal / Stage → Proposal | `generating-quotations` |
| Contract signed / payment received / Stage → Won | `generating-invoices` |

---

## Pitfalls
- Activity Type must match exact SingleSelect option: 電話 / 實體拜訪 / 線上會議 / WhatsApp/LINE / Demo / 訊息
- Date = millisecond timestamp (UTC+8): `int(datetime(y,m,d,tzinfo=tz).timestamp()*1000)`
- DuplexLink = `{"link_record_ids": ["recXXX"]}` — need actual record_id
- Owner field is User type — format: `[{"id": "open_id"}]` + param `user_id_type: open_id`
- Never create Opportunity without a linked Client record
- Stage Advanced? = boolean, not string
