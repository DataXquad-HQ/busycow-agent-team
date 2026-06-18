# Deployed Agents

This folder contains the design specs for every agent that has been built and deployed in the DataXquad BusyCow team.

These specs are the human-readable record of what each agent does, why it exists, and how it was designed. They are not runtime configuration — runtime lives in each agent's `SOUL.md` and skills.

## Active Agents

| Agent | Title | The Number It Owns | Status |
|---|---|---|---|
| [Iris](iris-spec.md) | Chief of Staff | Company health × Knowledge integrity × System uptime | ✅ Deployed |
| [Leo](leo-spec.md) | BD Lead Agent | Partner count × Pipeline × Conversion rate | ✅ Deployed |

## Pending Agents

| Agent | Title | Notes |
|---|---|---|
| Maya | Inbound Lead Generation | SOUL.md exists, skills in progress |
| Rex | Customer Success | SOUL.md exists, skills in progress |
| Steve | Software Development | SOUL.md exists, not yet active |
| Vera | Partner Success | Pending — build later |

## How to Read These Specs

Each spec follows the [Agent Design Spec Template](../00-agent-spec-template.md). The spec is the "hiring brief" — it explains why the agent was created, what it does, and how it maps to actual build artifacts (SOUL.md, skills, .env, cron jobs).
