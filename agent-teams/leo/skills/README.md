# Skills — BD Lead Agent (Leo)

Each skill is a self-contained folder. Copy the entire folder when installing — not just `SKILL.md`.

```bash
cp -r agent-teams/leo/skills/* ~/.hermes/profiles/<your-agent>/skills/
```

After copying, restart your Hermes session. See `SOUL.md` for the full list of `{{PLACEHOLDER}}` values you need to fill in before the agent will work.

---

## BD Capabilities

Skills that implement Leo's core BD capabilities. These are the "what Leo does" skills.

| Skill | What it does | Capability |
|---|---|---|
| `capturing-leads` | Capture new contacts from networking/events into CRM as Leads | C1 |
| `prospect-scouting` | Analyse a raw prospect list — prioritise, cross-reference ICP, enter as PROSPECT in CRM | C1 |
| `enriching-accounts` | Level 1 (shallow, pre-outreach) and Level 2 (deep, pre-meeting) account intelligence enrichment | C3 |
| `nurturing-leads` | Monthly personalised outreach to cold Leads; Flow A = draft, Flow B = send | C4 |
| `monitoring-inbox-replies` | Poll inbox for inbound replies; log Engagement, update CRM, notify review channel | C4 |
| `log-engagement` | Convert a raw interaction (meeting, call, email) into structured CRM Engagement + follow-up Tasks | C5 |
| `sending-daily-pipeline-reminder` | Morning task reminder for all Sales Reps — today's tasks, overdue flags, suggested approach | C5 |
| `advising-on-tasks` | Deep context-based advice on how to execute a specific CRM task | C5 |
| `handling-pipeline-interactions` | After a meeting/call — update opportunity stage, health, next action in CRM | C5 |
| `creating-report-back-tasks` | Create structured "report back" tasks when humans need to verify something in a live meeting | C5 |
| `checking-pipeline-health` | Weekly health check — pipeline coverage vs revenue target, stall flags, AT_RISK items | C6 |
| `checking-pipeline-strategy` | Monthly strategy review — memory freshness, trend signals, gap analysis vs sales strategy | C6 |
| `ingesting-sales-strategy` | Load a `sales-strategy.md` document into GBrain so C6 health checks can run gap analysis | C6 |

---

## Infrastructure Skills

Tools and systems Leo uses across all capabilities.

| Skill | What it enables |
|---|---|
| `twenty-crm` | Query and mutate all CRM objects via GraphQL — the foundational tool layer under every CRM read/write |
| `openmail` | Send and receive email — draft outreach, check inbox, manage thread state |
| `capturing-to-gbrain` | Save knowledge from conversations into GBrain as long-term structured memory |
| `github-core-repos` | Read and write internal GitHub repos via SSH — pull content, push updates, sync to GBrain |
| `managing-tasks` | Create and update tasks in the internal Task Tracker (Lark Base) |
| `reviewing-tasks` | Query and summarise tasks from the internal Task Tracker |
| `managing-skills` | Create, update, rename, and delete Hermes skills |
