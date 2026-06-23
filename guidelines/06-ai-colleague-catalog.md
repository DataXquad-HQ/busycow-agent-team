# AI Colleague Catalog

> Audience: humans evaluating this package.
> Purpose: show which AI colleagues are designed, packaged, testable, or active.

This catalog is the human-facing index. The installable runtime source of truth remains `artifacts/agents/`.

Do not mark a colleague as Active unless the runtime artifacts, credentials, context sources, authority rules, and verification checks have all passed.

---

## Status Definitions

| Status | Meaning |
|---|---|
| Concept | role idea exists but design is incomplete |
| Designed | human-facing design spec exists |
| Packaged | runtime artifacts exist under `artifacts/agents/{{agent_slug}}/` |
| Testing | profile can be installed and is being verified |
| Active | verified and approved for real operation |
| Paused | installed but routines/actions are disabled |
| Deprecated | no longer intended for use |

---

## Catalog

| AI colleague | Role | Status | Human design spec | Runtime artifacts | Notes |
|---|---|---|---|---|---|
| Iris | AI colleague / system operator pattern | Needs review | Check existing package docs and artifacts | Check `artifacts/agents/iris/` if present | Do not assume active until runtime checklist passes |
| Leo | BD / pipeline-related colleague pattern | Needs review | Check existing package docs and artifacts | Check `artifacts/agents/leo/` if present | Do not assume active until runtime checklist passes |
| Maya | content / growth-related colleague pattern | Needs review | Check existing package docs and artifacts | Check `artifacts/agents/maya/` if present | Do not assume active until runtime checklist passes |

---

## Required Catalog Fields for Each Colleague

Each colleague should eventually have:

| Field | Purpose |
|---|---|
| role | what responsibility this colleague owns |
| human owner | who is accountable for its direction |
| status | concept, designed, packaged, testing, active, paused, deprecated |
| design spec | human-facing operating design |
| build blueprint | implementation mapping |
| runtime artifacts checklist | activation tracker |
| artifact path | installable runtime package location |
| primary context sources | GBrain, Hindsight, structured systems, workspace |
| authority summary | what it may do without approval and what requires approval |
| routine summary | autonomous jobs, if any |
| evaluation path | human or evaluator review mechanism |

---

## Runtime Artifact Expectation

A packaged colleague should follow this shape:

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

If this shape is missing, the colleague may still be useful as a design example, but Default Hermes should install it as Draft or stop before activation.

---

## Maintenance Rule

When a new AI colleague is added:

1. create or update its human design spec
2. add or update its artifact package
3. verify activation criteria
4. update this catalog
5. do not inflate status beyond verified reality