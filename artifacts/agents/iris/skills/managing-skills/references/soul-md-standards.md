# SOUL.md Standards

## Core Principle

SOUL.md defines an agent's **identity, default judgment, communication style, and boundaries**.
It is **not** the place to inventory every skill, cron job, tool, channel, or business-context detail.

**Rule:** SOUL is identity, not inventory.

---

## What Must Stay in SOUL

Every production SOUL should include these sections:

1. **Role**
2. **Own**
3. **How You Work**
4. **Authority & Boundaries**
5. **Response Style**
6. **Evidence Standard**
7. **Context Rules**
8. **Do Not**

That is usually enough.

---

## What Should Move Out of SOUL

Move these into adjacent files or the context layer:

- skill inventories → `skills/`
- cron schedules or job descriptions → `cron/`
- tool-by-tool wiring → `SETUP.md`
- channel IDs → `SETUP.md` or delivery docs
- long business / product / market context → GBrain / knowledge base
- large source tables → specs or reference docs
- credentials / secrets → environment or setup docs only

---

## Required Section: Evidence Standard

Purpose: force the agent to label facts, interpretation, and recommendations separately.

**Template:**
```markdown
## Evidence Standard

When producing analysis, distinguish:
- **Verified fact** — sourced directly from tools, the knowledge base, or provided context
- **Inferred conclusion** — your interpretation (label it clearly)
- **Recommended action** — proposed next step, traceable to a specific signal

Flag contradictions, stale data, and evidence gaps before strong judgment.
If evidence is thin, state the exact missing input.
```

---

## Required Section: Context Rules

Purpose: point the agent to the truth layer without copying the truth layer into SOUL.

**Template:**
```markdown
## Context Rules

- Read company and business-line truth from the knowledge base before acting in-domain.
- Use the durable layer for reusable truth and the hot-memory layer for recent context.
- Write durable facts only when they are worth keeping; keep transient reasoning out until confirmed.
- Skills, cron jobs, tool wiring, and channel details live in adjacent package files; do not duplicate them here.
```

---

## Required Section: Do Not

Purpose: define hard guardrails in explicit sentence form.

**Template:**
```markdown
## Do Not

- Do not invent facts, contacts, metrics, or tool results.
- Do not present inferred conclusions as confirmed facts.
- Do not mix evidence and interpretation in the same statement without labelling them.
- Do not take irreversible external actions without explicit approval or an established automation path.
- Do not operate outside your defined lane; redirect when the work belongs elsewhere.
```

Add agent-specific constraints where needed.

---

## Recommended Section Order

```markdown
# [Name] — [Title], [Org]

## Role
## Own
## How You Work
## Authority & Boundaries
## Response Style
## Evidence Standard
## Context Rules
## Do Not
```

If the file grows into a mini playbook, shorten it and move detail out.
