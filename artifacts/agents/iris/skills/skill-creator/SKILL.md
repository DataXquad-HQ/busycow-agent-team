---
name: skill-creator
description: >
  Build new skills or improve existing ones for any Hermes agent.
  Use when creating a skill from scratch, updating outdated steps,
  adding Quality Bar or Fallback Behavior blocks, fixing broken
  triggers, renaming a skill, or converting a one-off workflow into
  a reusable skill. Trigger on: "create a skill", "build a skill for X",
  "update this skill", "add quality bar", "this skill is wrong",
  "skill needs improving", "rename skill", "skill creator".
triggers:
  - "create a skill"
  - "build a skill"
  - "update this skill"
  - "improve this skill"
  - "add quality bar"
  - "rename skill"
  - "skill creator"
  - "make this a skill"
  - "turn this into a skill"
  - "skill needs fixing"
---

# Skill Creator

Build, test, and improve Hermes agent skills. Jump in wherever the
user is — drafting from scratch, refining bad output, or patching
a skill that's missing Quality Bar and Fallback Behavior.

The cycle: **understand → draft → test → refine → ship.**

---

## What a Skill Is

A skill is a named workflow an agent loads on demand. One skill = one
trigger situation. It encodes the exact steps, pitfalls, quality
standards, and fallback paths for a repeatable task — so the agent
doesn't reinvent the approach every session.

Skills are not knowledge dumps. Keep them focused and executable.

**Create a skill when:**
- The workflow has 3+ steps with non-obvious pitfalls
- It will be triggered repeatedly across sessions
- Without it, the agent would re-discover the same steps from scratch

**Don't create a skill when:**
- It's a one-time fix → write it in GBrain
- It's a single API call with no surrounding logic
- The workflow is already covered by an existing skill

---

## Skill Structure

```
skill-name/
├── SKILL.md          # required — loaded when skill triggers
├── references/       # optional — loaded only when explicitly needed
├── scripts/          # optional — deterministic code, never auto-loaded
└── assets/           # optional — output templates, not reasoning material
```

**SKILL.md** is the control plane. Keep it under 500 lines. When it
grows beyond that, move detail into `references/` and link clearly.

