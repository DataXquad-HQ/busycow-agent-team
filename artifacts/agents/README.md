# Agent Artifacts

This folder contains the **runtime agent packages**.

Each subdirectory is an installable agent artifact set — the files an agent or operator copies into a Hermes profile or uses during agent-specific rollout.

## Structure per agent

```text
artifacts/agents/<agent>/
├── SOUL.md
├── SETUP.md
├── skills/
└── cron/
```

Some directories still contain legacy files from the older package structure.
Those should be treated as cleanup candidates unless explicitly referenced by a current playbook.

## Important

This layer is **not** the human-readable architecture spec for an agent.
That belongs in:

```text
guidelines/deployed-agents/
```

This layer is the deployable runtime material.
