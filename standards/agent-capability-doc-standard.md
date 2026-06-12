# Agent Capability Document Standard
**Version: 1.0 | Status: Canonical**

This is the standard structure for every agent CAPABILITIES.md in the DataXquad agent team.
All new agents follow this format. Existing docs migrate to this format on next revision.

---

## Core Design Principles (Read Before Writing)

### Capability ≠ Feature List
A Capability is not a list of things an agent can do. It is the answer to one question:

> **"Does the [human] still need to watch this themselves?"**

If the human still needs to watch it, the Capability is not done. Every Capability exists to buy back human attention — nothing else.

### Authority Has Three Levels Only
| Symbol | Level | Meaning |
|---|---|---|
| ✅ | Autonomous | Agent decides and executes — human not involved |
| ⚠️ | Confirmation | Agent prepares — human confirms before execution |
| 🚫 | Human Decision | Human decides — agent does not intervene |

No other levels. No "partially autonomous". No ambiguity.

### Cron = Trigger Only. Logic Lives in Skill.
A cron job is a single trigger line. All logic lives in the corresponding Skill.
Any Capability can be invoked manually at any time with identical behaviour.
If the logic is in the cron prompt, it's in the wrong place.

### Three-Layer Context Separation
Structural, Contextual, and Memory are always separated. Never mix them.
- **Structural** = data schema (CRM objects, field definitions)
- **Contextual** = judgment knowledge (sales principles, product context, pipeline definitions)
- **Memory** = live state (CRM) + narrative (GBrain) + learning (Hindsight, pending)

---

## Document Structure

---

### S1 — Identity & Pipeline

**Contents:**
1. **Role & Position** — Agent's role, position in the team, reporting line
2. **Existence Value** — One `-ing` gerund phrase describing why this agent exists
   - Format: `"[Verb]-ing every [object] from [start state] to [end outcome]"`
   - Example: `"Moving every lead from first contact to closed outcome"`
   - Must be a single sentence. No hedging. No lists.
3. **Pipeline Diagram** — Where this agent sits in the full business process
   - Show upstream inputs (what feeds this agent) and downstream outputs (what this agent feeds)
   - Use ASCII or Mermaid. No external image dependencies.
4. **Capabilities at a Glance** — One-line summary table of all Capabilities

```markdown
## Capabilities at a Glance

| # | Capability | One-Line Summary |
|---|---|---|
| C1 | [Name] | [What it buys back — one sentence] |
| C2 | [Name] | [What it buys back — one sentence] |
```

---

### S2 — Context

**Contents:**

#### Structural Data
The data structures the agent operates on. Not what the agent knows — what the agent reads and writes.

| Object | Fields Used | Read / Write | Source |
|---|---|---|---|
| [CRM object] | [field list] | R / W / RW | [system] |

Include field definitions if non-obvious. This section should be enough for a developer to understand the agent's data footprint.

#### Contextual Data
The knowledge sources the agent uses to make judgments. Not live data — principles, definitions, product context.

| Knowledge Source | What It Contains | Location |
|---|---|---|
| [name] | [what judgment it enables] | GitHub / GBrain / Lark |

Pipeline definitions, ICP definitions, sales principles, pricing logic — all go here.
Canonical location: `busycow-playbooks/` or `dataxquad-core/` on GitHub.

#### Memory Layer

| Layer | What It Stores | System | Status |
|---|---|---|---|
| Live State | Current records, status, recent activity | CRM (Twenty) | ✅ Active |
| Narrative Memory | Relationship history, decision context, deal narratives | GBrain | ✅ Active |
| Learning Layer | Pattern recognition from past outcomes, hindsight loops | Hindsight | ⏳ Pending |

---

### S3 — Utilities

#### Tools

| Tool | Purpose | Used By |
|---|---|---|
| [tool name] | [what it does for this agent] | [C1, C2, ...] |

#### Setup
Endpoints, credentials, paths, environment variables. Enough for another engineer to wire this agent from scratch.

```
CRM endpoint: http://localhost:3001
GBrain: ~/gbrain/
Lark: lark-mcp (see lark-mcp-setup skill)
```

#### Cron Jobs

| Job Name | Schedule | Capability | Skill | Description |
|---|---|---|---|---|
| [job-name] | [cron or frequency] | [C#] | [skill-name] | [one line — trigger only, no logic] |

---

### S4 — Capabilities

One section per Capability. Strict format for every Capability — no exceptions.

---

#### C[N] — [Capability Name in -ing gerund form]

Examples of correct naming:
- ✅ `Generating Leads` / `Progressing Opportunities` / `Monitoring Partner Health`
- ❌ `Lead Generation` / `Opportunity Management` / `Partner Health`

```
> [Agent] is responsible for [X] — so [human role] never has to [Y].
```

**Outcome**
What "done" looks like. One sentence. Measurable or verifiable.
> When this Capability is healthy: [specific observable state].

**What [Agent] Owns**
Specific processes and decisions this agent owns. Bullet list.
- [process 1]
- [process 2]
- [decision this agent makes without asking]

**Trigger & Cadence**
| Trigger | Cadence | Notes |
|---|---|---|
| [what fires this] | [how often] | [any conditions] |

**Authority**
| Action | Authority | Notes |
|---|---|---|
| [specific action] | ✅ / ⚠️ / 🚫 | [boundary or condition] |

**Skills & Crons**
- **Skills** *(building blocks):* `skill-name` · `skill-name`
- **Cron:** → `job-name` — [schedule], [one-line description]

**Status**
| Trigger | Execution | Quality |
|---|---|---|
| ✅ / ⚠️ / ❌ + reason | ✅ / ⚠️ / ❌ + reason | ✅ / ⚠️ / ❌ + reason |

Status key:
- ✅ = fully operational
- ⚠️ = partial / pending build
- ❌ = not yet built

---

### S5 — Design Principles

#### Pipeline Definitions
Define the status lifecycle for every object this agent manages.

| Status | Definition | Health Check |
|---|---|---|
| [status name] | [what it means exactly] | [how to verify it's correct] |

#### Alert Thresholds
| Signal | Threshold | Action |
|---|---|---|
| [silence / inactivity / decline] | [N days / % drop] | [what agent does] |

#### Principles
One principle per paragraph. Name in `-ing` gerund form.

**[Principle Name in -ing form]**
[One paragraph explaining why this principle exists and what it prevents. Not a rule list — a reasoned explanation.]

---

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Capability name | `-ing` gerund | `Progressing Deals`, `Monitoring Health` |
| Existence value | `-ing` gerund phrase | `"Moving every lead from first contact to closed outcome"` |
| Design Principle name | `-ing` gerund | `Owning the Blocker, Not Just the Triage` |
| Skill name | `kebab-case` gerund | `managing-partnership-pipeline` |
| Cron job name | `kebab-case` descriptive | `partner-health-weekly` |

---

## Migration Notes

Existing CAPABILITIES docs (Iris, Maya, Leo, Vera) were written before this standard.
Migrate on next major revision. Priority order: Leo → Maya → Vera → Iris.

Key gaps in current docs vs this standard:
- S1 pipeline diagram missing in all docs
- S2 structural data table missing
- S3 utilities / setup section missing
- Capability names not consistently in `-ing` gerund form
- S5 pipeline definitions and alert thresholds missing
