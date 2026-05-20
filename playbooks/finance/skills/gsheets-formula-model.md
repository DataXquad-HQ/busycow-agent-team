---
name: gsheets-formula-model
description: >
  Build a live, formula-driven financial model in Google Sheets — all P&L, cashflow,
  and summary cells use formulas that reference a single Assumptions tab. Changing any
  assumption recalculates the entire model. Use when the user wants a working financial
  model (not a static data dump) with tab-to-tab cell linkage, named ranges, scenario
  switcher, and conditional formatting. Designed for [your product] v5 but the architecture
  applies to any SaaS / B2G financial model.
version: 1.0.0
author: BusyCow/Hermes
metadata:
  hermes:
    tags: [Google-Sheets, financial-model, formulas, named-ranges, scenario-model, B2G, SaaS]
---

# Google Sheets Formula-Driven Financial Model

A live financial model where every calculated cell uses formulas referencing Assumptions.
Change one input → entire model recalculates.

## Architecture (10 tabs)

```
┌─────────────────────────────────────────────────────────┐
│  Assumptions  ← ONLY tab with hardcoded values          │
│    Named ranges: SEED, SUB_T3, TARIFF_MY, SAL_BD, etc.  │
│    Scenario switcher: cell B2 = "Base" or "Target"      │
├─────────────────────────────────────────────────────────┤
│  Ramp         ← deployment schedule (plan data)         │
│    Columns: Mo, Date, Base New/Cum/ARR/PF,              │
│              Target New/Cum/ARR/PF, BD Comm             │
├─────────────────────────────────────────────────────────┤
│  P&L          ← pure formulas → Assumptions + Ramp      │
│  Cashflow     ← pure formulas → P&L (with DSO offset)   │
│  Summary      ← SUMIF aggregating P&L by year           │
│  Comparison   ← hardcoded results + delta formulas      │
│  Unit Econ    ← formulas → Assumptions                  │
│  KPI Dash     ← formulas → Summary + P&L               │
│  Sensitivity  ← data table referencing Assumptions      │
│  UoP          ← mostly static                          │
└─────────────────────────────────────────────────────────┘
```

## Assumptions Cell Map (column B = value)

| Row | Named Range | Value | Description |
|---|---|---|---|
| B3 | SEED | 1000000 | Seed raise USD |
| B7 | SUB_T1 | 30000 | Tier 1 >3000HP sub/yr |
| B8 | SUB_T2 | 20000 | Tier 2 1500-3000HP |
| B9 | SUB_T3 | 10000 | Tier 3 500-1500HP |
| B10 | SUB_T4 | 5000 | Tier 4 <500HP |
| B13 | TARIFF_TW | 0.130 | Taiwan USD/kWh |
| B14 | TARIFF_MY | 0.095 | Malaysia USD/kWh |
| B15 | TARIFF_ID | 0.065 | Indonesia USD/kWh |
| B16 | SEC | 0.35 | kWh/m³ |
| B19 | PF_ELEC_CON | 0.10 | Conservative saving |
| B21 | PF_SHARE | 0.50 | 50/50 split |
| B22 | PF_START | 12 | PF start month |
| B23 | PF_DUR | 36 | PF duration months |
| B26 | IMPL_EXT | 3000 | External impl USD |
| B27 | MANDAY_RATE | 300 | USD/manday |
| B28 | IMPL_DAYS_Y1 | 20 | Mandays Year 1 |
| B29 | IMPL_DAYS_Y2 | 10 | Mandays Year 2+ |
| B30 | SUPPORT_DAYS | 12 | Support mandays/yr |
| B31 | IMPL_Y1 | =B26+B28*B27 | Total impl Y1 |
| B32 | IMPL_Y2 | =B26+B29*B27 | Total impl Y2+ |
| B33 | SUPPORT_MO | =B30*B27/12 | Support $/mo/station |
| B34 | COGS_EXT | =B26 | P&L COGS (ext only) |
| B37 | SAL_FOUNDERS | 20000 | 4 founders USD/mo |
| B38 | SAL_TW | 5800 | TW PM+PE USD/mo |
| B39 | SAL_BD | 5000 | BD Director USD/mo |
| B40 | SAL_AI | 10000 | AI Engineer USD/mo |
| B41 | SAL_MY | 2800 | MY team USD/mo |
| B42 | SAL_ID | 2700 | ID team USD/mo |
| B43 | SAL_PLAT | 10000 | Platform Eng USD/mo |
| B46 | MO_BD | 4 | BD hire trigger month |
| B47 | MO_TW | 3 | TW hire month |
| B48 | MO_MY | 5 | MY hire month |
| B49 | MO_ID | 7 | ID hire month |
| B50 | MO_PLAT | 18 | Platform hire month |
| B53 | RENT | 3000 | Rent+admin USD/mo |
| B54 | TRAVEL | 2500 | Travel USD/mo |
| B55 | MARKETING | 3000 | Marketing USD/mo |
| B56 | CLOUD | 2000 | Cloud USD/mo |
| B57 | MO_CLOUD | 13 | Cloud start month |
| B58 | RD | 8000 | R&D USD/mo |
| B59 | MO_RD | 15 | R&D start month |
| B60 | SERA | 5000 | Series A prep USD/mo |
| B61 | MO_SERA | 21 | SerA start month |
| B64 | GRANT_ESG | 296000 | EnterpriseSG USD |
| B65 | MO_GRANT_ESG | 9 | ESG grant month |
| B66 | GRANT_MY | 38500 | Malaysia grant USD |
| B67 | MO_GRANT_MY | 12 | MY grant month |
| B68 | GRANT_TW | 77500 | Taiwan grant USD |
| B69 | MO_GRANT_TW | 15 | TW grant month |
| B72 | DSO | 2 | DSO months delay |

