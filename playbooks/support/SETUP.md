# Support Playbook Setup

## What this creates
- 5 role-specific skills installed into the `rex` agent profile
- Rex can: manage Lark workspace, create Bitable schemas, write Docs, read files, geocode locations

## Prerequisites
- Phase 2 (core) setup complete — Lark MCP + GBrain connected
- `rex` Hermes profile exists

## Steps

### 1. Install skills (run as the machine hosting the rex profile)

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SKILLS_SRC="$HERMES_HOME/skills"
REX_SKILLS="$HERMES_HOME/profiles/rex/skills"

# Role-specific skills for Rex
declare -A SKILL_MAP=(
  ["lark-im-pitfalls"]="lark-ops/lark-im-pitfalls"
  ["lark-bitable-schema-setup"]="lark-ops/lark-bitable-schema-setup"
  ["lark-docx-writer"]="lark-ops/lark-docx-writer"
  ["reading-lark-files"]="lark-ops/reading-lark-files"
  ["maps"]="sales/maps"
  ["google-workspace"]="core/google-workspace"
)

for name in "${!SKILL_MAP[@]}"; do
  src="$SKILLS_SRC/${SKILL_MAP[$name]}"
  dest="$REX_SKILLS/$name"
  if [ -d "$src" ]; then
    ln -sfn "$src" "$dest"
    echo "✅ $name"
  else
    echo "❌ $name: source not found at $src"
  fi
done
```

### 2. Verify

```bash
ls ~/.hermes/profiles/rex/skills/ | grep -v '_shared\|apple\|creative\|devops'
```

Expected output includes: `lark-im-pitfalls`, `lark-bitable-schema-setup`, `lark-docx-writer`, `reading-lark-files`, `maps`, `google-workspace`

## Next step

Add Rex's Worker Type to the Task Board `Worker Type` field options, then assign tasks with `Worker Type = Rex`.
