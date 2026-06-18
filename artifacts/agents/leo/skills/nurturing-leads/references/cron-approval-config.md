# Cron Approval Config — Critical Setup Note

## Problem

When Leo's cron jobs call `terminal()` or `execute_code()` (e.g. to run curl against
Hindsight or CRM), Hermes flags these as potentially dangerous commands and requires
user approval. In a live session the user can approve interactively. In a cron session
**there is no user present** — the command is BLOCKED and the job fails silently.

Default behaviour: `approvals.cron_mode: deny` → all flagged commands blocked in cron.

## Fix

Set `approvals.cron_mode: approve` in Leo's profile config:

```bash
hermes --profile leo config set approvals.cron_mode approve
```

This tells Hermes to auto-approve flagged terminal/execute_code calls in cron sessions.
It only affects the `leo` profile — other profiles are unaffected.

**Verified 2026-06-15.** Without this setting, Lead Nurturing Scanner and all other
Leo cron jobs that use terminal() will be BLOCKED.

## Verification

```bash
grep "cron_mode" ~/.hermes/profiles/leo/config.yaml
# Should output: cron_mode: approve
```

## Why It's Safe for Leo

Leo's cron jobs only perform:
- HTTP calls to localhost (Hindsight at :8888, CRM at :3001)
- Web search (read-only)
- Lark API calls (send messages)
- OpenMail API calls (send email)

None of these are system-destructive operations. Auto-approve is appropriate.
