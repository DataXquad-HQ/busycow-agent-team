# Leo — Agent Setup

Step-by-step guide to get Leo operational from scratch. Complete these in order — each step is a prerequisite for the next.

---

## Overview

Leo requires the following before the agent can run:

| # | What | Type | Est. time |
|---|---|---|---|
| 1 | Hermes Agent + core infrastructure | Self-hosted | 30 min |
| 2 | Twenty CRM | Self-hosted | 20 min |
| 3 | Hindsight | Self-hosted | 15 min |
| 4 | OpenMail inbox | Cloud (SaaS) | 5 min |
| 5 | Tavily API key | Cloud (API) | 5 min |
| 6 | Anthropic API key | Cloud (API) | 5 min |
| 7 | Leo profile + credentials | Configuration | 15 min |
| 8 | Skills installation | Configuration | 10 min |
| 9 | Cron jobs | Configuration | 10 min |
| 10 | GBrain content | Content | 30 min |
**Total: ~2 hours**

---

## Step 1 — Core Infrastructure

Complete the core stack setup first:

→ `../../SETUP.md`

This installs Hermes Agent, GBrain, and wires up your communication platform (Lark or equivalent).

---

## Step 2 — Twenty CRM

Leo's primary data store. All pipeline objects live here.

→ `../../playbooks/integrations/twenty-crm/SETUP.md`

After setup, record:

```
TWENTY_API_KEY=<jwt token from Settings → API & Webhooks>
CRM_EXTERNAL_URL=https://crm.{{YOUR_DOMAIN}}   # public URL for human-facing links
```

---

## Step 3 — Hindsight

Leo's contextual memory layer. Must be running before any cron jobs execute.

**Install:**

```bash
# Clone and start Hindsight
git clone https://github.com/{{HINDSIGHT_REPO}} /your/install/path
cd /your/install/path
docker compose up -d

# Verify
curl -sf http://localhost:8888/health && echo "UP"
```

**Create Leo's memory banks:**

```bash
# Create all required banks
for bank in pipeline global agent-leo internal human-sales-rep human-manager; do
  curl -s -X POST http://localhost:8888/v1/default/banks \
    -H "Content-Type: application/json" \
    -d "{\"id\": \"{{ORG_PREFIX}}-${bank}\", \"name\": \"${bank}\"}"
  echo "Created: {{ORG_PREFIX}}-${bank}"
done
```

Replace `{{ORG_PREFIX}}` with your organisation's short prefix (e.g. `acme`).

**Banks created:**

| Bank | Purpose |
|---|---|
| `{{ORG_PREFIX}}-pipeline` | Per-opportunity context — primary bank for C5/C6 |
| `{{ORG_PREFIX}}-global` | Company-level facts approved across the team |
| `{{ORG_PREFIX}}-agent-leo` | Leo's private working memory |
| `{{ORG_PREFIX}}-internal` | Cross-agent handoffs |
| `{{ORG_PREFIX}}-human-sales-rep` | Sales Rep's priorities (read-only for Leo) |
| `{{ORG_PREFIX}}-human-manager` | Manager's priorities (read-only for Leo) |

---

## Step 4 — OpenMail

Leo's dedicated outbound/inbound email inbox.

