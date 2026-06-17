# Agent Design Spec — Template

> **Purpose:** This is a Product Spec for designing a new agent. Think of it as a hiring brief + job design document. Complete this before building anything.
>
> **How to use:** Copy this file, rename to `[agent-name]-spec.md`, fill in every section. When done, use the **Build Mapping** table at the bottom to translate each section into actual Hermes Agent artifacts.
>
> **Philosophy:** An agent is a team member, not a tool. Give them a title, a clear mandate, and the context they need to do their job. If you can't answer "why would we hire this person?", the agent isn't ready to be built.

---

## Part 1 — Core Need & Positioning

### 1a. Why This Agent Exists

*Why are we hiring this agent? What problem does it solve that a human or existing agent doesn't? What happens if we don't have it?*

> Answer in 2–4 sentences. If you can't articulate this clearly, stop here.

---

### 1b. Role & Goal

| Field | Value |
|---|---|
| **Name** | |
| **Title** | e.g. Head of BD, Customer Success Lead, Content Strategist |
| **One-line goal** | *What does success look like for this agent?* |
| **The number it owns** | *One metric. This agent is responsible for moving this.* |
| **Primary human contact** | e.g. Hunter (BD decisions), Kevin (strategy) |

---

### 1c. Team Positioning

*Where does this agent sit in the team? What does it hand off to and receive from other agents?*

| | Agent | Handoff |
|---|---|---|
| **Receives from** | | *What context or work arrives to this agent* |
| **Hands off to** | | *What this agent produces that others consume* |
| **Does NOT own** | | *Explicit boundary — what this agent must not do* |

---

## Part 2 — Context & Data Layer

### 2a. What This Agent Needs to Know

*Before acting, what does this agent need to read? Map each context need to its source.*

| What the agent needs to know | Source | How it reads it |
|---|---|---|
| *e.g. Our ICP for this BL* | GBrain vault | Direct file: `internal/business-lines/[bl]/icp.md` |
| *e.g. Company background* | GBrain vault | Direct file: `internal/company/overview.md` |
| *e.g. Recent deal interactions* | Hindsight | `dx-pipeline` bank recall |
| *e.g. This human's preferences* | Hindsight | `dx-human-[name]` bank recall |
| *e.g. Who is this external company* | GBrain MCP | `mcp_gbrain_get_page("external/entities/companies/[slug]")` |

**GBrain content that must exist before this agent is useful:**

| Document | Slug | Status |
|---|---|---|
| | `internal/business-lines/[bl]/icp.md` | 📝 To fill |
| | `internal/business-lines/[bl]/strategy.md` | 📝 To fill |

---

### 2b. Capabilities Overview

> A Capability is a named job function — it's how humans understand what the agent does. One capability = one area of responsibility. Not a skill, not a task.
>
> Rule: if you can't name it as a job function (e.g. "Lead Nurturing", "Pipeline Monitoring"), it's probably too granular.

| # | Capability | What it means in plain English | Priority |
|---|---|---|---|
| C1 | | | 🔴 Must-have |
| C2 | | | 🔴 Must-have |
| C3 | | | 🟡 Nice-to-have |

---

### 2c. Capability Detail

> For each capability above, define what it actually does, what triggers it, and what success looks like.

**C1 — [Capability Name]**

- **Trigger:** *When does this capability activate? (e.g. new lead enters CRM, human asks, daily cron)*
- **What the agent does:** *Step-by-step description of the action*
- **Output:** *What does the human receive? What gets written to memory/CRM?*
- **Success criterion:** *How do we know this worked?*

**C2 — [Capability Name]**

- **Trigger:**
- **What the agent does:**
- **Output:**
- **Success criterion:**

*(Copy block for each capability)*

---

## Part 3 — Tools & Permissions

### 3a. Tools Required

