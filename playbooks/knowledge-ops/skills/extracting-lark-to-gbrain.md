---
name: extracting-lark-to-gbrain
description: >
  Pull yesterday's (or a specified day's) Lark group chat messages, filter noise,
  and extract meaningful knowledge into GBrain via extract_facts. Use when user says
  "跑一下 Lark 萃取", "extract lark to gbrain", "手動跑萃取", or when called by
  the nightly cron job at 03:00 TWN.
triggers:
  - "跑一下 Lark 萃取"
  - "extract lark to gbrain"
  - "手動跑萃取"
  - "lark extract"
  - "nightly extract"
version: "1.0"
author: BusyCow
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
| `{{CHAT_ID}}` | [your product] Product & Dev |
| `{{CHAT_ID}}` | [DX] Daily Task Tracking |
| `{{CHAT_ID}}` | [BC] Core Group |
| `{{CHAT_ID}}` | [GK] Core Group |
| `{{CHAT_ID}}` | [BC] Sales & Marketing |
| `{{CHAT_ID}}` | [GK] Sales & Marketing |
| `{{CHAT_ID}}` | [DX] Sales & Partnership |
| `{{CHAT_ID}}` | [AO] Core Group |
| `{{CHAT_ID}}` | [your product] IR & Fundraising |
| `{{CHAT_ID}}` | NP360 Support |
| `{{CHAT_ID}}` | [DX] Financial |
| `{{CHAT_ID}}` | [DX] Strategy |
| `{{CHAT_ID}}` | BusyCow - Team |
| `{{CHAT_ID}}` | [Proj] BusyCow 台水提案計畫2026 |
| `{{CHAT_ID}}` | Proj - Leighton Cam Integration dev |
| `{{CHAT_ID}}` | [Proj] HK MTR Patrol Robots 2026 |
| `{{CHAT_ID}}` | Proj - GeoShare Dev |
| `{{CHAT_ID}}` | Proj - 台水green tech & ai challenge |

For each chat, call `mcp_lark_im_v1_message_list` with:
```
container_id_type: "chat"
container_id: {chat_id}
start_time: start_ts
end_time: end_ts
sort_type: "ByCreateTimeAsc"
page_size: 50
```

---

## Step 3: Filter Messages

**Keep** if ALL conditions met:
- `msg_type == "text"`
- Text content (extracted from body JSON) is **≥ 10 characters**
- ✅ Bot messages are **included** — they contain response state and decisions

**Skip:**
- Non-text messages (images, files, stickers, cards)
- Messages shorter than 10 characters

Extract text:
```python
import json
body = json.loads(msg.get("body", {}).get("content", "{}"))
text = body.get("text", "").strip()
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

```
✅ Lark → GBrain Extract 完成 ({date})
- 掃描群組: 18
- 有效訊息: N 條
- Facts: X inserted, Y skipped (duplicate), Z updated
```

---

## Pitfalls
- Lark message timestamps are in **seconds**, not milliseconds — use `start_time`/`end_time` as second-level string timestamps
- `body.content` is a JSON string that needs to be parsed — not plain text
- If a chat has no messages in the window, `items` will be empty — skip silently, don't error
- Bot messages often contain structured info (task confirmations, stage updates) — never filter them out
- **`extract_facts` may return 0 inserts on pglite engine GBrain instances** — the LLM extraction pipeline is not supported. If `inserted: 0, duplicate: 0, superseded: 0` after a rich corpus, fall back to `put_page` directly. Save the day's intel as `daily/YYYY-MM-DD` with full structured markdown. The page creation response will include `facts_backstop: queued: true` confirming background extraction is scheduled. Report this fallback in the summary.
- When using the `put_page` fallback, include all key intel in the page (pipeline updates, decisions, people, technical findings) — this becomes the durable record even if `extract_facts` is unavailable.
