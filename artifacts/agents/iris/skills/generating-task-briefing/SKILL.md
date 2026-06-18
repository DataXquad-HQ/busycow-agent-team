---
name: generating-task-briefing
description: >
  Generate the daily task briefing message for the Task Tracking group. Determines
  today's day of week (Taiwan time) and outputs the appropriate format — Monday
  includes this week priorities, Wednesday is mid-week check-in, Friday invites reflections,
  Tuesday/Thursday is standard. Called by the Daily Task Briefing cron job.
triggers:
  - called by cron
  - "send today briefing"
  - "daily briefing"
version: "1.0"
author: [Org]
---

# Generating Task Briefing

## Base & Tables
- **App Token:** `{{LARK_APP_TOKEN}}`
- **Tasks:** `{{LARK_TABLE_ID}}`
- **Initiatives:** `{{LARK_TABLE_ID}}`
- **Goals:** `{{LARK_TABLE_ID}}`

Auth: see `references/lark-api-auth.md`

> **Preferred auth pattern**: Use `lark-cli api --as bot` — it handles token acquisition automatically. Do NOT manually curl `open.larksuite.com` (returns 10014); this app is on `open.feishu.cn` but `lark-cli` abstracts this away.

---

## Delivery
- Send the briefing message to Task Tracking group via `mcp_lark_im_v1_message_create`:
  - `receive_id_type`: `chat_id`
  - `receive_id`: `{{LARK_CHAT_ID}}`
  - `msg_type`: `text`
  - `content`: `{"text": "<briefing content>"}`
- After sending, reply to cron with a short confirmation: "✅ Briefing sent to Task Tracking"

## Step 1 — Determine Day of Week

```python
from datetime import datetime
import pytz
tz = pytz.timezone('Asia/Taipei')
day = datetime.now(tz).strftime('%A')  # Monday / Tuesday / ... / Friday
date_str = datetime.now(tz).strftime('%-m/%-d')
weekday_zh = {'Monday':'Monday','Tuesday':'Tuesday','Wednesday':'Wednesday','Thursday':'Thursday','Friday':'Friday'}
```

---

## Step 2 — Fetch Tasks

Use `lark-cli api --as bot` (MCP unavailable in cron context; manual curl unreliable).

```bash
lark-cli api POST /open-apis/bitable/v1/apps/{{LARK_APP_TOKEN}}/tables/{{LARK_TABLE_ID}}/records/search \
  --as bot \
  --data '{"page_size": 100}' > /tmp/tasks_raw.json
```

Paginate if `has_more=true` using `page_token`.

**Actual Tasks table fields (verified May 2026):**
- `Task Name` — array of text segments → join `.get("text","")`
- `Priority` — string like `"🔴 High"`, `"🟡 Medium"`, `"🟢 Low"`
- `Deadline` — ms timestamp integer (divide by 1000 for datetime)
- `Business Line` — string (use as goal/grouping, replaces missing `Goal` field)
- `Description` — array of text segments
- `Opportunity` / `Partnership` — linked record IDs
- `📋 Initiatives-Tasks` — linked record IDs

**NOTE: `Done`, `Responsible Person`, `Goal`, `Initiative` fields do NOT exist in this table view.** Owner cannot be determined from tasks alone.

Classify into buckets:
- **overdue**: deadline < TODAY_START
- **due_today**: TODAY_START ≤ deadline ≤ TODAY_END
- **high_no_date**: Priority = 🔴 High AND no deadline
- **this_week**: TODAY_END < deadline ≤ WEEK_END
- **rest**: everything else

Filter out tasks with empty Task Name.

---

## Step 3 — Generate Message by Day

### Monday — start of week
```
🗓 {date_str} Monday｜start of week

🔴 Due today / overdue
{overdue + due_today items, max 5}
(if none, write "none")

⚡ High priority, unscheduled
{high_no_date items, max 3}
(if none, write "none")

📋 this week priorities
{group by Goal → top task per Initiative, max 3 Goals × 2 tasks}

---
📝 New week: please post a quick task update today.
   What got done, what is blocked, and what the next step is.
   Reply here and I will update it.
```

