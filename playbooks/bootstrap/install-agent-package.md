# Install AI Colleague Package

> Audience: Default Hermes.
> Scope: install selected role-owning AI colleagues after the core stack has been verified.

Run this only after `playbooks/bootstrap/install-core-stack.md` has completed or after a human owner has accepted remaining core gaps.

---

## 0. Stop Conditions

Stop before installing or activating a colleague if:

- no approved design spec exists or the human owner explicitly accepts a draft install only
- no target Hermes profile name is defined
- required credentials are missing
- required context sources are missing with no fallback
- structured system writes are required but no write authority or gateway exists
- external publishing or messaging is requested without approval rules
- no human owner is known

---

## 1. Select Colleague Artifact

Expected artifact location:

```text
artifacts/agents/{{agent_slug}}/
```

Expected minimum artifact set:

```text
artifacts/agents/{{agent_slug}}/
  design-spec.md              # human-facing source, if included
  build-blueprint.md          # implementation mapping, if included
  runtime-artifacts.md        # activation checklist, if included
  profile/
    SOUL.md
    config.yaml.template
    cron/
  workspace/
    AGENTS.md
    role-context.md
    authority.md
    tool-policy.md
    memory-policy.md
    routines.md
    evaluation-policy.md
  skills/
```

If this structure does not exist, create a gap report. Do not invent production status.

---

## 2. Review Design Before Build

Confirm the colleague has decisions for all seven layers:

| Layer | Required decision |
|---|---|
| Identity | role, owner, responsibilities, non-responsibilities |
| Context | GBrain, Hindsight, structured systems, workspace, source priority |
| Capability | skills, tools, outputs, inputs |
| Authority | allowed actions, approval-required actions, forbidden actions |
| Autonomy | routines, schedules, stop conditions |
| Evaluation | quality checks, tests, reviewer |
| Governance | logs, audit, change management, escalation |

If a high-risk decision is missing, install as draft only or stop.

---

## 3. Create Hermes Profile

Create or confirm profile:

```bash
hermes profile create {{profile_name}}
hermes profile use {{profile_name}}
```

Expected path:

```text
~/.hermes/profiles/{{profile_name}}/
```

Install profile artifacts:

```bash
cp artifacts/agents/{{agent_slug}}/profile/SOUL.md ~/.hermes/profiles/{{profile_name}}/SOUL.md
cp artifacts/agents/{{agent_slug}}/profile/config.yaml.template ~/.hermes/profiles/{{profile_name}}/config.yaml
```

Only install cron templates after a dry run and human approval when needed.

---

## 4. Create Agent Workspace

Default path:

```text
/srv/ai-colleagues/workspaces/{{profile_name}}/
```

Create directories:

```bash
mkdir -p /srv/ai-colleagues/workspaces/{{profile_name}}/{drafts,notes,scratch,examples,runbooks,review-queues}
```

Copy workspace docs:

```bash
cp artifacts/agents/{{agent_slug}}/workspace/*.md /srv/ai-colleagues/workspaces/{{profile_name}}/
```

Required docs:

- `AGENTS.md`
- `role-context.md`
- `authority.md`
- `tool-policy.md`
- `memory-policy.md`
- `routines.md`
- `evaluation-policy.md`

If any are missing, mark the colleague as draft only.

---

## 5. Install Skills

Install mandatory shared skills first, then role-specific skills.

Mandatory skill reference:

```text
guidelines/05-mandatory-skills.md
```

Copy only the skills required by the design spec or build blueprint.

```bash
cp -r artifacts/shared-skills/{{skill_name}} ~/.hermes/profiles/{{profile_name}}/skills/{{skill_name}}
cp -r artifacts/agents/{{agent_slug}}/skills/{{skill_name}} ~/.hermes/profiles/{{profile_name}}/skills/{{skill_name}}
```

After copying:

```bash
hermes skills list
```

Stop if a required skill is missing.

---

## 6. Configure Context

### GBrain

Confirm:

- required canonical sources are readable
- evidence zones exist or are marked missing
- home write source is defined
- canonical writes go through review or publisher flow

### Hindsight

Confirm:

- personal bank exists for this profile
- memory mode is `hybrid`
- auto-recall works
- auto-retain works for personal bank, unless explicitly disabled
- shared/domain bank writes are governed

### Structured systems

Confirm:

- read tools work
- write tools are allowed only where authority permits
- approval-required writes use gateway or human approval
- logs are available

### Workspace

Confirm the workspace docs state:

- context source priority
- read-router rules
- write-router rules
- promotion workflow

---

## 7. Credentials

Do not invent or commit credentials.

Use the target environment's approved secret process.

Confirm required environment variables exist in the profile runtime without printing secret values:

```bash
hermes profile env check {{profile_name}}
```

If the command is not available, use the deployment's approved secret verification method.

---

## 8. Verification

Run:

```bash
hermes doctor
hermes profile use {{profile_name}}
hermes skills list
```

Then test:

- context retrieval from GBrain canonical
- evidence retrieval where relevant
- Hindsight recall
- Hindsight personal retain, if enabled
- structured read access
- structured write dry run or approval flow
- one role-specific skill dry run
- one routine dry run, if routines exist
- evaluation path
- audit/log output

---

## 9. Activation Decision

Use these statuses:

| Status | Meaning |
|---|---|
| Draft | artifacts copied but missing decisions or credentials |
| Testing | profile works but still needs verification |
| Active | verification passed and human owner approved |
| Paused | installed but routines/actions disabled |

A colleague may be marked Active only when:

- human owner is known
- authority policy exists
- required credentials exist
- required context sources work
- required skills pass dry run
- logs are written
- evaluation path exists
- high-risk actions have approval rules

---

## 10. Output Report

Default Hermes should produce an install report:

```text
Agent: {{agent_name}}
Profile: {{profile_name}}
Status: Draft / Testing / Active / Paused
Installed artifacts:
Missing artifacts:
Missing credentials:
Missing tools:
Missing data sources:
Missing approval rules:
Verification results:
Human decisions needed:
Recommended next step:
```