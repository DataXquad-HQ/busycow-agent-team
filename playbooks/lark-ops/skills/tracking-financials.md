---
name: tracking-financials
description: >
  Manage the BusyCow financial forecast and actuals in Lark Bitable — update revenue rows,
  enter expenses, review monthly cashflow, or set up the tracker schema from scratch.
  Use when user asks to update financials, enter a new deal's revenue, check cashflow,
  or build/extend the Revenue/Expenses/Summary tables.
triggers:
  - "financial tracker"
  - "revenue forecast"
  - "P&L bitable"
  - "forecast vs actual"
  - "product line tracking"
---

# Lark Bitable Financial Tracker

## Table Architecture (4 tables)

```
⚙️ Product Config     — pricing master, one row per SKU
💰 Revenue Tracker    — one row per month × product × entry type
💸 Expenses           — one row per month × category × entry type
📊 Monthly Summary    — one row per month, rollup of all lines
```

### Why this structure?
- Dual-purpose: same Revenue Tracker holds both Forecast rows and Actual rows (distinguished by `Entry Type` field)
- Forecast rows are unit-based (Units × Unit Price) — easy to model scenarios
- Actual rows are entered when invoiced/collected — match against forecast
- Monthly Summary aggregates both, enabling variance analysis per product line

---

## Product Config Table Schema

| Field | Type | Notes |
|-------|------|-------|
| Product Line | Text (primary) | [your product] / BusyCow / [your product] / Others |
| Product / Service Name | Text | SKU display name |
| Fee Type | Single Select | License Fee / Service Fee / Subscription / Maintenance / Training / Project |
| Unit Price (USD) | Number | Our wholesale/revenue price per unit |
| Unit Price (local) | Number | Local currency (HKD/TWD) if applicable |
| Pricing Unit | Single Select | Per Year / Per Month / One-time / Per Device / Per Seat / Per Project / Per Hour |
| COGS Per Unit (USD) | Number | Engineering cost, time cost, or partner cost |
| COGS % of Revenue | Number (%) | Derived: COGS/Revenue |
| Typical Deal Size (USD) | Number | For pipeline sizing |
| Active | Checkbox | Filter out retired SKUs |
| Notes | Text | Pricing rationale, contract refs, special conditions |

**Pitfall**: If COGS has multiple calculation rules (e.g. "HKD 15k or 30% of list, whichever is larger"), document the rule in Notes — Bitable can't enforce conditional formulas reliably via API. Record the resolved number.

---

## Revenue Tracker Table Schema

| Field | Type | Notes |
|-------|------|-------|
| Month (primary) | Date | Set to first of month; format yyyy/MM/dd |
| Product Line | Single Select | [your product] / BusyCow / [your product] / Others |
| Entry Type | Single Select | **Forecast** or **Actual** — the dual-purpose toggle |
| Product / Service | Text | SKU name (mirrors Config table) |
| Fee Type | Single Select | Same options as Config |
| Units | Number | Number of deployments/licenses/seats |
| Unit Price (USD) | Number | Snapshot from Config at time of entry |
| Revenue (USD) | Number | Units × Unit Price |
| Revenue (local) | Number | TWD/HKD equivalent |
| COGS (USD) | Number | Units × COGS Per Unit |
| COGS (local) | Number | Local currency equivalent |
| Gross Profit (USD) | Number | Revenue − COGS |
| Gross Margin % | Number (%) | GP / Revenue |
| Sales Commission (USD) | Number | Add if commission structure exists |
| Client | Text | Customer name |
| Invoice # | Text | For Actual rows |
| Status | Single Select | Forecast / Invoiced / Collected / Overdue / Cancelled |
| Notes | Text | Region, deal context, distribution notes |

### Entry Type logic
- **Forecast rows**: filled by Hunter/agent with planned units + prices; Status = "Forecast"
- **Actual rows**: entered when deal closes; Status → Invoiced → Collected
- Filter by Entry Type to get pure forecast view or pure actuals view
- Variance = Actual Revenue − Forecast Revenue (compute in Summary table)

---

## Monthly Summary Table Schema

| Field | Type | Notes |
|-------|------|-------|
| Month (primary) | Date | |
| Year-Month | Text | "2026-07" for display |
| {ProductLine} Forecast Rev (USD) | Number | One column per product line |
| {ProductLine} Actual Rev (USD) | Number | One column per product line |
| {ProductLine} COGS (USD) | Number | One column per product line |
| Total Forecast Revenue (USD) | Number | Sum across lines |
| Total Actual Revenue (USD) | Number | Sum across lines |
| Total COGS (USD) | Number | |
| Forecast Gross Profit (USD) | Number | |
| Actual Gross Profit (USD) | Number | |
| Gross Margin % | Number (%) | |
| Forecast Expenses (USD) | Number | From Expenses table |
| Actual Expenses (USD) | Number | |
| Net Cash Flow (USD) | Number | |
| Opening Balance (USD) | Number | Manual entry |
| Closing Balance (USD) | Number | |
| Cumulative Balance (USD) | Number | |
| Status | Single Select | Draft / Closed |
| Notes | Text | |

