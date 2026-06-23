# AI Colleague Design Spec Template

> Purpose: design a Hermes-native AI colleague as an operating teammate before implementation.
> Copy this file, rename it to `{{agent-name}}-design-spec.md`, and complete the sections before building the profile.

A completed spec should answer:

- Who is this colleague?
- What responsibility does it own?
- What context does it need?
- What can it do?
- What is it allowed to do?
- What does it do autonomously?
- How is its work evaluated?
- How is it governed?

Do not start by writing a prompt. Start by designing the operating architecture.

---

## 0. Document Metadata

| Field | Value |
|---|---|
| Agent name | {{Agent Name}} |
| Role | {{Role}} |
| Human owner | {{Human Owner}} |
| Design owner | {{Design Owner}} |
| Status | Draft / Review / Approved / Deprecated |
| Version | v0.1 |
| Last updated | {{YYYY-MM-DD}} |
| Target runtime | Hermes Agent |
| Target profile name | {{profile_name}} |
| Primary business line | {{business_line}} |
| Primary systems of record | {{systems_of_record}} |
| Primary home write source | {{home_write_source}} |

---

## 1. Identity Layer

### Mission

```text
{{Mission statement}}
```

### Role Definition

```text
{{Agent Name}} is the {{Role}}. This AI colleague owns {{responsibility area}} within approved boundaries.
```

### Responsibilities

- {{Responsibility 1}}
- {{Responsibility 2}}
- {{Responsibility 3}}

### Non-Responsibilities

- {{Boundary 1}}
- {{Boundary 2}}
- {{Boundary 3}}

### Success Metrics

| Metric | Definition | Source | Review cadence |
|---|---|---|---|
| {{Metric}} | {{Definition}} | {{Data source}} | Daily / Weekly / Monthly |

### Human Relationships

| Relationship | Person / Role | Notes |
|---|---|---|
| Human owner | {{Name}} | Owns direction and final accountability |
| Approval owner | {{Name or role}} | Approves high-risk actions |
| Reviewer | {{Name or reviewer agent}} | Reviews output quality and risk |
| Collaborators | {{Names or roles}} | Works with the colleague regularly |

---

## 2. Context Layer

### Context Layer Summary

| Layer | What this colleague uses it for | Required sources |
|---|---|---|
| GBrain canonical | approved truth, policies, playbooks, decisions | {{sources}} |
| GBrain evidence | source material, meeting notes, evidence pages | {{sources}} |
| Hindsight personal bank | personal experience, corrections, learned patterns | {{bank_id}} |
| Hindsight shared/domain banks | shared patterns, customer voice, product feedback | {{bank_ids}} |
| Structured systems | owners, stages, approvals, tasks, logs | {{systems}} |
| Workspace | drafts, queues, local operating docs | {{workspace_path}} |

### Source Priority

Use this priority order unless a higher-level policy says otherwise:

1. current human instruction
2. approved structured state or approval system
3. GBrain canonical
4. GBrain evidence
5. workspace current-work context
6. Hindsight memory
7. agent inference

### Required Canonical Knowledge

| GBrain path or source | Purpose | Status |
|---|---|---|
| {{path}} | {{purpose}} | Missing / Draft / Approved |

### Required Evidence Zones

| Evidence zone | Typical material | Status |
|---|---|---|
| {{zone}} | {{material}} | Missing / Active |

### Hindsight Banks

| Bank | Access | Write mode | Purpose |
|---|---|---|---|
| {{personal_bank}} | Read/write | Auto-retain personal | profile-local experience |
| {{shared_bank}} | Read / governed write | Propose / governed direct | shared domain learning |

### Structured Systems of Record

| System | Authoritative for | Access | Write rule |
|---|---|---|---|
| {{CRM}} | {{state}} | Read / Write / Propose | {{rule}} |
| {{Plane}} | {{state}} | Read / Write / Propose | {{rule}} |
| {{Approvals}} | approval state | Read / Propose | write through gateway |

