---
name: weekly-pipeline-review
version: 1.0
author: BD Lead Agent
description: >
  Weekly pipeline health review. Covers all active Opportunities and Partnerships:
  health status, days since last engagement, stage distribution, and recommended
  focus areas for next week. Runs automatically every Friday at 17:00, or on-demand.
  Daily task reminders are handled by daily-briefing.
triggers:
  - weekly review
  - pipeline review
  - pipeline health
  - 本週 pipeline
  - 這週有哪些單
  - 整體狀況
---

## Purpose

Weekly strategic view of the full pipeline. Answer three questions:
1. What is moving? (healthy, progressing)
2. What is at risk? (stalled, needs attention)
3. What should be the focus next week?

Not a task list. Not a daily reminder. The weekly review is for the sales rep to assess the overall pipeline state and make strategic decisions: which deals to prioritise, which partnerships to accelerate, which to deprioritise.

## CRM Reference
Twenty CRM: http://localhost:3001 (always localhost)
GraphQL endpoint: http://localhost:3001/graphql

## Data Pull

### 1. All Active Opportunities
```graphql
query {
  opportunities(
    filter: {
      stage: { notIn: ["CLOSED_WON", "CLOSED_LOST"] }
    }
    orderBy: { lastUpdateDate: AscNullsFirst }
    first: 100
  ) {
    edges {
      node {
        id name stage
        healthCheck
        currentStatusSummary
        nextActionSummary
        lastUpdateDate
        closeDate
        amount { amountMicros currencyCode }
        company { name }
        pointOfContact { edges { node { name { firstName lastName } } } }
        engagements(
          filter: { engagementStatus: { eq: "COMPLETED" } }
          orderBy: { engagementDate: DescNullsLast }
          first: 1
        ) {
          edges { node { engagementDate engagementType outcome } }
        }
      }
    }
  }
}
```

### 2. All Active Partnerships
```graphql
query {
  partnerships(
    filter: {
      stage: { notIn: ["SIGNED", "LOST", "CANCELLED"] }
    }
    orderBy: { lastUpdateDate: AscNullsFirst }
    first: 50
  ) {
    edges {
      node {
        id name stage
        healthCheck
        currentStatusSummary
        nextActionSummary
        lastUpdateDate
        company { name }
      }
    }
  }
}
```

## Algorithm

1. Fetch all active opportunities + partnerships
2. For each, calculate days_since_last_engagement
3. Group opportunities by healthCheck: AT_RISK / NEEDS_FOLLOWUP / ON_TRACK / AWAITING
4. Group partnerships by healthCheck: AT_RISK / NEEDS_FOLLOWUP / ON_TRACK
5. Identify focus recommendations for next week
6. Format and deliver

## Focus Recommendation Logic

Priority 1 (Must act this week):
- Any AT_RISK opportunity with amount > 0
- Any opportunity with closeDate within 14 days
- Any partnership AT_RISK for 14+ days

Priority 2 (Should act this week):
- NEEDS_FOLLOWUP opportunities not yet actioned
- Partnerships with no engagement in 14-21 days

Priority 3 (Monitor):
- ON_TRACK opportunities — no action needed unless closeDate approaching
- AWAITING — client is deciding, confirm follow-up date is set

## Message Format

```
📊 Weekly Pipeline Review — {YYYY-MM-DD}

🎯 OPPORTUNITIES ({total} active)

🔴 At Risk ({n})
| Opportunity | Company | Stage | Days silent | Next action |
|---|---|---|---|---|
| {name} | {company} | {stage} | {N}d | {nextActionSummary} |

🟡 Needs Follow-up ({n})
| Opportunity | Company | Stage | Days silent | Next action |

⏳ Awaiting Client ({n})
| Opportunity | Company | Status |

✅ On Track ({n})
{name} ({company}, {stage}) • ...

---

🤝 PARTNERSHIPS ({total} active)

🔴 At Risk ({n})
| Partnership | Company | Stage | Days silent |

🟡 Needs Follow-up ({n})
| Partnership | Company | Stage | Days silent |

✅ On Track ({n})
{name} ({company}) • ...

---

🎯 Focus for Next Week

Priority 1 — Must act:
1. {Opportunity/Partnership name} — {why urgent} — {recommended action}
2. ...

Priority 2 — Should act:
1. ...

---
{DATE} · Leo
```

If pipeline is fully healthy (all ON_TRACK): still send the review with a summary — do not go silent.

## Output Delivery
- Cron: deliver to origin Feishu chat
- Manual: reply in conversation

## Cron Integration
Schedule: 0 9 * * 5 (Friday 17:00 Taiwan = 09:00 UTC)
Runs after deal-health-check has already updated all healthCheck fields.

## Pitfalls
1. Always use localhost — never external URL
2. healthCheck is the field to read (not dealStatus)
3. days_since_last_engagement: use last completed engagement date, not lastUpdateDate
4. If no partnerships exist yet: omit the partnerships section entirely
5. amount.amountMicros ÷ 1,000,000 = display value
6. closeDate approaching = within 14 days from today
7. Always deliver even if all healthy — weekly review confirms the pipeline was checked
8. Do NOT list individual tasks — that is daily-briefing's job
