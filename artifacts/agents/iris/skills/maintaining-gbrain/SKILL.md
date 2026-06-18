---
name: maintaining-gbrain
description: >
  Run GBrain's nightly dream maintenance cycle. Use when user says "gbrain maintain",
  "run dream", "sync brain", "sync brain", or when called by the nightly cron job.
  Executes gbrain dream --json, captures output, and returns structured results.
triggers:
  - "gbrain maintain"
  - "run dream"
  - "sync brain"
  - "sync brain"
  - "dream cycle"
---

# Maintaining GBrain

## Purpose
Run the GBrain dream maintenance cycle — lint, sync, embed, consolidate, orphans, purge.

## Brain Directory

**Current vault:** `/mnt/disks/data/{{GBRAIN_SOURCE_ID}}` (GitHub: `[Org]-HQ/{{GBRAIN_SOURCE_ID}}`, branch `master`)

> Legacy path `{{HOME_DIR}}/brain` and repo `dataxquad-gbrain` are stale — do not use.

## GBrain Config
- Engine: **Postgres** (Docker container `gbrain-postgres`, port 5433)
- Embedding: **Google Gemini** (`gemini-embedding-001`, 768 dims)
- The `gbrain` wrapper at `~/.local/bin/gbrain` sets `GOOGLE_GENERATIVE_AI_API_KEY`, `GBRAIN_EMBEDDING_MODEL`, `GBRAIN_EMBEDDING_DIMENSIONS`, and `unset OPENAI_API_KEY`
- If DB is down: `docker start gbrain-postgres`

## Steps

### 1. Run Dream
```bash
source ~/.nvm/nvm.sh 2>/dev/null || true
cd /mnt/disks/data/{{GBRAIN_SOURCE_ID}}
HOME={{HOME_DIR}} gbrain dream --json --dir /mnt/disks/data/{{GBRAIN_SOURCE_ID}} 2>&1
```

### 2. Capture Result
Parse the JSON output for:
- `status` — overall success/failure
- Phase results: lint, sync, embed, consolidate, orphans, purge
- Any errors or warnings

### 3. Report
Return structured summary:
```
✅ GBrain Dream complete
- Sync: N pages updated
- Embed: N chunks embedded
- Consolidate: N facts → takes
- Lint: N issues
- Orphans: N pages
- Errors: none / [list]
```

If dream fails (non-zero exit or error in JSON), return ❌ with full error output.
Do NOT proceed to memory sync if dream fails — caller (cron) handles the flow.

## Fixing Lint Issues

### `gbrain lint --fix` does NOT auto-fix anything
Despite the flag existing, it fixes 0 issues in practice. All lint fixes must be done manually.

### Common lint issues and fixes

**`missing-created`** (most common — ~30 pages at once):
Use a Python script to inject `created:` into existing frontmatter:
```python
from pathlib import Path
import re, subprocess

brain_dir = Path("{{HOME_DIR}}/brain")

def get_date_from_filename(f):
    m = re.match(r'^(\d{4}-\d{2}-\d{2})', Path(f).stem)
    return m.group(1) if m else None

def get_git_date(fp):
    r = subprocess.run(["git", "log", "--follow", "--format=%as", "--", str(fp)],
                       cwd=str(brain_dir), capture_output=True, text=True)
    lines = r.stdout.strip().split('\n')
    return lines[-1] if lines and lines[-1] else None

for f in files_needing_created:
    fp = brain_dir / f
    date = get_date_from_filename(f) or get_git_date(fp) or "2026-05-01"
    content = fp.read_text()
    lines = content.split('\n')
    if lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                lines.insert(i, f'created: "{date}"')
                break
    fp.write_text('\n'.join(lines))
```

**`no-frontmatter`**: Prepend a full `---\ntitle: ...\ncreated: ...\ntype: note\n---\n\n` block.

**`missing-type`**: Insert `type: note` (or `person`, `company`, etc.) before closing `---`.

**`placeholder-date`** on template/SOP files: **False positive** — `{YYYY-MM-DD}` is intentional template syntax. Safe to ignore.

**After fixing lint, force a full re-sync**
Dream's incremental sync misses files modified outside git commits. Always run:
```bash
HOME={{HOME_DIR}} gbrain sync --full --dir /mnt/disks/data/{{GBRAIN_SOURCE_ID}}
```
This forces all 30+ pages to be re-imported and chunks re-created.

### Brain score 45 — orphan pages are the real bottleneck
Lint fixes alone won't raise brain score. The dominant factor is **orphan pages** (pages with no wikilinks to/from other pages). With 32/32 pages as orphans, the graph is empty and score stays ~45. To raise score: add `[[other-page]]` wikilinks between related pages.

## Upgrading GBrain

When upgrading to a new version:
```bash
cd ~/gbrain
git pull origin master
bun install
gbrain apply-migrations     # check for pending schema migrations
gbrain init --migrate-only  # run migrations now (schema vX → Y)
gbrain sync --source default
gbrain extract --stale
gbrain embed --stale
gbrain doctor               # verify health score
```

