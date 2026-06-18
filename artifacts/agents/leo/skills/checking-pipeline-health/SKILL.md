---
name: checking-pipeline-health
description: >
  C6 Pipeline Health Check — weekly review of the full pipeline against
  revenue targets and strategy. Calculates weighted pipeline value, identifies
  gaps to target, flags stalled opportunities and partnerships, estimates
  close probability, and surfaces recommended actions. Requests missing data
  from the sales team via CRM Tasks. Runs every Monday morning.
triggers:
  - "pipeline health check"
  - "weekly pipeline review"
  - "how is the pipeline"
  - "are we on track"
  - "pipeline status"
  - "health check"
  - "C6"
  - "pipeline 健不健康"
  - "本週 pipeline review"
  - "我們達標嗎"
---

# Pipeline Health Check Skill

## Purpose

Every week, Leo acts as BD Lead — reviewing the full pipeline like a manager
would. The core question is always: **are we on track to hit our revenue target?**

If yes: confirm what's working and flag anything at risk.
If no: quantify the gap, identify why, and recommend concrete actions.

---

## When to Run

- **Cron:** Every Monday at 09:00 CST (01:00 UTC)
- **Human trigger:** "pipeline health check" / "are we on track"

---

## Step 1 — Recall strategy context

Recall from both memory layers before touching CRM.

```python
import requests

# Hindsight — goals and benchmarks
goals = requests.post(
    "http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-global/memories/recall",
    json={"query": "revenue target and new customer goal", "top_k": 3}
).json()

benchmarks = requests.post(
    "http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-global/memories/recall",
    json={"query": "pipeline benchmarks conversion rates stall threshold", "top_k": 3}
).json()

icp = requests.post(
    "http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-global/memories/recall",
    json={"query": "ICP ideal customer profile target industries", "top_k": 2}
).json()
```

Also read GBrain for structured numbers:
```python
mcp_gbrain_get_page(slug="concepts/sales-goals")
mcp_gbrain_get_page(slug="concepts/pipeline-benchmarks")
```

