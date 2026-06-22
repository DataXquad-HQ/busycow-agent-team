# Shared Skills

This folder contains **canonical shared skill artifacts** that can be copied into multiple Hermes profiles.

These are governed centrally, then distributed into profile-local runtime copies.

For the full governance model, read:
- `../../guidelines/reference/shared-skill-model.md`
- `managing-shared-skills/references/shared-skill-registry.md`
- `managing-shared-skills/references/shared-skill-rollout-plan.md`

## Current shared skills

| Skill | Purpose |
|---|---|
| `capturing-to-gbrain/` | Shared durable-knowledge capture pattern for writing entities, decisions, and intel into GBrain |
| `twenty-crm/` | Common CRM access and schema usage patterns |
| `routing-report-delivery/` | Shared rule for full human reports vs short cron receipts, plus cron recovery / resume handling |
| `managing-shared-skills/` | Shared governance workflow for canonical-source + per-profile-copy distribution |
| `skill-creator/` | Shared skill-authoring and improvement workflow |
| `blog-content-crew/` | Reusable long-form drafting crew for blog-post production with Tavily-backed research |

## Shared core baseline (current)

The current shared-core baseline for active agents is:

- `skill-creator/`
- `managing-skills/`
- `managing-shared-skills/`
- `capturing-to-gbrain/`
- `routing-report-delivery/`

These skills are governed centrally, then copied into profile-local runtime skill directories.

## Installation model

- canonical shared artifact lives here
- target runtime copy goes into `artifacts/agents/<agent>/skills/` or directly into a live Hermes profile
- do not rely on runtime symlinks as the default package pattern

## Scope boundary

- shared reusable client-facing skill artifact → package here
- internal-only DataXquad knowledge operation skill → keep out of the package repo

Example: `operating-dx-gbrain-vault` is an internal operating skill and should not be published as a client package artifact.
