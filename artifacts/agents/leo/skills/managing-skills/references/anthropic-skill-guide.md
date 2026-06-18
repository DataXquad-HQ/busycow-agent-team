# Anthropic Complete Guide to Building Skills for Claude

Source: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf

---

## What a Skill Contains

```
your-skill-name/
├── SKILL.md          # Required — exact case, no exceptions
├── scripts/          # Optional — Python, Bash, etc. (0 tokens, never auto-loaded)
├── references/       # Optional — docs loaded only when explicitly needed
└── assets/           # Optional — templates, fonts, icons
```

**No README.md inside skill folder** — all docs go in SKILL.md or references/.

---

## Progressive Disclosure (3-Level System)

| Level | Content | When Loaded |
|---|---|---|
| YAML frontmatter | Trigger metadata, name, description | Always (in system prompt) |
| SKILL.md body | Full instructions, steps, pitfalls | When skill is relevant |
| Linked files (references/) | Supplementary docs, API specs | Only when explicitly loaded |

**Design for this model:** keep SKILL.md tight. Move detail to references/.

---

## YAML Frontmatter

**Minimal required:**
```yaml
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

**All optional fields:**
```yaml
name: skill-name
description: [required]
license: MIT
allowed-tools: "Bash(python:*) Bash(npm:*) WebFetch"
metadata:
  author: Company Name
  version: 1.0.0
  category: productivity
  tags: [project-management, automation]
```

**Security restrictions:**
- ❌ No XML angle brackets `< >` anywhere in frontmatter
- ❌ No skills named with `claude` or `anthropic` prefix (reserved)
- Description max: **1024 characters**

---

## Naming Rules

```
✅ managing-tasks        (kebab-case, gerund)
✅ lark-im               (tool name as-is)
❌ ManagingTasks         (no capitals)
❌ managing_tasks        (no underscores)
❌ task-manager          (noun, not gerund)
❌ claude-helper         (reserved prefix)
```

- Lowercase, hyphens only
- Gerund form for action skills (verb+ing)
- Tool names: keep as-is (lark-im, twenty-crm, himalaya)
- Avoid generic suffixes: helper, utils, tools, data, files

---

## Writing Effective Descriptions

**Structure:** `[What it does] + [When to use it] + [Trigger phrases]`

```yaml
# ✅ Good
description: >
  Creates and updates tasks in the Lark task board.
  Use when user says "add a task", "create a task", "新增任務",
  or needs to track a follow-up action.

# ✅ Good — multiple trigger patterns
description: >
  Manages Linear sprint workflows including task creation and status updates.
  Use when user mentions "sprint", "Linear tasks", "create tickets", or
  asks to plan a sprint.

# ❌ Too vague
description: Helps with tasks.

# ❌ Missing triggers
description: Creates sophisticated multi-step task workflows.
```

---

## SKILL.md Structure

```markdown
---
name: your-skill
description: Use when...
---

# Skill Name

## When to Use
[1-2 lines on trigger conditions]

## Steps
1. [First step — be specific]
2. [Second step]
3. [Third step]

## Pitfalls
- [Known failure mode and fix]

## Verification
[How to confirm it worked]
```

---

## Skill Categories

| Category | Purpose | Example |
|---|---|---|
| **Document & Asset Creation** | Consistent output (docs, designs) | `generating-invoices` |
| **Workflow Automation** | Multi-step processes | `managing-tasks` |
| **MCP Enhancement** | Workflow guidance on top of MCP tools | `lark-im`, `twenty-crm` |

---

## When to Create vs Not

**Create if:**
- Workflow has 3+ steps
- Has pitfalls or quirks worth encoding
- Will be triggered repeatedly across sessions
- Saves significant re-explanation

**Don't create if:**
- One-time fix → goes in GBrain
- Single API call → just use the tool
- Already covered by an existing skill
- Pure reference knowledge (no steps) → goes in GBrain

---

## Success Criteria

- Skill triggers on **90%** of relevant queries
- Zero failed API calls per workflow
- New user can accomplish task on first try without extra prompting
- Consistent results across sessions

---

## Composability

Skills work alongside other skills — don't assume exclusivity. Design each skill to do one thing well. If a workflow spans two domains, consider whether it's one skill or a handoff between two.

---

## MCP + Skills Relationship

| MCP | Skills |
|---|---|
| Connects Claude to services | Teaches Claude how to use them |
| Provides tool access (what) | Encodes workflow knowledge (how) |
| Real-time data access | Best practices, pitfalls, steps |

MCP without skills = inconsistent results, no workflow guidance.  
Skills without MCP = instructions with no tools to execute.  
Both together = reliable, repeatable agent behaviour.