## P&L Formula Patterns

Row 2 = Month 0 (Oct 2026). Mo index = `B2`-based.

```
Col F (Sub Rev):    =E{r}/12
Col G (Perf Fee):   pulled from Ramp tab: =Ramp!F{ramp_r}  (or G for target)
Col H (Grant):      =IF(B{r}=MO_GRANT_ESG,GRANT_ESG,IF(B{r}=MO_GRANT_MY,GRANT_MY,IF(B{r}=MO_GRANT_TW,GRANT_TW,0)))
Col I (Total Rev):  =F{r}+G{r}+H{r}
Col J (Ext COGS):   =C{r}*COGS_EXT
Col K (Support):    =D{r}*SUPPORT_MO
Col L (Tot COGS):   =J{r}+K{r}
Col M (Gross P):    =F{r}+G{r}-L{r}
Col N (GM%):        =IFERROR((F{r}+G{r}-L{r})/(F{r}+G{r}),0)
Col O (Headcount):  =SAL_FOUNDERS+IF(B{r}>=MO_TW,SAL_TW,0)+IF(B{r}>=MO_BD,SAL_BD+SAL_AI,0)+IF(B{r}>=MO_MY,SAL_MY,0)+IF(B{r}>=MO_ID,SAL_ID,0)+IF(B{r}>=MO_PLAT,SAL_PLAT,0)
Col P (BD Comm):    =Ramp!H{ramp_r}   (pre-calculated in Ramp tab)
Col Q (Fixed OpEx): =RENT+TRAVEL+MARKETING+IF(B{r}>=MO_CLOUD,CLOUD,0)+IF(B{r}>=MO_RD,RD,0)+IF(B{r}>=MO_SERA,SERA,0)
Col R (Tot OpEx):   =O{r}+P{r}+Q{r}
Col S (Tot Exp):    =L{r}+R{r}
Col T (EBITDA):     =I{r}-S{r}
Col U (Op EBITDA):  =F{r}+G{r}-S{r}
```

## Cashflow Formula Patterns

```
Col B (Sub Cash):   =IFERROR(INDEX('P&L'!F:F,MATCH(A{r},'P&L'!A:A,0)-DSO),0)
                    or simpler: ='P&L'!F{r-DSO}  (2-row offset for DSO)
Col C (PF Cash):    ='P&L'!G{r}
Col D (Grant Cash): ='P&L'!H{r}
Col E (Total In):   =B{r}+C{r}+D{r}
Col F (Total Out):  ='P&L'!S{r}
Col G (Net CF):     =E{r}-F{r}
Col H (Cum Balance):=H{r-1}+G{r}  (H1 = SEED)
```

## Summary Formula Patterns

```
=SUMIF('P&L'!$A$2:$A$28,">="&DATE(year,1,1),'P&L'!F$2:F$28)
  - or use SUMPRODUCT with YEAR() function
```

