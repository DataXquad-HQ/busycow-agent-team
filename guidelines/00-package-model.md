# Package Model

> Audience: humans designing or evaluating this repository.
> Purpose: define what this package is, what it is not, and how another team should apply it after base Hermes exists.

---

## 1. What This Package Is

This repository is a reusable distribution package for Hermes-native AI colleagues.

It should help another team move from a base Hermes install to a working AI colleague system by providing:

- human-readable architecture and design guidance
- agent-readable install and verification playbooks
- installable runtime artifacts for Hermes profiles, workspaces, skills, memory policy, schemas, and templates

This package should not be treated as a prompt library. A real AI colleague needs an operating architecture, not just instructions.

---

## 2. The Three Runtime Phases

### Phase 0: Human bootstrap

Owned by the human/operator.

Expected result:

- VM or host exists
- base Hermes is installed
- Default Hermes can run
- repository access exists
- secrets and approval ownership are known

This repository may document this phase, but it should not assume it can fully automate host creation or credential issuance.

### Phase 1: Core AI colleague infrastructure

Owned by Default Hermes with human approval where required.

Expected result:

- Hermes runtime sanity checks pass
- workspace root exists
- GBrain source topology is configured or explicitly marked missing
- Hindsight memory provider and bank conventions are configured or explicitly marked missing
- structured systems of record are identified
- approval and audit assumptions are documented
- integration playbooks have been run or marked out of scope

### Phase 2: AI colleague installation

Owned by Default Hermes using this repository's artifacts.

Expected result for each role-owning colleague:

- one Hermes profile
- one short `SOUL.md`
- one agent workspace
- workspace `AGENTS.md`
- role context, authority, memory, tool, routine, and evaluation docs
- required skills copied or installed
- memory provider configured
- credentials provided through approved channels
- activation checklist completed

---

## 3. Repository Contract

| Layer | Audience | Contract |
|---|---|---|
| `guidelines/` | humans | explain why the system works this way |
| `playbooks/` | Hermes agents | state exact steps, checks, and stop conditions |
| `artifacts/` | installers and agents | provide files that can be copied, adapted, or installed |

A file belongs in `guidelines/` when it explains architecture or design rationale.
A file belongs in `playbooks/` when it tells Default Hermes what to do in order.
A file belongs in `artifacts/` when it is intended to become part of a live system.

---

## 4. AI Colleague Design Stack

Every role-owning colleague should be designed through these layers:

1. Identity Layer: who the colleague is and what responsibility it owns
2. Context Layer: what it knows, remembers, retrieves, treats as truth, and uses as working context
3. Capability Layer: what tasks, skills, tools, and workflows it can perform
4. Authority Layer: what it may decide, propose, write, publish, or escalate
5. Autonomy Layer: what routines it may run without being asked
6. Evaluation Layer: how its work is checked
7. Governance Layer: how logs, approvals, review, and change management work

The package should make these layers concrete. A profile with a long prompt but no context routing, authority, evaluation, or governance is not a finished AI colleague.

---

## 5. Context Layer Contract

Use this default model unless a target team explicitly overrides it.

| Context responsibility | Source | Rule |
|---|---|---|
| Canonical knowledge | GBrain canonical | approved, durable, reviewable truth |
| Evidence and source material | GBrain evidence | traceable support for claims and history |
| Experiential memory | Hindsight | recent interactions, corrections, learned patterns, emerging signals |
| Operational state | structured systems | CRM, Plane, approvals, stages, owners, deadlines, logs |
| Current work | agent workspace | drafts, queues, notes, local runbooks, working docs |

Do not collapse these into one memory system.

When sources conflict, use this priority order:

1. human explicit instruction in the current session
2. approved structured state or approval system
3. GBrain canonical knowledge
4. GBrain evidence when the question is about what happened or why
5. workspace context for current in-progress work
6. Hindsight recent memory and observations
7. agent inference

Hindsight may inform judgment, but it must not override GBrain canonical knowledge or structured operational state.

---

## 6. Package Completeness Criteria

The package is ready for a new target team when it contains:

- clear human architecture docs
- Default Hermes setup playbooks
- core infrastructure verification checklist
- at least one complete agent artifact example
- shared skill artifacts or references
- memory policy templates
- authority and tool policy templates
- evaluation policy templates
- structured data schema expectations
- activation and stop conditions

If an item is missing, the package can still be useful, but Default Hermes should report the gap rather than claim the installation is production-ready.