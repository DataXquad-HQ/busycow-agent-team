---
name: daily-briefing
version: 4.0
author: BD Lead Agent
description: >
  Generate and deliver the daily task briefing. Pulls today's due and overdue
  tasks from Twenty CRM, plus a preview of the next 3 days. Delivers to Feishu.
  Runs automatically at 08:00 daily via cron, or on-demand.
  Weekly opportunity/partnership health is handled by weekly-pipeline-review.
triggers:
  - daily briefing
  - 今天有什麼要做
  - morning briefing
  - 今天的任務
---

## Purpose

Every morning: pull today's due tasks (including overdue), show what needs to happen. Brief and actionable.

Opportunity and Partnership health is NOT in the daily briefing. That is in the weekly-pipeline-review. The logic: AT_RISK opportunities already have [STALL] tasks created by deal-health-check. Those tasks appear in the daily briefing automatically — no need to list opportunities separately.

No computation or analysis. Just reads tasks and formats them.

## CRM Reference
Twenty CRM: http://localhost:3001 (always localhost)
GraphQL endpoint: http://localhost:3001/graphql

## Data Pull

### 1. Overdue + Today's Tasks
```graphql
query {
  tasks(
    filter: {
      and: [
        { status: { notIn: ["DONE"] } }
        { dueAt: { lte: "{today_end_iso}" } }
      ]
    }
    orderBy: [{ taskPriority: AscNullsLast }, { dueAt: AscNullsLast }]
    first: 50
  ) {
    edges {
      node {
        id
        title { text }
        dueAt
        taskPriority
        status
        agentAdvice
        taskTargets {
          edges {
            node {
              opportunity { id name company { name } }
              partnership { id name company { name } }
            }
          }
        }
      }
    }
  }
}
```

### 2. Next 3 Days Preview
Same query but filter: dueAt > today AND dueAt <= today+3 days

## Algorithm
1. Fetch overdue+today tasks
2. Fetch next-3-days tasks
3. Separate overdue (dueAt < today) from due-today
4. Sort all by priority (URGENT first), then by dueAt
5. Format and deliver

## Message Format

```
📋 Daily Briefing — {YYYY-MM-DD}

🔥 需要處理 ({n} 個任務)
• [URGENT] {Task title} — {Company if linked}
• [HIGH] {Task title} — {Company if linked}
• [MEDIUM] {Task title}

📅 未來 3 天 ({n} 個任務)
• {Task title} — due {date} — {Company if linked}
• ...

[If nothing due: All clear ✔️ 沒有需要處理的任務]

———
{TIME} · Leo
```

Rules:
- Show [priority label] for URGENT and HIGH tasks only. MEDIUM and LOW show no label.
- If task is linked to an Opportunity or Partnership, show the company name after em dash
- If task is overdue (dueAt < today), add ⚠️ overdue marker
- If no tasks due today AND no tasks in next 3 days: send 'All clear ✔️' message (do not go silent — confirm briefing ran)
- agentAdvice is NOT shown in the briefing — it is for the human to read when they open the task

## Output Delivery
- Cron: deliver to origin Feishu chat
- Manual: reply in conversation

## Cron Integration
Schedule: 0 0 * * * (08:00 Taiwan = 00:00 UTC)
Dependency: deal-health-check runs at 03:00 — stall tasks are created before briefing fires

## Pitfalls
1. Always use localhost — never external URL
2. dueAt filter for today: use lte: today_end_iso to catch overdue tasks too
3. title is structured TEXT — extract .text from object
4. taskPriority sort: URGENT > HIGH > MEDIUM > LOW
5. Do NOT include opportunity/partnership health analysis — that is weekly-pipeline-review
6. Do NOT go silent if no tasks — always deliver briefing so human knows it ran
7. If deal-health-check created stall tasks overnight, they appear automatically — no special handling needed
