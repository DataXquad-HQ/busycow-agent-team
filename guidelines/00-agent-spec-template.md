# Agent Spec Template

> Copy this file and rename it `[agent-name]-spec.md`.
> Fill in every section before starting Phase 2.
> This document is for humans — runtime behaviour lives in SOUL.md + skills.

---

## Agent Overview

| Field | Value |
|---|---|
| **Name** | |
| **Role** | |
| **Owns** | |
| **Does not own** | |
| **Reports to** | |
| **Primary human contact** | |

---

## Goal

*One paragraph. What does this agent exist to do? What is the success criterion?*

---

## Capabilities

> One row per Capability. A Capability is a grouping for humans — it does not exist in the agent's runtime.
> Each Capability maps to one or more Skills (one skill = one trigger situation).

| # | Capability | What the agent does | Skill(s) | Status |
|---|---|---|---|---|
| C1 | | | | 📝 Pending |
| C2 | | | | 📝 Pending |

*(Mark ✅ only after tested in a real scenario.)*

---

## Skills

> List every skill this agent needs. Split into Capability Skills (unique to this agent) and General Skills (shared tooling).

### Capability Skills

| Skill name | Trigger situation | Capability |
|---|---|---|
| | | |

### General Skills

| Skill name | Purpose |
|---|---|
| `twenty-crm` | CRM read/write |
| `lark-im` | Send/receive Lark messages |
| *(add or remove as needed)* | |

---

## Knowledge

> Documents this agent needs to query at runtime. Must exist in GBrain before the agent is useful.
> After creating each document, run `gbrain sync` and verify with `mcp_gbrain_get_page`.

| Document | GBrain slug | Purpose | Status |
|---|---|---|---|
| ICP Definition | `wiki/[org-prefix]-icp` | Who to target and why | 📝 To be created |
| Sales / Product Strategy | `wiki/[org-prefix]-strategy` | Direction and priorities | 📝 To be created |

---

## Memory (Hindsight Banks)

> List every Hindsight bank this agent reads from or writes to.
> All banks must be created in Hindsight before skills that use them are tested.

| Bank ID | Access | Purpose | Shared / Private |
|---|---|---|---|
| `[org-prefix]-pipeline` | read + write | Opportunity interaction history | Shared |
| `[org-prefix]-agent-[name]` | read + write | Agent's private working memory | Private |
| `[org-prefix]-human-[name]` | read only | Human's communication style and priorities | Shared |

---

## Credentials & Third-Party Tools

> Every credential listed here must be in the agent's per-profile `.env` before skills are tested.

| Service | Purpose | How to obtain | `.env` key |
|---|---|---|---|
| | | | |

---

## Delivery Channels (Lark)

> Where the agent sends output. Confirm channel IDs before setting up cron jobs.

| Channel name | `chat_id` | What goes here |
|---|---|---|
| `[Agent] Daily Update` | `{{CHANNEL_ID}}` | Human-facing summaries and decisions |
| `[System] Backend Report` | `{{CHANNEL_ID}}` | Cron job ops logs, errors |

---

## Cron Jobs

> Only fill this in after all relevant skills are verified (✅).

| Job name | Schedule | Skill called | Delivers to |
|---|---|---|---|
| | | | |