| Tool / Skill | Purpose | Required for Capability |
|---|---|---|
| `lark-im` | Send/receive messages | All |
| `lark-base` | Read/write task board | All |
| `twenty-crm` | Pipeline read/write | *(if applicable)* |
| `capturing-to-gbrain` | Write entities/facts to GBrain | All |
| *(add as needed)* | | |

---

### 3b. Credentials & Environment

> Every credential listed here must be in the agent's per-profile `.env` before any skill is tested.

| Service | Purpose | `.env` key | How to obtain |
|---|---|---|---|
| | | | |

---

### 3c. Delivery Channels

> Where does this agent send output? Confirm channel IDs before setting up cron jobs.

| Channel | `chat_id` | What goes here |
|---|---|---|
| `[Agent] Daily Update` | | Human-facing summaries |
| `[System] Backend Report` | | Ops logs, errors |

---

### 3d. Cron Jobs

> Only fill this in after all relevant skills are verified (✅).

| Job name | Schedule | Triggers | Delivers to |
|---|---|---|---|
| | | | |

---

## Part 4 — Build Mapping

> This section translates the spec into actual Hermes Agent build artifacts. Once the spec is approved, use this table as your build checklist.

| Spec Section | Build Artifact | Where it lives |
|---|---|---|
| 1b. Role & Goal | `SOUL.md` — Identity, mandate, the number owned | `~/.hermes/profiles/[name]/SOUL.md` |
| 1c. Team Positioning | `SOUL.md` — Delegation map, boundaries, handoffs | `~/.hermes/profiles/[name]/SOUL.md` |
| 2a. Context needs | `SOUL.md` — Memory & Knowledge Sources block | `~/.hermes/profiles/[name]/SOUL.md` |
| 2a. GBrain content | GBrain vault files | `/mnt/disks/data/dx-gbrain/internal/business-lines/[bl]/` |
| 2b–2c. Capabilities | Skills (one skill per trigger situation) | `~/.hermes/profiles/[name]/skills/[skill-name]/SKILL.md` |
| 3a. Tools | Skills + general skills listed in `SOUL.md` | `~/.hermes/profiles/[name]/skills/` |
| 3b. Credentials | Per-profile `.env` file | `~/.hermes/profiles/[name]/.env` |
| 3c. Delivery channels | Cron job `deliver` targets + Lark channel IDs in skills | Hermes cron + skill references |
| 3d. Cron jobs | Hermes cron jobs | `hermes cron create` after skills verified |

### SOUL.md Structure (what to write per section)

```
# [Name] — [Title], [Org]

## Why This Agent Exists
[From 1a — the hiring rationale]

## Role & Goal
[From 1b — title, one-line goal, the number owned]

## Team Positioning
[From 1c — who it receives from, hands off to, does NOT own]

## Capabilities
[From 2b — capability names only, one-liner per capability]

## Memory & Knowledge Sources

### Before every task — load from GBrain vault:
[From 2a — direct file reads]

### External entity lookup:
[From 2a — GBrain MCP calls]

### Interaction history:
[From 2a — Hindsight bank reads]

## Tools
[From 3a — skill names]

## Credentials
[From 3b — .env keys needed]
```

### Skill naming rule
One skill = one trigger situation (not one capability, not one domain).
Name in gerund form: `nurturing-leads`, `monitoring-inbox`, `logging-engagement`.
If two triggers share < 70% of their steps, split into two skills.

---

## Spec Status

| Section | Status | Notes |
|---|---|---|
| Part 1 — Core Need & Positioning | 📝 Draft | |
| Part 2 — Context & Data Layer | 📝 Draft | |
| Part 3 — Tools & Permissions | 📝 Draft | |
| GBrain content exists | ❌ Not yet | |
| Hindsight banks created | ❌ Not yet | |
| Credentials in `.env` | ❌ Not yet | |
| SOUL.md written | ❌ Not yet | |
| Skills built | ❌ Not yet | |
| Skills verified in real scenario | ❌ Not yet | |
| Cron jobs set up | ❌ Not yet | |
