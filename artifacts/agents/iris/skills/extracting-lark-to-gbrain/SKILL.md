---
name: extracting-lark-to-gbrain
description: >
  Pull yesterday's (or a specified day's) Lark group chat messages, filter noise,
  and extract meaningful knowledge into GBrain via extract_facts. Use when user says
  "run the Lark extraction", "extract lark to gbrain", "run extraction manually", or when called by
  the daily cron job (19:00 UTC / 03:00 TWN, job name: "Daily Lark → GBrain Extraction", created 2026-06-17).
triggers:
  - "run the Lark extraction"
  - "extract lark to gbrain"
  - "run extraction manually"
  - "lark extract"
  - "nightly extract"
version: "1.0"
author: [Org]
---

# Extracting Lark Chats → GBrain

## Purpose
Scan all bot-accessible Lark group chats for a given day, filter out noise, and feed the result into GBrain `extract_facts` so meaningful knowledge (people, decisions, intel, deal updates) is automatically captured.

---

## Step 1: Determine Time Window

Default = **yesterday (Taiwan time, UTC+8)**. Can be overridden by user specifying a date.

**MANDATORY:** Always fetch the actual current Taiwan time first via terminal before calculating:
```python
# Confirm Taiwan date before proceeding
result = terminal("TZ=Asia/Taipei date '+%Y-%m-%d %H:%M:%S'")
# Use this as the anchor for "now" — never assume UTC or server local time

from datetime import datetime, timezone, timedelta

tz8 = timezone(timedelta(hours=8))
now_tw = datetime.now(tz8)
yesterday = now_tw.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
today_midnight = yesterday + timedelta(days=1)

# Lark API uses second-level Unix timestamps (as strings)
start_ts = str(int(yesterday.timestamp()))
end_ts   = str(int(today_midnight.timestamp()))

# Log for verification
print(f"Extracting: {yesterday.strftime('%Y-%m-%d')} 00:00 → {today_midnight.strftime('%Y-%m-%d')} 00:00 (TWN)")
```

---

## Step 2: Scan All Active Chats

Bot-accessible group chats (18 groups — SYS groups excluded):

| Chat ID | Name |
|---------|------|
| `{{LARK_CHAT_ID}}` | [Portfolio Company] Product & Dev |
| `{{LARK_CHAT_ID}}` | [DX] Daily Task Tracking |
| `{{LARK_CHAT_ID}}` | [BC] Core Group |
| `{{LARK_CHAT_ID}}` | [GK] Core Group |
| `{{LARK_CHAT_ID}}` | [BC] Sales & Marketing |
| `{{LARK_CHAT_ID}}` | [GK] Sales & Marketing |
| `{{LARK_CHAT_ID}}` | [DX] Sales & Partnership | ⚠️ bot may not be in group (230002) — skip on error |
| `{{LARK_CHAT_ID}}` | [AO] Core Group |
| `{{LARK_CHAT_ID}}` | [Portfolio Company] IR & Fundraising |
| `{{LARK_CHAT_ID}}` | NP360 Support | ⚠️ group name may change ([Founder 2] renames it) — chat_id stays the same |
| `{{LARK_CHAT_ID}}` | [DX] Financial |
| `{{LARK_CHAT_ID}}` | [DX] Strategy |
| `{{LARK_CHAT_ID}}` | [Product A] - Team |
| `{{LARK_CHAT_ID}}` | [Proj] [Product A] water-utility proposal 2026 |
| `{{LARK_CHAT_ID}}` | Proj - Leighton Cam Integration dev |
| `{{LARK_CHAT_ID}}` | [Proj] HK MTR Patrol Robots 2026 |
| `{{LARK_CHAT_ID}}` | Proj - GeoShare Dev |
| `{{LARK_CHAT_ID}}` | Proj - water utility green tech & ai challenge |

For each chat, call `mcp_lark_im_v1_message_list` with:
```
container_id_type: "chat"
container_id: {chat_id}
start_time: start_ts
end_time: end_ts
sort_type: "ByCreateTimeAsc"
page_size: 50
```

**Pagination**: if the response has `has_more: true`, repeat the call with the returned `page_token` until `has_more: false`. Accumulate all `items`. Active chats like `[Portfolio Company] IR & Fundraising` can exceed 50 messages on busy days.

**Error handling**: if the API returns error 230002 ("Bot/User can NOT be out of the chat"), skip the group silently and note it in the report — do not crash.

---

## Step 3: Filter Messages

**Keep** if ALL conditions met:
- `msg_type == "text"`
- Text content (extracted from body JSON) is **≥ 10 characters**
- ✅ Bot messages are **included** — they contain response state and decisions
- ❌ **Skip bot tool-call log lines** — bot messages whose entire text is a tool call summary (e.g. `🐍 execute_code: "..."`, `👁️ vision_analyze: "..."`, `📚 skill_view: "..."`, `💻 terminal: "..."`, `📄 web_extract: "..."`, `⏰ cronjob: "create"`, `⚙️ mcp_...:`) contain no knowledge value. Detect by: (1) text starts with an emoji from the TOOL_LOG_PATTERN set (`📄` and `⏰` included), AND (2) text contains a tool keyword from TOOL_KEYWORDS (`web_extract` and `cronjob` included).

