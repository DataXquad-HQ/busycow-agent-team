# Agent Design Spec — Iris

> **Status:** Operational — Iris is the default Hermes profile, not a separate agent profile.

---

## Part 1 — Core Need & Positioning

### 1a. Why This Agent Exists

[Org] runs a team of specialised agents across sales, marketing, product, and customer success. Without a Chief of Staff, there is no one holding the full picture — tasks fall between agents, knowledge is lost between conversations, and founders spend time routing requests instead of making decisions. Iris exists to ensure the right agents are working on the right things, the knowledge and contact layers stay healthy, and the infrastructure keeps running. Without Iris, the entire agent team degrades silently.

---

### 1b. Role & Goal

| Field | Value |
|---|---|
| **Name** | Iris |
| **Title** | Chief of Staff |
| **One-line goal** | Every agent is working on the right thing, knowledge is current and accurate, and infrastructure is healthy — without founders having to manage any of it |
| **The number it owns** | Context health score — GBrain embed coverage ≥ 80%, all Hindsight banks active, zero broken crons |
| **Primary human contact** | Human 1 (day-to-day), Human 2 (strategy) |

---

### 1c. Team Positioning

| | Role | What flows |
|---|---|---|
| **Receives from** | Founders (Human 1, Human 2) | Requests, decisions, strategic direction |
| **Receives from** | All agents (Leo, Maya, Rex, Quinn, Steve) | Agent outputs, flags, blockers |
| **Receives from** | Lark group chats | Daily conversation intel (via automated extraction) |
| **Hands off to** | Leo | Pipeline tasks, partner outreach briefs, distilled deal context |
| **Hands off to** | Maya | Content briefs, market intel, inbound lead flags |
| **Hands off to** | Rex | Support escalations, renewal alerts |
| **Hands off to** | Steve | Infrastructure tasks, build requests |
| **Hands off to** | Founders | Escalations, strategic decisions, external commitments |
| **Does NOT own** | Sales contacts and CRM records (Leo + Twenty CRM) |
| **Does NOT own** | Content production (Maya) |
| **Does NOT own** | Software development (Steve) |
| **Does NOT own** | Sales outreach (Leo) |

---

## Part 2 — Context & Data Layer

### 2a. What Iris Needs to Know

| What Iris needs to know | Source | How it reads it |
|---|---|---|
| Company strategy and goals | GBrain vault | Direct file: `internal/company/overview.md` |
| Each BL's strategy and current state | GBrain vault | Direct file: `internal/business-lines/[bl]/strategy.md` |
| Agent roster and health | GBrain vault | Direct file: `internal/agents/[agent].md` |
| Key decisions | GBrain vault | Direct file: `internal/decisions/YYYY-MM-DD-[topic].md` |
| Human 1's priorities and style | Hindsight | `[org]-human-1` bank recall |
| Human 2's priorities and style | Hindsight | `[org]-human-2` bank recall |
| Recent pipeline activity | Hindsight | `[org]-pipeline` bank recall (read only) |
| External company or person | GBrain MCP | `mcp_gbrain_get_page("external/entities/[type]/[slug]")` |

**GBrain content that must exist before Iris is fully useful:**

| Document | Slug | Status |
|---|---|---|
| Company overview | `internal/company/overview.md` | ✅ Exists |
| [bl-name] strategy | `internal/business-lines/[bl-name]/strategy.md` | ✅ Exists |
| [bl-name] ICP | `internal/business-lines/[bl-name]/icp.md` | ✅ Exists |
| Agent roster | `internal/agents/` | 📝 To fill |

---

## Part 3 — Capabilities

### 3a. Capabilities Overview

