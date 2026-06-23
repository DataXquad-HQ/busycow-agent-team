# Artifacts

This layer contains the installable or copyable assets used by the Hermes AI colleague package.

Artifacts answer: which file should be installed, copied, adapted, or used as a runtime template?

---

## Rules

- Artifacts are concrete runtime assets.
- Human-readable design rationale belongs in `guidelines/`.
- Step-by-step operating instructions belong in `playbooks/`.
- Secrets must not be committed.
- If an artifact is missing, installers should report the gap instead of claiming production readiness.

---

## Structure

```text
artifacts/
├── README.md
├── agents/
├── shared-skills/
├── schemas/
└── knowledge-base-templates/
```

### `agents/`

Per-agent runtime packages. Each role-owning AI colleague should eventually have an artifact directory.

Recommended shape:

```text
artifacts/agents/{{agent_slug}}/
  design-spec.md
  build-blueprint.md
  runtime-artifacts.md
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

A minimal draft install may omit some files, but activation should require the missing items to be resolved or explicitly accepted by the human owner.

### `shared-skills/`

Canonical shared skill artifacts that can be copied into multiple profiles.

Shared skills should remain installable per profile. Runtime profiles should own their own copies so profile behavior is inspectable and stable.

### `schemas/`

Structured data schemas and table expectations for operational systems such as CRM, Plane, approval tables, routine logs, tool action logs, and evaluation logs.

### `knowledge-base-templates/`

Templates for building a target team's GBrain canonical and evidence sources.

These templates should preserve the separation between:

- canonical knowledge
- evidence and source material
- operational state
- workspace context

---

## Installation Principle

Artifacts may be copied into:

- Hermes profiles
- agent workspaces
- GBrain canonical sources
- GBrain evidence zones
- Hindsight setup/configuration processes
- structured operational systems
- deployment directories

The installer should always verify the artifact landed in the right context layer.