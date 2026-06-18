---
name: checking-context-health
description: >
  Daily automated audit of the full context layer — GBrain, Hindsight banks,
  agent cron status, and VM disk. Use when running the daily health check cron
  or when founders ask about system status. Silent if all green; alerts on issues.
triggers:
  - "run context health check"
  - "check system health"
  - "is everything healthy"
  - "daily health check"
---

# Context Health Check

Run all checks in order. Report only issues unless instructed otherwise.
Deliver a full report if any check fails. Stay silent (deliver nothing) if all pass.

---

## Check 1 — GBrain Source & Sync

```
mcp_gbrain_sources_list()
```

**Pass criteria:**
- Source `{{GBRAIN_SOURCE_ID}}` exists and is not archived
- `last_synced_at` is within the last 26 hours

**Check embed coverage:**
```
mcp_gbrain_get_health()
```

**Pass criteria:**
- `embed_coverage` ≥ 80%
- `orphan_count` ≤ 20
- `stale_pages` ≤ 10

---

## Check 2 — Hindsight Banks

```
GET http://localhost:8888/v1/default/banks
```

**Pass criteria — all of these banks must exist:**
- `{{HINDSIGHT_PIPELINE_BANK}}`
- `{{HINDSIGHT_AGENT_BANK_1}}`
- `{{HINDSIGHT_AGENT_BANK_2}}`
- `{{HINDSIGHT_AGENT_BANK_3}}`
- `{{HINDSIGHT_FOUNDER_1_BANK}}`
- `{{HINDSIGHT_FOUNDER_2_BANK}}`
- `{{HINDSIGHT_GLOBAL_BANK}}`

**Additional check on {{HINDSIGHT_PIPELINE_BANK}}:**
- If Leo has been running for more than 2 weeks AND `{{HINDSIGHT_PIPELINE_BANK}}` fact_count = 0 → flag as broken write pipeline

---

## Check 3 — Agent Cron Status

Check the last run status of each active agent cron in Leo's profile:

```
cat ~/.hermes/profiles/leo/cron/jobs.json
```

**Pass criteria for each enabled job:**
- `last_status` = `"ok"` OR `last_run_at` is null (never run yet, not an error)
- No job has `last_status` = `"error"` with `last_run_at` within the last 48 hours

Also check Iris's own active crons via `cronjob(action='list')`:
- `GBrain Nightly Dream + Memory Sync` → enabled, last_status ok
- `{{GBRAIN_SOURCE_ID}}-nightly-sync` → enabled

---

## Check 4 — VM Disk Space

```
df -h /mnt/disks/data
```

**Pass criteria:**
- Use% ≤ 85%

```
df -h /
```

**Pass criteria:**
- Use% ≤ 80%

---

## Check 5 — {{GBRAIN_SOURCE_ID}} GitHub Sync

```
cd /mnt/disks/data/{{GBRAIN_SOURCE_ID}} && git log --oneline -1 && git status --short
```

**Pass criteria:**
- Last commit is within 48 hours
- Working tree is clean (no uncommitted changes with significant content)

---

## Reporting Rules

**If ALL checks pass:**
- Deliver nothing (silent run — cron no_agent output is empty = no message sent)

**If ANY check fails:**
- Deliver a concise alert with:
  - ❌ which check failed
  - What the actual value was vs the threshold
  - Suggested fix (one line)

**Report format:**
```
🔍 Context Health Alert — [DATE] [TIME] Taiwan

❌ [Check name] — [what failed]
   Found: [actual value]
   Expected: [threshold]
   Fix: [one-line action]

[Repeat for each failure]

✅ [N] checks passed
```

---

## Pitfalls

- GBrain `last_synced_at` may be null if the source was just registered — treat null as a warning, not a hard fail, if the source was registered within 24 hours
- `{{HINDSIGHT_AGENT_BANK_4}}` may not exist if that agent isn't deployed — skip it without flagging
- Hindsight may return a 503 if the container is restarting — retry once after 10 seconds before flagging
- `df` output may show `/mnt/disks/data` at high usage during a sync — cross-check with `git status` to confirm it's not a runaway write

## Related References

- `references/lark-channel-management-pitfalls.md` — pitfalls for creating Lark channels and adding members (missing scopes, empty membership after MCP create, open_id lookup pattern)