---

## 3. Capability Layer

### Capabilities

| Capability | What it means in plain English | Skills | Priority |
|---|---|---|---|
| {{Capability}} | {{Description}} | {{skills}} | Must-have / Later |

### Skills

| Skill | Trigger | Output | Source artifact |
|---|---|---|---|
| {{skill-name}} | {{when used}} | {{result}} | `artifacts/...` |

### Tools and Integrations

| Tool | Purpose | Access class | Credential needed | Gateway? |
|---|---|---|---|---|
| {{tool}} | {{purpose}} | Read / Write / Dangerous | {{env var or secret ref}} | Yes / No |

---

## 4. Authority Layer

### Allowed Without Approval

- {{allowed action}}
- {{allowed action}}

### Requires Human Approval

- {{approval action}}
- {{approval action}}

### Never Allowed

- {{forbidden action}}
- {{forbidden action}}

### External Write Policy

| Action | Risk | Approval rule | Log destination |
|---|---|---|---|
| {{action}} | Low / Medium / High | {{rule}} | {{log}} |

---

## 5. Autonomy Layer

### Autonomous Routines

| Routine | Schedule | Purpose | Output | Stop condition |
|---|---|---|---|---|
| {{routine}} | {{schedule}} | {{purpose}} | {{output}} | {{condition}} |

Rules:

- Start with minimal cron jobs.
- Do not run external write routines unless authority and approval rules are defined.
- Routine output should be logged.

---

## 6. Evaluation Layer

### Quality Criteria

| Work product | Evaluation criteria | Reviewer | Cadence |
|---|---|---|---|
| {{output}} | {{criteria}} | Human / evaluator agent | {{cadence}} |

### Required Tests Before Activation

- [ ] context retrieval test
- [ ] authority boundary test
- [ ] tool access test
- [ ] memory write/read test
- [ ] routine dry run, if routines exist
- [ ] human review of unresolved gaps

---

## 7. Governance Layer

### Logging and Audit

| Log | What it records | Required? |
|---|---|---|
| routine runs | schedule, result, errors | Yes |
| tool actions | tool, input summary, risk, result | Yes |
| approvals | request, approver, decision, timestamp | Yes |
| evaluations | score, reviewer, notes | Yes |

### Change Management

| Artifact | Change rule |
|---|---|
| `SOUL.md` | review before production activation |
| workspace docs | agent may draft; human review for authority changes |
| skills | test before rollout |
| cron jobs | dry run before activation |
| shared memory policy | governed review required |
| GBrain canonical writes | review/publisher flow required |

---

## 8. Build Mapping

| Design section | Runtime artifact | Location |
|---|---|---|
| Identity Layer | `SOUL.md` | `~/.hermes/profiles/{{profile_name}}/SOUL.md` |
| Identity and operating rules | `AGENTS.md`, `role-context.md` | `/srv/ai-colleagues/workspaces/{{profile_name}}/` |
| Context Layer | `memory-policy.md`, GBrain source config, Hindsight bank config | workspace + runtime config |
| Capability Layer | skills and tool config | profile skills + MCP/tool config |
| Authority Layer | `authority.md`, action gateway rules | workspace + gateway |
| Autonomy Layer | `routines.md`, cron jobs | workspace + profile cron |
| Evaluation Layer | `evaluation-policy.md`, evaluator skills, eval logs | workspace + structured logs |
| Governance Layer | audit/logging/review docs | workspace + structured logs |

---

## 9. Open Questions and Risky Assumptions

### Open Questions

- {{question}}

### Risky Assumptions

- Assumption: {{assumption}}

### Missing Before Activation

- [ ] credentials
- [ ] tools
- [ ] approval rules
- [ ] GBrain sources
- [ ] Hindsight banks
- [ ] structured systems
- [ ] workspace docs
- [ ] skills
- [ ] evaluation path