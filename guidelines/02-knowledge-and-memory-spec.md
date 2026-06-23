# Context Layer and Memory Spec

> Audience: humans designing or evaluating an AI colleague deployment.
> Purpose: define how AI colleagues use GBrain, Hindsight, structured systems, and workspace context without mixing their responsibilities.

---

## 1. Core Rule

Do not collapse all context into one memory system.

A Hermes-native AI colleague uses five context responsibilities:

| Responsibility | System | What it answers |
|---|---|---|
| Canonical knowledge | GBrain canonical | What has the company approved as durable truth? |
| Evidence and source material | GBrain evidence | What source material supports or explains a claim? |
| Experiential memory | Hindsight | What happened recently, what patterns are emerging, what did the agent learn? |
| Operational state | structured systems | What is the current owner, stage, status, deadline, approval, or workflow state? |
| Current work | agent workspace | What is the agent drafting, reviewing, queueing, or operating on now? |

Each layer has a different job. The package must preserve those boundaries.

---

## 2. Source Priority

When context sources conflict, agents should use this priority order:

1. human explicit instruction in the current session
2. approved structured state or approval system
3. GBrain canonical knowledge
4. GBrain evidence when the question is about what happened or why
5. workspace context for current in-progress work
6. Hindsight recent memory and observations
7. agent inference

Rules:

- Hindsight may inform judgment but must not override GBrain canonical or structured state.
- Workspace can guide current work but must not become canonical truth.
- Evidence can challenge canonical knowledge, but that should trigger review instead of silent override.
- Agent inference is always the weakest source.

---

## 3. GBrain Canonical

GBrain canonical stores approved, durable, reviewable knowledge.

Use it for:

- policies
- playbooks
- business-line strategy
- ICP definitions
- messaging
- product principles
- technical decisions
- decision records
- approved customer, partner, or market patterns

Do not use it for:

- private scratch notes
- raw conversation dumps
- mutable task state
- unreviewed assumptions
- approval state

Recommended frontmatter:

```yaml
---
type: {{page_type}}
business_line: {{business_line}}
knowledge_state: canonical
approval_status: approved
owner: {{owner}}
reviewers: [{{reviewer}}]
effective_date: {{YYYY-MM-DD}}
last_reviewed_at: {{YYYY-MM-DD}}
source_refs:
  - {{source_ref}}
confidence: high
---
```

---

## 4. GBrain Evidence

GBrain evidence stores traceable source material and evidence pages.

Use it for:

- meeting notes
- call notes
- transcripts
- source imports
- email evidence
- raw research notes
- evidence pages tied to a subject page

Rules:

- Keep evidence pages distinct from canonical pages.
- Organize evidence by primary subject when possible.
- Use raw `sources/` zones for raw dumps and imports.
- Large generated transcripts or imports should use a non-repo storage tier where available.
- Evidence supports claims; it does not automatically become truth.

Recommended evidence metadata:

```yaml
---
type: evidence_note
knowledge_state: evidence
source_system: {{source_system}}
source_date: {{YYYY-MM-DD}}
related_subjects:
  - {{gbrain_subject_path}}
owner: {{owner}}
retention: {{policy}}
---
```

---

## 5. GBrain Source Topology

Recommended V1 sources:

```text
shared
customers
partners
product-eng
internal
```

Use sources for access control and write authority.

Suggested folder shape:

```text
shared/
  business-lines/
  policies/
  concepts/
  people/
  companies/
customers/
  customer-pages/
  companies/
  people/
  meetings/
  product-feedback/
  objection-patterns/
  sources/
partners/
  partner-pages/
  companies/
  people/
  meetings/
  partner-feedback/
  sources/
product-eng/
  projects/
  tech-decisions/
  meetings/
  postmortems/
  sources/
internal/
  strategy/
  finance/
  legal/
  people-ops/
```

Each AI colleague should usually have one home write source. Cross-source canonical writes should go through review or publisher flow.

---

## 6. Hindsight

Hindsight is the hot semantic memory layer.

Use it for:

- recent interactions
- customer or partner signals
- corrections
- learned patterns
- emerging opportunities
- campaign or workflow learnings
- agent behavior notes
- promotion candidates

Do not use it as the only source for:

- task status
- approval state
- CRM stage
- official policy
- canonical product claims
- financial amounts
- audit logs

Recommended V1 bank model:

| Bank type | Purpose | Write rule |
|---|---|---|
| personal agent bank | profile-local experiential memory | auto-retain by default |
| shared/domain bank | cross-agent patterns or domain observations | governed write or proposal flow |
| human/context bank, if used | human preferences or relationship context | explicit governance and privacy rules |

Recommended memory mode for role-owning profiles:

```text
memory_mode = hybrid
auto_recall = enabled
auto_retain = enabled for personal bank
```

Shared banks should not become raw transcript dumps. Important shared memories should keep evidence references.

---

## 7. Memory Object Types

Recommended V1 memory object types:

1. `interaction_memory`
2. `customer_signal`
3. `team_decision`
4. `correction`
5. `experience_learning`
6. `research_note`
7. `product_opportunity_signal`
8. `campaign_learning`
9. `agent_behavior_note`
10. `promotion_candidate`

Recommended metadata:

```yaml
memory_type: {{memory_type}}
business_line: {{business_line}}
source: {{source}}
source_date: {{YYYY-MM-DD}}
created_by: {{agent_or_human}}
confidence: low | medium | high
status: active | stale | promoted | invalidated
visibility: personal | shared | restricted
related_gbrain_docs:
  - {{path_or_slug}}
related_structured_records:
  - {{record_ref}}
tags:
  - biz:{{business_line}}
  - domain:{{domain}}
promotion_candidate: true | false
ttl: {{optional_expiry}}
```

---

## 8. Structured Operational State

Structured data is the source of truth for operational state.

Examples:

- account owner
- deal stage
- task status
- issue status
- approval state
- deadline
- amount
- workflow state
- routine run history
- tool action logs
- evaluation results

Rule: if the information needs reliable querying, auditability, ownership, workflow state, or approval state, it belongs in a structured system, not only in Hindsight or workspace notes.

---

## 9. Agent Workspace Context

Workspace stores current work and role-local operating material.

Use it for:

- `AGENTS.md`
- role context
- authority policy
- memory policy
- tool policy
- routine policy
- evaluation policy
- drafts
- notes
- scratch material
- review queues

Workspace should not replace GBrain canonical knowledge, Hindsight memory, or structured systems of record.

---

## 10. Read Router Rules

Use these defaults:

| Question type | First source |
|---|---|
| current owner, status, deadline, approval, workflow state | structured system |
| approved policy, playbook, claim, decision | GBrain canonical |
| what happened, why a claim exists, source trail | GBrain evidence, then Hindsight |
| recent interaction pattern or learned experience | Hindsight |
| current draft, queue, local operating note | workspace |
| missing or conflicting information | escalate or create review item |

---

## 11. Write Router Rules

Use these defaults:

| Claim or artifact type | Destination |
|---|---|
| operational state | structured system of record |
| raw evidence | GBrain evidence zone |
| recent experience | Hindsight personal bank |
| shared learned pattern | governed shared/domain Hindsight bank |
| canonical candidate | workspace review queue or GBrain proposal flow |
| approved canonical knowledge | GBrain canonical |
| draft context | workspace |
| tool action or routine result | structured log |

---

## 12. Promotion Workflow

Default promotion path:

```text
Raw Signal
  -> Memory Capture / Evidence Capture
  -> Shared Insight Candidate
  -> Governed Review
  -> Canonical Knowledge
```

When a memory becomes canonical, link the Hindsight memory to the GBrain document and mark the memory as promoted.

Do not let unreviewed memory silently become canonical truth.

---

## 13. Setup Checklist

For each deployment, confirm:

- [ ] GBrain sources are defined
- [ ] canonical and evidence zones are separated
- [ ] schema/page types are documented
- [ ] each role-owning profile has a personal Hindsight bank
- [ ] shared/domain banks have write rules
- [ ] structured systems of record are identified
- [ ] workspace root and per-agent workspace convention exist
- [ ] read-router rules are documented
- [ ] write-router rules are documented
- [ ] promotion workflow exists
- [ ] authority and approval rules exist for writes and publishing
- [ ] logs exist for routine runs, tool actions, and evaluations