## Named Ranges Setup (via API)

```python
def add_named_ranges(sid, token, sheet_id, named_ranges):
    """
    named_ranges: dict of {name: (row_1indexed, col_1indexed)}
    All in Assumptions tab (sheet_id = gid of Assumptions)
    """
    requests = []
    for name, (row, col) in named_ranges.items():
        requests.append({
            "addNamedRange": {
                "namedRange": {
                    "name": name,
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row - 1,
                        "endRowIndex": row,
                        "startColumnIndex": col - 1,
                        "endColumnIndex": col
                    }
                }
            }
        })
    batch_update(sid, token, requests)
```

## When to Use Crew vs Direct API Writes

**Use CrewAI crew:** When the agent needs to *reason* about what to write — designing formula chains, auditing cross-tab references, generating narrative content, or deciding column structure.

**Use `execute_code` direct API:** When you already know exactly what every cell should contain. Verified financial model data (numpy-financial pre-computed numbers) should be written directly — not through a crew. Crew agents default to writing one row at a time (126 calls observed for a 27-row sheet), burning iterations and producing partial output.

**Rule of thumb:** Crew for design + spec + audit. `execute_code` for the actual write.

## Hydro-Format Infrastructure Model Architecture

Mirrors a professional infrastructure financial model (e.g. hydro power company format):

```
CF tab (SPINE — all other tabs reference this)
  Rows A-D = hierarchical label columns (Category / Sub / Sub-sub / Item)
  Col E = FY2026 | F = FY2027 | G = FY2028 | H = FY2029E  ← annual totals
  Col I-Q = quarterly (Q4-26, Q1-27 ... Q4-28)             ← quarterly subtotals
  Col R onwards = monthly Oct-26 ... Dec-28 (27 cols)       ← actual data
  FY cols = =SUM() of 3 or 12 monthly cols
  Quarterly cols = =SUM() of 3 monthly cols

P&L tab (summary view)
  Pulls annual + quarterly from CF: =CF!E{row}, =SUM(CF!I{row}:CF!K{row})
  Hierarchical label rows, empty rows as section separators
  Shows: Revenue sections → COGS → Gross Profit → OpEx breakdown → EBITDA → Cash summary

Other tabs: BS, DCF (with sensitivity matrix), Sub Assumptions (unit economics), 
  Station Pipeline (site list), OpEx by Month, Market Peers, Cap Table
```

Key formatting conventions (hydro style):
- Navy (`#0B2546`) header row, white bold text
- Medium blue (`#1F4E79`) section header rows, white text  
- Light blue (`#BDD7EE`) subtotal/total rows, bold
- Freeze row 1 + freeze cols A-D on CF tab
- Number format: `#,##0` (no decimals for USD)

## Pitfalls

