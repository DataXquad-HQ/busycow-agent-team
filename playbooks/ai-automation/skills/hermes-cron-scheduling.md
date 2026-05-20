---
name: hermes-cron-scheduling
description: >
  Scheduling conventions and time-window philosophy for Hermes cron jobs across all profiles.
  Covers daytime-vs-night windowing, profile inventory, and how to update schedules across
  the default and named profiles. Use when creating, reviewing, or rescheduling cron jobs.
triggers:
  - "review cron"
  - "reschedule cron"
  - "cron timing"
  - "cron windows"
  - "when should cron run"
---

# Hermes Cron Scheduling Conventions

## Time Window Philosophy

Hunter works late into the evening (often past 22:00–23:00 TWN), so the correct
window for heavy background jobs is **deep night: 02:00–06:00 TWN**, not "after work".

| Window | TWN Time | UTC | Use For |
|--------|----------|-----|---------|
| 🌞 Daytime | 09:00–18:00 | 01:00–10:00 | Reminders, CRM reports, anything a human must see at the start of work |
| 🌑 Deep Night | 02:00–06:00 | 18:00–22:00 | LLM-heavy jobs, content generation, data ingests |
| 🌅 Weekend Night | Sat/Sun 02:00–06:00 | Fri/Sat 18:00–22:00 | Monthly heavyweight jobs (stakeholder intel, exports) |
| ⏱️ Interval | Every N mins/hours | — | Lightweight syncs with no LLM (calendar sync, etc.) |

**Rule of thumb:**
- If a human needs to *read the output at the start of their workday* → run at 09:00 TWN (01:00 UTC)
- If the job *generates something* (content, analysis, intel) → run 02:00–05:00 TWN so results are ready when work starts
- If the job is *interval-based with no LLM* → run anytime, it doesn't matter
- **Never move reminders to night** — they lose their purpose

## Stagger Heavy Jobs

When multiple LLM-heavy jobs could overlap, stagger by 30–60 minutes:

```
02:00 TWN (18:00 UTC) — StandupLog → GBrain Ingest
02:30 TWN (18:30 UTC) — Tasks → GBrain Ingest
03:00 TWN (19:00 UTC) — Content Intelligence scan
04:00 TWN (20:00 UTC) — Monthly exports / heavyweight jobs
05:00 TWN (21:00 UTC) — Blog generation
```

## Profile Inventory

The `cronjob` tool only operates on the **currently active (default) profile**.
Named profile jobs must be edited directly in their `jobs.json` file.

| Profile | Path | Purpose |
|---------|------|---------|
| default | `~/.hermes/cron/jobs.json` | BusyCow mother company ops |
| busycow | `~/.hermes/profiles/busycow/cron/jobs.json` | BusyCow sales & content |
| aquaoptima | `~/.hermes/profiles/aquaoptima/cron/jobs.json` | [your product] client ops |
| geokernel | `~/.hermes/profiles/geokernel/cron/jobs.json` | [your product] (no jobs yet) |

## Updating Named Profile Schedules

The `cronjob` tool cannot update named profiles — edit JSON directly:

