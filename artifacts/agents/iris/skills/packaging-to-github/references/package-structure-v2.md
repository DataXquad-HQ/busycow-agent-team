# Package Structure v2

Authoritative repo model for `busycow-agent-package` as of 2026-06-18.

## Three-layer model

- `guidelines/` — human-readable specs
- `playbooks/` — agent-readable operational instructions
- `artifacts/` — concrete installable / copyable assets

## Human path

`README.md` → `guidelines/`

## Agent path

`README.md` → `playbooks/` → `artifacts/`

## Key artifact locations

- agent runtime packages → `artifacts/agents/<agent>/`
- canonical shared skills → `artifacts/shared-skills/<skill>/`
- schemas → `artifacts/schemas/`
- knowledge base starter templates → `artifacts/knowledge-base-templates/`

## Playbook locations

- core bootstrap → `playbooks/bootstrap/install-core-stack.md`
- system integrations → `playbooks/integrations/<tool>/`

## Migration rule

If any older packaging note mentions `agent-teams/`, `context/schemas/`, `knowledge-base-setup/`, or `third-party-tools/` as live top-level package paths, treat those as legacy names and map them to the v2 structure above.