---
name: numpy-financial
description: >
  Use numpy-financial for all financial calculations — NPV, IRR, MIRR, PMT, PV, FV,
  loan amortisation, payback, discount rates, LTV, DCF analysis. Use when doing any
  financial forecast, valuation, unit economics, or time-value-of-money computation.
  Always import numpy_financial as npf instead of hand-coding financial formulas.
version: 1.0.0
author: BusyCow/Hermes
metadata:
  hermes:
    tags: [finance, numpy, IRR, NPV, DCF, LTV, financial-model]
---

# numpy-financial

Python library for financial calculations. Separated from NumPy core in v1.17.
Official docs: https://numpy.org/numpy-financial/

## Installation

Already installed in the Hermes venv:
```
~/.hermes/hermes-agent/venv/bin/python
```
Note: venv symlink may resolve to ~/.hermes/hermes-agent/venv/bin/python

Verified working: v1.0.0

```bash
# If ever needs reinstalling (use full path — symlink may not resolve):
~/.hermes/hermes-agent/venv/bin/python -m pip install numpy-financial
# or via pip3:
~/hermes-agent/venv/bin/pip3 install numpy-financial
```

## Standard Import

```python
import numpy_financial as npf
import numpy as np
```

## Full Function Reference

### `npf.npv(rate, values)` — Net Present Value
```python
# rate: discount rate per period (e.g. 0.10 for 10% annual)
# values: array of cashflows; values[0] is at t=0
npv = npf.npv(0.10, [-1_000_000, 200_000, 350_000, 400_000, 500_000])
# → NPV of an investment with initial outlay and 4 years of inflows
```

### `npf.irr(values)` — Internal Rate of Return
```python
# values: cashflow array (must change sign at least once)
irr = npf.irr([-9_000, 2_424*12, 2_424*12, 2_424*12])  # [your product] PF example
print(f"IRR: {irr*100:.1f}%")
```

### `npf.mirr(values, finance_rate, reinvest_rate)` — Modified IRR
```python
# Use when reinvestment rate differs from financing rate (more realistic than IRR)
mirr = npf.mirr([-9_000, 2_424*12, 2_424*12, 2_424*12], 0.10, 0.08)
```

### `npf.pv(rate, nper, pmt, fv=0, when='end')` — Present Value
```python
# Discount a series of equal payments back to today
# Rate, nper must be same period (monthly rate for monthly payments)
pv = npf.pv(0.10/12, 36, -2_424)   # PV of 36 months of $2,424 perf fee at 10% discount
```

### `npf.fv(rate, nper, pmt, pv=0, when='end')` — Future Value
```python
fv = npf.fv(0.05/12, 60, -500, 0)  # Invest $500/mo for 5yr at 5% → future value
```

### `npf.pmt(rate, nper, pv, fv=0, when='end')` — Payment (Loan / Annuity)
```python
# Monthly payment on a loan or annuity
monthly_payment = npf.pmt(0.06/12, 30*12, 200_000)  # 30yr mortgage at 6%
```

### `npf.ppmt(rate, per, nper, pv)` — Principal portion of payment
```python
principal_paid = npf.ppmt(0.06/12, 1, 30*12, 200_000)  # month 1 principal
```

### `npf.ipmt(rate, per, nper, pv)` — Interest portion of payment
```python
interest_paid = npf.ipmt(0.06/12, 1, 30*12, 200_000)   # month 1 interest
```

### `npf.nper(rate, pmt, pv, fv=0)` — Number of periods
```python
months_to_payback = npf.nper(0.0, -9_000, 9_000+5_065, 0)  # CAC payback period
```

### `npf.rate(nper, pmt, pv, fv)` — Interest rate per period
```python
r = npf.rate(36, 2_424, -9_000, 0)   # Implied monthly return on station investment
print(f"Monthly: {r*100:.2f}%  Annual: {((1+r)**12-1)*100:.1f}%")
```

---

## [your product] Financial Model Patterns

