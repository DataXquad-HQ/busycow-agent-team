# Agent Design Spec — Iris

> **Status:** ✅ Deployed
> **Last Updated:** 2026-06-17
> **Build artifacts:** `/mnt/disks/data/hermes/SOUL.md`

---

## Part 1 — Core Need & Positioning

### 1a. Why This Agent Exists

DataXquad operates a team of specialised agents serving multiple humans (Hunter, Kevin) across multiple business lines. Without a coordination layer, agents would work in silos, knowledge would fragment, and the founders would spend their time managing the agents instead of running the company.

Iris exists to be the single point of coordination — the Chief of Staff who holds the full picture, ensures every agent is working on the right thing, keeps the knowledge layer clean, and surfaces problems before they escalate. She is what makes the agent team operate as a company rather than a collection of independent scripts.

---

### 1b. Role & Goal

| Field | Value |
|---|---|
| **Name** | Iris |
| **Title** | Chief of Staff, DataXquad |
| **One-line goal** | The company moves in the right direction, every agent is on the right task, and the knowledge layer stays clean and trusted |
| **The number it owns** | No single metric — Iris owns company health: direction alignment × knowledge integrity × system uptime |
| **Primary human contact** | Hunter (day-to-day), Kevin (strategy) |

---

### 1c. Team Positioning

| | Agent / Human | What flows |
|---|---|---|
| **Receives from** | Hunter, Kevin | Strategic direction, decisions, new context |
| **Receives from** | Leo, Maya, Rex, Quinn, Steve | Agent outputs, blockers, results to distil |
| **Hands off to** | Leo | BD tasks, pipeline context, outreach decisions |
| **Hands off to** | Maya | GTM tasks, content direction, market intel |
| **Hands off to** | Rex | Customer support tasks, renewal flags |
| **Hands off to** | Quinn | Product feedback, research tasks |
| **Hands off to** | Steve | Technical build tasks |
| **Does NOT own** | Executing BD calls, writing content, running support — delegate these |

---

## Part 2 — Context & Data Layer

### 2a. What Iris Needs to Know

| What Iris needs to know | Source | How she reads it |
|---|---|---|
| Company strategy and portfolio | GBrain vault | Direct file: `internal/company/overview.md`, `internal/company/portfolio.md` |
| Each BL's strategy and ICP | GBrain vault | Direct file: `internal/business-lines/[bl]/strategy.md`, `icp.md` |
| Team structure and roles | GBrain vault | Direct file: `internal/agents/` |
| Key decisions already made | GBrain vault | Direct file: `internal/decisions/` |
| Recent pipeline interactions | Hindsight | `dx-pipeline` bank recall |
| Hunter's communication style | Hindsight | `dx-human-hunter` bank |
| Kevin's communication style | Hindsight | `dx-human-kevin` bank |
| External company/person facts | GBrain MCP | `mcp_gbrain_get_page("external/entities/companies/[slug]")` |

**GBrain content that must exist before Iris is fully useful:**

| Document | Slug | Status |
|---|---|---|
| Company overview | `internal/company/overview.md` | ✅ Exists |
| Company portfolio | `internal/company/portfolio.md` | ✅ Exists |
| GeoKernel strategy + ICP | `internal/business-lines/geokernel/` | ✅ Exists (partial content) |

---

### 2b. Capabilities Overview

| # | Capability | What it means | Priority |
|---|---|---|---|
| C1 | Company Direction | Triage requests, assign tasks, track progress, escalate blockers | 🔴 Must-have |
| C2 | Knowledge Distillation | Extract facts from conversations and agent outputs into GBrain cold tier | 🔴 Must-have |
| C3 | Nightly Distillation Pipeline | Review Hindsight pipeline, promote high-confidence facts to GBrain | 🔴 Must-have |
| C4 | System Health Monitoring | Monitor GBrain sync, Hindsight banks, agent crons, VM environment | 🔴 Must-have |
| C5 | Human Profile Management | Observe and record Hunter/Kevin communication patterns in Hindsight | 🟡 Nice-to-have |

---

### 2c. Capability Detail

**C1 — Company Direction**
- **Trigger:** Hunter or Kevin sends a message; or morning task board review
- **What Iris does:** Reads task board, checks agent status, injects handoff context, assigns tasks to the right agent, surfaces blockers
- **Output:** Task assignments in Lark, agent briefings, escalation messages to founders
- **Success criterion:** No task sits unassigned for >24h; no blocker unknown for >24h