### Tuesday / Thursday — standard briefing
```
🗓 {date_str} {weekday_zh}

🔴 Due today / overdue
{overdue + due_today, max 5}
(if none, write "none")

⚡ High priority, unscheduled
{high_no_date, max 3}
(if none, write "none")

📋 In progress this week
{this_week items grouped by Goal, max 3 Goals × 1 task}
```

### Wednesday — mid-week review
```
🗓 {date_str} Wednesday｜mid-week review

🔴 Due today / overdue
{overdue + due_today, max 5}
(if none, write "none")

⚡ High priority, unscheduled
{high_no_date, max 3}
(if none, write "none")

---
📝 Mid-week: please update your progress.
   Anything blocked or needing support?
   Reply here and I will log it.
```

### Friday — before weekend
```
🗓 {date_str} Friday｜before weekend

🔴 Due today / overdue
{overdue + due_today, max 5}
(if none, write "none")

⚡ High priority, unscheduled
{high_no_date, max 3}
(if none, write "none")

---
📝 Before the weekend, please update task progress
   What got done this week? Any blockers or lessons?
   What should continue next week?
   Reply here and I will log it.
```

---

## Formatting Rules
- Max 15 lines total (excluding nudge section)
- Each task line: `• [Task Name] — [Owner or Business Line]（[Deadline or no deadline]）`
  - Owner not available in tasks table — omit or use Business Line as proxy
- If a section has no items → write `(none)` on one line, don't skip the section header
- Goal grouping format (using Business Line): `[Business Line] → • task`
- Nudge section always goes at the bottom, separated by `---`
- No extra explanations or filler text

---

## Pitfalls
- **pytz is NOT installed** in the cron sandbox — always use the stdlib fallback: `timezone(timedelta(hours=8))` from `datetime`
- Deadline field returns ms timestamp — divide by 1000 for Python datetime
- **Responsible Person field does NOT exist in tasks table** — actual fields are: `Business Line`, `Priority`, `Task Name`, `Deadline`, `Description`, `Opportunity`, `Partnership`, `📋 Initiatives-Tasks`. Owner is NOT stored at the task level in this view.
- **No `Goal` or `Done` fields** in the tasks table — use `Business Line` as the goal grouping column instead. There is no checkbox for Done; filter by other means if needed (e.g. skip tasks with no name).
- Initiative DuplexLink returns array — may need second API call to resolve name
- If no tasks at all → still send the message with all sections showing "none"
- **Large API response (~200KB for 147 records)** — always pipe `lark-cli` output to a temp file (`> /tmp/tasks_raw.json`) and parse with a separate `python3 /tmp/classify_tasks.py` call. Never try to parse inline.
- **Complex Python logic** (multi-step classification): write to `/tmp/script.py` via `write_file` then run with `terminal("python3 /tmp/script.py")` — avoids quoting hell and 20K stdout cap
- **`execute_code` tool redacts secrets mid-string** — causes `SyntaxError: unterminated string literal` when credentials appear in assignments. Always use `write_file` + `terminal` for any script that touches APP_TOKEN, APP_SECRET, or TOKEN.
- **`open.larksuite.com` returns `10014 app unauthorized`** — this app uses `open.feishu.cn`. However, the cleanest approach is to use `lark-cli api POST ... --as bot` which handles auth automatically without manual token fetching.
- **`lark-cli api` is the preferred fetch method** — no manual curl+token needed. Example: `lark-cli api POST /open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search --as bot --data '{"page_size": 100}' > /tmp/tasks_raw.json`
- Active task count was 147 in May 2026; always fetch with `page_size=100` and check `has_more` — paginate if true
- The `[DX] Daily Task Tracking` group chat_id is `{{LARK_CHAT_ID}}`

## References
- `references/lark-api-auth.md` — API credentials and curl pattern
- `references/timestamp-helper.md` — date and ms timestamp helpers