### Station-Level IRR
```python
import numpy_financial as npf

# Tier 3 MY station (conservative)
impl_cost   = 9_000   # Y1 fully-loaded impl
sub_yr      = 10_000  # annual subscription
pf_mo       = 2_424   # monthly performance fee (Y2-Y4)
support_yr  = 3_600   # annual support cost

cashflows = [
    -(impl_cost + 5_065),          # Y0: impl + CAC
    sub_yr - support_yr,           # Y1: sub - support (no PF)
    sub_yr + pf_mo*12 - support_yr, # Y2: sub + PF - support
    sub_yr + pf_mo*12 - support_yr, # Y3
    sub_yr + pf_mo*12 - support_yr, # Y4 (last PF year)
    sub_yr - support_yr,           # Y5: renewal only
]
irr = npf.irr(cashflows)
npv_10 = npf.npv(0.10, cashflows)
print(f"Station IRR: {irr*100:.1f}%")
print(f"NPV @ 10% discount: ${npv_10:,.0f}")
```

### Portfolio NPV (Seed Investment)
```python
# Discount annual cashflows at VC hurdle rate (typically 30-40% for seed)
annual_cashflows = [-1_000_000, -73_750, -203_912, 169_007]  # Y0 seed, Y1, Y2, Y3
npv_30 = npf.npv(0.30, annual_cashflows)
irr = npf.irr(annual_cashflows)
print(f"Portfolio IRR: {irr*100:.1f}%")
print(f"NPV @ 30% hurdle: ${npv_30:,.0f}")
```

### Loan / Revenue-Based Financing Amortisation
```python
loan_amount = 500_000
annual_rate = 0.08
term_months = 36

monthly_payment = npf.pmt(annual_rate/12, term_months, loan_amount)
# Build amortisation schedule
for month in range(1, 7):
    principal = npf.ppmt(annual_rate/12, month, term_months, loan_amount)
    interest  = npf.ipmt(annual_rate/12, month, term_months, loan_amount)
    print(f"Month {month}: P=${-principal:,.0f}  I=${-interest:,.0f}")
```

### Cohort LTV Discounting
```python
# Discount a cohort's multi-year cashflows to present value
discount_rate = 0.15  # 15% annual hurdle
cashflows_by_year = [-2_600, 35_488, 35_488, 35_488, 6_400]  # Tier3 MY 5yr GP
ltv_discounted = npf.npv(discount_rate, cashflows_by_year)
ltv_undiscounted = sum(cashflows_by_year)
print(f"LTV (undiscounted): ${ltv_undiscounted:,.0f}")
print(f"LTV (discounted @{discount_rate*100:.0f}%): ${ltv_discounted:,.0f}")
```

### CAC Payback Period (Precise)
```python
# Monthly GP stream until cumulative GP >= CAC + impl cost
total_investment = 5_065 + 9_000  # CAC + impl
monthly_gp = sub_yr/12 - support_yr/12
months_payback = npf.nper(0, -monthly_gp, total_investment)
print(f"Payback: {months_payback:.1f} months")
```

---

## When to Use Each Function

| Task | Function |
|---|---|
| Is this investment worth it at X% discount? | `npv()` |
| What return does this investment generate? | `irr()` or `mirr()` |
| How long to pay back investment? | `nper()` or manual loop |
| What's the PV of future performance fees? | `pv()` |
| Loan / SaaS payment modelling | `pmt()` |
| Amortisation schedule | `ppmt()` + `ipmt()` |
| Implied discount rate | `rate()` |

---

## Pitfalls

1. **Period consistency**: if `rate` is monthly, `nper` must be months and `pmt` must be monthly amount
2. **Sign convention**: outflows are negative, inflows are positive (or vice versa — be consistent)
3. **npv() values[0]**: the first element is at t=0 (immediate). Use `npf.npv(r, [0] + future_flows)` if you want t=0 cashflow to be zero
4. **irr() convergence**: may return `nan` if cashflows don't change sign or have complex roots. Check with `np.isnan()`
5. **mirr() vs irr()**: prefer `mirr()` for realistic models where reinvestment rate ≠ IRR (common in B2G long-cycle businesses)
