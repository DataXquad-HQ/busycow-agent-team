# Setup Entrypoint

This file is the entrypoint into the new package structure.

## Use the right layer

- Want to understand the architecture first?
  → `guidelines/README.md`

- Want an agent to perform setup or migration?
  → `playbooks/README.md`

- Need the actual files that get installed or copied?
  → `artifacts/README.md`

## Recommended install entrypoint

For a fresh rollout after Hermes is already minimally installed:

```text
playbooks/bootstrap/install-core-stack.md
```
