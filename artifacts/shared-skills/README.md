# Shared Skills

This folder contains **canonical shared skill artifacts** that can be copied into multiple Hermes profiles.

These are governed centrally, then distributed into profile-local runtime copies.

## Current shared skills

| Skill | Purpose |
|---|---|
| `twenty-crm/` | Common CRM access and schema usage patterns |
| `routing-report-delivery/` | Shared rule for full human reports vs short cron receipts |
| `managing-shared-skills/` | Shared governance workflow for canonical-source + per-profile-copy distribution |

## Installation model

- canonical shared artifact lives here
- target runtime copy goes into `artifacts/agents/<agent>/skills/` or directly into a live Hermes profile
- do not rely on runtime symlinks as the default package pattern
