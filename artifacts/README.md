# Artifacts

This layer contains the **actual installable / copyable assets** used by the BusyCow agent framework.

Artifacts answer: **which file should be installed, copied, or adapted into the target system?**

## Rules

- Artifacts are concrete runtime assets
- Artifacts should not carry long explanatory prose unless required for use
- Human-readable design rationale belongs in `guidelines/`
- Step-by-step operating instructions belong in `playbooks/`

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
Per-agent runtime packages: SOULs, skills, cron templates, and agent setup files.

### `shared-skills/`
Canonical shared skill artifacts that can be copied into multiple profiles.

### `schemas/`
Structural data schemas used by operational systems such as CRM or task boards.

### `knowledge-base-templates/`
Templates for building the client's own knowledge base / GBrain source repository.

---

## Installation Principle

Artifacts are the files an agent eventually copies into:
- Hermes profiles
- client knowledge repos
- operational systems
- deployment directories
