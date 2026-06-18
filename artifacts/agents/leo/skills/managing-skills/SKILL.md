---
name: managing-skills
description: >
  Use when creating, updating, renaming, or deleting any skill — private or shared.
  Before writing any skill, load skill-creator and follow it.
  For cron architecture patterns (two-channel delivery, channel IDs, naming rules),
  load references/cron-architecture.md. If the skill should be available to all agents,
  follow the shared skill SOP in this file.
triggers:
  - "create a skill"
  - "add a skill"
  - "rename skill"
  - "delete skill"
  - "update skill"
  - "make this a shared skill"
  - "add skill"
  - "create skill"
  - "delete skill"
  - "shared skill"
version: "2.0"
---

# Managing Skills

## Step 0 — Before writing any skill

**Load and read the guide first:**
```
skill_view(name='skill-creator')
```

Follow those guidelines for structure, naming, description, and frontmatter.
The quick rules below are a summary — the reference is authoritative.

---

## Quick Rules (summary of guide)

**Naming:** lowercase kebab-case, gerund form — `processing-pdfs` ✅, `task-tracker` ❌  
**Description:** lead with "Use when..." + trigger phrases + key capabilities. Max 1024 chars.  
**Structure:** `SKILL.md` (exact case) + optional `scripts/`, `references/`, `assets/`  
**Token budget:** SKILL.md body < 1k tokens target; details go in `references/`  
**Create if:** 3+ steps, has pitfalls, triggered repeatedly  
**Don't create if:** one-time fix, single API call, already covered, or knowledge belongs in GBrain

---

## Workflow

### Create
1. Read the guide (Step 0 above)
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
| **Canonical source** | `~/.hermes/skills/<category>/<skill>/` | Operator-maintained source of truth |
| **Agent runtime copy** | `~/.hermes/profiles/<agent>/skills/<skill>/` | That agent only |

### SOP — Making a skill shared

**1. Create the canonical skill** in `~/.hermes/skills/<category>/<skill-name>/`.

**2. Copy it into each agent profile that should use it** (real directory, no symlinks):

```python
# /tmp/copy_skill.py
import os, shutil

HOME = os.path.expanduser("~")
SKILL_NAME = "my-skill"
SRC = os.path.join(HOME, ".hermes/skills/category", SKILL_NAME)

for agent in ["leo", "maya", "rex"]:
    dst = os.path.join(HOME, f".hermes/profiles/{agent}/skills", SKILL_NAME)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(SRC, dst)
    print(f"OK {agent}: {dst}")
```

**3. Verify:**
```python
import os
skill = "my-skill"
for agent in ["leo", "maya", "rex"]:
    p = f"{os.path.expanduser('~')}/.hermes/profiles/{agent}/skills/{skill}"
    print(f"{agent}: {'OK' if os.path.isdir(p) else 'MISSING'}")
```

---

## Skills Registry

- **App token**: `{{SKILLS_REGISTRY_APP_TOKEN}}`
- **Table**: `{{SKILLS_REGISTRY_TABLE_ID}}`
- **Fields**: Name (text), Description (text), Source (single select), Type (single select)

---

## Pitfalls

- After rename: patch `name:` in frontmatter too — directory name ≠ name field
- `skill_manage(action='delete')` may return "not found" if dir name ≠ frontmatter name — use `terminal("rm -rf ...")` as fallback
- Descriptions: no person names — `user says`, not `the sales rep says`
- One-time fixes → GBrain, not a skill
- Do not use `_shared/` symlink trees or `shared_skills/` registries — the live model is canonical source + per-profile copies
- Agent profile skills are NOT backed up by nightly brain sync — lost on profile delete