**If strategy context is missing** (GBrain pages don't exist, Hindsight empty):
- Flag in the report: "⚠️ No strategy data found. Run `ingesting-sales-strategy` first."
- Still proceed with CRM data — produce a pipeline snapshot without targets.

---

## Step 2 — Pull all active opportunities from CRM

```graphql
{
  opportunities(filter: {
    stage: { notIn: [CUSTOMER] }
    closeDate: { isNullable: { isNull: false } }
  }) {
    edges { node {
      id
      name
      stage
      healthCheck
      amount { amountMicros currencyCode }
      closeDate
      probability
      businessLine
      dealType
      nextFollowUpDate
      nextActionSummary
      currentStatusSummary
      createdAt
      updatedAt
      company { id name }
      pointOfContact { id name { firstName lastName } }
    }}
  }
}
```

Also pull closed-won this period (for progress tracking):
```graphql
{
  opportunities(filter: {
    stage: { eq: CUSTOMER }
  }) {
    edges { node {
      id name
      amount { amountMicros currencyCode }
      closeDate
      businessLine
    }}
  }
}
```

---

## Step 3 — Pull all active partnerships from CRM

```graphql
{
  partnerships(filter: {
    stage: { notIn: [SIGNED] }
  }) {
    edges { node {
      id
      name
      stage
      healthCheck
      updatedAt
      createdAt
      company { id name }
      primaryContact { id name { firstName lastName } }
    }}
  }
}
```

---

## Step 4 — Calculate pipeline metrics

### 4a — Weighted pipeline value

For each opportunity:
```python
# Use CRM probability if set, else use benchmark conversion rate for that stage
stage_benchmarks = {
    "NEW": 0.60 * 0.50 * 0.40 * 0.25,  # full-funnel from NEW
    "SCREENING": 0.50 * 0.40 * 0.25,
    "MEETING": 0.40 * 0.25,
    "PROPOSAL": 0.25,
}

prob = opportunity["probability"] / 100 if opportunity["probability"] else stage_benchmarks.get(opportunity["stage"], 0.1)
amount = opportunity["amount"]["amountMicros"] / 1_000_000 if opportunity["amount"] else None
weighted = amount * prob if amount else None
```

Sum all weighted values → **weighted pipeline value**.

### 4b — Gap to target

```python
revenue_target = [from GBrain concepts/sales-goals]
closed_won_revenue = sum of CUSTOMER opportunities this period
remaining_target = revenue_target - closed_won_revenue
pipeline_coverage = weighted_pipeline_value / remaining_target
# Healthy = coverage > 3x (industry standard)
# At risk = coverage < 2x
# Critical = coverage < 1x
```

### 4c — Stall detection

For each opportunity and partnership:
```python
from datetime import datetime, timezone

stall_threshold_days = [from GBrain concepts/pipeline-benchmarks, default 30]
days_in_stage = (datetime.now(timezone.utc) - datetime.fromisoformat(last_activity)).days
is_stalled = days_in_stage > stall_threshold_days
```

Use `updatedAt` as proxy for last activity if no engagement data is available.

### 4d — Data quality check

Flag opportunities missing critical fields:
- `amount` is null → can't calculate weighted value
- `probability` is null → using benchmark (note this)
- `closeDate` is null → can't assess urgency
- `healthCheck` is null → no risk signal

---

## Step 5 — Assess pipeline health

```
HEALTHY   — coverage >= 3x AND no AT_RISK items AND < 20% stalled
WATCH     — coverage 2x–3x OR some AT_RISK items OR 20–40% stalled
AT_RISK   — coverage 1x–2x OR multiple AT_RISK items OR > 40% stalled
CRITICAL  — coverage < 1x OR majority stalled OR no active pipeline
```

---

## Step 6 — Generate CRM Tasks for missing data

For each opportunity missing `amount` or `closeDate`:

```graphql
mutation {
  createTask(data: {
    title: "[補資料] [Opportunity name] — 請填入預估金額與預計成交日"
    body: { markdown: "**Opportunity:** [name]\n\n**Missing:** [amount / closeDate / both]\n\n**Why it matters:** Leo cannot calculate pipeline coverage without this data. Please update in CRM.\n\nCRM: {{CRM_EXTERNAL_URL}}/objects/opportunities/[UUID]" }
    status: TODO
    dueAt: "[tomorrow 09:00 CST]"
  }) { id }
}
```

---

## Step 7 — Output the Health Report

Deliver to `[Sales] Pipeline Review` channel. **If you don't have the chat_id yet, store it in GBrain (`concepts/sales-strategy-meta`) after the human provides it — do not write it into this skill file.** Format:

```
📊 Weekly Pipeline Health Check — [Date]

**Overall: [HEALTHY / WATCH / AT_RISK / CRITICAL]**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 REVENUE SNAPSHOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Target ([period]):     [revenue_target]
Closed so far:         [closed_won_revenue] ([pct]% of target)
Remaining to close:    [remaining_target]

Weighted pipeline:     [weighted_pipeline_value]
Pipeline coverage:     [N]x  [🟢 / 🟡 / 🔴]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PIPELINE BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEW          [N] opportunities   [total value]
SCREENING    [N] opportunities   [total value]
MEETING      [N] opportunities   [total value]
PROPOSAL     [N] opportunities   [total value]

Partnerships in progress: [N]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  NEEDS ATTENTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stalled (>[N] days no activity):
  • [Company] — [stage] — [N] days stalled
  • [Company] — [stage] — [N] days stalled

AT_RISK:
  • [Company] — [stage] — [reason from currentStatusSummary]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 LEO'S ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2–4 sentences: what the numbers mean, why we're on track or not,
 what the biggest risk is right now]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ RECOMMENDED ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [Specific action — who, what, why]
2. [Specific action]
3. [Specific action — max 5]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 DATA GAPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[N] opportunities missing amount/closeDate.
Tasks created in CRM — please fill in by [tomorrow].
```

---

## Step 8 — Write summary to Hindsight {{ORG_PREFIX}}-pipeline

Store this week's snapshot for Strategy Check to reference:

```python
requests.post(
    "http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories",
    json={"items": [{
        "content": f"Weekly Health Check [date]: status=[HEALTHY/WATCH/AT_RISK/CRITICAL]. Coverage=[N]x. Closed=[value]. Weighted pipeline=[value]. Stalled=[N]. AT_RISK=[N]. Key finding: [one sentence].",
        "tags": ["health-check", "weekly", "pipeline-snapshot", f"[YYYY-MM]"]
    }]}
)
```

---

## Lark Channels

| Channel | What goes here |
|---|---|
| `[Sales] Pipeline Review` (chat_id stored in `concepts/sales-strategy-meta` in GBrain once confirmed) | Full Health Report — weekly |
| `[System] Backend Report` `{{SYSTEM_BACKEND_CHANNEL_ID}}` | Ops log — run stats, tasks created, errors |

**CRM links always use** `{{CRM_EXTERNAL_URL}}/objects/[type]/[UUID]`.

---

## Pitfalls

- **Never use "deal"** — always "opportunity" (CRM object name).
- **No strategy data = no targets** — still produce the pipeline snapshot, just omit the coverage ratio and gap analysis. Flag the missing ingest.
- **amount is stored as amountMicros** — divide by 1,000,000 to get the actual value.
- **Use updatedAt as stall proxy** — if no Engagement data is linked, updatedAt is the best available signal for last activity.
- **Coverage ratio is directional, not precise** — weighted pipeline uses estimated probabilities. Communicate this clearly in the report.
- **Tasks for missing data** — create them, but don't block the report on them. Produce the report with available data, note what's missing.
- **Never hardcode team member names** — use "the sales team", "the rep", "our team".