**Skip:**
- Non-text messages (images, files, stickers, cards)
- Messages shorter than 10 characters
- Bot tool-call log messages (pure tool summary lines with no actual intel)

Extract text:
```python
import json, re

body = json.loads(msg.get("body", {}).get("content", "{}"))
text = body.get("text", "").strip()

# Skip bot tool-call log messages (no knowledge value)
TOOL_LOG_PATTERN = re.compile(r'^[🐍👁️📚🔍💻⚙️✍️🔀📨⏳💾🌐🧠❌⚠️📄⏰🔧🛠️]+\s*\w')
SYSTEM_STATUS_PATTERN = re.compile(r'^[⏳⚠️❌💾🧠]\s*(Retrying|Max retries|API call failed|API failed|Self-improvement review|memory:)', re.IGNORECASE)
is_bot = msg.get("sender", {}).get("sender_type") == "app"
# Skip bot tool-call log messages (no intel)
TOOL_KEYWORDS = {"execute_code","vision_analyze","terminal","skill_view","web_search","mcp_","write_file","send_message","delegate_task","web_extract","cronjob","read_file","search_files","image_generate","patch","scp","ssh","curl"}
if is_bot and TOOL_LOG_PATTERN.match(text) and any(kw in text for kw in TOOL_KEYWORDS):
    continue  # skip — pure tool log, no intel
# Skip bot system status messages (retry notices, self-improvement logs, memory echoes)
if is_bot and SYSTEM_STATUS_PATTERN.match(text):
    continue  # skip — system status noise, no intel
# Skip bot task-preemption notices (e.g. "⚡ Interrupting current task (1 min elapsed...)")
if is_bot and text.startswith("⚡ Interrupting"):
    continue  # skip — Hermes internal interrupt notice, no business intel
# Skip bot background-process completion dumps (e.g. "[Background process proc_xxx finished...]")
if is_bot and text.startswith("[Background process"):
    continue  # skip — raw process log dump, no business intel
# Skip bot long-task heartbeat messages (e.g. "⏳ Still working... (10 min elapsed — iteration N/90...)")
if is_bot and text.startswith("⏳ Still working"):
    continue  # skip — Hermes internal heartbeat, no business intel
```

---

## Step 4: Compile Corpus

Format each message as:
```
[CHAT: {chat_name}] {sender_id}: {text}
```

Concatenate all into one block. If 0 messages total → log and stop.

---

## Step 5: Extract Facts into GBrain

```python
mcp_gbrain_extract_facts(
    turn_text=corpus,
    entity_hints=[
        "people/hunter-lin", "people/kevin-chan",
        "people/morris-chou", "people/chun-er",
        "busycow/dataxquad", "busycow/aquaoptima",
        "busycow/busycow", "busycow/geokernel",
        "projects/distify"
    ]
)
```

---

## Step 6: Report

**Happy path (extract_facts succeeded):**
```
✅ Lark → GBrain Extract complete ({date})
- Chats scanned: 18
- Chats skipped: N（chat name — reason）
- Valid messages: N items
- Facts: X inserted, Y skipped (duplicate), Z updated
```

**Fallback path (put_page succeeded):**
```
✅ Lark → GBrain Extract complete ({date})
- Chats scanned: 18 | Valid messages: N items
- extract_facts: 0 inserted（pglite engine fallback）
- Fallback: put_page daily/{date} ✅
```

**Double-fallback path (add_timeline_entry only):**
```
✅ Lark → GBrain Extract complete ({date})
- Chats scanned: 18 | Valid messages: N items
- extract_facts: 0 inserted（pglite engine）
- put_page: ❌ failed（embedding dimension mismatch：expected 768, not 1536）
- Fallback → add_timeline_entry: ✅ N  entries written successfully
- ⚠️ GBrain embedding model configuration mismatch; run `gbrain rebuild` or fix the embedding model config
```

---

