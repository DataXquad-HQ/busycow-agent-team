# Knowledge Ops Playbook — Setup

## What this creates

- 5 GBrain and knowledge management skills installed into your Hermes skills directory
- Nightly extraction + sync cron jobs (optional, guided below)

## Prerequisites

- Core playbook installed (`core/SETUP.md` completed)
- GBrain running (`gbrain status` returns OK)
- Lark MCP configured (if using Lark extraction)

---

## Step 1 — Install skills

Copy the 5 skill files into your Hermes skills directory:

```bash
SKILLS_DIR="${HERMES_HOME:-~/.hermes}/skills/knowledge-ops"
mkdir -p "$SKILLS_DIR"

BASE_URL="https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/knowledge-ops/skills"

for skill in building-gbrain-knowledge-graph extracting-lark-to-gbrain extracting-notion-pages syncing-brain-memory managing-team-knowledge; do
  mkdir -p "$SKILLS_DIR/$skill"
  curl -fsSL "$BASE_URL/$skill.md" -o "$SKILLS_DIR/$skill/SKILL.md"
  echo "✅ $skill"
done
```

## Step 2 — Configure Notion token (if using extracting-notion-pages)

Add to `~/.hermes/.env`:
```bash
NOTION_TOKEN={{NOTION_TOKEN}}
```

Get your token at: https://www.notion.so/my-integrations → Create integration → copy Internal Integration Token.

## Step 3 — Schedule nightly extraction (optional but recommended)

Ask your Hermes agent:

> "Create a cron job that runs every night at 03:00 local time using the `extracting-lark-to-gbrain` skill, and another at 04:30 that runs `syncing-brain-memory`."

## Verify

```bash
hermes /skills
```

Confirm all 5 skills appear in the list.

## Next

- Run `building-gbrain-knowledge-graph` skill to enrich your brain with entity pages
- Set up the `maintaining-gbrain` cron from the core playbook if not already running
