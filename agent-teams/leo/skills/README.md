# Skills — BD Lead Agent

Agent-specific Hermes skills for the BD Lead Agent profile.
These are loaded in addition to the shared skills in `../../shared-skills/`.

---

## Before You Install — Customisation Notes

These skills were built for a specific deployment. Before installing, review the following and adapt to your environment.

### 1. Agent Name

Skills in this folder were written for an agent named **Leo**. Your agent may have a different name.

Search for references to the agent name in any SKILL.md and update accordingly:
```bash
grep -r "Leo" ~/.hermes/profiles/<your-agent>/skills/
```

The name appears in:
- `author:` fields in skill frontmatter
- Any skills that reference the agent by name in instructions or confirmation messages

### 2. CRM Address

Skills use `http://localhost:3001` as the Twenty CRM address. This is the default for a local install.

If your CRM runs on a different host or port, update the address in each skill:
```bash
grep -r "localhost:3001" ~/.hermes/profiles/<your-agent>/skills/
```

Replace with your actual CRM endpoint — e.g. `http://192.168.1.100:3000` or a tunnelled domain.

### 3. CRM Object Names

Skills use Twenty CRM's default internal object names:
- Company → `company`
- Person → `person`
- Opportunity → `opportunity`

If you are using a different CRM or have renamed objects, update the GraphQL queries and mutations in each skill accordingly.

### 4. Product Names

Any references to `[Product]` in skill content are placeholders. Replace with your actual product or service names.

### 5. Owner / Human Names

Skills reference the human sales rep as **Hunter** in examples and agent advice. Replace with the actual name of the person using the system.

Search:
```bash
grep -r "Hunter" ~/.hermes/profiles/<your-agent>/skills/
```

---

## Installation

Each skill is a folder. Copy the entire folder — not just the SKILL.md file:

```bash
# Copy all skills for this agent
cp -r agent-teams/leo/skills/* ~/.hermes/profiles/<your-agent>/skills/

# Or copy individual skills
cp -r agent-teams/leo/skills/engagement-logging ~/.hermes/profiles/<your-agent>/skills/
```

After copying, restart your Hermes session so the new skills are loaded.

---

## Skills in This Folder

| Skill | What it does | Used by Capability |
|---|---|---|
| `account-onboarding` | When sales rep meets someone new — extract info, create Company + Person in CRM, trigger enrichment, confirm relationship type | C1 |
| `enriching-leads` | Web-search a company domain to build a company profile; writes findings to CRM notes and GBrain | C1 |
| `capturing-sales-intel` | Extract and store intel from any conversation mention of a company or person | C1 |
| `engagement-logging` | Accept any input (chat log, meeting notes, transcript) — extract summary + outcome, confirm with human, write to CRM + GBrain | C2, C3 |
| `task-management` | Identify all actionable work items from an engagement, create Tasks with owner + deadline + agent advice | C2, C3 |
| `deal-progressing` | After engagement logged — recalculate opportunity health, priority, and risk; update CRM | C2 |
| `deal-health-check` | Daily scan of all open opportunities — detect stalls, flag AT_RISK, create stall tasks | C2 |
| `deal-advisory` | Deep diagnosis of a stalled or stuck opportunity — history + recovery plan | C2 |
| `meeting-prep` | Day-before brief for any planned engagement — context, history, suggested talking points | C2, C3 |
| `managing-partnership-pipeline` | Log partner engagements, track progression toward signed agreement | C3 |
| `daily-partnership-health-check` | Daily scan of all active partnerships — detect silence, flag at-risk | C3 |
| `reviewing-partnership-pipeline` | On-demand review of full partnership pipeline | C3 |
| `reviewing-sales-pipeline` | On-demand review of full opportunity pipeline | C4 |
| `daily-briefing` | Morning summary — open tasks, at-risk deals, today's planned engagements | C4 |
| `lead-nurturing` | Monthly batch — identify cold contacts (30+ days no engagement), draft personalised re-outreach | C5 |
| `follow-up-email` | Draft a follow-up email based on engagement context and last interaction | C2, C3, C5 |
| `generating-quotations` | Generate quotation document from Opportunity and Company data | C2 |
| `generating-invoices` | Generate invoice after contract is signed | C2 |
| `meeting-prep` | Pre-meeting brief with context, history, and talking points | C2, C3 |