Restart the Hermes gateway after upgrade so the MCP server picks up the new binary:
```bash
systemctl --user restart hermes-gateway.service
```
Note: restarting from inside the gateway session will kill the session — trigger from an external shell or accept the reconnect.

**Version note:** GBrain vault (knowledge data) lives in `~/brain/` as markdown + Postgres DB. `~/gbrain/` is the source code repo. Do not confuse them.

**GitHub sync:** `~/brain/` has `origin → [Org]-HQ/dataxquad-gbrain` (private repo). The nightly cron pushes markdown vault + MEMORY.md + USER.md. GitHub is a backup + human PR review layer — no visual knowledge-graph interface, just raw `.md` files. That is expected and correct.

**GBrain vault = single source of truth (2026-06-17):**
The `{{GBRAIN_SOURCE_ID}}` vault at `/mnt/disks/data/{{GBRAIN_SOURCE_ID}}` now holds ALL knowledge — BL knowledge (`business-lines/`), company layer (`company/`), external entities (`companies/`, `people/`), decisions, and agent specs. The separate `dx-internal-kb` repo was deprecated and merged in. Agents read BL/company files directly from the vault path; GBrain DB is used for entity lookup and semantic search only.

**Dual-track memory architecture:**
- GBrain = cold tier (compiled truth — human-reviewed static facts)
- Hindsight = hot tier (episodic memory — bulk write at session end only)
- `auto_retain` and `auto_reflect` in Hindsight are DISABLED — agents never write mid-conversation
- Nightly Iris distillation: Iris reviews Hindsight pipeline observations → promotes high-confidence facts → writes to GBrain vault → human reviews PR → merges → GBrain re-indexes

**Additional GBrain sources:**
| Source ID | Local path | Content |
|---|---|---|
| `busycow-agent-package` | `{{PACKAGE_REPO_DIR}}` | Agent capabilities, guidelines (optional — agents read directly) |

**Deprecated sources (removed 2026-06-17):**
- `dx-internal-wiki` / `dx-internal-kb` — merged into `{{GBRAIN_SOURCE_ID}}` vault
- `aquaoptima-core` — [Portfolio Company] now independent
- `dx-wiki-gbrain-sync` cron — paused; new design reads vault files directly

**Registering a new repo as a GBrain source — MUST use CLI, not MCP:**
```bash
# CORRECT — CLI sets local_path correctly
HOME={{HOME_DIR}} gbrain sources remove {{GBRAIN_SOURCE_ID}} --confirm-destructive 2>&1
HOME={{HOME_DIR}} gbrain sources add {{GBRAIN_SOURCE_ID}} --path /mnt/disks/data/{{GBRAIN_SOURCE_ID}} --federated 2>&1

# WRONG — MCP sources_add returns local_path: null and page_count: 0
# mcp_gbrain_sources_add(id="{{GBRAIN_SOURCE_ID}}", path="...", federated=True)  ← DO NOT USE for new sources
```

**Why:** `mcp_gbrain_sources_add` does not correctly set the local vault path — it returns `local_path: null` and `page_count: 0` even with a valid path argument. The CLI `gbrain sources add` is the only reliable registration method.

After registering, sync immediately:
```bash
mcp_gbrain_sync_brain(repo="/mnt/disks/data/{{GBRAIN_SOURCE_ID}}")
```

**Query pattern for agents:**
```python
mcp_gbrain_query(query="Maya Growth Lead Capabilities", source_id="busycow-playbooks")
# or cross-source (all federated sources):
mcp_gbrain_query(query="[Portfolio Company] ICP")
```

**DeepSeek provider error on cron jobs:** If cron jobs fail with `RuntimeError: Provider 'deepseek' is set in config.yaml but no API key was found`, the fix is to restart the Hermes gateway after verifying `~/.hermes/config.yaml` has `provider: anthropic`. The error was caused by a stale gateway process holding an old config reference — not an actual deepseek entry in config.yaml.

## Pitfalls
- GBrain uses `tsx` runtime via `gbrain` CLI — ensure PATH includes it
- `--json` flag outputs structured JSON; without it output is human-readable only
- If `gbrain` not found: try `~/.local/bin/gbrain` or `npx gbrain`
- Dream can take 30–120 seconds depending on page count
- **PGLite WASM crashes on this Linux host** — always use Postgres, never PGLite
- If DB is down: `docker start gbrain-postgres` (port 5433, db=gbrain)
- **Embedding dim mismatch** (1536 vs 768): connect to DB and run `ALTER TABLE chunks DROP COLUMN embedding;` — gbrain will recreate at 768 dims on next embed
- If `no_database` warnings appear in dream output: DB is not connected — check Docker container is running and config points to correct port
- `OPENAI_API_KEY` must be unset in wrapper — if present, gbrain ignores Google key entirely (OpenAI has higher priority in provider selection)
- **Dream sync shows 0 modified after manual file edits** — run `gbrain sync --full` to force re-import; incremental sync uses file hash and may miss changes not committed to git