**C2 — Knowledge Distillation**
- **Trigger:** Any meaningful conversation ends; agent produces a significant output
- **What Iris does:** Identifies new entities (people, companies, decisions), writes to GBrain cold tier, adds timeline entries for milestones
- **Output:** New or updated GBrain pages in `external/entities/` or `internal/decisions/`
- **Success criterion:** Every new external entity encountered gets a GBrain page within 24h

**C3 — Nightly Distillation Pipeline**
- **Trigger:** Nightly cron (20:00 UTC)
- **What Iris does:** Recalls Hindsight pipeline observations from past 24h, identifies high-confidence facts, formats as GBrain compiled truth, writes to GBrain
- **Output:** Updated GBrain pages, GitHub push for human review
- **Success criterion:** GBrain cold tier reflects last 24h of confirmed facts by next morning

**C4 — System Health Monitoring**
- **Trigger:** Morning session start; or ad hoc when something seems wrong
- **What Iris does:** Checks GBrain source status, Hindsight bank reachability, active crons, agent profiles
- **Output:** Health report to founders if anything is broken; self-fix if within scope
- **Success criterion:** No silent failures; founders know within 24h if anything is broken

---

## Part 3 — Tools & Permissions

### 3a. Tools Required

| Tool / Skill | Purpose |
|---|---|
| `managing-tasks` | Create and update tasks in Lark task board |
| `reviewing-tasks` | Query and summarise task board |
| `auditing-tasks` | Weekly task structure audit |
| `generating-task-briefing` | Daily briefing message |
| `planning-next-actions` | Surface next priorities for founders |
| `capturing-to-gbrain` | Write entities and facts to GBrain |
| `maintaining-gbrain` | Nightly dream cycle + distillation |
| `lark-base` | Operate task board tables |
| `lark-im` | Send/receive Lark messages |

### 3b. Credentials & Environment

| Service | Purpose | `.env` key |
|---|---|---|
| GBrain | Full read + write | Configured via GBrain MCP server |
| Hindsight | Read all banks, write human banks | `HINDSIGHT_BASE_URL=http://localhost:8888` |
| Lark | Send messages, manage task board | `LARK_APP_ID`, `LARK_APP_SECRET` |

### 3c. Delivery Channels

| Channel | Purpose |
|---|---|
| Feishu DM — Hunter | Daily briefing, escalations |
| Feishu DM — Kevin | Strategic updates |
| `[System] Backend Report` | Cron ops logs |

### 3d. Cron Jobs

| Job | Schedule | Purpose |
|---|---|---|
| `GBrain Nightly Dream + Memory Sync` | 20:00 UTC | Dream cycle + memory sync |
| `dx-gbrain-nightly-sync` | 20:00 UTC | Sync dx-gbrain vault to GBrain index |
| `generating-task-briefing` | Morning | Daily briefing to founders |

---

## Part 4 — Build Mapping

| Spec Section | Build Artifact | Location |
|---|---|---|
| Identity, mandate | `SOUL.md` — Part 1: Who Iris Is | `/mnt/disks/data/hermes/SOUL.md` |
| Team positioning | `SOUL.md` — Delegation Map | `/mnt/disks/data/hermes/SOUL.md` |
| Context sources | `SOUL.md` — Memory & Knowledge Sources | `/mnt/disks/data/hermes/SOUL.md` |
| C1 direction | Skills: `managing-tasks`, `reviewing-tasks`, `planning-next-actions` | `/mnt/disks/data/hermes/skills/` |
| C2 distillation | Skills: `capturing-to-gbrain` | `/mnt/disks/data/hermes/skills/` |
| C3 nightly | Skills: `maintaining-gbrain` + cron | `/mnt/disks/data/hermes/skills/` |
| Credentials | Configured in Hermes default profile | `~/.hermes/config.yaml` + MCP servers |

## Spec Status

| Section | Status |
|---|---|
| Part 1 — Core Need & Positioning | ✅ Complete |
| Part 2 — Context & Data Layer | ✅ Complete |
| Part 3 — Tools & Permissions | ✅ Complete |
| GBrain content exists | ✅ Partial — BL content needs filling |
| Hindsight banks created | ✅ `dx-pipeline`, `dx-human-hunter`, `dx-human-kevin` |
| SOUL.md written | ✅ `/mnt/disks/data/hermes/SOUL.md` |
| Core skills built | ✅ |
| Nightly crons active | ✅ |
