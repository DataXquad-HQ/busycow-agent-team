---
name: managing-skills
description: >
  Use when creating, updating, renaming, or deleting any Hermes skill — private or shared.
  Before writing any skill, load skill-creator and follow it.
  For Leo cron architecture patterns (two-channel delivery, channel IDs, naming rules),
  load references/leo-cron-architecture.md. If the skill should be available to all agents,
  follow the shared skill SOP in this file.
triggers:
  - "create a skill"
  - "add a skill"
  - "rename skill"
  - "delete skill"
  - "update skill"
  - "make this a shared skill"
  - "新增 skill"
  - "建立 skill"
  - "刪除 skill"
  - "shared skill"
version: "2.0"
---

# Managing Skills

## Step 0 — Before writing any skill

**Load and read the Anthropic guide first:**
```
skill_view(name='skill-creator')
```

Follow those guidelines for structure, naming, description, and frontmatter.
The quick rules below are a summary — the reference is authoritative.

---

## Quick Rules (summary of Anthropic guide)

**Naming:** lowercase kebab-case, gerund form — `processing-pdfs` ✅, `task-tracker` ❌  
**Description:** lead with "Use when..." + trigger phrases + key capabilities. Max 1024 chars.  
**Structure:** `SKILL.md` (exact case) + optional `scripts/`, `references/`, `assets/`  
**Token budget:** SKILL.md body < 1k tokens target; details go in `references/`  
**Create if:** 3+ steps, has pitfalls, triggered repeatedly  
**Don't create if:** one-time fix, single API call, already covered, or knowledge belongs in GBrain

---

## Workflow

### Create
1. Read Anthropic guide (Step 0 above)
2. `skill_manage(action='create', name='gerund-name', category='...', content='...')`

### Rename
1. `skill_view(name='OLD')` to get full content
2. `skill_manage(action='edit', name='OLD', content='...')` — set new `name:` in frontmatter
3. `terminal("mv ~/.hermes/skills/.../old-name ~/.hermes/skills/.../new-name")`

### Update
1. `skill_manage(action='patch', name='...', old_string='...', new_string='...')`

### Delete
1. `skill_manage(action='delete', name='...', absorbed_into='...' or '')`

---
| Tier | Location | Visible to |
|---|---|---|
| **Iris private** | `~/.hermes/skills/<category>/<skill>/` | Iris only |
| **Shared** | `~/.hermes/shared_skills/<skill>` (registry) + agent `_shared/` symlinks | All agents + Iris |
| **Agent private** | `~/.hermes/profiles/<agent>/skills/<skill>/` (real dir) | That agent only |

### SOP — Making a skill shared

**1. Create the skill** in `~/.hermes/skills/<category>/<skill-name>/` as usual.

**2. Register + symlink using Python** (never bash loops — produces circular symlinks):

```python
# /tmp/link_skill.py
import os

HOME = os.path.expanduser("~")
SKILL_NAME = "my-skill"
SKILL_SRC = HOME + "/.hermes/skills/category/" + SKILL_NAME
SHARED = HOME + "/.hermes/shared_skills"

# Register in shared_skills/
link = SHARED + "/" + SKILL_NAME
if os.path.lexists(link): os.unlink(link)
os.symlink(SKILL_SRC, link)

# Symlink into each agent profile (point directly to source)
for agent in ["leo", "maya", "rex"]:
    agent_link = HOME + f"/.hermes/profiles/{agent}/skills/_shared/{SKILL_NAME}"
    if os.path.lexists(agent_link): os.unlink(agent_link)
    os.symlink(SKILL_SRC, agent_link)
    print(f"{'OK' if os.path.isdir(agent_link) else 'FAIL'} {agent}")
```

**3. Verify:**
```python
import os
skill = "my-skill"
for agent in ["leo", "maya", "rex"]:
    p = f"{os.path.expanduser('~')}/.hermes/profiles/{agent}/skills/_shared/{skill}"
    print(f"{agent}: {'OK' if os.path.isdir(p) else 'BROKEN'}")
```

---

## Lark Base — Skills Registry

- **App token**: `{{SKILLS_REGISTRY_APP_TOKEN}}`
- **Table**: `{{SKILLS_REGISTRY_TABLE_ID}}`
- **Fields**: Name (text), Description (text), Source (single select), Type (single select)

---

## Pitfalls

- After rename: patch `name:` in frontmatter too — directory name ≠ name field
- `skill_manage(action='delete')` may return "not found" if dir name ≠ frontmatter name — use `terminal("rm -rf ...")` as fallback
- Descriptions: no person names — `user says`, not `Hunter says`
- One-time fixes → GBrain, not a skill
- Circular symlink: bash `ln -sf $PATH/$skill $PATH/$skill` self-references. Always use Python `os.symlink()` with absolute target paths
- Agent profile skills are NOT backed up by nightly brain sync — lost on profile delete