1. **Named ranges must be created AFTER values are written** — the cell must exist before naming it
2. **Named ranges are spreadsheet-scoped** — you can use `=SEED` directly in any cell across any tab
3. **DSO offset in cashflow** — use `OFFSET` or row index arithmetic, not VLOOKUP (VLOOKUP on dates is fragile)
4. **Circular reference risk** — cashflow Cum Balance H{r}=H{r-1}+G{r} — row 2 must explicitly reference SEED not H1
5. **Array formulas in Summary** — use `SUMPRODUCT(YEAR('P&L'!A$2:A$28)=year, 'P&L'!T$2:T$28)` not SUMIF with dates
6. **Scenario switcher** — use a dropdown validation on Assumptions!B2 (Base/Target), then P&L pulls from Ramp using `IF(Assumptions!$B$2="Target", Ramp!G{r}, Ramp!C{r})`
7. **`USER_ENTERED` value input** — formulas must be passed as strings starting with `=` and `valueInputOption=USER_ENTERED`
8. **Named range names** — no spaces, no special chars, max 255 chars, case-insensitive in formulas
9. **Rate limits** — `batchUpdate` for formatting: max 100 requests per call, add `time.sleep(0.5)` between calls
10. **Cell reference style** — use `$` anchoring for Assumption refs: `Assumptions!$B$37` not `Assumptions!B37` (so filling down doesn't shift the row)
11. **Don't re-derive verified numbers — hardcode them** — If a source-of-truth dataset exists (numpy-financial EBITDA, pre-audited monthly figures), hardcode those exact values as Python lists and write them directly. Attempting to re-derive inside crew tasks produces subtly wrong numbers (missing BD commission, wrong COGS netting). Lock the numbers.
12. **COGS formula must net correctly** — `COGS = new_stations × impl_cost + cumulative_stations × support_cost`. The cumulative support cost grows every month and is easy to mis-net. Always verify Mo1 COGS manually: `2×$3,000 + 3×$300 = $6,900`. If it doesn't match the verified source, your formula has a bug.
13. **Target scenario monthly cash requires anchoring** — Proportional scaling of base EBITDA to hit target annual totals produces a correct end-of-year figure but wrong intermediate months. Always anchor Mo26 (or final month) to the verified end-cash figure after scaling, and note that intermediate months are estimates.
14. **Lark/Feishu files — download via Drive API, not direct file URL** — Files shared via Lark (`/file/TOKEN`) can be downloaded using: `GET {DOMAIN}/open-apis/drive/v1/files/{file_token}/download` with tenant access token. The `/medias/` endpoint returns 403. File type detected from `Content-Disposition` header.

## Direct REST API vs gws CLI

When building sheets from **inside a Docker container** (e.g. CrewAI crew), use direct REST calls — not the `gws` CLI bridge. The gws binary isn't available inside `python:3.11-slim` containers.

```python
def sheets_request(method: str, url: str, body: dict = None) -> dict:
    """Authenticated Google Sheets/Drive API request using refreshed OAuth token."""
    import subprocess, requests as req_lib, os
    env = dict(os.environ)
    env["HERMES_HOME"] = "/workspace"   # gws_bridge.py + token must be here
    env["PYTHONPATH"] = "/workspace"
    script = "from gws_bridge import get_valid_token; print(get_valid_token())"
    res = subprocess.run(["python3", "-c", script], capture_output=True,
                         text=True, timeout=15, env=env)
    token = res.stdout.strip()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    fn = getattr(req_lib, method.lower())
    kwargs = {"headers": headers, "timeout": 30}
    if body:
        kwargs["json"] = body
    r = fn(url, **kwargs)
    try:
        return r.json()
    except Exception:
        return {"error": r.text, "status_code": r.status_code}

# Key endpoints
# Create sheet:  POST  https://sheets.googleapis.com/v4/spreadsheets
# Write values:  POST  https://sheets.googleapis.com/v4/spreadsheets/{id}/values:batchUpdate
# Read values:   GET   https://sheets.googleapis.com/v4/spreadsheets/{id}/values/{range}
# Format/struct: POST  https://sheets.googleapis.com/v4/spreadsheets/{id}:batchUpdate
# Share:         POST  https://www.googleapis.com/drive/v3/files/{id}/permissions
```

Files needed in `/workspace/` inside container:
- `gws_bridge.py` — from `$HERMES_HOME/skills/productivity/google-workspace/scripts/`
- `google_token.json` — from `$HERMES_HOME/`
- `google_client_secret.json` — from `$HERMES_HOME/`

```bash
HERMES_HOME="~/.hermes
docker cp $HERMES_HOME/skills/productivity/google-workspace/scripts/gws_bridge.py crewai:/workspace/gws_bridge.py
docker cp $HERMES_HOME/google_token.json crewai:/workspace/google_token.json
docker cp $HERMES_HOME/google_client_secret.json crewai:/workspace/google_client_secret.json
docker exec crewai pip install -q google-auth google-auth-oauthlib requests
```

Smoke test from inside container:
```bash
docker exec -e HERMES_HOME=/workspace -e PYTHONPATH=/workspace crewai python3 -c "
import os, requests, subprocess
env = dict(os.environ)
token = subprocess.run(['python3','-c','from gws_bridge import get_valid_token; print(get_valid_token())'],
    capture_output=True, text=True, env=env).stdout.strip()
r = requests.post('https://sheets.googleapis.com/v4/spreadsheets',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={'properties': {'title': 'SMOKE_TEST'}}, timeout=15)
sid = r.json().get('spreadsheetId')
print('Created:', sid)
requests.delete(f'https://www.googleapis.com/drive/v3/files/{sid}',
    headers={'Authorization': f'Bearer {token}'}, timeout=10)
print('Cleaned up')
"
```


