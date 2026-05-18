---
name: maintaining-gbrain
description: >
  Run GBrain's dream maintenance cycle — lint, sync, embed, consolidate, orphan
  detection, and purge. Use when user says "gbrain maintain", "run dream",
  "sync brain", or when triggered by a nightly cron job.
triggers:
  - "gbrain maintain"
  - "run dream"
  - "sync brain"
  - "dream cycle"
---

# Maintaining GBrain

## Purpose
Run the GBrain dream cycle to keep the knowledge base clean, embedded, and consolidated.

## Steps

### 1. Run Dream
```bash
source ~/.nvm/nvm.sh 2>/dev/null || true
cd ~/brain
gbrain dream --json 2>&1
```

### 2. Parse Output
Look for:
- `status` — overall success/failure
- Phases: lint, sync, embed, consolidate, orphans, purge
- Any errors or warnings

### 3. Report
```
✅ GBrain Dream complete
- Sync: N pages updated
- Embed: N chunks embedded
- Consolidate: N facts → takes
- Lint: N issues
- Orphans: N pages
- Errors: none / [list]
```

If dream fails (non-zero exit or error), return ❌ with full error output.

## Pitfalls
- GBrain uses `tsx` runtime via `gbrain` CLI — ensure PATH includes it
- `--json` flag outputs structured JSON; without it output is human-readable only
- If `gbrain` not found: try `~/.local/bin/gbrain` or `npx gbrain`
- Dream can take 30–120 seconds depending on brain size
