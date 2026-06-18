# Cron Jobs — BD Lead Agent (Leo)

Scheduled jobs that run autonomously. Each job calls a skill — no business logic lives in the cron prompt itself.

---

## Before You Install

Replace every `{{PLACEHOLDER}}` in `jobs.json` before enabling any job.

| Placeholder | What it is |
|---|---|
| `{{SYSTEM_BACKEND_CHANNEL_ID}}` | Lark chat_id for ops logs and system reports (internal, not human-facing) |
| `{{SALES_DAILY_UPDATE_CHANNEL_ID}}` | Lark chat_id for the sales team's daily update channel |
| `{{OUTREACH_REVIEW_CHANNEL_ID}}` | Lark chat_id where outreach drafts are sent for human review before sending |
| `{{CRM_EXTERNAL_URL}}` | Public-facing CRM URL shown in Lark messages (e.g. `https://crm.yourcompany.com`) |
| `{{AGENT_EMAIL}}` | Leo's OpenMail address (e.g. `leo@yourdomain.com`) |
| `{{ORG_PREFIX}}` | Your organisation's Hindsight bank prefix (e.g. `acme`) |
| `{{COMPANY_BLOG_URL}}` | Your company blog URL — used when scouting for relevant content to reference in outreach |

---

## Installing

`jobs.json` is a reference template — it is **not** directly importable into Hermes. Use it to manually create each cron job via the Hermes CLI:

```bash
hermes cron create \
  --profile <your-agent> \
  --name "Daily Pipeline Reminder" \
  --schedule "0 1 * * 1-5" \
  --skill sending-daily-pipeline-reminder \
  --prompt "..." \
  --deliver "feishu:{{SYSTEM_BACKEND_CHANNEL_ID}}"
```

Or trigger each job's prompt interactively first to verify it works before scheduling.

---

## Jobs

| Job | Schedule | Skill | What it does |
|---|---|---|---|
| **Daily Pipeline Reminder** | `0 1 * * 1-5` (weekdays) | `sending-daily-pipeline-reminder` | Pulls all TODO CRM tasks per Sales Rep, prioritises by date, flags overdue items, suggests approach per task. Delivers to Sales Daily Update channel. |
| **Lead Nurturing Scanner** | `0 1 * * *` (daily) | `nurturing-leads` | Finds leads with no contact in 30+ days, drafts personalised outreach, stores as DRAFT OutreachMessages in CRM, notifies Outreach Review channel for approval. |
| **Outreach Message Sender** | `0 4 * * *` (daily) | `nurturing-leads` | Sends SCHEDULED OutreachMessages via OpenMail, re-alerts on overdue DRAFTs, updates CRM status + lastContactDate, logs Engagement. |
| **Inbox Monitor** | `0 2 * * *` (daily) | `monitoring-inbox-replies` | Checks inbox for inbound replies, matches to CRM Person, logs Engagement, notifies review channel. Silent if no replies. |
| **Weekly Pipeline Health Check** | `0 1 * * 1` (Mondays) | `checking-pipeline-health` | Checks pipeline coverage vs revenue target, flags stalled + AT_RISK items, creates Tasks for data gaps. |
| **Monthly Pipeline Strategy Check** | `0 1 1 * *` (1st of month) | `checking-pipeline-strategy` | Reviews last 4 health check snapshots, surfaces trend signals and strategy gaps. |
| **Monthly Account Intelligence Update** | `0 2 1 * *` (1st of month) | `enriching-accounts` | Deep-enriches all active accounts (NURTURE/OPPORTUNITY tier), updates CRM + Hindsight + GBrain. |

---

## Delivery Architecture

All cron jobs deliver their ops log to `{{SYSTEM_BACKEND_CHANNEL_ID}}` (the backend report channel — internal only).

Human-facing notifications (draft reviews, reminders) are pushed **mid-run** directly to the relevant Sales channel — not via the cron `deliver` field. This keeps the ops log separate from human-readable output.
