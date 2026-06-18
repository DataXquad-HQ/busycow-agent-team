# Repo Structure Migration Map

This document records the package restructure into three layers:

- `guidelines/` — human-readable specs
- `playbooks/` — agent-readable operational instructions
- `artifacts/` — concrete installable assets

## Migration Table

| Old path | New path | Layer | Why |
|---|---|---|---|
| `agent-teams/` | `artifacts/agents/` | Artifacts | These are runtime agent files, not just descriptions |
| `context/schemas/` | `artifacts/schemas/` | Artifacts | Schemas are install/reference assets used by setup and runtime |
| `knowledge-base-setup/` | `artifacts/knowledge-base-templates/` | Artifacts | These are templates that get copied into a client knowledge base |
| `third-party-tools/` | `playbooks/integrations/` | Playbooks | These files mainly explain how to set up and use integrations operationally |
| shared skills governed outside the repo | `artifacts/shared-skills/` | Artifacts | Canonical shared skill artifacts to copy into multiple profiles |
| `architecture/overview.md` | `guidelines/reference/architecture-overview.md` | Guidelines | Human-readable architecture reference |
| `standards/agent-capability-doc-standard.md` | `guidelines/reference/agent-capability-doc-standard.md` | Guidelines | Human-readable documentation standard |
| top-level `SETUP.md` (old mixed content) | `playbooks/bootstrap/install-core-stack.md` | Playbooks | Core setup instructions belong in the agent-readable runbook layer |
| top-level `SETUP.md` (new stub) | `SETUP.md` | Entrypoint | Kept as a simple router into the new structure |

---

## Resulting Model

### Human path
`README.md` → `guidelines/`

### Agent path
`README.md` → `playbooks/` → `artifacts/`

### Core rule
**Human reads guidelines, agent runs playbooks, system installs artifacts.**