**references/** holds supplementary material read during execution:
API patterns, schemas, lookup tables, domain rules. Not auto-loaded —
only when the skill explicitly calls for them.

**scripts/** holds deterministic code that shouldn't be re-written
every run. Better reliability than instructing the agent to invent
the same logic each time.

**assets/** holds output templates and boilerplate. Used in the
deliverable, not loaded into context for reasoning.

---

## 3-Level Loading

Hermes loads skills progressively to keep context lean:

| Level | Content | When loaded |
|---|---|---|
| YAML frontmatter | `name` + `description` | Always — determines if skill fires |
| SKILL.md body | Full instructions | When skill is relevant to the request |
| references/ / scripts/ | Supplementary files | Only when explicitly needed |

The description is the trigger mechanism. If it's vague, the skill
fires silently or not at all. Write it as if it's the only thing
Hermes will read when deciding whether to load the skill.

---

## Naming Rules

| ✅ Do | ❌ Don't |
|---|---|
| Gerund: `nurturing-leads`, `checking-pipeline` | Noun: `pipeline-checker`, `lead-manager` |
| Tool name as-is: `twenty-crm`, `lark-im` | Generic suffix: `crm-helper`, `lark-tool` |
| Lowercase, hyphens only | CamelCase or underscores |

**One skill = one trigger situation.** If two situations share fewer
than 70% of steps, they belong in separate skills.

---

## Writing the Description

The description controls when the skill fires — it's not documentation
for humans.

```yaml
# ✅ Good — specific, includes trigger phrases
description: >
  Weekly pipeline review against revenue targets. Flags stalled
  opportunities and surfaces recommended actions. Use when user asks
  "pipeline health check", "are we on track", or "weekly review".

# ❌ Bad — won't trigger reliably
description: Reviews pipeline data.
```

When in doubt, over-specify triggers rather than under-specify.
Silent non-triggering is harder to catch than over-eager triggering.

---

## Required Sections in SKILL.md

Every skill needs these (adapt names to fit the domain):

```markdown
## When to Use
[1–2 lines — specific trigger conditions, not generic]

## Steps
[Numbered, specific, executable — exact API calls / tool names where relevant]

## Quality Bar
[Self-check before returning output — see below]

## Fallback Behavior
[What to do when tools fail or data is missing — see below]

## Pitfalls
[Known failure modes and fixes — discovered through real use]
```

---

## Quality Bar (Mandatory for Analytical Skills)

Any skill that produces analysis, recommendations, or reports must
include a `## Quality Bar` block. The agent runs this before returning.

**Base template:**
```markdown
## Quality Bar

Before returning output:
- Every recommendation traceable to a source (GBrain, CRM, tool
  result, or user-provided context)?
- Facts and inferred conclusions kept separate — not mixed in the
  same bullet without a label?
- No invented data, metrics, contacts, statuses, or tool results?

If any check fails, rewrite that section before returning.
```

Adapt the checks to the skill's domain. A pipeline skill might add:
"Coverage ratio labelled as estimate (benchmark probabilities, not actuals)?"
A content skill might add: "No claims about features not in the product doc?"

The base template is a starting point, not the final version — the
checks should reflect what could actually go wrong in this specific skill.

---

## Fallback Behavior (Mandatory for Skills with External Dependencies)

Any skill that calls CRM, GBrain, email, or Hindsight must include
a `## Fallback Behavior` block that names each dependency explicitly.

**Base template:**
```markdown
## Fallback Behavior

- If [tool] is unavailable: state what is missing, explain impact on
  confidence, produce best output from remaining data.
- If evidence is too thin for a confident recommendation: say so —
  "Based on available data…" — and state the exact missing input.
- Do not block the entire output because one source failed — degrade
  cleanly and note each gap.
```

"If tools fail" is not specific enough. Name each one: "If CRM is
unreachable", "If GBrain strategy pages are missing", "If Hindsight
returns no snapshots". The agent needs to know which fallback applies.

---

## Creation Process

### Step 1 — Understand the trigger before writing

Answer three questions before drafting:
1. What exact user phrases should fire this skill?
2. What does a good output look like — be specific about format and content?
3. What external tools does it call, and what happens when each is unavailable?

If the user says "turn this conversation into a skill", extract from
the conversation: tools used, steps taken, corrections made, output
format observed. Ask only about what's still unclear — don't re-ask
things already answered.

### Step 2 — Identify what belongs in references/ and scripts/

For each step, ask: would the agent reinvent this every run?
- Code that runs the same way each time → `scripts/`
- Lookup tables, API patterns, domain schemas → `references/`
- Output templates the deliverable is built from → `assets/`

### Step 3 — Draft SKILL.md

Write the draft. Then read it with fresh eyes and ask:
- Does it explain *why*, not just *what*? An agent that understands
  the reasoning handles edge cases better than one following rigid rules.
- Would a different agent instance succeed on the first try?
- Is the Quality Bar specific to this skill's actual outputs — not just
  a copy of the base template?
- Does Fallback Behavior name every external dependency explicitly?

Prefer explaining reasoning over hard-capped rules. If you find yourself
writing ALWAYS or NEVER in all caps, step back — reframe as reasoning.

### Step 4 — Test with realistic trigger prompts

Write 2–3 prompts using the exact phrasing a real user would type.
Run them and check:
- Does the skill fire on these prompts? (If not, tighten the description.)
- Does the output format match expectations?
- Does the skill degrade cleanly when a data source is missing?

### Step 5 — Iterate

When improving based on test results:
- **Generalise from failures** — don't patch the specific test case,
  fix the underlying gap in the instructions
- **Remove dead weight** — instructions that don't change behaviour
  consume context for nothing
- **Check Quality Bar is actually domain-specific** — if it reads
  identically to the base template, it probably needs refinement

---

## Updating an Existing Skill

1. Read the current skill first: `skill_view(name='skill-name')`
2. Identify specifically what's wrong — don't rewrite everything
3. Use `skill_manage(action='patch')` for targeted fixes
4. Use `skill_manage(action='edit')` for structural overhauls only
5. Test the same trigger prompts after editing to confirm the fix worked

Never overwrite a skill without reading it first.

---

## Renaming a Skill

```python
# 1. Read old skill content
skill_view(name='old-name')

# 2. Create new skill with updated name
skill_manage(action='create', name='new-name', content='...')

# 3. Delete old skill, declare what absorbed it
skill_manage(action='delete', name='old-name', absorbed_into='new-name')

# 4. Update any SOUL.md or skills referencing the old name
```

---

## Making a Skill Shared (All Agents)

When a skill should be available across all agent profiles:

```python
# /tmp/link_skill.py
import os

HOME = os.path.expanduser("~")
SKILL_NAME = "my-skill"
SKILL_SRC = HOME + "/.hermes/skills/category/" + SKILL_NAME
SHARED = HOME + "/.hermes/shared_skills"

link = SHARED + "/" + SKILL_NAME
if os.path.lexists(link): os.unlink(link)
os.symlink(SKILL_SRC, link)

for agent in ["leo", "maya", "rex"]:
    agent_link = HOME + f"/.hermes/profiles/{agent}/skills/_shared/{SKILL_NAME}"
    if os.path.lexists(agent_link): os.unlink(agent_link)
    os.symlink(SKILL_SRC, agent_link)
    print(f"{'OK' if os.path.isdir(agent_link) else 'FAIL'} {agent}")
```

Use Python `os.symlink()` — never bash loops. Bash produces circular symlinks.

---

## Pitfalls

- **Vague description = silent failure** — the skill never fires, and
  no error appears. Test trigger phrases before shipping.
- **Quality Bar must be domain-specific** — the base template is a
  starting point. Adapt the checks to what could actually go wrong here.
- **Fallback must name each tool dependency** — "if tools fail" is
  not specific enough for the agent to act correctly.
- **One trigger situation per skill** — if you write "OR use when…",
  that's likely a second skill.
- **references/ is not auto-loaded** — explicitly call for it in the
  step that needs it, or the agent won't read it.
- **Don't nest references more than one level** — SKILL.md →
  references/file.md is the limit. Deeper nesting is rarely worth it.
- **After renaming: update the frontmatter `name:` field too** —
  directory name ≠ frontmatter name field. Both must match.
- **Agent profile skills are not backed up by nightly brain sync** —
  lost permanently on profile delete. Back up manually before any
  profile deletion.