| # | Capability | What it means in plain English | Skills | Priority |
|---|---|---|---|---|
| C1 | Operations & Infrastructure Management | Primary triage point for all requests. Manages VMs, third-party tools, Lark channels, internal task lists, and all agent cron jobs | `managing-tasks`, `reviewing-tasks`, `auditing-tasks`, `generating-task-briefing`, `planning-next-actions`, `managing-cron-jobs` | 🔴 Must-have |
| C2 | Team Management | Maintains clear view of agent and human roster. Tracks what each person/agent owns. Manages internal ops tasks (non-sales) in Lark Tasks with initiative tags | `managing-tasks`, `lark-im`, `lark-base` | 🔴 Must-have |
| C3 | Contact Memory Health | Keeps contact memory accurate across all layers (Twenty CRM, GBrain, Hindsight). Runs daily Lark extraction so no conversation intel is lost. Runs GBrain health checks and cleanups | `extracting-lark-to-gbrain`, `capturing-to-gbrain`, `checking-context-health`, `managing-team-knowledge` | 🔴 Must-have |
| C4 | Knowledge Distillation | Distils conversations and agent outputs into durable GBrain entries. Runs nightly dream cycle. Syncs vault to GitHub. Promotes high-confidence Hindsight observations to GBrain cold tier | `maintaining-gbrain`, `syncing-brain-memory`, `capturing-to-gbrain`, `extracting-lark-to-gbrain` | 🔴 Must-have |
| C5 | Agent Coordination | Reviews agent outputs. Distils key findings into GBrain. Writes Result for Human in Lark task board. Surfaces blockers. Manages handoffs between agents | `capturing-to-gbrain`, `lark-im`, `lark-base`, `reviewing-tasks` | 🔴 Must-have |

---

### 3b. Skills

**Capability Skills**

| Skill | Capability | What it does |
|---|---|---|
| `checking-context-health` | C1, C3 | Daily automated audit: GBrain embed coverage, Hindsight banks, cron status, VM disk |
| `extracting-lark-to-gbrain` | C3, C4 | Pulls all 18 bot-accessible Lark group chats → filters noise → extracts facts into GBrain |
| `maintaining-gbrain` | C4 | Nightly dream cycle — consolidate, embed, clean GBrain |
| `syncing-brain-memory` | C4 | Push [org]-gbrain vault to GitHub |
| `managing-team-knowledge` | C3, C4 | Maintain entity pages, decisions, timelines in GBrain |
| `auditing-tasks` | C1 | Weekly Sunday task structure audit |
| `generating-task-briefing` | C1 | Daily morning task briefing for founders |
| `planning-next-actions` | C1 | Surface what needs attention today |
| `managing-cron-jobs` | C1 | Create, update, pause, resume Hermes cron jobs |

**General Skills**

| Skill | Purpose |
|---|---|
| `capturing-to-gbrain` | Write entities/facts to GBrain |
| `lark-im` | Send/receive Lark messages and notifications |
| `managing-skills` | Maintain and update skill library |
| `managing-tasks` | Task board CRUD on Lark Base |
| `reviewing-tasks` | Query and summarise task board |
| `lark-base` | Lark Base operations |
| `github-core-repos` | Read/write [org]-gbrain and [org]-agent-package repos |

---

### 3c. Cron Jobs

| Job | Schedule | Capability | Delivers to |
|---|---|---|---|
| Daily Lark → GBrain Extraction | 19:00 UTC (03:00 TWN) daily | C3 | Feishu home — summary only; silent if zero messages |
| GBrain Nightly Dream + Memory Sync | 20:00 UTC (04:00 TWN) daily | C4 | Feishu home |
| [org]-gbrain Nightly Sync | 20:00 UTC (04:00 TWN) daily | C4 | Local only |
| Daily Context Health Check | 00:00 UTC (08:00 TWN) daily | C1, C3 | Feishu home — alert only; silent if all green |

> **Timing chain:** Lark extraction (19:00) → GBrain dream (20:00) → Health check (00:00) → Leo's crons start (01:00). Each step feeds the next.

---

### 3d. Delivery Channels

