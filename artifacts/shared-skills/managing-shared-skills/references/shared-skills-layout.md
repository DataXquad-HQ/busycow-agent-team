# Shared Skills Layout & Sync Rules

## Canonical Model

Use a **canonical-source + per-profile copies** model.

- Canonical source lives under `~/.hermes/skills/`
- Runtime copies live under `~/.hermes/profiles/<agent>/skills/`
- Packaging later uses real files under `shared-skills/` and `artifacts/agents/<agent>/skills/`

This keeps governance centralized while preserving profile isolation.

---

## Recommended Directory Layout

### Local canonical source

```text
~/.hermes/skills/
  core/
    routing-report-delivery/
    managing-shared-skills/
  lark/
    <shared lark skill if canonically maintained here>
```

### Profile runtime copies

```text
~/.hermes/profiles/
  leo/skills/
  maya/skills/
  rex/skills/
```

### Future package layout

```text
<repo-root>/
  artifacts/
    shared-skills/
      routing-report-delivery/
      managing-shared-skills/
    agents/
      leo/skills/
      maya/skills/
      rex/skills/
```

---

## Ownership Model

### Iris-owned canonical layer
Iris is the owner of shared skill governance.
That means Iris is responsible for:
- deciding whether a skill is shared
- editing the canonical source first
- deciding sync policy
- distributing updates to profiles

### Profile-owned runtime layer
Each profile owns its runtime copy.
If a profile intentionally diverges, that copy becomes a local fork until reconciled.

---

## Sync Policies

### overwrite-on-sync
Use for strict shared governance.
Examples: infra policies, reporting delivery rules, org-wide formatting rules.

### manual-review-before-overwrite
Default safe mode.
Use when a profile may have made local edits.

### forked-no-auto-sync
Use when a profile copy is now intentionally different.
Treat it as a derivative skill, not a strict mirror.

---

## Decision Checklist

Before distributing a skill:
1. Is this skill truly reused by more than one profile?
2. Does the canonical source avoid hardcoded profile-specific assumptions?
3. Which profiles should get it now?
4. What sync policy applies?
5. Are you copying a fresh version or reconciling an existing profile fork?

---

## Anti-Patterns

- Editing only a profile copy and forgetting the canonical source
- Using symlinks as the default production pattern
- Copying every shared skill into every profile without a reason
- Overwriting a diverged profile copy without review
- Treating `~/.hermes/skills/` as automatically global at runtime across all profiles