**Note**: Bitable formula/lookup fields are unreliable via API. Populate Summary rows via API script that aggregates Revenue Tracker rows, or instruct user to use Bitable's built-in field grouping/rollup views.

**NTD columns in Summary**: Add a `USD/NTD Rate 匯率` field (Number) per row — user updates monthly. Then add NTD equivalent fields for each key USD figure: Revenue, COGS, Expenses, Net CF, Closing Balance. This is the correct approach — do NOT use TWD fields on detail tables (Revenue/Expenses), only on the Summary. Removing TWD from detail tables simplifies data entry and avoids FX confusion.

---

## Expenses Table Additions (vs default)

Add these fields on top of standard expense tracking:
- `Entry Type` (Single Select): Forecast / Actual — same pattern as Revenue
- `Product Line` (Single Select): which line this cost belongs to (or "Shared")

Category options to use:
```
Payroll / Cloud & Hosting / Software & SaaS / Sales & Marketing /
R&D / Admin & Legal / Travel & Entertainment / Hardware / COGS / Other
```

---

## Unit Economics Pattern

When inputting a new product line, always resolve these 5 numbers first before touching the DB:

```python
# Per-unit economics template
list_price      = ?       # SRP / customer-facing price
our_revenue     = ?       # wholesale price (what we actually receive)
cogs_per_unit   = ?       # engineering / partner / time cost
gross_profit    = our_revenue - cogs_per_unit
gross_margin    = gross_profit / our_revenue

# Optional commission layer
commission_rate = 0.25    # e.g. 25% of GP
commission      = gross_profit * commission_rate
net_after_comm  = gross_profit - commission
net_margin      = net_after_comm / our_revenue
```

Print and verify all numbers **before** inserting into Bitable. Prevents wrong data that's tedious to clean up row by row.

---

## Multi-Currency Handling

- Primary currency: **USD** (all Revenue, COGS, GP fields)
- Local currency fields (HKD, TWD) stored as raw numbers — label the field clearly
- HKD/USD peg: **7.78** (use this unless user specifies otherwise)
- TWD/USD: ~32 (check current rate)
- Store the FX rate used in the Notes field of each row for auditability

---

## Forecast Distribution Patterns

When user gives annual/semi-annual targets, spread into monthly rows:

```python
# Even spread
units_per_month = total_units / num_months

# Front-loaded (typical for sales ramp)
# e.g. 30 units over 12 months: lighter H1, heavier H2
tw_2027_pro = [(1,2),(2,2),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,2),(11,1),(12,2)]
assert sum(u for _,u in tw_2027_pro) == 30

# Back-loaded (e.g. product launches in Q4)
os_2026_lc = [(10,2),(11,2),(12,1)]
```

Always `assert sum(...) == total` before inserting — catches distribution errors.

---

## API Notes (Lark Bitable)

- **Field update**: use `PUT` not `PATCH` on `/bitable/v1/apps/{token}/tables/{tid}/fields/{fid}`
  - `PATCH` returns HTTP 404 (confirmed broken as of 2026-05)
- **Record update**: same — use `PUT` not `PATCH` on `/bitable/v1/apps/{token}/tables/{tid}/records/{rid}`
  - `PATCH` on records also returns HTTP 404
- **Auth**: use BusyCow profile app `cli_a97aab1888f8de17` — has bitable write permissions
- **Insert records**: `POST /bitable/v1/apps/{token}/tables/{tid}/records` with `{\"fields\": {...}}`
- **Rate limit**: add `time.sleep(0.25)` between record inserts to avoid throttling; `time.sleep(0.15)` for deletes
- **Select fields**: pass the option text string directly (e.g. `\"Forecast 預測\"`) — no option ID needed on insert
- **Date fields**: pass millisecond timestamps — `int(datetime(y, m, d).timestamp() * 1000)`
- **Rename table**: `PATCH /bitable/v1/apps/{token}/tables/{tid}` with `{\"name\": \"New Name\"}` — works
- **Read doc content**: `GET /docx/v1/documents/{doc_id}/raw_content` returns full plain text — useful for reading agreement/pricing docs before entering data
- **Download file**: `GET /drive/v1/files/{file_token}/download` — returns file bytes; docx can be parsed with Python zipfile + xml.etree to extract text

## Confirmed Working Table IDs (BusyCow Financial Tracker)

- **Base**: `LRUIb9hpmaHCnDssq1OjRv73pOe`
- **Revenue Tracker**: `{{TABLE_ID}}`
- **Expenses**: `{{TABLE_ID}}`
- **Monthly Summary**: `{{TABLE_ID}}`
- **Product Config**: `{{TABLE_ID}}`

## GBrain Ingest

After building the tracker, write a summary MD and import into GBrain:

