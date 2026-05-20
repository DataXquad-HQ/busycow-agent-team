---
name: generating-invoices
description: >
  Generate invoices for BusyCow clients after a quotation is accepted or a
  contract is signed. Creates Invoice record in Lark Base, fills Google Doc
  template, exports PDF, and uploads to Google Drive. Use when user says
  "generate invoice", "create invoice", "出 invoice", "跑一張 invoice", or
  when a Quotation Status moves to Accepted. Comes AFTER generating-quotations
  in the sales flow: Opportunity → Quotation → [Contract] → Invoice.
triggers:
  - "generate invoice"
  - "create invoice"
  - "出 invoice"
  - "跑一張 invoice"
  - "invoice PDF"
  - "billing"
---

# Generating Invoices

## ⚠️ MANDATORY PRE-CHECKS (run BEFORE anything else)

### 1. Get Taiwan Current Date
**NEVER assume or guess today's date.** Always fetch it:
```python
result = terminal("TZ=Asia/Taipei date '+%Y-%m-%d'")
today_tw = result.strip()  # e.g. "2026-05-19"
```
Use this for `{{INVOICE_DATE}}` and all date calculations. If terminal is unavailable:
```python
from datetime import datetime, timezone, timedelta
today_tw = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')
```
**Do NOT use UTC or local server time. Taiwan = UTC+8.**

### 2. Determine Invoice ID
Format: `IN-{ENTITY}-{YYYYMM}{NNN}`
- `YYYYMM` = from the Taiwan date fetched above (never hardcode)
- `NNN` = query Invoices table first, find max existing NNN for that entity + month, then +1

```python
# Get next sequence number
records = mcp_lark_bitable_v1_appTableRecord_search(
    path={"app_token": "{{LARK_APP_TOKEN}}", "table_id": "{{TABLE_ID}}"},
    data={"filter": {"conjunction": "and", "conditions": [
        {"field_name": "Invoice ID", "operator": "contains", "value": [f"IN-{entity}-{yyyymm}"]}
    ]}}
)
existing_nnn = [int(r['fields']['Invoice ID'][-3:]) for r in records if ...]
next_nnn = max(existing_nnn, default=0) + 1
invoice_id = f"IN-{entity}-{yyyymm}{next_nnn:03d}"
```

---

## Base & Tables
- **Base Token:** `{{LARK_APP_TOKEN}}`
- **Invoices Table:** `{{TABLE_ID}}`
- **Invoice Items Table:** `{{TABLE_ID}}`

### Invoice Items Schema

| Field | Field ID | Type |
|-------|----------|------|
| Item Name (primary) | `fldAJWU82P` | Text |
| Description | `fldX8Yigan` | Text |
| Qty | `fldy0wnvjm` | Number |
| Unit | `fldV21gxIL` | Text |
| Unit Price | `fldTSlbqRX` | Number |
| Amount | `fldMVL0xzg` | Number |
| Notes | `fldXcUyaCl` | Text |
| Invoices (link) | `fldojCUTXy` | DuplexLink → Invoices table |

Items are linked to the Invoice via `fldojCUTXy` (DuplexLink). Always pull items by filtering on this field using the Invoice record ID.

---

## Step 0: Collect Context + Pull Items from Base

```
MUST HAVE:
□ Invoice record ID (or Invoice ID string to look up)
□ Language (EN or CH) → determines template

SHOULD HAVE:
□ Related Quotation or Contract ID
□ Notes / special conditions override
```

### Pull line items from Invoice Items table

Once you have the Invoice record ID, fetch all linked items:

```python
# Search Invoice Items — filter by linked Invoice record ID
items = mcp_lark_bitable_v1_appTableRecord_search(
    path={"app_token": "{{LARK_APP_TOKEN}}", "table_id": "{{TABLE_ID}}"},
    data={"filter": {"conjunction": "and", "conditions": [
        {"field_name": "Invoices", "operator": "contains", "value": [invoice_record_id]}
    ]}}
)
line_items = [
    {
        "name":        r["fields"].get("Item Name", ""),
        "description": r["fields"].get("Description", ""),
        "qty":         r["fields"].get("Qty", 1),
        "unit":        r["fields"].get("Unit", ""),
        "unit_price":  r["fields"].get("Unit Price", 0),
        "amount":      r["fields"].get("Amount", 0),
        "notes":       r["fields"].get("Notes", ""),
    }
    for r in items.get("items", [])
]
```

Also pull Invoice header from `{{TABLE_ID}}` for: client, currency, subtotal, tax, total.

Confirm to user before proceeding: "找到 N 個項目，小計 HKD XX,XXX。確認？"

If no items found in table → ask user to provide items manually.

---

## Templates — 2 Options

| Template | Doc ID | Use When |
|----------|--------|----------|
| EN | `1zQ4w3GbVDNTWzH2TCsxNjuRBxRpN93xVWNfO15MHQrQ` | English client |
| CH | `1y1ZPn65MsUfaz1Cl9HiokH67YdxmOdh342mppY4qO68` | Chinese client |

Language selection: ask if not obvious from client profile or prior quotation.

---

## Placeholders

