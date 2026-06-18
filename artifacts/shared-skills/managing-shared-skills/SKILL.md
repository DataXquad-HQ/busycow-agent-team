---
name: managing-shared-skills
description: >
  Govern skills that should be reused across multiple Hermes profiles. Use when Iris creates,
  updates, versions, or distributes a shared skill from the canonical source into agent profile
  copies, or when deciding whether a skill should stay shared or become an agent-local fork.
triggers:
  - "shared skill"
  - "distribute this skill to other profiles"
  - "sync skill to leo"
  - "sync skill to maya"
  - "shared skills governance"
  - "copy this skill to all agents"
  - "update shared skill"
  - "sync skill to other profiles"
  - "manage shared skill"
version: "1.0"
owner: Iris
---

# Managing Shared Skills

## When to Use

Use this skill when a skill should exist in more than one Hermes profile.
The canonical owner is **Iris**. Iris creates and governs the shared source first,
then distributes concrete copies into agent profiles.

This skill is for:
- deciding whether a skill is truly shared or agent-private
- creating the canonical shared source
- copying that source into one or more profiles
- re-syncing updates later
- deciding whether a profile copy should remain synced or become a local fork

---

## Core Principle

**Profiles are runtime boundaries. Shared skills are governance boundaries.**

So:
- keep one canonical source under the shared governance layer
- distribute concrete copies into each profile's `skills/` directory
- do not assume Hermes treats one central skill file as truly global across profiles
- do not rely on symlinks as the default production pattern

---

## Standard Architecture

### Canonical shared source
Store the maintained source in Iris's shared skill layer:

```text
~/.hermes/skills/<category>/<skill-name>/
```

In this environment that usually resolves to:

```text
/home/hunter_lin/.hermes/skills/<category>/<skill-name>/
```

### Runtime profile copies
Install concrete copies into each target profile:

```text
~/.hermes/profiles/<agent>/skills/<skill-name>/
```

Examples:
- `~/.hermes/profiles/leo/skills/<skill-name>/`
- `~/.hermes/profiles/maya/skills/<skill-name>/`
- `~/.hermes/profiles/rex/skills/<skill-name>/`

### Future package layout
When packaging later, use real files, not symlinks:

```text
artifacts/shared-skills/<skill-name>/
artifacts/agents/<agent>/skills/<skill-name>/
```

`shared-skills/` is the right package directory for org-wide reusable skills.

---

## Classification Rule

Before distributing any skill, classify it:

### Class A — Shared canonical
Use shared governance when:
- multiple agents should use the same workflow
- the logic should stay centrally maintained
- any profile-specific differences are small or temporary

Examples:
- report delivery rules
- common Lark operational workflows
- shared GBrain capture rules
- profile-agnostic infra patterns

### Class B — Shared base, local fork allowed
Use this when:
- the core workflow is shared
- a specific agent will likely tune the wording, channels, or edge cases

Pattern:
- create canonical source
- copy into target profile
- allow the profile copy to diverge intentionally

### Class C — Agent private
Keep the skill local when:
- it only makes sense for one agent
- it hardcodes one agent's tool flow or domain
- sharing would confuse other agents

---

## Workflow

## Step 1 — Create or update the canonical source
Always edit the canonical shared copy first.

Path pattern:

```text
~/.hermes/skills/<category>/<skill-name>/SKILL.md
```

Use `skill_manage` for the canonical source.
If there are references, templates, or scripts, keep them in the same canonical directory.

## Step 2 — Decide target profiles
List which profiles should receive the skill.
In this environment, current named profiles are typically:
- `leo`
- `maya`
- `rex`

Do not distribute by habit. Choose profiles deliberately.

## Step 3 — Copy, do not symlink
Distribute by concrete copy:

```bash
cp -r ~/.hermes/skills/<category>/<skill-name> ~/.hermes/profiles/leo/skills/<skill-name>
```

Repeat for each target profile.

If a profile copy already exists:
- compare first if you suspect local changes
- overwrite only when you intend to re-sync
- if the profile has intentionally diverged, treat it as a fork and do not blindly overwrite

## Step 4 — Record the sync decision
For every shared skill, keep these decisions explicit:
- canonical owner: Iris
- source path
- target profiles
- sync policy:
  - `overwrite-on-sync`
  - `manual-review-before-overwrite`
  - `forked-no-auto-sync`

## Step 5 — Verify each installed copy
After copying, verify:
- directory exists
- `SKILL.md` exists
- frontmatter `name:` matches the directory name
- target profile can see the skill in its own runtime layer

---

## Sync Policies

### overwrite-on-sync
Use when the shared skill must stay identical everywhere.
Typical for governance or infra skills.

### manual-review-before-overwrite
Use when profiles may have small local edits that need inspection before overwrite.
This is the default safe choice.

### forked-no-auto-sync
Use when a profile copy has intentionally diverged.
At that point, it is no longer a strict shared copy.
Treat it as a local skill derived from the shared base.

---

## Recommended Naming and Metadata

For shared skills, prefer frontmatter that makes governance obvious:

```yaml
name: routing-report-delivery
version: "1.0"
owner: Iris
```

Optional fields if useful:

```yaml
shared: true
sync_policy: manual-review-before-overwrite
```

Do not encode per-profile assumptions in a shared skill unless the whole point of the skill is to act as a base template.

---

## Directory Structure Rules

### Canonical source

```text
~/.hermes/skills/
  core/
    managing-shared-skills/
      SKILL.md
      references/
      scripts/
```

### Profile installs

```text
~/.hermes/profiles/
  leo/
    skills/
      managing-shared-skills/
  maya/
    skills/
      managing-shared-skills/
```

### Future package structure

```text
artifacts/
  shared-skills/
    <skill-name>/
  agents/
    leo/skills/
    maya/skills/
    rex/skills/
```

---

## Quality Bar

Before declaring a skill "shared":
- The skill really belongs to more than one profile, rather than merely being reusable in theory?
- The canonical source is updated first, rather than editing one profile copy and forgetting the source?
- Target profiles were chosen deliberately, not copied everywhere by default?
- The chosen sync policy is explicit: overwrite, manual review, or forked?
- Any profile-specific assumptions were removed from the shared copy, or clearly marked as template placeholders?
- The installed profile copies were verified to exist after distribution?

If any check fails, do not call the rollout complete.

---

## Fallback Behavior

- **If you are unsure whether a skill is really shared**: do not distribute it yet. Keep it local until the reuse pattern is confirmed.
- **If a target profile already has a modified version**: stop and compare before overwriting. Default to `manual-review-before-overwrite`.
- **If one profile needs a different behavior immediately**: copy the canonical source once, then allow that profile to become a deliberate fork instead of corrupting the shared source.
- **If packaging is not ready yet**: keep the canonical source under `~/.hermes/skills/` and postpone GitHub distribution. Local governance still works.

---

## Pitfalls

- **Do not assume `~/.hermes/skills/` is magically global across profiles at runtime.** Hermes profile boundaries are real.
- **Do not use symlinks as the default production pattern.** They increase blast radius and complicate packaging.
- **Do not edit only a profile copy and forget the canonical source.** That breaks the governance chain.
- **Do not copy every shared skill into every profile automatically.** Distribution should be intentional.
- **Do not overwrite a profile copy that has become a local fork unless you explicitly want to erase its divergence.**
- **Do not confuse shared governance with shared runtime storage.** Governance can be centralized while runtime remains profile-local.
