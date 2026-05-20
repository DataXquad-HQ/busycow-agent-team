# Finance Playbook — Setup

## What this creates

- 3 financial modeling and invoicing skills

## Prerequisites

- Core playbook installed (`core/SETUP.md` completed)
- Google Workspace configured (`core/skills/google-workspace.md`)

---

## Step 1 — Install skills

```bash
SKILLS_DIR="${HERMES_HOME:-~/.hermes}/skills/finance"
mkdir -p "$SKILLS_DIR"

BASE_URL="https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/finance/skills"

for skill in building-investor-financial-model gsheets-formula-model generating-invoices; do
  mkdir -p "$SKILLS_DIR/$skill"
  curl -fsSL "$BASE_URL/$skill.md" -o "$SKILLS_DIR/$skill/SKILL.md"
  echo "✅ $skill"
done
```

## Step 2 — Install numpy-financial

```bash
# In the Hermes venv
~/.hermes/hermes-agent/venv/bin/pip install numpy-financial

# Verify
~/.hermes/hermes-agent/venv/bin/python -c "import numpy_financial as npf; print('✅ numpy-financial', npf.__version__)"
```

## Step 3 — Prepare invoice template (for generating-invoices)

1. Create a Google Doc with invoice layout — use `{{FIELD}}` placeholders for dynamic values
2. Note the Google Doc ID from the URL
3. Create a Lark Bitable with a Quotation table (Client, Amount, Date, Status fields)
4. Add both IDs to the skill configuration when prompted

## Verify

```bash
hermes /skills
```

Confirm all 3 skills appear.

## Next

- Try: "Build an investor financial model for [your product] — 3-year projection, two scenarios"
- Try: "Generate an invoice for [client name] based on the quotation in our CRM"