```python
# 1. Write to obsidian vault
write_file('~/obsidian-vault/Projects/company-financial-forecast-YYYY.md', content)

# 2. Import via gbrain — MUST be a directory, not a single file
terminal("gbrain import ~/obsidian-vault/Projects/ --no-embed 2>&1")
# ❌ FAILS: gbrain import ~/obsidian-vault/Projects/myfile.md  (ENOTDIR error)

# 3. Verify
terminal("gbrain search 'financial forecast YYYY' 2>&1")
```

MD frontmatter:
```yaml
---
type: analysis
tags: [finance, forecast, company, YYYY, cashflow, annual-plan]
created: YYYY-MM-DD
accountable: ceo-name
consulted: other-name
---
```

Include in the MD: revenue table, pricing structure, OpEx table, monthly cashflow table, key risks, and $1M ARR analysis if applicable. This makes the financial model queryable from any future session without reopening Lark.

---

## [your product] Pricing (as of 2026-05, Sky Dynamics agreement)

| SKU | Type | Wholesale USD | COGS USD | GM% |
|-----|------|--------------|----------|-----|
| SD - Annual Subscription | Subscription/yr | $2,300 | $2,000 | 13% |
| Pro - Perpetual | One-time | $4,060 | $2,000 | 51% |
| LC - Perpetual | One-time | $8,050 | $3,000 | 63% |
| LC - Subscription | Subscription/yr | $3,500 | $3,000 | 14% |
| ER - Perpetual | One-time | $11,550 | $3,000 | 74% |
| ER - Subscription | Subscription/yr | $5,000 | $3,000 | 40% |

COGS = time/engineering cost (same pool as Pro for SD).

## BusyCow Pricing (as of 2026-05, [Client] Reseller Agreement)

| Item | HKD | USD (÷7.78) |
|------|-----|-------------|
| List price (SRP) | 50,000 | 6,427 |
| Our revenue (WS, 40% disc) | 30,000 | 3,856 |
| COGS (eng partner, 30% of list) | 15,000 | 1,928 |
| Gross Profit | 15,000 | 1,928 (50%) |
| Hunter commission (25% of GP) | 3,750 | 482 |
| Net after commission | 11,250 | 1,446 (37.5%) |

**COGS rule**: 30% of list price (not 30% of wholesale). If deal size changes, COGS adjusts accordingly. Compute in Python at insertion time — don't hardcode.

## [your product] Pricing (as of 2026-05)

| Item | Amount | Notes |
|------|--------|-------|
| 2026 initial deployment | HKD 150,000 = USD 19,280 | One-time from [Client], Sep 2026 |
| Dev cost (Jul–Dec 2026) | NTD 50,000/mo = USD 1,538/mo | Goes to **Expenses (R&D)**, not Income COGS |
| 2027 subscription | HKD 15,000/mo = USD 1,928/mo | [Client] recurring, near-zero marginal COGS |
| Overseas license | USD 10,000/unit | COGS USD 3,000/unit (30%), GM 70% |

Key pattern: **initial project payment ≠ per-unit COGS**. The NTD 50k/mo dev cost is an operating expense during build phase, booked to Expenses not Income COGS.

## OpEx Structure (BusyCow 2026-2027)

| Item | NTD/mo | USD/mo | Notes |
|------|--------|--------|-------|
| Hunter basic salary | 45,000 | 1,385 | Always paid |
| Gov insurance + retirement | 30,000 | 923 | Always |
| Cloud & SaaS | 10,000 | 308 | Always |
| Office rental | 12,500 avg | 385 avg | Quarterly NTD 37,500; book as lump in payment month for cashflow accuracy |
| Kevin salary | 0–150,000 | 0–4,615 | From Jul 2026; capped by cashflow |
| [your product] dev cost | 50,000 | 1,538 | Jul–Dec 2026 only |

**Kevin cashflow-capping pattern**: compute running cumulative balance month by month; Kevin gets `min(max_salary, max(0, ncf_before_kevin))`. Flag months where Kevin is capped — these are cashflow risk months.

## Cashflow Analysis Print Pattern

```python
SEP = "═"*90
for (y, m) in all_months:
    # ... compute ...
    flag = "🔴" if net_cf < 0 else ("🟡" if kevin < kevin_max else "")
    print(f"  {y}-{m:02d} | Rev {total_rev:>8,.0f} | GP {total_gp:>7,.0f} ({gm:.0%}) "
          f"| OpEx {total_opex:>6,.0f} | NCF {net_cf:>7,.0f} | Cum {cumbal:>8,.0f} "
          f"| NTD {cumbal*USD_NTD:>10,.0f} {flag}")
    # detail line: Comm / Kevin / Office / special items
    print(f"  {'':<9} Comm ${comm:,.0f}  Kevin ${kevin:,.0f}  Office ${office:,.0f}")
```

Print year totals and Kevin feasibility warnings at the end. 🔴 = negative NCF (check buffer). 🟡 = Kevin capped.

**Important**: Negative NCF months are not a crisis if cumulative buffer is large enough. Always show both monthly NCF AND running cumulative balance.

