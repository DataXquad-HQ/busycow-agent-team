# Hermes Cron Configuration for Leo

## approvals.cron_mode

**Problem:** By default, Hermes blocks terminal/execute_code calls in cron sessions that trip the security scanner (e.g. piping to python3, -c flag usage). Cron sessions have no user present to approve them, so the default `deny` causes silent failures.

**Fix:** Set in Leo's profile config:
```yaml
approvals:
  cron_mode: approve
```

**Command:**
```bash
hermes --profile leo config set approvals.cron_mode approve
```

This is already set in Leo's config as of 2026-06-15. If it ever resets (e.g. after a profile rebuild), reapply this.

**Why it's safe:** Leo's cron jobs only do HTTP calls (CRM, Hindsight), web search, and Lark messaging. None of these are destructive system operations. The `approve` mode is correct for this profile.

**How it works:**
- `HERMES_CRON_SESSION=1` env var is set for all cron runs
- `tools/approval.py` reads `approvals.cron_mode` from config
- Values `approve | off | allow | yes` → auto-approve flagged commands
- Value `deny` (default) → BLOCKED with no user to resolve it

## CRM URL pattern in cron output

Two different URLs for two different audiences:
- **API calls:** `http://localhost:3001/graphql` — fast, no external traffic, used in all Python scripts
- **Human-facing links in Lark:** `{{CRM_EXTERNAL_URL}}/objects/[type]/[UUID]` — never localhost

Pattern to apply when building CRM record links:
```python
CRM_BASE_EXTERNAL = "{{CRM_EXTERNAL_URL}}"

def crm_link(object_type: str, uuid: str) -> str:
    return f"{CRM_BASE_EXTERNAL}/objects/{object_type}/{uuid}"

# e.g.
crm_link("outreachMessages", "fc2f8a96-0a74-42e3-a048-678dca9345b4")
# → {{CRM_EXTERNAL_URL}}/objects/outreachMessages/fc2f8a96-0a74-42e3-a048-678dca9345b4
```

## No-hardcode-names rule

Never write specific team member names (e.g. "Hunter", "Kevin") into skill logic, cron prompts, or message drafts. Use:
- "the team" / "our BD team" / "our team"
- "the Sales Rep" / "the user" / "Human"

This ensures skills work as the team grows beyond the initial two people.
