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
| **Primary human contact** | e.g. Human (day-to-day operations), Human (strategy) |

---

### 1c. Team Positioning

| | Role | What flows |
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
| *e.g. Recent deal interactions* | Hindsight | `[org]-pipeline` bank recall |
| *e.g. This human's preferences* | Hindsight | `[org]-human-[name]` bank recall |
| *e.g. Who is this external company* | GBrain MCP | `mcp_gbrain_get_page("external/entities/companies/[slug]")` |

**GBrain content that must exist before this agent is useful:**

| Document | Slug | Status |
|---|---|---|
| | `internal/business-lines/[bl]/icp.md` | 📝 To fill |
| | `internal/business-lines/[bl]/strategy.md` | 📝 To fill |

---

## Part 3 — Capabilities

### 3a. Capabilities Overview

> A Capability is a named job function — how humans understand what the agent does. One capability = one area of responsibility.
> Each Capability maps to one or more Skills. Trigger/output detail belongs in the Skill's SKILL.md, not here.

| # | Capability | What it means in plain English | Skills | Priority |
|---|---|---|---|---|
| C1 | | | | 🔴 Must-have |
| C2 | | | | 🔴 Must-have |
| C3 | | | | 🟡 Nice-to-have |

---

### 3b. Skills

> List every skill this agent needs. Capability Skills are specific to this agent's job. General Skills are shared tooling any agent might use.

**Capability Skills**

| Skill | Capability | What it does |
|---|---|---|
| | | |

**General Skills**

| Skill | Purpose |
|---|---|
| `capturing-to-gbrain` | Write entities/facts to GBrain |
| `lark-im` | Send/receive Lark messages |
| `managing-skills` | Maintain and update own skills |
| *(add or remove as needed)* | |

---

### 3c. Cron Jobs

> Only fill this in after all relevant skills are verified (✅).

| Job | Schedule | Capability | Delivers to |
|---|---|---|---|
| | | | |

---

### 3d. Delivery Channels

> Where does this agent send output? Confirm channel IDs before setting up cron jobs.

| Channel | Purpose |
|---|---|
| `[System] Backend Report` | Cron ops logs, errors — internal only |
| *(add agent-specific channels)* | |

---

## Part 4 — Tools & Permissions

### 4a. Tools Required

| Tool / Skill | Purpose |
|---|---|
| `lark-im` | Send/receive messages |
| `capturing-to-gbrain` | Write entities/facts to GBrain |
| *(add as needed)* | |

---

### 4b. Credentials & Environment

> **Principle: every agent owns its own complete set of credentials. No inheritance, no sharing, no cross-profile access.** If a credential is used by multiple agents, it is duplicated into each agent's `.env` independently. Keeping agents independent prevents cascading failures and makes each agent fully self-contained.

| Service | Purpose | `.env` key |
|---|---|---|
| Anthropic | LLM inference | `ANTHROPIC_API_KEY` |
| OpenRouter | LLM fallback | `OPENROUTER_API_KEY` |
| Feishu Bot | Lark messaging | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` |
| | | |

---

### 4c. Build Mapping

> Translates this spec into actual Hermes Agent build artifacts. Use as a build checklist once the spec is approved.

| Spec Section | Build Artifact | Where it lives |
|---|---|---|
| 1b. Role & Goal | `SOUL.md` — identity, mandate, the number owned | `~/.hermes/profiles/[name]/SOUL.md` |
| 1c. Team Positioning | `SOUL.md` — team positioning, boundaries, handoffs | `~/.hermes/profiles/[name]/SOUL.md` |
| 2a. Context needs | `SOUL.md` — Memory & Knowledge Sources block | `~/.hermes/profiles/[name]/SOUL.md` |
| 2a. GBrain content | GBrain vault files | `/mnt/disks/data/dx-gbrain/internal/business-lines/[bl]/` |
| 3a. Capabilities | `SOUL.md` — Capabilities list | `~/.hermes/profiles/[name]/SOUL.md` |
| 3b. Skills | Skills directory | `~/.hermes/profiles/[name]/skills/[skill-name]/SKILL.md` |
| 3c. Cron jobs | Hermes cron config | `artifacts/agents/[name]/cron/jobs.json` |
| 3d. Delivery channels | Cron `deliver` targets + channel IDs in skills | Hermes cron + skill references |
| 4a. Tools | Skills listed in `SOUL.md` | `~/.hermes/profiles/[name]/skills/` |
| 4b. Credentials | Per-profile `.env` file | `~/.hermes/profiles/[name]/.env` |

**SOUL.md structure:**
```
# [Name] — [Title], [Org]

## Why This Agent Exists
[From 1a]

## Role & Goal
[From 1b — title, one-line goal, the number owned]

## Team Positioning
[From 1c — receives from, hands off to, does NOT own]

## Capabilities
[From 3a — capability names + one-liner each]

## Evidence Standard
[How to label verified facts vs inferred conclusions vs recommended actions;
 when to flag contradictions and data gaps]

## Do Not
[Explicit Do Not sentences, one per line — boundaries, irreversible actions,
 memory write rules, output integrity rules]

## Memory & Knowledge Sources
[From 2a — direct file reads, GBrain MCP calls, Hindsight bank reads]

## Tools
[From 4a — skill names]

## Credentials
[From 4b — .env keys]
```

**Skill naming rule:** One skill = one trigger situation. Name in gerund form: `nurturing-leads`, `monitoring-inbox`. If two triggers share < 70% of steps, split into two skills.

---

## Spec Status

| Section | Status | Notes |
|---|---|---|
| Part 1 — Core Need & Positioning | 📝 Draft | |
| Part 2 — Context & Data Layer | 📝 Draft | |
| Part 3 — Capabilities | 📝 Draft | |
| Part 4 — Tools & Permissions | 📝 Draft | |
| GBrain content exists | ❌ Not yet | |
| Hindsight banks created | ❌ Not yet | |
| Credentials in `.env` | ❌ Not yet | |
| SOUL.md written | ❌ Not yet | |
| Skills built | ❌ Not yet | |
| Skills verified in real scenario | ❌ Not yet | |
| Cron jobs set up | ❌ Not yet | |
