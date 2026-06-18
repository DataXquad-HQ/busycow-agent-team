---
name: checking-pipeline-strategy
description: >
  C6 Pipeline Strategy Check — monthly review of whether the sales strategy
  is still valid, memory layers are healthy, and the team is on track at a
  strategic level. Compares recent weekly health check snapshots against
  targets, checks GBrain and Hindsight for stale or missing strategy data,
  verifies the Wiki document is current, and alerts the team if strategy
  adjustments may be needed. Runs on the 1st of each month.
triggers:
  - "strategy check"
  - "monthly strategy review"
  - "is our strategy working"
  - "strategy health"
  - "C6 strategy"
  - "策略檢查"
  - "本月策略 review"
  - "策略還對嗎"
---

# Pipeline Strategy Check Skill

## Purpose

Leo acts as BD Lead conducting a monthly strategic review. The question is
not "are individual opportunities healthy" (that's the weekly Health Check)
but **"is our strategy still the right strategy?"**

Three sub-questions:
1. **Memory health** — are GBrain and Hindsight strategy data up to date?
2. **Pattern analysis** — what do the last 4 weekly snapshots tell us?
3. **Strategic signal** — does the data suggest the strategy needs adjusting?

---

## When to Use

- **Cron:** 1st of each month at 09:00 CST (01:00 UTC)
- **Human trigger:** "strategy check", "is our strategy working", "策略檢查"
- **Prerequisite:** `checking-pipeline-health` must have run for at least 2 weeks to have meaningful snapshots in Hindsight. If fewer than 2 snapshots exist, still run memory layer health check but skip trend analysis.

---

## When to Run

- **Cron:** 1st of each month at 09:00 CST (01:00 UTC)
- **Human trigger:** "strategy check" / "is our strategy working"

---

## Step 1 — Check GBrain strategy pages

Vault pages live at `internal/business-lines/[bl]/` — NOT `concepts/`. Check the
active business line's folder. For your active business line, the canonical pages are (replace `[BL]` with your BL slug):

```python
# Vault pages for active BL (replace [BL] with your business line slug)
bl_pages = [
    "internal/business-lines/[BL]/icp",
    "internal/business-lines/[BL]/gtm",
    "internal/business-lines/[BL]/strategy",
    "internal/business-lines/[BL]/product",
    "internal/business-lines/[BL]/market",
    "internal/business-lines/[BL]/overview",
]

# Company-level
company_pages = [
    "internal/company/overview",
]

for slug in bl_pages + company_pages:
    page = mcp_gbrain_get_page(slug=slug)
    # Check: exists? status != "work-in-progress"? updated_at within 90 days?
```

Flag any page that:
- Does not exist → `❌ Missing`
- Has `status: work-in-progress` or `review_needed: true` → `⚠️ Draft — needs human review`
- Has `updated_at` older than 90 days → `⚠️ Stale`
- Exists, is current, and has real content → `✅ OK`

> **Pitfall:** Pages with `status: work-in-progress` in frontmatter are placeholders —
> they exist in GBrain but contain no actionable data. Treat them the same as missing
> for strategy-check purposes. Always read the `compiled_truth` field, not just
> whether the page exists.

---

## Step 2 — Check Hindsight {{ORG_PREFIX}}-global

Verify strategy memories are present:

```python
import requests

checks = [
    "revenue target and new customer goal",
    "ICP ideal customer profile",
    "pipeline benchmarks conversion rates",
    "sales motion and approach",
    "partnership goals and criteria",
]

for query in checks:
    result = requests.post(
        "http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-global/memories/recall",
        json={"query": query, "top_k": 1}
    ).json()
    # Flag if no results returned
```

If any query returns empty → flag as missing.

---

## Step 3 — Retrieve last 4 weekly health check snapshots

```python
result = requests.post(
    "http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories/recall",
    json={"query": "weekly health check pipeline snapshot status coverage", "top_k": 8}
).json()

# Filter to last 4 weeks by date in content
# Extract: status, coverage ratio, key finding per week
```

---

## Step 4 — Analyse patterns across the 4 snapshots

Look for these signals:

| Pattern | Signal | Recommended action |
|---|---|---|
| Coverage < 2x for 3+ consecutive weeks | Pipeline consistently underfilled | Review lead generation — C1/C2 may need attention |
| Same opportunities stalled for 3+ weeks | Execution problem or wrong ICP | Review those opportunities against ICP criteria |
| PROPOSAL→CUSTOMER conversion below benchmark for 2+ weeks | Proposal quality or pricing issue | Review proposal approach or pricing strategy |
| No new opportunities added in 3+ weeks | Top of funnel is dry | Activate outbound (C2) or review lead capture (C1) |
| Partnership pipeline empty for 2+ months | Partnership strategy not executing | Review partner strategy and activation |
| Health consistently HEALTHY | Strategy is working | Confirm strategy, note what's working |

---

## Step 5 — Check Wiki document freshness

Ask human to confirm the Wiki URL (or use stored URL from last ingest):

```
Note: Leo cannot proactively check GitHub without a stored URL.
If the Wiki URL was provided during ingest, store it in GBrain:

mcp_gbrain_put_page(
    slug="concepts/sales-strategy-meta",
    content="---\ntype: concept\n---\n# Strategy Document Meta\n\n**Wiki URL:** [URL]\n**Last ingested:** [date]\n**Last confirmed current by human:** [date]\n"
)
```

In the Strategy Check report, always include:
- Date of last ingest
- Prompt for human to confirm document is still current

---

## Step 6 — Generate Strategy Check Report

Deliver to `[Sales] Pipeline Review` channel. Format:

```
🧭 Monthly Strategy Check — [Month Year]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗂️ MEMORY LAYER HEALTH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GBrain strategy pages:
  ✅ internal/business-lines/[BL]/strategy   (updated [date])
  ✅ internal/business-lines/[BL]/icp         (updated [date])
  ⚠️ internal/business-lines/[BL]/gtm         (last updated [date] — 90+ days ago)
  ❌ internal/business-lines/[BL]/market      (missing)

Hindsight {{ORG_PREFIX}}-global:
  ✅ Revenue target recalled
  ✅ ICP recalled
  ⚠️ Benchmarks not found

**Action needed:** Re-run `ingesting-sales-strategy` to refresh stale/missing pages.
Wiki URL: [URL or "not stored — please provide"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 LAST 4 WEEKS TREND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[date]:  [HEALTHY/WATCH/AT_RISK/CRITICAL] — coverage [N]x — [key finding]
[date]:  [status] — coverage [N]x — [key finding]
[date]:  [status] — coverage [N]x — [key finding]
[date]:  [status] — coverage [N]x — [key finding]

Pattern: [one sentence summary of the trend]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 STRATEGIC SIGNALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[List signals detected from pattern analysis table above]
e.g.:
• ⚠️ Pipeline coverage has been below 2x for 3 consecutive weeks — top of funnel may need attention
• ✅ PROPOSAL→CUSTOMER conversion is tracking above benchmark
• ⚠️ No new partnerships added in 6 weeks — partner strategy may not be executing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 LEO'S STRATEGIC ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[3–5 sentences: is the current strategy working? what's the biggest strategic
 risk? what should the team discuss or adjust? be direct — this is a BD Lead
 assessment, not a status update.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 RECOMMENDED DISCUSSION ITEMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Items for the human to review, confirm, or decide — not operational tasks
 but strategic questions]

1. [e.g. "Should we adjust the minimum opportunity size? Three recent opportunities
    below the floor are taking significant time with low probability."]
2. [e.g. "The ICP currently excludes SMEs — two warm leads this month are SME.
    Should we reconsider?"]
3. [e.g. "Partnership pipeline is empty — is partner activation still a priority
    this quarter?"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 DOCUMENT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sales-strategy.md last ingested: [date]
Please confirm: is the Wiki document still current? 
If updated, reply "ingest sales strategy from [URL]" to refresh Leo's memory.
```

---

## Step 7 — Create CRM Task if strategy discussion needed

If signals are flagged (anything other than all-clear):

```graphql
mutation {
  createTask(data: {
    title: "[Strategy Review] Monthly check flagged [N] items for discussion"
    body: { markdown: "**Month:** [month]\n\n**Items flagged:**\n[list of signals]\n\n**Leo's recommendation:** [one sentence]\n\nFull report delivered to [Sales] Pipeline Review channel." }
    status: TODO
    dueAt: "[7 days from now]"
  }) { id }
}
```

---

## Lark Channels

| Channel | What goes here |
|---|---|
| `[Sales] Pipeline Review` (chat_id stored in `internal/company/sales-strategy-meta` in GBrain once confirmed) | Full Strategy Check report |
| `[System] Backend Report` `{{SYSTEM_BACKEND_CHANNEL_ID}}` | Ops log — memory check results, tasks created |

---

## Quality Bar

Before returning the Strategy Check report:
- Every strategic signal in the "STRATEGIC SIGNALS" section traceable to a specific snapshot or pattern from the last 4 weeks (not a general impression)?
- Memory layer health status for each GBrain page labelled as one of: ✅ OK / ⚠️ Stale / ⚠️ Draft / ❌ Missing — not conflated?
- Leo's Strategic Assessment (3–5 sentences) clearly labelled as assessment/interpretation, not presented as confirmed fact?
- Recommended discussion items phrased as specific questions or observations, not vague directives like "review strategy"?
- Coverage ratio statements include the label "(benchmark probability estimate, not actuals)"?
- No invented snapshot data — if fewer than 2 weekly snapshots exist, trend analysis section explicitly says "Insufficient data — [N] snapshot(s) found"?

If any check fails, revise that section before delivering.

## Fallback Behavior

- **If GBrain is unreachable**: skip memory layer health check entirely; note "GBrain unavailable — memory layer status cannot be assessed" in the report; proceed with Hindsight + CRM data only.
- **If Hindsight `{{ORG_PREFIX}}-global` returns empty** on strategy queries: flag each missing item individually (e.g. "Revenue target not found in {{ORG_PREFIX}}-global — may not have been ingested"). Do not silently skip.
- **If Hindsight `{{ORG_PREFIX}}-pipeline` returns fewer than 2 weekly health check snapshots**: skip trend analysis; state "Trend analysis requires at least 2 weekly health checks — only [N] found. Run weekly Health Check for [X] more week(s) before Strategy Check is meaningful."
- **If CRM is unreachable**: omit any CRM-sourced data from the report; note the gap; deliver memory-layer and pattern sections with available data.
- **If sales-strategy.md ingest has never been run** (`internal/business-lines/[BL]/strategy` missing or is work-in-progress in GBrain): flag prominently at top of report — "No sales strategy ingested. Health Check targets and benchmarks are unavailable. Run `ingesting-sales-strategy` first."
- Do not block the full report because one source failed — degrade cleanly, flag each gap, deliver what's available.

## Pitfalls

- **No weekly snapshots = no trend** — if Hindsight has fewer than 2 health check entries, note this and skip trend analysis. Recommend running weekly Health Check for a month before Strategy Check is meaningful.
- **Never use "deal"** — always "opportunity".
- **Strategy Check is advisory, not prescriptive** — Leo surfaces signals and asks questions. The human decides whether to change strategy. Never update GBrain strategy pages autonomously — only on explicit human instruction.
- **Memory layer check is not optional** — stale GBrain pages mean the weekly Health Check is running on wrong targets. Flag this prominently.
- **Recommended discussion items must be specific** — not "review the strategy" but a concrete question or observation that requires a human decision.
- **Never hardcode team member names** — use "the team", "the sales rep", "the BD team".
