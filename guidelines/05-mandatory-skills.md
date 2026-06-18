# Mandatory Skills — Every Agent

Every agent, regardless of role, must have these skills installed before
being considered operational. They are not optional add-ons — they are
the base layer that makes agents consistent, self-improving, and safe.

Install by copying the skill directory directly into the agent's profile:
```bash
cp -r /path/to/skill-name ~/.hermes/profiles/[agent]/skills/skill-name
```

No symlinks, no shared registry. Each agent owns a full copy.

---

## 1. `lark-im`

**Why mandatory:** Every agent communicates via Lark. Without this,
the agent cannot send messages, read channels, or receive instructions.

**Source:** Bundled with Hermes — installed automatically on profile creation.

---

## 2. `lark-shared`

**Why mandatory:** Handles lark-cli auth setup, `--as` identity switching,
permission errors, and scope issues. Any agent using Lark tools will hit
these edge cases.

**Source:** Bundled with Hermes — installed automatically on profile creation.

---

## 3. `capturing-to-gbrain`

**Why mandatory:** The mechanism by which agents write durable knowledge
into GBrain. Without it, insights from every session evaporate. This is
the agent's memory write path.

**Source:** `artifacts/agents/leo/skills/capturing-to-gbrain/` — copy to each agent.

---

## 4. `managing-skills`

**Why mandatory:** Agents must be able to create, update, and fix their
own skills without human scaffolding. This is the self-improvement loop.
Also contains the shared skill SOP and Leo cron architecture reference.

**Source:** `artifacts/agents/leo/skills/managing-skills/` — copy to each agent.
Note: the `references/leo-cron-architecture.md` inside is Leo-specific;
other agents may remove it.

---

## 5. `skill-creator`

**Why mandatory:** The authoritative guide for building and improving skills
— naming rules, 3-level loading, Quality Bar, Fallback Behavior, testing
process. Every time an agent builds or patches a skill, it loads this first.

Without it, agents build skills inconsistently and skip quality checks.

**Source:** `artifacts/agents/[any]/skills/skill-creator/` — copy to each agent.

---

## Installation Checklist (New Agent Setup)

When onboarding any new agent, verify these five skills are present before
the first cron or live task:

```bash
ls ~/.hermes/profiles/[agent]/skills/ | grep -E \
  "lark-im|lark-shared|capturing-to-gbrain|managing-skills|skill-creator"
```

Expected output — all five names should appear:
```
capturing-to-gbrain
lark-im
lark-shared
managing-skills
skill-creator
```

If any are missing, copy from the relevant source above before proceeding.

---

## What Is Not Listed Here

Skills that are role-specific (e.g. `twenty-crm`, `openmail`, `checking-pipeline-health`)
belong in each agent's own `artifacts/agents/[name]/skills/` directory, not here.

Bundled Hermes skills (apple, github, lark-base, etc.) are installed
automatically by Hermes on profile creation and do not need to be
managed manually.

---

## Keeping This List Current

When a new skill is determined to be universally required:
1. Add it to this file with the Why mandatory and Source fields filled in
2. Copy it into all existing live agent profiles
3. Copy it into all `artifacts/agents/[name]/skills/` directories in this package
4. Add it to the Installation Checklist grep above
