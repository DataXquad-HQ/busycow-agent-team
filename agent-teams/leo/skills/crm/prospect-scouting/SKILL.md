---
name: prospect-scouting
description: >
  C1 Prospect Scouting — given a list of companies or people (event attendees,
  cold list, industry directory), analyse who is worth prioritising and why.
  Cross-references ICP, existing CRM/GBrain relationships, and product fit.
  Used before events, before outbound prospecting runs, and any time the Sales Rep
  needs to triage a list of potential contacts.
triggers:
  - "prospect scouting"
  - "誰值得拜訪"
  - "幫我篩選"
  - "活動名單"
  - "參展名單"
  - "attendee list"
  - "cold list"
  - "誰最值得"
  - "哪些公司值得"
  - "scouting"
  - "prioritise list"
  - "prioritize list"
---

# Prospect Scouting Skill

## When to Use

Use before events, conferences, or outbound prospecting runs when the Sales Rep has a list of companies or people to evaluate. Also use when triaging a cold list or industry directory. This skill is read-only — it analyses and ranks, but does not write to CRM.

## Purpose

Given a list of companies or people, figure out who is worth the Sales Rep's time — and why.

This skill is used in two contexts:
1. **Pre-event** — the Sales Rep is about to attend an expo or conference and has the attendee/exhibitor list
2. **Pre-outbound** — before running C2 Outbound Prospecting, triage a cold list to identify the best targets

The output is a **prioritised shortlist with reasoning and suggested approach** — not just a ranking, but enough context for the Sales Rep to walk in prepared.

---

## Inputs

| Input | Format | Notes |
|---|---|---|
| Company / person list | Text, paste, or file | Names, URLs, LinkedIn links, any format |
| Event name (if applicable) | Text | Used for context in output |
| Focus area (optional) | Text | e.g. "focus on water utilities this time" |
| Business line (optional) | e.g. BUSYCOW, AQUAOPTIMA | Narrows fit assessment |

If no focus area is given, Leo assesses fit across all relevant DX business lines.

---

## Flow

### Step 1 — Load knowledge context
Before analysing anyone, check what's available:

```python
# ICP and strategy (graceful degrade if missing)
mcp_gbrain_get_page(slug="wiki/dx-icp")
mcp_gbrain_get_page(slug="wiki/dx-sales-strategy")

# Relevant product wikis (load only the ones relevant to the focus area)
mcp_gbrain_get_page(slug="wiki/products/[business-line]")
```

If ICP page doesn't exist: continue, note the absence in output, use existing opportunity patterns to infer fit criteria.

### Step 2 — For each company/person on the list

Check in parallel:
```python
# CRM — already a contact?
{ companies(filter: { name: { like: "%CompanyName%" } }) {
    edges { node { id name status people { edges { node { name { firstName lastName } status } } } } }
} }

# GBrain — any existing intel or relationships?
mcp_gbrain_get_page(slug="companies/[company-slug]", fuzzy=True)
mcp_gbrain_query(query="[company name] relationship history")

# Hindsight — any prior context?
POST http://localhost:8888/v1/default/banks/dx-pipeline/memories/recall
{"query": "[company name]", "top_k": 3}
```

### Step 3 — Assess fit for each

Score each company/person on:
1. **ICP fit** — matches ideal customer profile (industry, size, geography, problem space)
2. **Product fit** — clear use case for one or more DX business lines
3. **Relationship warmth** — existing contact, prior opportunity, mutual connection, or completely cold
4. **Timing signal** — any news, funding, expansion, or trigger that makes now a good time

### Step 4 — Output prioritised shortlist

```
🎯 **Prospect Scouting — [Event/Context Name]**
[Date] | [Focus area if specified]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 **優先接觸（必見）**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **[Company Name]** — [Key Person / Role if known]
   產品契合：[business line] — [why they fit]
   關係現況：[existing contact / warm intro / cold]
   建議切入：[specific angle or opening]
   觸發點：[any timing signal — news, expansion, known pain]

2. **[Company Name]** ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 **值得聊聊（時間允許）**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. **[Company Name]** — [brief reason]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚪ **可略過**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [Company] — [one-line reason: wrong industry / too small / no fit]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **Summary**
Total assessed: [N] | 必見: [N] | 值得聊: [N] | 略過: [N]

[If ICP missing]: ⚠️ 無 ICP 文件，以現有 opportunity 歷史推斷。建議建立 `wiki/dx-icp` 以提升準確度。
```

---

## Fit Assessment Heuristics

When ICP document is unavailable, use these defaults based on known DX patterns:

| Business Line | Strong fit signals |
|---|---|
| **BusyCow** | Field workforce, construction, logistics, facilities management |
| **GeoKernel** | GIS, spatial data, mapping, smart city, infrastructure planning |
| **AquaOptima** | Water utilities, wastewater, irrigation, water treatment plants |
| **Distify** | Distribution, FMCG, supply chain, route optimisation |
| **TRACI** | Transport, fleet, traffic management |
| **DataXquad** | Enterprise data, analytics, digital transformation |

Geography priority (unless stated otherwise): Taiwan, Hong Kong, Malaysia, Southeast Asia.

---

## Relationship Warmth Tiers

| Tier | Signal |
|---|---|
| 🔥 Hot | Existing LEAD/OPPORTUNITY in CRM, or prior engagement logged |
| 🟠 Warm | In GBrain with timeline entries, or known mutual connection |
| 🟡 Tepid | Company in CRM/GBrain but no active relationship |
| ⚪ Cold | No prior record anywhere |

Warm tiers should always be ranked higher than cold tiers with equivalent fit.

---

## After Scouting

If the Sales Rep confirms they want to engage with a company from the shortlist:
- If they **attend the event and meet**: hand off to `lead-capture` skill afterwards
- If they are a **cold outbound target**: hand off to `C2 Outbound Prospecting` (when built)
- If already in CRM as LEAD: update via `pipeline-interaction` skill

Prospect Scouting does **not** write to CRM or Hindsight by itself.
It is a read-only analysis tool. Writing happens in the downstream skill.

---

## Pitfalls

- **Don't skip knowledge context loading** — even if ICP is missing, check anyway and note it in the output. The ⚠️ flag reminds the Sales Rep to build that wiki page.
- **Company name matching is fuzzy** — CRM `like` search may miss variations. Try multiple spellings. Use GBrain fuzzy=True.
- **Warm relationships always beat cold fit** — a tepid-fit company with an existing warm contact is usually worth more than a perfect-fit cold company.
- **Don't over-rank** — 必見 list should be 3–5 companies max. If everything is high priority, nothing is.
- **Ask for focus area upfront if list is large (20+)** — without a focus, assessment takes longer and output is less actionable.
- **This skill is read-only** — never write to CRM or Hindsight during scouting. Writing happens after the Sales Rep decides to engage.