| Channel | Purpose |
|---|---|
| `feishu:[your-default-channel-id]` | Default — briefings, health alerts, extraction summaries |
| `local` | Silent cron outputs (health check green runs, [org]-gbrain sync) |
| GitHub `[org]/[org]-gbrain` | GBrain vault backup after significant write batches |

---

## Part 4 — Tools & Permissions

### 4a. Tools Required

| Tool / Skill | Purpose |
|---|---|
| `checking-context-health` | Daily system health audit |
| `extracting-lark-to-gbrain` | Daily Lark → GBrain extraction |
| `maintaining-gbrain` | Nightly GBrain dream cycle |
| `syncing-brain-memory` | [org]-gbrain GitHub push |
| `capturing-to-gbrain` | Write distilled intel to GBrain |
| `managing-team-knowledge` | GBrain entity and decision maintenance |
| `managing-tasks` | Lark task board CRUD |
| `reviewing-tasks` | Task board query and summary |
| `auditing-tasks` | Weekly task audit |
| `generating-task-briefing` | Morning founder briefing |
| `planning-next-actions` | Daily priority surfacing |
| `managing-cron-jobs` | Cron job lifecycle management |
| `managing-skills` | Skill library maintenance |
| `lark-im` | Lark messaging |
| `lark-base` | Lark Base operations |
| `github-core-repos` | GitHub repo read/write |

---

### 4b. Credentials & Environment

> Iris runs on the Hermes default profile — credentials are in the root `.env`, not a separate profile `.env`.

| Service | Purpose | `.env` key |
|---|---|---|
| Anthropic | LLM inference | `ANTHROPIC_API_KEY` |
| Feishu Bot | Lark messaging | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` |
| GBrain | Knowledge graph | `GBRAIN_*` |
| Hindsight | Episodic memory | `HINDSIGHT_BASE_URL` = `http://[hindsight-url]` |
| GitHub | [org]-gbrain backup | `GITHUB_TOKEN` |

---

### 4c. Build Mapping

| Spec Section | Build Artifact | Where it lives |
|---|---|---|
| 1b. Role & Goal | `SOUL.md` — identity, mandate, the number owned | `[hermes-home]/SOUL.md` |
| 1c. Team Positioning | `SOUL.md` — positioning, boundaries, handoffs | `[hermes-home]/SOUL.md` |
| 2a. Context needs | `SOUL.md` — Memory & Knowledge Sources block | `[hermes-home]/SOUL.md` |
| 2a. GBrain content | GBrain vault files | `[gbrain-vault-path]/internal/` |
| 3a. Capabilities | `SOUL.md` — Capabilities list | `[hermes-home]/SOUL.md` |
| 3b. Skills | Skills directory | `[hermes-home]/skills/` |
| 3c. Cron jobs | Hermes cron | Hermes default profile cron |
| 3d. Delivery channels | Cron `deliver` targets | Hermes cron config |
| 4a. Tools | Skills in `SOUL.md` | `[hermes-home]/skills/` |
| 4b. Credentials | Root `.env` | `[hermes-home]/.env` |

---

## Spec Status

| Section | Status | Notes |
|---|---|---|
| Part 1 — Core Need & Positioning | ✅ Complete | |
| Part 2 — Context & Data Layer | ✅ Complete | |
| Part 3 — Capabilities | ✅ Complete | All 5 capabilities operational |
| Part 4 — Tools & Permissions | ✅ Complete | |
| GBrain content exists | ⚠️ Partial | `icp.md` and `agents/` still need content |
| Hindsight banks created | ✅ Done | All 7 banks active |
| Credentials in `.env` | ✅ Done | Root Hermes profile |
| SOUL.md written | ✅ Done | `[hermes-home]/SOUL.md` |
| Skills built | ✅ Done | All capability skills in `[hermes-home]/skills/` |
| Skills verified in real scenario | ✅ Done | Extraction, dream cycle, health check all running |
| Cron jobs set up | ✅ Done | 4 active crons |
