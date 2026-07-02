# Setup Entrypoint

Use this file as the package entrypoint.

Before starting, the installer agent should read:
- `artifacts/infrastructure/hermes/installer-agent-mission.md`
- `contextual-layer/README.md`

## Assumptions

This package assumes the target environment already has:
- a machine or VM
- base Hermes installed
- repo access
- a credential handoff process
- a named human owner for approvals

## Install Order

### Phase A — Shared infrastructure
Run these in order:
1. `playbooks/infrastructure/01-setup-hermes-runtime.md`
2. `playbooks/infrastructure/02-setup-contextual-layer.md`
3. `playbooks/infrastructure/03-setup-collaboration-and-governance.md`
4. `playbooks/infrastructure/04-verify-infrastructure.md`

### Phase B — Agent installation
Then install one or more agents:
- `playbooks/agents/install-iris.md`
- additional agent playbooks as they are added

## Stop Rule

If infrastructure verification fails, do not install or activate an agent package yet.
