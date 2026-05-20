---
name: building-investor-financial-model
description: >
  Build an investor-grade financial forecast for a B2G/SaaS company — multi-scenario
  Python model, Lark Doc (AI-parseable), and Google Sheets prompt. Use when asked to
  build, update, or review a startup financial model for fundraising (seed/Series A).
version: 2.0.0
author: BusyCow/Hermes
metadata:
  hermes:
    tags: [finance, investor, financial-model, seed-round, B2G, SaaS, [your product]]
---

# Building an Investor-Grade Financial Model

Learned from [your product] v1→v5 iteration across one session. Covers the full pipeline:
Python model → Lark Doc → Google Sheets prompt → Google Sheet (direct API).

## When to Use

- User asks to build/update a startup financial forecast for investors
- User has a B2G or outcome-based SaaS business model
- User needs two scenarios (base + target) for a pitch
- Existing model has been challenged by VC questions → rebuild

## The Right Build Order

```
1. Lock assumptions with user FIRST (pricing, ramp, costs, scenarios)
2. Build Python model → verify numbers → catch errors early
3. Write Lark Doc (human-readable + AI-parseable with [TAG] sections)
4. Update/create Google Sheets prompt (self-contained, all data embedded)
5. Build Google Sheet directly via API (google-workspace skill)
```

**Do NOT build the sheet before the Python model is verified.** Wrong numbers in sheet
= full rebuild. Always run the Python model and sanity-check output first.

## Python Model Structure

```python
import numpy_financial as npf  # always use for financial calcs
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
from collections import defaultdict

# Section order:
# 0. Shared parameters (all in one place, sourced)
# 1. Timeline (list of date objects)
# 2. Station/unit sets per scenario
# 3. Revenue calculators (subscription, performance fee, grants)
# 4. Cost calculators (COGS, headcount, opex)
# 5. Model engine: run(stations, ramp) → list of monthly result dicts
# 6. Unit economics with npf.irr/mirr/npv/pv
# 7. Cohort NRR (same-station only, NOT total revenue growth)
# 8. Portfolio metrics (seed IRR, MIRR, NPV at multiple hurdle rates)
# 9. Annual summaries
# 10. Scenario comparison table
# 11. Save JSON for sheet generation
```

### Key patterns

```python
# Always run multiple scenarios from one engine
BASE_RES   = run(BASE_STATIONS,   BASE_RAMP,   "con")
TARGET_RES = run(TARGET_STATIONS, TARGET_RAMP, "con")

# Unit economics MUST use numpy-financial, not manual formulas
cf = [-(impl + cac), gp_y1, gp_y2, gp_y2, gp_y2, gp_y5]
irr  = npf.irr(cf)
mirr = npf.mirr(cf, 0.10, 0.08)  # prefer MIRR over IRR for B2G long cycles
npv  = npf.npv(0.15, cf)         # 15% discount rate for LTV

# Cohort NRR: compare same cohort Year 1 vs Year 2 revenue
# NEVER use monthly total revenue as NRR denominator — misleading
def cohort_nrr(stations, deploy_start, deploy_end):
    cohort = [s for s in stations if deploy_start <= s["deploy_idx"] <= deploy_end]
    rev_y1 = sum(s["sub_yr"] for s in cohort)
    rev_y2 = sum(s["sub_yr"] + pf_annual(s) for s in cohort)
    return rev_y2 / rev_y1 * 100
```

## Common Mistakes That Required Reworking ([your product] v1→v5)

| Mistake | Fix |
|---|---|
| NRW in performance fee base case | Strip NRW — attribution unproven. Electricity saving only. |
| Monthly NRR calculation | Use cohort NRR only. Monthly total looks like 1,540% = destroys credibility. |
| CAC too low (forgot marketing/events) | Include: expo budget (AsiaWater, IWW, IWA, SWAN) + founder time + BD + travel |
| Implementation cost too low | Fully-loaded = external cost + internal mandays × day rate |
| Grant timing too optimistic | Push grants 6+ months. EnterpriseSG takes 6-9 months to disburse. |
| 2028 EBITDA too high | Reinvest surplus: R&D, new hire, Series A prep. VCs expect reinvestment. |
| NRR of 1,540% in monthly table | Remove from P&L tab entirely. Only show cohort NRR in dashboard. |
| Project fee conflated with subscription | Separate: Y1 project fee ≠ recurring subscription. Clarify billing model first. |
| Target scenario ends with less cash | Expected if extra units deploy late — their PF unlocks in Year 3. Add Year 3 extrapolation. |
| Single scenario model | Always build Base + Target (or conservative/base/aggressive). |

