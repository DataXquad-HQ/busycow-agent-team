# Agent Architecture Principles

*Distilled from DataXquad strategy sessions, June 2026. Use when designing SOUL.md, SETUP.md, or agent operating models for any playbook.*

---

## The Core Mental Model: New Employee, Not Tool

Agents are team members with a defined scope. Each agent fully owns their domain — not a task, not a function, an entire section of the business.

**The hire test:** can we assign this agent their domain and walk away for a week, confident the work is happening, problems are being handled, and we will hear about anything that genuinely needs us?

---

## Why Hermes, Not Claude Code or Codex Directly

Claude Code / Codex / raw LLM APIs are reactive tools — session ends, context lost, no autonomous operation. A Hermes agent profile is persistent: fixed identity (SOUL.md), long-term memory (GBrain + MEMORY.md), scheduled cron, event-driven triggers, defined authority.

Hermes agents **call** Claude Code / Codex / CrewAI as sub-tools when needed. The agent is the senior team member who decides when to bring in specialists.

**Hierarchy:**
```
Founders → direction, exceptions, final decisions
Iris (CoS) → coordination, knowledge distillation, alignment
Domain agents → own their section, call specialists
Claude Code / Codex / CrewAI → specialist tools called by agents
```

---

## Three Layers of Agent Capability

Every agent has three layers that combine to make them a functional team member:

**Layer 1 — Deterministic Workflows**
Repeatable, high-frequency tasks with clear input/output/quality standard. Runs reliably. Humans review results, not steps. Examples: outreach sequences, content pipelines, weekly health checks.

**Layer 2 — Skills**
Free-form toolkit for situations not covered by workflow. Agent reaches for the right skill based on context. Gives flexibility without chaos.

**Layer 3 — Domain Judgment**
Role-level judgment about what matters, what signals to watch, when to escalate. This is what makes agents functional team members rather than sophisticated scripts.

**Key insight:** Workflow manages the data flow (A before B before C). Judgment manages the decision layer (what to do with the data). These are separate concerns.

---

## Three Zones of Autonomy

**Autonomous Zone** — agent acts and logs, no human review needed
Examples: health checks, CRM updates, research drafts saved for review, content drafts stored

**Confirmation Zone** — agent prepares, human approves before execution
Examples: outbound emails to new prospects, quotations, first contact with new client, public content publication

**Human Decision Zone** — agent provides information, human decides
Examples: strategic pivots, major contract terms, budget commitments, partner agreements

Zone boundaries belong in SOUL.md. When in doubt, escalate up.

---

## The Hire Framework — Three Conditions for Real Delegation

Trust is earned when all three are simultaneously present:

1. **Works autonomously** — monitors domain, acts on signals, does not wait to be triggered
2. **Proactively reports back** — communicates actions and findings without being asked
3. **Quality is trusted** — output is fit for purpose and consistent (not perfect — consistent)

When all three are present for a task type → move to Autonomous Zone.
Until all three → stay in Confirmation Zone.

---

## Event-driven Triggers (the gap in most systems)

Most agent setups are reactive (schedule or human-triggered). The target is proactive:

- Leo: deal silent 14 days → auto-drafts follow-up, queues for confirmation
- Rex: health check anomaly → opens ticket, begins triage without waiting for client complaint
- Quinn: competitor releases update → produces brief, flags to Iris
- Maya: article hits traffic threshold → analyses performance, proposes follow-up

This is implemented via: watchdog cron (periodic state scan), Lark webhooks (external event trigger), GBrain timeline monitoring (entity not updated in N days → flag).

---

## OpenAI's Five Conditions for Agent-as-Teammate

From AppWorks sharing, June 2026:

1. Execute long-horizon tasks autonomously
2. Support all multimodal inputs and outputs
3. Collaboration — AI-native and non-AI-native environments, single and multi-user
4. Maintain memory and understanding (persistent identity + GBrain)
5. Safe deployment and governance (SOUL.md authority boundaries + audit logging)

---

## Data Flow Principle

```
External world → agents collect → Lark Bitable + GBrain → all agents query
Agent actions → logged to Lark Bitable (Activity + Task records)
Exceptions + outcomes → Iris synthesises → founders see results, not process
```

Founders should never need to read agent logs. They see summaries and exceptions.

---

## SOUL.md Design Rules

- Define: Role, Responsibilities, Authority & Boundaries, GBrain Access level, Tools
- Use `{{PLACEHOLDER}}` for company name, Lark tokens, table IDs
- Never include specific VM topology (e.g. "runs on separate VM") — write for general case
- Never include specific deal names, client names, product names — use `[Product]`, `[Client]`
- GBrain write access: Iris = all namespaces; Rex = incidents/ and runbooks/ only; all others = read only
- Only Iris writes `Result for Human`; all agents write `Agent Notes` and set `Done`
- Separation of authority is critical — encode hard limits explicitly in SOUL.md