1. Sign up at [openmail.sh](https://openmail.sh)
2. Create an inbox — name it `leo` or similar
3. Set the email address (e.g. `leo@{{YOUR_DOMAIN}}.openmail.sh` or a custom domain)
4. Copy the API token and inbox ID from the dashboard

Record:

```
OPENMAIL_API_KEY=<your api token>
OPENMAIL_INBOX_ID=<your inbox id>
AGENT_EMAIL=<leo's email address>
```

---

## Step 5 — Tavily API Key

Leo uses Tavily for web search in enrichment and scouting skills.

1. Sign up at [app.tavily.com](https://app.tavily.com)
2. Go to Dashboard → API Keys → Create key
3. Record:

```
TAVILY_API_KEY=*** api key>
```

This goes into Leo's `.env`. Hermes will route all `web_search` calls through Tavily automatically when this key is present.

---

## Step 6 — Anthropic API Key

Leo uses Claude as its reasoning model via Hermes.

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. Record:

```
ANTHROPIC_API_KEY=<your api key>
```

This goes into the Hermes global `.env`, not Leo's profile `.env`.

---

## Step 7 — Create Leo's Profile

```bash
# Create the Leo profile in Hermes
hermes profile create leo

# This creates: ~/.hermes/profiles/leo/
```

**Write the SOUL.md:**

```bash
cp artifacts/agents/leo/SOUL.md ~/.hermes/profiles/leo/SOUL.md
```

Open the file and fill in all `{{PLACEHOLDER}}` values. See the full placeholder list below.

**Write Leo's `.env`:**

```bash
cat > ~/.hermes/profiles/leo/.env << 'EOF'
TWENTY_API_KEY=*** here>
OPENMAIL_API_KEY=*** here>
OPENMAIL_INBOX_ID=<paste here>
AGENT_EMAIL=<paste here>
TAVILY_API_KEY=*** here>
EOF
```

**Configure Leo's `config.yaml`:**

Key settings to add/update in `~/.hermes/profiles/leo/config.yaml`:

```yaml
agent:
  name: Leo
  profile: leo

models:
  default: claude-sonnet-4   # or your preferred model

toolsets:
  enabled:
    - web
    - terminal
    - file
    - mcp
  # Do NOT enable: image_gen, spotify, computer_use
```

---

## Step 8 — Install Skills

```bash
# Copy all Leo skills into the profile
cp -r artifacts/agents/leo/skills/* ~/.hermes/profiles/leo/skills/

# Verify
hermes --profile leo skills list
```

After copying, search for any remaining `{{PLACEHOLDER}}` values in the skills and replace them:

```bash
grep -r "{{" ~/.hermes/profiles/leo/skills/ --include="*.md" -l
```

---

## Step 9 — Set Up Cron Jobs

Leo's cron jobs are defined in `artifacts/agents/leo/cron/jobs.json` as a reference template. They must be created manually via the Hermes CLI — the JSON file is not directly importable.

First, fill in the channel IDs. You need three Lark (or equivalent) channel IDs:

```
SALES_DAILY_UPDATE_CHANNEL_ID=<sales team daily channel>
OUTREACH_REVIEW_CHANNEL_ID=<channel for draft review notifications>
SYSTEM_BACKEND_CHANNEL_ID=<internal ops log channel>
```

Then create each job. Example for the Lead Nurturing Scanner:

```bash
hermes --profile leo cron create \
  --name "Lead Nurturing Scanner" \
  --schedule "0 1 * * *" \
  --skill nurturing-leads \
  --deliver "feishu:{{SYSTEM_BACKEND_CHANNEL_ID}}" \
  --toolsets "web,terminal,file" \
  --prompt "..."   # copy prompt from cron/jobs.json
```

Repeat for all 7 jobs in `cron/jobs.json`. See that file for the full prompt and schedule for each.

**Verify cron is working:**

```bash
hermes --profile leo cron list
# Should show all 7 jobs in 'scheduled' state
```

---

## Step 10 — Fill GBrain Content

Before Leo can operate intelligently, the GBrain vault needs baseline content. This is your company's knowledge — fill in the files that already exist in the vault.

**GBrain vault location:** `/path/to/{{ORG_PREFIX}}-gbrain/`

**Files to fill (one per business line):**

```
internal/company/overview.md          ← Who you are, what you do
internal/company/portfolio.md         ← All BLs at a glance

internal/business-lines/[bl]/icp.md       ← Ideal Customer Profile
internal/business-lines/[bl]/strategy.md  ← Sales direction, priority markets
internal/business-lines/[bl]/product.md   ← Features, value props, objection handling
internal/business-lines/[bl]/gtm.md       ← Channels, sequences, pricing
```

Use the templates in `artifacts/knowledge-base-templates/` as a guide for what to write in each file.

After filling in content, run GBrain sync so Leo can query it:

```bash
gbrain sync --repo /path/to/{{ORG_PREFIX}}-gbrain
```

**Hindsight — seed human profiles (optional but recommended):**

```bash
curl -s -X POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-human-[name]/memories \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{
      "content": "[Role] — communication style: [style]. Key priorities: [priorities].",
      "tags": ["profile", "human"]
    }]
  }'
```

---

## Placeholder Reference

| Placeholder | Where | What to put |
|---|---|---|
| `{{ORG_PREFIX}}` | SOUL.md, skills, .env, banks | Short org identifier, e.g. `acme` |
| `{{COMPANY_NAME}}` | SOUL.md | Your company name |
| `{{COMPANY_BLOG_URL}}` | cron/jobs.json | Your blog or news URL |
| `{{CRM_EXTERNAL_URL}}` | SOUL.md, skills | Public-facing CRM URL |
| `{{AGENT_EMAIL}}` | SOUL.md, skills, .env | Leo's OpenMail address |
| `{{OPENMAIL_API_KEY}}` | skills/openmail | Leo's OpenMail API token |
| `{{OPENMAIL_INBOX_ID}}` | skills/openmail, .env | Leo's inbox ID |
| `{{SALES_DAILY_UPDATE_CHANNEL_ID}}` | SOUL.md, cron | Sales team daily channel ID |
| `{{OUTREACH_REVIEW_CHANNEL_ID}}` | SOUL.md, cron | Draft review channel ID |
| `{{PIPELINE_STRATEGY_CHANNEL_ID}}` | SOUL.md, cron | Pipeline & strategy channel ID |
| `{{SYSTEM_BACKEND_CHANNEL_ID}}` | SOUL.md, cron | Ops log channel ID |
| `{{BL_SLUG}}` | SOUL.md | Business line folder name e.g. `geokernel` |

---

## Verify Everything

```bash
# Profile is loaded
hermes --profile leo whoami

# Skills are visible
hermes --profile leo skills list | grep -E "twenty-crm|openmail|nurturing"

# Cron jobs scheduled
hermes --profile leo cron list

# CRM is reachable
curl -sf http://localhost:3001/healthz && echo "CRM UP"

# Hindsight is reachable
curl -sf http://localhost:8888/health && echo "HINDSIGHT UP"

# Test a live interaction — ask Leo to check the pipeline
hermes --profile leo chat "How many active opportunities are in the CRM right now?"
```

---

## Next Steps After Setup

1. **Ingest the sales strategy** — use the `ingesting-sales-strategy` skill to load your strategy document. This enables C6 pipeline health checks to run gap analysis.
2. **Enter first contacts** — use C1 Lead Capture to onboard your first prospects.
3. **Run inbox monitor manually** — trigger the `monitoring-inbox-replies` skill once to verify OpenMail integration end-to-end.
4. **Let the first cron fire** — watch the `{{SYSTEM_BACKEND_CHANNEL_ID}}` channel for the first ops log.