## B2G-Specific VC Metrics to Show

| Metric | Notes |
|---|---|
| Unit-level IRR | More meaningful than company IRR for unit economics |
| MIRR (not just IRR) | B2G has long cycles; MIRR is more realistic |
| Discounted LTV | Use 15% discount rate, show undiscounted alongside |
| Cohort NRR | Only same-unit cohort; explain dominant-market (TW 100%) vs expansion-market split |
| Portfolio IRR | Seed investor perspective; include terminal value at ARR multiple |
| NPV at 20%, 30%, 40% | Show VC hurdle sensitivity explicitly |
| Payback period | B2G acceptable up to 36 months; flag if >36 |

## Critical Review Before Showing Investors

Always self-review for these before finalising:
1. Is every assumption at best-case? (No model should be optimistic on all dimensions)
2. NRW / indirect savings included without measurement proof? → Remove
3. Grant timing realistic? → Add 6 months minimum
4. CAC includes all marketing and event costs? → Include expo budget
5. Implementation cost validated against real deployed cost?
6. Negative-IRR units flagged explicitly? → Flag Tier 4 TW etc.
7. If Target ends with less cash than Base → add Year 3 extrapolation explaining why

## Lark Doc Structure (AI-Parseable)

Use `[TAG]` section headers for machine extraction:
```markdown
## [ASSUMPTIONS.TIERS] Subscription Tiers
## [UNIT_ECONOMICS.TABLE] Per-Station Economics
## [ANNUAL_SUMMARY.BASE] Base Case P&L
## [SCENARIO_COMPARISON] Scenario Comparison
## [MODEL_NOTES] Notes for AI/Claude Parsing
```

The `[MODEL_NOTES]` section at the end tells Claude/AI exactly how to build the sheet:
tab names, column order, key formula approaches, validation checks.

## Google Sheet Tab Structure (10 tabs)

1. **Cover** — title, version, both scenarios headline numbers
2. **Assumptions** — named ranges, all inputs sourced
3. **Scenario Comparison** ← investor-facing front page, Base vs Target delta table
4. **Base P&L** — monthly, model-period rows
5. **Target P&L** — monthly, model-period rows
6. **Cashflow** — Base + Target side-by-side (apply DSO delay on subscription revenue)
7. **Unit Economics** — all tiers, IRR/MIRR/NPV/LTV:CAC/flags
8. **KPI Dashboard** — milestones, ARR build, cohort NRR, portfolio metrics, Year 3
9. **Sensitivity** — 6-8 scenarios, critical risk notes
10. **Use of Proceeds** — pie chart + detail

**Scenario Comparison is always Tab 3.** Investor sees this first.
Max 15 rows, 3 columns (Base | Target | Delta).

## Google Sheets Direct API

Authentication already active (OAuth token present). Use google-workspace skill.

```python
HERMES_HOME = "~/.hermes
PYTHON  = f"{HERMES_HOME}/hermes-agent/venv/bin/python"
GBRIDGE = f"{PYTHON} {HERMES_HOME}/skills/productivity/google-workspace/scripts/gws_bridge.py"

# Create spreadsheet
body = {"properties": {"title": "Company Financial Forecast vX"}}
terminal(f"{GBRIDGE} sheets spreadsheets create --json '{json.dumps(body)}' 2>&1")
```

## Pitfalls

1. **Build order**: Python → verify → Lark doc → sheet. Never sheet first.
2. **Scenario comparison tab**: always Tab 3, always the investor-facing page.
3. **NRR**: cohort only, never monthly total. State clearly in doc.
4. **Grants**: push timeline 6+ months from naive estimate. Treat as upside not base.
5. **Negative-IRR tiers**: flag explicitly in unit economics. State deployment rule.
6. **Year 3 extrapolation**: if target scenario ends with less cash than base in Year 2
   (extra units deploy late), add Year 3 row showing when advantage appears.
7. **numpy-financial for all calcs**: never hand-code NPV, IRR, payback. Import npf.
8. **DSO separation**: P&L uses accrual. Cashflow tab applies DSO delay (2 months typical
   for government clients). Show both; they differ materially in early months.
9. **Manday cost double-counting**: internal manday cost is in headcount/salary OpEx.
   Only external contractor cost goes to P&L COGS. Do not add both.