## Pitfalls
- Lark message timestamps are in **seconds**, not milliseconds — use `start_time`/`end_time` as second-level string timestamps
- `body.content` is a JSON string that needs to be parsed — not plain text
- If a chat has no messages in the window, `items` will be empty — skip silently, don't error
- Bot messages often contain structured info (task confirmations, stage updates) — never filter them out
- **`[DX] Sales & Partnership` (`{{LARK_CHAT_ID}}`) may return error 230002 "Bot/User can NOT be out of the chat"** — bot was removed from this group. Skip gracefully (treat as empty), don't error. The group is still listed for when the bot is re-added.
- **Bot tool-call log messages are noise** — bot messages whose text is only tool call summaries (e.g. `🐍 execute_code: "..."`, `👁️ vision_analyze: "..."`, `📚 skill_view: "..."`, `📄 web_extract: "..."`, `⏰ cronjob: "create"`) contain no knowledge value. These pass the ≥10 char filter but must be filtered. The TOOL_LOG_PATTERN emoji set MUST include `📄` (web_extract), `⏰` (cronjob), `🔧`, `🛠️` — these slipped through in earlier versions. The TOOL_KEYWORDS set must include `web_extract` and `cronjob`. Both the emoji match AND a keyword match are required to filter (avoids false positives on legitimate bot messages that happen to start with an emoji).
- **Bot system status messages are also noise** — bot messages like `⏳ Retrying in 3.0s (attempt 1/3)...`, `⚠️ Max retries (3) exhausted — trying fallback...`, `❌ API failed after 3 retries — HTTP 200: Overloaded`, `💾 Self-improvement review: User profile updated`, and `🧠 memory: "..."` pass the ≥10 char filter and are NOT caught by the tool-log pattern. Add a second filter using `SYSTEM_STATUS_PATTERN = re.compile(r'^[⏳⚠️❌💾🧠]\s*(Retrying|Max retries|API call failed|API failed|Self-improvement review|memory:)', re.IGNORECASE)` to skip these — they contain zero knowledge intel.
- **Additional bot noise patterns not caught by TOOL_LOG_PATTERN** — two more bot-only noise patterns that slip through:
  - `⚡ Interrupting current task (1 min elapsed, iteration 3/90)...` — task preemption notices. Add `if is_bot and text.startswith("⚡ Interrupting"): continue`
  - `[Background process proc_XXXX finished with exit code N~ Here's the final output: ...]` — raw process completion dumps. Add `if is_bot and text.startswith("[Background process"): continue`
  These are informational logs from Hermes internals with no business intel value.
  - `⏳ Still working... (10 min elapsed — iteration N/90, running: terminal)` — long-task heartbeat messages. These start with `⏳` but the SYSTEM_STATUS_PATTERN only catches `⏳ Retrying...`. Add a dedicated check: `if is_bot and text.startswith("⏳ Still working"): continue`
- **`has_more: true` on large chats** — `[Portfolio Company] Product & Dev`, `[Portfolio Company] IR & Fundraising`, and **`NP360 Support`** regularly return `has_more: true` (NP360 Support can produce 150+ messages on active support days across 3+ pages). For chats with `has_more: true`, paginate using the returned `page_token` until `has_more: false`. This is especially important for `[Portfolio Company] IR & Fundraising` (rich fundraising discussions) and `NP360 Support` (long SSH/debugging sessions). If context window pressure is mounting, prioritize finishing pagination for already-started chats before starting new ones — partial pages are better than skipped chats.
- **`extract_facts` may return 0 inserts on pglite engine GBrain instances** — the LLM extraction pipeline is not supported. If `inserted: 0, duplicate: 0, superseded: 0` after a rich corpus, fall back to `put_page` directly. Save the day's intel as `daily/YYYY-MM-DD` with full structured markdown. The page creation response will include `facts_backstop: queued: true` confirming background extraction is scheduled. Report this fallback in the summary.
- When using the `put_page` fallback, include all key intel in the page (pipeline updates, decisions, people, technical findings) — this becomes the durable record even if `extract_facts` is unavailable.
- **`put_page` may ALSO fail on pglite instances with embedding dimension mismatch** — error looks like `"expected 768 dimensions, not 1536"`. This means the embedding model config is mismatched and new page creation is broken. In this case, fall back to **`add_timeline_entry`** on existing entity pages instead. Use `mcp_gbrain_resolve_slugs` to find the relevant slugs (people/hunter-lin, busycow/aquaoptima, busycow/dataxquad, busycow/geokernel, etc.) and add one timeline entry per major topic/entity. `add_timeline_entry` does NOT embed the content, so it works even when embeddings are broken. Report this double-fallback in the summary and note that `gbrain rebuild` or fixing the embedding model config is needed.
- **Fallback priority chain:** `extract_facts` → `put_page daily/YYYY-MM-DD` → `add_timeline_entry` on existing pages
- **Sunday is inherently low-activity** — most chats will be empty (16/18 is typical). The main signal on Sundays is the **weekly weekly review bot message** from `[DX] Daily Task Tracking`, which fires every Sunday morning with a task structure audit. This is valuable intel (orphaned tasks, BL mismatches, Initiative health) — make sure it passes the bot-message filter and gets captured. Do NOT mistake a low message count on Sundays for a scan failure.
- **The weekly task audit bot message is NOT a tool-call log** — it starts with `🔍` and contains `weekly task structure audit` or similar structured content. It passes the ≥10 char filter and does NOT match TOOL_KEYWORDS, so the filter correctly keeps it. Never add `🔍` to the noise-filter emoji set without also requiring a TOOL_KEYWORDS match.
