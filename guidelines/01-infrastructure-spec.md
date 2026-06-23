# Infrastructure Spec

> Audience: humans.
> Purpose: describe the core infrastructure that must exist after base Hermes is installed and before role-owning AI colleagues are activated.

---

## 1. Architecture Principle

A Hermes-native AI colleague is a role-owning teammate, not a generic tool.

Each colleague needs:

- identity: what responsibility it owns
- context: what it knows, remembers, retrieves, and treats as truth
- capability: skills, tools, workflows, and integrations
- authority: what it can decide or change
- autonomy: routines it may run without being asked
- evaluation: how work quality is checked
- governance: logging, approvals, review, and change control

The infrastructure should make those layers concrete.

---

## 2. Runtime Unit: Hermes Profile

For role-owning colleagues, one Hermes profile usually equals one AI colleague.

A profile owns or controls:

- runtime identity
- short `SOUL.md`
- profile config
- profile-local environment variables
- skills
- cron jobs
- memory provider configuration
- sessions and runtime state
- tool and MCP configuration

Do not simulate multiple durable colleagues inside one profile.

Expected profile shape:

```text
~/.hermes/profiles/{{profile_name}}/
  SOUL.md
  config.yaml
  .env              # never committed
  skills/
  cron/
```

`SOUL.md` should stay short. It should carry core identity, mission, top-level behavior principles, highest-priority authority boundaries, context priority rules, and escalation principles. Full operating detail belongs in workspace docs and skills.

---

## 3. Agent Workspace

Each AI colleague should have a role-specific workspace separate from the Hermes profile and separate from GBrain.

Recommended path:

```text
/srv/ai-colleagues/workspaces/{{profile_name}}/
```

Expected workspace files:

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

Workspace is for current work, drafts, queues, and role-local operating context. It is not canonical company truth and not the source of operational state.

---

## 4. Context Infrastructure

The Context Layer has five responsibilities.

| Layer | Runtime system | Purpose |
|---|---|---|
| GBrain canonical | GBrain | approved, durable, reviewable company truth |
| GBrain evidence | GBrain | traceable source material, evidence pages, imports, transcripts, meeting notes |
| Hindsight | Hindsight | experiential memory, corrections, recent signals, learned patterns |
| Structured operational state | CRM, Plane, approvals, logs, other systems of record | owners, status, deadlines, stages, approval state, workflow state |
| Agent workspace | filesystem/workspace docs | drafts, queues, notes, role-local operating material |

Do not collapse all context into Hindsight, GBrain, or workspace.

### Source priority

When sources conflict, use this priority order:

1. human explicit instruction in the current session
2. approved structured state or approval system
3. GBrain canonical knowledge
4. GBrain evidence when the question is about what happened or why
5. workspace context for current in-progress work
6. Hindsight recent memory and observations
7. agent inference

---

## 5. GBrain

GBrain is the shared company-brain layer.

It should contain both:

- canonical knowledge: approved durable truth
- evidence zones: source material and evidence trails

These must remain distinct.

Recommended V1 sources:

```text
shared
customers
partners
product-eng
internal
```

Use sources as access-control and write-authority boundaries, not as the whole taxonomy.

Rules:

- each AI colleague should usually have one home write source
- cross-source canonical writes should go through review or publisher flow
- canonical pages should include owner, status, review date, and source references
- evidence pages should support claims but should not silently become policy
- large transcripts and imports should use the appropriate non-repo storage tier where available

---

## 6. Hindsight

Hindsight is the hot semantic memory layer for what happened, what the team is learning, and what may matter later.

Recommended V1:

- one personal Hindsight bank per role-owning profile
- a small number of shared/domain banks
- tags for business slicing before creating many more banks
- profile memory mode: `hybrid`
- auto-recall enabled
- auto-retain enabled for the personal bank unless the agent design says otherwise
- governed write rules for shared/domain banks

Hindsight must not be the only source for operational state, approval state, official policy, or approved external claims.

---

## 7. Structured Systems of Record

Structured data owns mutable operational truth.

Examples:

- CRM account, contact, lead, and deal state
- Plane or task-board work items
- approval state
- workflow stage
- deadline
- owner
- amount
- routine run logs
- tool action logs
- evaluation results

Dangerous writes should go through an action gateway where possible. The gateway should handle permission checks, approval checks, idempotency, risk classification, audit trail, and escalation.

---

## 8. Tools and Credentials

Each AI colleague should have scoped tool access based on role and authority.

Rules:

- do not commit secrets
- do not invent credentials
- credentials should be provided through the target team's approved secret process
- dangerous write tools should be gated
- tool actions should be logged
- read access and write access should be configured separately where possible

---

## 9. Package Installation Boundary

This repository assumes base Hermes already exists.

This package should install or guide installation of:

- core workspace conventions
- GBrain/Hindsight/context routing assumptions
- shared skills and templates
- selected AI colleague profiles and artifacts
- authority, memory, tool, routine, evaluation, and governance docs
- verification and activation checklists

This package should not silently perform:

- host provisioning
- credential issuance
- irreversible external actions
- production activation without verification

---

## 10. Activation Criteria

Before a colleague is marked active:

- Hermes profile exists and starts
- workspace exists with required operating docs
- context priority rules are documented
- GBrain read/write scope is known
- Hindsight personal bank is configured and tested
- structured system access is tested or marked missing
- authority policy exists
- dangerous writes require approval or gateway
- routine logs and tool action logs exist
- evaluation policy exists
- human owner has reviewed unresolved gaps