```python
import json

path = '~/.hermes/profiles/busycow/cron/jobs.json'
with open(path) as f:
    data = json.load(f)

# Find job by ID and update schedule
for job in data['jobs']:
    if job['id'] == 'YOUR_JOB_ID':
        job['schedule']['expr'] = '0 19 * * *'      # UTC cron expression
        job['schedule']['display'] = '03:00 TWN daily'  # human-readable

with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

The internal schema uses `id` (not `job_id`), and `schedule` is a nested object:
```json
{
  "id": "44233711aa33",
  "schedule": {
    "kind": "cron",
    "expr": "0 19 * * *",
    "display": "03:00 TWN daily"
  }
}
```

For interval jobs: `"kind": "interval", "minutes": 60, "display": "every 60m"`

## Current Job Registry

Full registry with Purpose + What It Does is maintained in Lark Base:
**URL**: https://cjpg0xp67g6h.jp.larksuite.com/base/OircbPodaawVZlsQP2vjThkQp6b

Quick reference — confirmed schedules (as of 2026-05-01):

| Job ID | Name | Profile | TWN Time | UTC Expr |
|--------|------|---------|----------|----------|
| 28ac9856fe24 | Task Tracker → Lark Calendar Sync | default | Every hour | every 60m |
| 1da29709b48b | StandupLog → GBrain Ingest | default | 02:00 daily | 0 18 * * * |
| 3a1ac386e6e6 | Tasks → GBrain Ingest | default | 02:30 daily | 30 18 * * * |
| 1b9b4c3a9d6d | GBrain → Obsidian Export | default | Fri 04:00 | 0 20 * * 5 |
| 23f27e76deb5 | BusyCow CRM 每日彙報 | busycow | 09:00 Mon-Fri + holiday guard | 0 1 * * 1-5 |
| 44233711aa33 | Content Intelligence | busycow | 03:00 daily | 0 19 * * * |
| 8753f489f389 | Monthly Stakeholder Intel | busycow | 1st Mon 04:00 + holiday guard | 0 20 1-7 * 1 |
| d5d609622cdc | [your product] CRM 每日晨報 | aquaoptima | 09:00 Mon-Fri + holiday guard | 0 1 * * 1-5 |
| 098448f6913a | [your product] Blog 2x Weekly | aquaoptima | Sun+Wed 05:00 | 0 21 * * 0,3 |
| 18adba8709bf | [your product] Investor Reminder | aquaoptima | 28th 17:00 | 0 9 28 * * |

## UTC ↔ TWN Conversion Quick Reference

TWN = UTC+8. Cron expressions use UTC.

| TWN | UTC |
|-----|-----|
| 01:00 | 17:00 prev day |
| 02:00 | 18:00 prev day |
| 03:00 | 19:00 prev day |
| 04:00 | 20:00 prev day |
| 05:00 | 21:00 prev day |
| 09:00 | 01:00 |
| 17:00 | 09:00 |

## Memory Backup Cron Jobs
- `c2a353c2d6ed` — Daily memory snapshot at 02:30 TWN → GBrain `hermes-memory/YYYY-MM-DD` (default profile)
- `98abd95ebad4` — Monthly first Monday 09:00 TWN → BusyCow DEV group (`{{CHAT_ID}}`) with Memory change review report

## Graphify Assessment (2026-05)
Evaluated for BusyCow stack. Verdict: **按需工具，不加入日常 stack**。
- Use case: client codebase analysis ([your product]/[your product] technical due diligence), not daily CRM/content ops
- GBrain integration: run Graphify → export GRAPH_REPORT.md → gbrain put (not real-time sync)
- MCP-native (7 graph tools), tree-sitter for code (zero LLM cost), Leiden clustering
- Con: no auto-update, maintenance overhead for 2-person team

## `deliver=origin` Does NOT Work in Cron Jobs

Cron jobs run in an isolated session with no chat context. `deliver=origin` cannot resolve a target and will silently fail with `no delivery target resolved for deliver=origin`.

**Always pass an explicit deliver target when creating monitor/report crons:**
```python
cronjob(action='create',
    deliver='feishu:oc_CHAT_ID:THREAD_ID',  # ✅ explicit
    # deliver='origin'  ← NEVER USE THIS in cron jobs
    ...
)
```

Common explicit targets:
- BusyCow HQ thread 133: `feishu:{{CHAT_ID}}:133`
- Hunter DM: `feishu:{{USER_OPEN_ID}}`
- Daily standup group: `feishu:{{CHAT_ID}}`

---

## Decision Checklist When Adding a New Cron Job

1. **Does a human need to read it at work start?** → 09:00 TWN (01:00 UTC), Daytime window
2. **Is it a reminder/alert?** → Keep daytime, don't move to night
3. **Does it involve LLM generation or heavy processing?** → Deep Night (02:00–05:00 TWN)
4. **Is it a monthly heavyweight?** → Weekend Night, first Saturday of month
5. **Is it lightweight/no LLM?** → Interval or any off-peak time
6. **Does it conflict with another job in the same window?** → Stagger by 30 min
7. **Always sync the Lark Base** after ANY create/modify/delete (see section below)

---

## Lark Base Sync — MANDATORY After Every Cron Operation

**Base:** `OircbPodaawVZlsQP2vjThkQp6b` → Table: `{{TABLE_ID}}` (Cron Jobs)  
**Credentials:** busycow Feishu (default app token, no useUAT needed)

### Field Schema

| Field Name | Field ID | Type | Notes |
|---|---|---|---|
| Job Name | `fldTQxSQCQ` | Text (primary) | Human-readable name |
| Job ID | `fld8FRabwU` | Text | Hermes cron job ID (hex) |
| Status | `fldS5SV4oq` | SingleSelect | `✅ Active` / `⏸️ Paused` / `❌ Disabled` / `📝 Draft` |
| Schedule (TWN) | `fld8lLCHgr` | Text | e.g. `03:00 TWN daily` |
| What It Does | `fldWzwir6n` | Text | Brief description of the job's purpose |
| Output / Delivery | `fldvNqBKas` | Text | Where results are sent (channel, DM, file, etc.) |
| Product Line | `fld3fFZgwQ` | SingleSelect | `🐄 BusyCow` / `💧 [your product]` / `🏢 BusyCow` / `⚙️ System` |
| Deliver To | `fldgh7cBzJ` | Text | deliver param value, e.g. `telegram:-100xxx:92` or `feishu:ou_xxx` |

### 1. New Cron Job → Create Record

After `cronjob(action='create')` succeeds and you have the job ID:

```python
mcp_lark_bitable_v1_appTableRecord_create(
    path={"app_token": "OircbPodaawVZlsQP2vjThkQp6b", "table_id": "{{TABLE_ID}}"},
    data={"fields": {
        "Job Name": "<name>",
        "Job ID": "<job_id>",
        "Status": "✅ Active",
        "Schedule (TWN)": "<e.g. 03:00 TWN daily>",
        "What It Does": "<description>",
        "Output / Delivery": "<description of output>",
        "Product Line": "<🐄 BusyCow | 💧 [your product] | 🏢 BusyCow | ⚙️ System>",
        "Deliver To": "<deliver param value>"
    }}
)
```

### 2. Modified Cron Job → Update Record

First search for the record by Job ID, then update:

```python
# Step 1: find the record_id
mcp_lark_bitable_v1_appTableRecord_search(
    path={"app_token": "OircbPodaawVZlsQP2vjThkQp6b", "table_id": "{{TABLE_ID}}"},
    data={"filter": {"conjunction": "and", "conditions": [
        {"field_name": "Job ID", "operator": "is", "value": ["<job_id>"]}
    ]}}
)

# Step 2: update with changed fields only
mcp_lark_bitable_v1_appTableRecord_update(
    path={"app_token": "OircbPodaawVZlsQP2vjThkQp6b", "table_id": "{{TABLE_ID}}", "record_id": "<record_id>"},
    data={"fields": { ...changed fields only... }}
)
```

### 3. Paused / Deleted Job → Update Status

```python
# Paused
{"Status": "⏸️ Paused"}

# Permanently removed
{"Status": "❌ Disabled"}
```

### DM Delivery Format

If a cron job is set to deliver to a specific person via DM, record it in `Deliver To`:
- Feishu DM: `feishu:<open_id>` (e.g. `feishu:{{USER_OPEN_ID}}`)
- Telegram DM: `telegram:<chat_id>`
- Feishu group topic: `feishu:<chat_id>:<thread_id>`
