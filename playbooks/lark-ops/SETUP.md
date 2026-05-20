# Lark Ops Playbook — Setup

## What this creates

- 5 Lark/Feishu Bitable and document management skills

## Prerequisites

- Core playbook installed (`core/SETUP.md` completed)
- Lark MCP configured (`core/skills/lark-mcp-setup.md`)
- Lark App token with bitable + doc permissions in `~/.hermes/.env`:
  ```
  LARK_APP_ID={{LARK_APP_ID}}
  LARK_APP_SECRET={{LARK_APP_SECRET}}
  ```

---

## Step 1 — Install skills

```bash
SKILLS_DIR="${HERMES_HOME:-~/.hermes}/skills/lark-ops"
mkdir -p "$SKILLS_DIR"

BASE_URL="https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/lark-ops/skills"

for skill in lark-bitable-schema-setup lark-docx-writer reading-lark-files feishu-lark-bitable-calendar-sync tracking-financials; do
  mkdir -p "$SKILLS_DIR/$skill"
  curl -fsSL "$BASE_URL/$skill.md" -o "$SKILLS_DIR/$skill/SKILL.md"
  echo "✅ $skill"
done
```

## Step 2 — Grant App permissions in Lark Developer Console

Go to https://open.larksuite.com/app → your app → Permissions & Scopes, add:
- `bitable:app` (read + write)
- `docx:document` (read + write)
- `drive:file` (read + write)
- `calendar:calendar` (read + write) — for calendar sync only
- Publish a new app version for scopes to take effect

## Step 3 — Share your Bitable docs with the App

In each Bitable you want the agent to access:
- Share → Add member → select your App → set to **Can manage**

## Verify

```bash
hermes /skills
```

Confirm all 5 skills appear.

## Next

- Use `lark-bitable-schema-setup` to build your first database schema
- Use `tracking-financials` to set up a financial tracker
