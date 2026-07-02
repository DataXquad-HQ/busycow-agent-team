# Install Iris

## Goal
Install the packaged Iris agent.

If Iris already exists in the target workspace and only the contextual-layer behavior needs alignment, use `align-existing-iris-contextual-layer.md` instead of this full install path.

## Inputs
- infrastructure phase completed
- target profile location known
- target workspace location known

## Artifact package
Use:
- `artifacts/agents/iris/README.md`
- `artifacts/agents/iris/SETUP.md`
- `artifacts/agents/iris/SOUL.md`
- `artifacts/agents/iris/skills/`
- `artifacts/agents/iris/workspace/`

## Steps
1. Read `artifacts/agents/iris/SETUP.md`.
2. Copy `SOUL.md` into the target Iris profile.
3. Copy `skills/` into the target Iris profile.
4. Copy `workspace/` into the target Iris workspace path.
5. Run the verification items listed in the Iris setup file.

## Stop conditions
Stop and report if:
- infrastructure phase is not complete
- the target profile path is unknown
- the target workspace path is unknown
- required secrets are missing

## Verify
- Iris profile has `SOUL.md`
- Iris skills exist
- Iris workspace harness exists
- the installer can open the packaged workspace README and setup file
