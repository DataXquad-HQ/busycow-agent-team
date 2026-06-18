---
name: ingesting-sessions-to-hindsight
description: >
  Extract today's Hermes conversation sessions and write meaningful intel to Hindsight
  human banks (dx-human-hunter, dx-human-kevin) and dx-global. This is the daily pipeline
  that ensures no conversation with founders is lost. Run nightly after the Lark extraction.
  Use when called by the nightly session ingest cron or when user says "ingest sessions",
  "save today's conversations", "write to hindsight".
triggers:
  - "ingest sessions"
  - "save today's conversations to hindsight"
  - "write sessions to hindsight"
  - "session ingest"
version: "1.0"
---

# Ingesting Hermes Sessions → Hindsight

## Purpose
Every conversation Iris has with founders contains decisions, preferences, priorities, and
context that must not be lost. This skill extracts today's sessions from the local session DB
and writes structured intel to the appropriate Hindsight banks. This is the primary mechanism
ensuring dx-human-hunter, dx-human-kevin, and dx-global stay current.

---

## Step 1: Confirm Current Taiwan Date

```bash
TZ=Asia/Taipei date '+%Y-%m-%d %H:%M:%S'
```

Use this as the anchor for "today". Extract sessions from the past 24 hours.

---

## Step 2: Retrieve Today's Sessions

Use session_search to find all conversations from today:

```
session_search(query="", sort="newest")
```

Look for sessions with `when` timestamps from today (Taiwan time).
For each session, note:
- `session_id`
- `title` / topic
- `bookend_start` + `bookend_end` — goal and resolution
- Key decisions, preferences, or intel mentioned

Filter out:
- Pure technical sessions (no human intel — e.g. code debugging with no decisions)
- Sessions where nothing meaningful was discussed
- Sessions already ingested (check `last_ingested_session` fact in dx-agent-iris bank)

---

## Step 3: Classify Each Session

For each meaningful session, classify what type of intel it contains:

| Type | Write to bank | Example |
|---|---|---|
| Hunter's preference / style / decision | `dx-human-hunter` | "Hunter prefers concise responses", "Hunter approved X" |
| Kevin's preference / style / decision | `dx-human-kevin` | "Kevin wants financial updates weekly" |
| Company-wide decision | `dx-global` | "Decided to sunset AquaOptima from DX portfolio" |
| Agent infrastructure change | `dx-global` | "Leo's stale skills removed, package updated" |
| Strategic direction | `dx-global` | "GeoKernel CEO search starting Oct 2026" |

---

## Step 4: Write to Hindsight Banks

For each classified item, write a concise structured memory:

```
POST http://localhost:8888/v1/default/banks/dx-human-hunter/memories
{
  "items": [{
    "content": "[YYYY-MM-DD]: [what was learned / decided / preferred]. Context: [brief]. Source: session [title].",
    "tags": ["session-ingest", "preference|decision|intel", "[topic-slug]"]
  }]
}
```

**Write rules:**
- One fact per write — do not bundle multiple facts into one memory item
- Be specific: "Hunter prefers bullet points over paragraphs for briefings" not "Hunter has communication preferences"
- Always include the date and source session in the content
- Skip anything that is temporary task state (e.g. "we were building X today") — only durable facts

**dx-global writes** — only for confirmed company-wide facts:
```
POST http://localhost:8888/v1/default/banks/dx-global/memories
{
  "items": [{
    "content": "[YYYY-MM-DD]: [company fact / decision]. Confirmed in conversation with [Hunter/Kevin].",
    "tags": ["session-ingest", "decision|strategy|structure", "[bl-slug]"]
  }]
}
```

---

## Step 5: Update Last Ingest Marker

Write a single marker to dx-agent-iris so future runs know what was already processed:

```
POST http://localhost:8888/v1/default/banks/dx-agent-iris/memories
{
  "items": [{
    "content": "[YYYY-MM-DD]: Session ingest completed. Sessions processed: N. Facts written: hunter=X, kevin=Y, global=Z.",
    "tags": ["session-ingest", "marker"]
  }]
}
```

---

## Step 6: Report

```
✅ Session → Hindsight Ingest 完成 (YYYY-MM-DD)
- Sessions reviewed: N
- Sessions with meaningful intel: N
- Facts written:
  - dx-human-hunter: X
  - dx-human-kevin: Y
  - dx-global: Z
- Skipped (no intel / already processed): N
```

Silent if zero meaningful sessions found.

---

## Pitfalls

- **Do not write task progress** — "we built X today" is not a durable fact. "Hunter decided X is the preferred approach for Y" is.
- **Do not duplicate** — if a fact was already in Hindsight from a prior run, skip it. Check with a recall query first if unsure: `POST /v1/default/banks/dx-human-hunter/memories/recall {"query": "[topic]", "top_k": 3}`
- **Session search returns polished pages, not raw transcripts** — use `session_search` with `query=""` and sort by newest to get recent sessions
- **auto_retain is OFF** — do not rely on any automatic session writing; this skill IS the write pipeline
- **Only Iris runs this skill** — agents do not write to human banks
- **Hindsight URL** is `http://localhost:8888` — always direct REST, not via a skill abstraction
