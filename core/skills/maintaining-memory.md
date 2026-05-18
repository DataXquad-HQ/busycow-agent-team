---
name: maintaining-memory
description: >
  Framework for deciding what goes in Memory vs Skills vs GBrain.
  Use when deciding where to store new information, cleaning up memory,
  or explaining the knowledge routing architecture.
triggers:
  - user asks what should go in memory
  - memory is getting full or cluttered
  - deciding where to store new information
  - cleaning up or restructuring memory
---

# Maintaining Memory

## The Four Layers

```
Layer 1: Memory (MEMORY.md)        ← Always injected, every turn
Layer 2: Skills                    ← Loaded on demand by trigger
Layer 3: GBrain                    ← Queried on demand (SSOT)
Layer 4: Session Search            ← Past conversation recall
```

**Core principle**: Memory should be as lean as possible. GBrain is the main knowledge base.

---

## What Goes Where

### Memory ✅
- Environment facts (base tokens, channel IDs, VM IPs)
- User preferences needed every session (language, style)
- Stable credentials pointer (e.g. "Hermes Registry Base: [token]")
- **One-line rule**: if it can't be said in one line, it doesn't belong here

### Skills ✅
- Any workflow with 3+ steps
- Format rules, ID conventions, required fields
- Anything you'd need to re-read before doing the task

### GBrain ✅
- People, companies, projects, decisions
- Business intelligence and market research
- Anything descriptive/narrative about the business
- Long-form reference content

### Nowhere ❌
- Task progress and session outcomes
- Intermediate debug steps
- Process logs ("we did X today")

---

## Pre-Check Before Every Write

```
Is it a repeatable SOP or format rule? → Skill
Is it a person/company/decision/intel? → GBrain
Is it an env fact needed every session? → Memory (one-liner)
Is it task state or a one-off fix?     → Nowhere
```

---

## GBrain Slug Conventions

| Content | Slug Pattern |
|---------|-------------|
| Person | `people/firstname-lastname` |
| Company | `companies/company-shortname` |
| Partner | `partners/partner-shortname` |
| Decision | `decisions/YYYY-MM-DD-topic` |
| Project | `projects/project-name` |
| Market intel | `market/topic` |

---

## Cleaning Up Memory

When memory is full or cluttered:
1. Read current: `cat ~/.hermes/memories/MEMORY.md`
2. For each entry: is this a one-liner credential/fact, or a description/playbook?
3. Move descriptive content → GBrain
4. Move playbook content → Skills
5. Rewrite with `write_file` if the memory tool's char limit blocks edits

---

## Memory Size Config

In `~/.hermes/config.yaml`:
```yaml
memory:
  memory_char_limit: 4000
  user_char_limit: 2000
```

Defaults are often too small for real business use. Adjust as needed.
