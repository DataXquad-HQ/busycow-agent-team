---
name: generating-task-briefing
description: >
  Generate the daily task briefing message for the Task Tracking group. Determines
  today's day of week (Taiwan time) and outputs the appropriate format — Monday
  includes 本週重點, Wednesday is mid-week check-in, Friday invites reflections,
  Tuesday/Thursday is standard. Called by the Daily Task Briefing cron job.
triggers:
  - called by cron
  - "發今天的 briefing"
  - "daily briefing"
version: "1.0"
author: DataXquad
---

# Generating Task Briefing

## Base & Tables
- **App Token:** `MtvNbgCHXaRAaUsWXsCjnekep2g`
- **Tasks:** `tblOqgxrhF6o1nUX`
- **Initiatives:** `tbl2xxpxkLIQuRPM`
- **Goals:** `tblkpN1cyt1CWwoY`

Auth: see `references/lark-api-auth.md`

> **Preferred auth pattern**: Use `lark-cli api --as bot` — it handles token acquisition automatically. Do NOT manually curl `open.larksuite.com` (returns 10014); this app is on `open.feishu.cn` but `lark-cli` abstracts this away.

---

## Delivery
- Send the briefing message to Task Tracking group via `mcp_lark_im_v1_message_create`:
  - `receive_id_type`: `chat_id`
  - `receive_id`: `oc_a5e03bcb6026a81a5a330b53c4e90575`
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
weekday_zh = {'Monday':'週一','Tuesday':'週二','Wednesday':'週三','Thursday':'週四','Friday':'週五'}
```

---

## Step 2 — Fetch Tasks

Use `lark-cli api --as bot` (MCP unavailable in cron context; manual curl unreliable).

```bash
lark-cli api POST /open-apis/bitable/v1/apps/MtvNbgCHXaRAaUsWXsCjnekep2g/tables/tblOqgxrhF6o1nUX/records/search \
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

### Monday — 本週開始
```
🗓 {date_str} 週一｜本週開始

🔴 今天到期 / 逾期
{overdue + due_today items, max 5}
（無則：「無」）

⚡ 高優先、未排時間
{high_no_date items, max 3}
（無則：「無」）

📋 本週重點
{group by Goal → top task per Initiative, max 3 Goals × 2 tasks}

---
📝 新的一週，請大家今天更新一下任務進展
   完成了什麼、卡在哪、下一步是什麼
   直接在這裡說，我幫你更新 ✍️
```

### Tuesday / Thursday — 標準 Briefing
```
🗓 {date_str} {weekday_zh}

🔴 今天到期 / 逾期
{overdue + due_today, max 5}
（無則：「無」）

⚡ 高優先、未排時間
{high_no_date, max 3}
（無則：「無」）

📋 本週進行中
{this_week items grouped by Goal, max 3 Goals × 1 task}
```

### Wednesday — 週中盤點
```
🗓 {date_str} 週三｜週中盤點

🔴 今天到期 / 逾期
{overdue + due_today, max 5}
（無則：「無」）

⚡ 高優先、未排時間
{high_no_date, max 3}
（無則：「無」）

---
📝 週中了，請大家更新一下進度
   有沒有什麼卡住的？需要協助的？
   直接說，我幫你記 ✍️
```

### Friday — 週末前
```
🗓 {date_str} 週五｜週末前

🔴 今天到期 / 逾期
{overdue + due_today, max 5}
（無則：「無」）

⚡ 高優先、未排時間
{high_no_date, max 3}
（無則：「無」）

---
📝 週末前，請大家更新任務進度
   這週做了什麼？有沒有卡點或心得？
   下週要繼續哪些事？
   直接說，我幫你記 ✍️
```

---

## Formatting Rules
- Max 15 lines total (excluding nudge section)
- Each task line: `• [Task Name] — [Owner or Business Line]（[Deadline or 無期限]）`
  - Owner not available in tasks table — omit or use Business Line as proxy
- If a section has no items → write `（無）` on one line, don't skip the section header
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
- If no tasks at all → still send the message with all sections showing 「無」
- **Large API response (~200KB for 147 records)** — always pipe `lark-cli` output to a temp file (`> /tmp/tasks_raw.json`) and parse with a separate `python3 /tmp/classify_tasks.py` call. Never try to parse inline.
- **Complex Python logic** (multi-step classification): write to `/tmp/script.py` via `write_file` then run with `terminal("python3 /tmp/script.py")` — avoids quoting hell and 20K stdout cap
- **`execute_code` tool redacts secrets mid-string** — causes `SyntaxError: unterminated string literal` when credentials appear in assignments. Always use `write_file` + `terminal` for any script that touches APP_TOKEN, APP_SECRET, or TOKEN.
- **`open.larksuite.com` returns `10014 app unauthorized`** — this app uses `open.feishu.cn`. However, the cleanest approach is to use `lark-cli api POST ... --as bot` which handles auth automatically without manual token fetching.
- **`lark-cli api` is the preferred fetch method** — no manual curl+token needed. Example: `lark-cli api POST /open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search --as bot --data '{"page_size": 100}' > /tmp/tasks_raw.json`
- Active task count was 147 in May 2026; always fetch with `page_size=100` and check `has_more` — paginate if true
- The `[DX] Daily Task Tracking` group chat_id is `oc_a5e03bcb6026a81a5a330b53c4e90575`

## References
- `references/lark-api-auth.md` — API credentials and curl pattern
- `references/timestamp-helper.md` — date and ms timestamp helpers