| Placeholder | Source |
|-------------|--------|
| `{{ENTITY_NAME}}` | Entity mapping (see below) |
| `{{ENTITY_ADDRESS}}` | Entity mapping |
| `{{INVOICE_NO}}` | `IN-{ENTITY}-{YYYYMM}{NNN}` format |
| `{{INVOICE_DATE}}` | Taiwan date from mandatory pre-check — EN: "28 May 2026" / CH: "2026年5月28日" — **never AI-generated** |
| `{{DUE_DATE}}` | Invoice Date + 30 days (default) |
| `{{BILL_TO_NAME}}` | Contact person name |
| `{{BILL_TO_COMPANY}}` | Client company full name |
| `{{BILL_TO_ADDRESS}}` | Client billing address |
| `{{SHIP_TO_NAME}}` | Ship-to contact (empty `""` if no hardware) |
| `{{SHIP_TO_ADDRESS}}` | Ship-to address (empty `""` if no hardware) |
| `{{ITEM_DESC}}` | Line item description |
| `{{ITEM_QTY}}` | Quantity |
| `{{ITEM_PRICE}}` | Unit price (formatted with commas) |
| `{{ITEM_AMOUNT}}` | Line total |
| `{{SUBTOTAL}}` | Sum of items |
| `{{TAX}}` | Tax amount (empty `""` if 0) |
| `{{TOTAL}}` | Grand total |
| `{{CURRENCY}}` | `HKD` / `USD` |
| `{{BANK_NAME}}` | Entity bank mapping |
| `{{BANK_ACCOUNT_NAME}}` | Entity bank mapping |
| `{{BANK_ACCOUNT_NO}}` | Entity bank mapping |
| `{{SWIFT_CODE}}` | Entity bank mapping |

---

| Segment | Rule |
|---------|------|
| `IN` | Fixed prefix, always |
| `{ENTITY}` | `ATA` = ATA Limited 應科聯有限公司 (TW entity) · `DX` = BusyCow Pte. Ltd. (SG entity) |
| `{YYYY}` | 4-digit year of invoice date |
| `{MM}` | 2-digit month of invoice date |
| `{NNN}` | 3-digit sequence, **per entity per month**, starting `001` |

**Examples:**
- `IN-ATA-202607001` — first ATA invoice in July 2026
- `IN-DX-202607001` — first DX invoice in July 2026 (no collision — different entity)
- `IN-ATA-202607002` — second ATA invoice in same month

### Invoice ID Format Summary
```
IN-{ENTITY}-{YYYYMM}{NNN}

ENTITY  = ATA or DX (see table below)
YYYYMM  = year+month from Taiwan date (pre-check step 1)
NNN     = 3-digit sequence, per entity per month, starting 001
```
**Examples:** `IN-ATA-202605001`, `IN-DX-202605001`, `IN-ATA-202605002`

### Which entity to use?
| Client / Product | Entity | Prefix |
|-----------------|--------|--------|
| Taiwan client | ATA Limited 應科聯 | `ATA` |
| [your product] / [your product] product | ATA Limited 應科聯 | `ATA` |
| Overseas client (HK, SG, MY) | BusyCow Pte. Ltd. | `DX` |
| BusyCow / [your product] product | BusyCow Pte. Ltd. | `DX` |

### Assigning the next sequence number
Before creating a new invoice, query the Invoices table to find the highest existing NNN for that entity + month:
```python
# Filter: Invoice ID starts with "IN-{ENTITY}-{YYYY}{MM}"
# Extract the NNN from matching records, take max, add 1
# If none exist → start at 001
```
Never reuse or skip numbers. Sequence is per-entity per-month — ATA and DX counters are independent.

## Pitfalls
- **Date must always be fetched via `TZ=Asia/Taipei date '+%Y-%m-%d'` — never assumed or AI-generated**
- **Invoice ID YYYYMM must come from the fetched Taiwan date — never hardcoded**
- Query existing invoice records before assigning NNN — avoid duplicate IDs
```
📝 Draft → 📤 Sent → 🔄 Partially Collected → ✅ Collected
                   ↘ ⏰ Overdue
                   ↘ 🔁 Revised
                   ↘ ❌ Cancelled
```

## References
- `references/company-entities.md` — entity bank details
- `references/gdocs-workflow.md` — full Google Docs copy/fill/export implementation

## Google Doc Template
- **Master Template:** `1-FPENawiV8b8FYYU_ZDxtxwrBVbUmEFWFj_PtPvjo-8`
- **Working Copy:** `1zQ4w3GbVDNTWzH2TCsxNjuRBxRpN93xVWNfO15MHQrQ`
- Workflow: copy master → fill `{{placeholders}}` via Docs API batchUpdate → export PDF
- See skill: `gdocs-invoice-template` for full implementation

## Placeholders
`{{COMPANY_NAME}}` `{{INVOICE_NO}}` `{{INVOICE_DATE}}` `{{DUE_DATE}}`
`{{BILL_TO_NAME}}` `{{BILL_TO_COMPANY}}` `{{BILL_TO_ADDRESS}}`
`{{ITEM_DESC}}` `{{ITEM_QTY}}` `{{ITEM_PRICE}}` `{{ITEM_AMOUNT}}`
`{{SUBTOTAL}}` `{{TAX}}` `{{TOTAL}}` `{{CURRENCY}}`
`{{BANK_NAME}}` `{{BANK_ACCOUNT_NAME}}` `{{BANK_ACCOUNT_NO}}` `{{SWIFT_CODE}}`
