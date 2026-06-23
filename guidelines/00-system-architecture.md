# System Architecture

> Audience: humans evaluating or extending this package.
> Purpose: define the outer architecture of the Hermes AI colleague system before looking at install playbooks or runtime artifacts.

---

## 1. What This Package Installs

This package installs the operating structure around AI colleagues.

A complete deployment has four infrastructure layers:

1. **Contextual Layer**: the systems that hold knowledge, evidence, memory, operational state, and current work context.
2. **AI Colleague Agent Layer**: the Hermes profiles that define and run each role-owning AI colleague.
3. **Workspace & Collaboration Layer**: the human-agent work environment, currently Lark/Feishu-first.
4. **Operations & Governance Layer**: the playbooks, policies, approvals, logs, evaluation, and activation rules that make the system safe to operate.

These layers work together, but each owns a different responsibility.

---

## 2. Contextual Layer

The Contextual Layer defines what an AI colleague knows, remembers, retrieves, treats as truth, and writes back into the company system.

It has five sublayers:

| Sublayer | System | Owns |
|---|---|---|
| GBrain canonical | GBrain | approved, durable, reviewable company truth |
| GBrain evidence | GBrain | source material, evidence pages, meeting notes, transcripts, imports |
| Hindsight | Hindsight | experiential memory, recent interactions, corrections, learned patterns |
| Structured operational state | CRM, Plane, approvals, logs, other systems of record | owners, stages, tasks, deadlines, approval state, workflow state |
| Agent workspace context | filesystem/workspace docs | drafts, queues, role-local notes, current working material |

The rule is simple: put context where it can be trusted and governed correctly.

---

## 3. AI Colleague Agent Layer

The Agent Layer is built on Hermes.

For durable role-owning AI colleagues, the default is:

```text
one AI colleague = one Hermes profile
```

Each profile should have:

```text
~/.hermes/profiles/{{profile_name}}/
  SOUL.md
  config.yaml
  .env              # never committed
  skills/
  cron/
```

The profile is the runtime container. It is not the whole colleague design.

A complete AI colleague also needs workspace docs, context routing, authority policy, memory policy, evaluation, governance, and installed skills.

---

## 4. Workspace & Collaboration Layer

The Workspace & Collaboration Layer is where humans and AI colleagues interact and where the colleague's current work can be inspected.

For V1, this package is **Lark/Feishu-first**.

The workspace layer includes:

- Lark/Feishu messaging and delivery channels
- human-facing reports and approvals
- shared collaboration spaces
- agent workspaces on disk
- review queues and draft areas

Slack is a valid future workspace target, but it is not part of this V1 install until Slack-specific artifacts, credentials, playbooks, and verification checks exist.

Recommended agent workspace path:

```text
/srv/ai-colleagues/workspaces/{{profile_name}}/
```

Recommended workspace files:

```text
AGENTS.md
role-context.md
authority.md
tool-policy.md
memory-policy.md
routines.md
evaluation-policy.md
operating-notes.md
drafts/
notes/
scratch/
review-queues/
```

---

## 5. Operations & Governance Layer

The Operations & Governance Layer keeps the system installable, auditable, and safe.

It includes:

- setup and migration playbooks
- authority rules
- approval rules
- tool policies
- routine policies
- evaluation policies
- routine run logs
- tool action logs
- approval logs
- activation checklists
- stop conditions

Where possible, dangerous or external write actions should route through an action gateway that handles permission checks, approval checks, risk classification, idempotency, logging, audit trail, and escalation.

---

## 6. Human and Agent Views

This repository must serve two views.

| View | Reads | Purpose |
|---|---|---|
| Human architecture view | `guidelines/` | understand the system, catalog, design model, and current agents |
| Default Hermes install view | `playbooks/` and `artifacts/` | install core infrastructure and selected AI colleagues |

The same repository should be useful in a demo and useful during a real installation.

---

## 7. Source Priority

When context sources conflict, AI colleagues should use this priority order:

1. explicit human instruction in the current session
2. approved structured state or approval system
3. GBrain canonical knowledge
4. GBrain evidence when the question is about what happened or why
5. workspace context for current in-progress work
6. Hindsight recent memory and observations
7. agent inference

Hindsight is useful memory, not canonical truth. Structured systems own operational state. GBrain canonical owns approved knowledge.