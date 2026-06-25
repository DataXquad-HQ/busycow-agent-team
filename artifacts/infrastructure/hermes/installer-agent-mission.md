# Installer Agent Mission

Use this file when a base Hermes agent is given this repository and asked to install the system.

## Mission

Build the shared AI colleague infrastructure first, verify it, then install the requested agent package.

## Your operating rules

1. Follow the package's canonical path. Do not invent an alternate install order.
2. Complete infrastructure before agent installation.
3. Stop on failed verification unless the human owner explicitly accepts the gap.
4. Prefer reusable templates from `artifacts/` over ad hoc local files.
5. Record placeholders, missing credentials, and blocked external approvals clearly.

## Read in this order

1. `SETUP.md`
2. `playbooks/infrastructure/README.md`
3. `playbooks/infrastructure/01-setup-hermes-runtime.md`
4. `playbooks/infrastructure/02-setup-contextual-layer.md`
5. `playbooks/infrastructure/03-setup-collaboration-and-governance.md`
6. `playbooks/infrastructure/04-verify-infrastructure.md`
7. `playbooks/agents/README.md`
8. `playbooks/agents/install-iris.md` or another requested agent playbook

## What you are expected to produce

### Phase A — Shared infrastructure
You should finish with:
- Hermes runtime configured from package templates
- contextual layer installed and routed
- collaboration / governance layer configured
- infrastructure verification completed

### Phase B — Agent installation
You should then finish with:
- target agent profile installed
- agent identity and skills copied or configured
- agent workspace harness installed
- agent-specific verification completed

## Stop conditions

Stop and escalate if any of these occur:
- required credentials are missing
- required external permissions or scopes are missing
- infrastructure verification fails
- the target environment conflicts with package assumptions
- a playbook instructs you to wait for human approval

## What to report back

Return a short structured summary with:
1. completed steps
2. current blockers
3. placeholders still needing human values
4. whether agent installation is allowed to proceed

## Canonical references

- infrastructure templates: `artifacts/infrastructure/`
- agent packages: `artifacts/agents/`
- minimal human orientation: `guidelines/README.md`
