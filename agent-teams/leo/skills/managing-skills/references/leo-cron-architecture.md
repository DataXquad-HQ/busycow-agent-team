# Leo Cron Architecture Patterns (confirmed 2026-06-16)

## Two-Channel Delivery Pattern

Every Leo cron job that produces human-facing output uses TWO channels:

| Channel | What goes here | How it gets there |
|---|---|---|
| Sales channel (e.g. Daily Update, Nurturing Review) | Human-facing content — drafts, reminders, reply notifications | **Mid-run push** via `mcp_lark_im_v1_message_create` inside the skill |
| `[System] Backend Report` (`oc_8c3706de744958173c700d995ccfd4ef`) | Full ops log — run stats, errors, flags, task IDs | **Hermes auto-deliver** via cron `deliver` field |

**Rule:** Cron `deliver` is ALWAYS set to `[System] Backend Report`. Never set it to a sales channel.
The skill itself pushes to the sales channel mid-run when human-facing content is ready.

**Why:** If `deliver` points to the sales channel, Hermes auto-delivers the agent's final response (which is the ops log) to the wrong audience. Sales team sees system noise; ops log is lost.

## Channel IDs (DataXquad)

| Channel | chat_id |
|---|---|
| `[DX] Sales Daily Update` | `oc_a5e03bcb6026a81a5a330b53c4e90575` |
| `[Sales] Nurturing Outreach Review` | `oc_28f34b34f4da3a13ddc618b19d1c458f` |
| `[System] Backend Report` | `oc_8c3706de744958173c700d995ccfd4ef` |

## Silent-When-Nothing Pattern

If a cron run has nothing to report (e.g. zero unread inbox replies), post NOTHING to either channel.
Do not send "no items found" messages — stay silent. Only the ops log to Backend Report if errors occurred.

## CRM Links in Lark Messages

Always use `https://sales.dataxquad.com/objects/[type]/[UUID]` in any Lark message.
Never use `http://localhost:3001` — humans cannot access localhost links.

## Skill Naming (Anthropic rules — confirmed via audit 2026-06-16)

- Action skills: gerund form — `nurturing-leads`, `capturing-leads`, `monitoring-inbox-replies`
- Tool skills: tool-name-as-is — `twenty-crm`
- Never noun phrases: ~~`inbox-monitor`~~, ~~`daily-reminder`~~, ~~`task-advice`~~
- Lowercase, hyphens only, no underscores

## Required Skill Body Sections (Anthropic standard)

Every skill MUST have:
1. `## When to Use` — explicit trigger conditions (not just "## Purpose")
2. `## Steps` or equivalent numbered flow
3. `## Pitfalls` — actionable, with exact fixes

Never hardcode team member names (Hunter, Kevin) in skill bodies — use "the Sales Rep", "our team".
