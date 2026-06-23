# Setup Entrypoint

This is the first file a human operator or Default Hermes should read after base Hermes is available in a target environment.

This repository assumes the human has already completed the host-level bootstrap:

- VM or host exists
- base Hermes is installed and runnable
- Default Hermes has access to this repository
- required credentials can be provided through the target environment's approved secret process

Do not start by installing individual AI colleagues. Install the core infrastructure assumptions first, then install selected colleague profiles.

---

## Choose the Right Layer

| Need | Start here |
|---|---|
| Understand the architecture | `guidelines/README.md` |
| Let Default Hermes perform setup | `playbooks/README.md` |
| Install or copy runtime files | `artifacts/README.md` |

---

## Default Install Flow

### Phase 0: Confirm human bootstrap

Default Hermes should confirm, not perform, these host-level items:

- VM or host exists
- base Hermes CLI works
- package repo is readable
- operator has identified the target organization name
- credential handoff process is defined
- human approval owner is known

### Phase 1: Install core AI colleague infrastructure

Run:

```text
playbooks/bootstrap/install-core-stack.md
```

This phase prepares shared runtime assumptions:

- Hermes runtime sanity checks
- workspace root conventions
- GBrain canonical and evidence architecture
- Hindsight personal and shared/domain memory assumptions
- structured system-of-record assumptions
- logging, audit, and approval gateway expectations

### Phase 2: Install selected AI colleagues

Run:

```text
playbooks/bootstrap/install-agent-package.md
```

This phase installs role-owning colleagues from `artifacts/agents/`.

Each installed colleague should get:

- one Hermes profile
- one `SOUL.md`
- one agent workspace
- workspace `AGENTS.md` and operating docs
- selected skills
- memory policy
- authority policy
- routine and evaluation policy
- credentials through the target environment's secret process

### Phase 3: Verify before activation

Before calling an AI colleague active, verify:

- profile can start
- required context sources are readable
- source priority and conflict rules are documented
- Hindsight personal bank works
- shared/domain memory write rules are governed
- structured data writes are gated where needed
- dangerous external actions require approval
- routine logs and tool action logs are written
- evaluator or human review path exists

---

## Human Reading Path

1. `guidelines/00-package-model.md`
2. `guidelines/01-infrastructure-spec.md`
3. `guidelines/02-knowledge-and-memory-spec.md`
4. `guidelines/04-agent-spec-template.md`
5. `artifacts/README.md`

## Agent Execution Path

1. `playbooks/README.md`
2. `playbooks/bootstrap/install-core-stack.md`
3. `playbooks/bootstrap/install-agent-package.md`
4. integration playbooks under `playbooks/integrations/`
5. selected files under `artifacts/`

---

## Safety Rule

If the package lacks an artifact, credential, approval rule, or data source for a requested AI colleague, Default Hermes should record the gap and stop before activation. It may draft missing files, but it should not pretend the colleague is production-ready.