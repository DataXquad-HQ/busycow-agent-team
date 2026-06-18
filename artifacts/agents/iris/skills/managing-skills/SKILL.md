---
name: managing-skills
description: >
  Use when creating, updating, renaming, or deleting any Hermes skill — private or shared.
  Before writing any skill, load skill-creator and follow it.
  If the skill should be available to all agents, follow the shared skill SOP in this file.
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

**Load skill-creator first:**
```
skill_view(name='skill-creator')
```

Follow those guidelines for structure, naming, description, Quality Bar, and Fallback Behavior.
The quick rules below are a summary — skill-creator is authoritative.

---

## Quick Rules (summary of skill-creator)

**Naming:** lowercase kebab-case, gerund form — `processing-pdfs` ✅, `task-tracker` ❌  
**Description:** lead with "Use when..." + trigger phrases + key capabilities. Max 1024 chars.  
**Structure:** `SKILL.md` (exact case) + optional `scripts/`, `references/`, `assets/`  
**Token budget:** SKILL.md body < 500 lines target; details go in `references/`  
**Create if:** 3+ steps, has pitfalls, triggered repeatedly  
**Don't create if:** one-time fix, single API call, already covered, or knowledge belongs in GBrain

**Mandatory sections for analytical skills:**
- `## Quality Bar` — self-check before returning output (domain-specific, not just the base template)
- `## Fallback Behavior` — name each external dependency explicitly (CRM, GBrain, Hindsight, email)

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
| **Canonical shared source** | `~/.hermes/skills/<category>/<skill>/` | Iris governance layer |
| **Agent runtime copy** | `~/.hermes/profiles/<agent>/skills/<skill>/` | That agent only at runtime |
| **Agent private** | `~/.hermes/profiles/<agent>/skills/<skill>/` (when not shared) | That agent only |

### SOP — Making a skill shared

Use a **canonical-source + per-profile copies** pattern.

**When to use this pattern:**
- the skill should be available to multiple agent profiles
- each profile may need small local edits later
- the skill will eventually be packaged to GitHub / `artifacts/agents/<agent>/skills/` or `artifacts/shared-skills/`
- you want profile isolation at runtime

**1. Create the canonical source** in `~/.hermes/skills/<category>/<skill-name>/` as usual.

**2. Distribute by copy, not runtime symlink**:

```bash
cp -r ~/.hermes/skills/<category>/<skill-name> ~/.hermes/profiles/leo/skills/<skill-name>
cp -r ~/.hermes/skills/<category>/<skill-name> ~/.hermes/profiles/maya/skills/<skill-name>
cp -r ~/.hermes/skills/<category>/<skill-name> ~/.hermes/profiles/rex/skills/<skill-name>
```

This makes the shared skill available everywhere while preserving profile isolation.
Each profile copy can later stay identical, or become an agent-local fork if needed.

**3. Treat the canonical source as governance layer; profile copies as runtime layer.**
- Canonical source = what Iris maintains
- Profile copy = what the agent actually loads in its own Hermes home

**4. Re-sync intentionally when the canonical skill changes.**
If the change should propagate to every agent, copy it out again to each profile.
If a profile has intentionally diverged, review before overwriting.

**5. Package distribution uses real files, not symlinks.**
For GitHub / package repos, always place concrete copies under `artifacts/agents/<agent>/skills/` or `artifacts/shared-skills/<skill>/`.

**Optional local-only mode: symlink registry**
If you explicitly want one edit to affect every profile immediately, you may maintain a local symlink-based registry. This is acceptable for experiments, but it is not the default operational pattern for multi-agent package workflows because the blast radius is larger.

---

## Lark Base — Skills Registry

- **App token**: `{{SKILLS_REGISTRY_APP_TOKEN}}`
- **Table**: `{{SKILLS_REGISTRY_TABLE_ID}}`
- **Fields**: Name (text), Description (text), Source (single select), Type (single select)

---

## SOUL.md Standards

When building or updating a SOUL.md, load the standards reference:
```
skill_view(name='managing-skills', file_path='references/soul-md-standards.md')
```
Covers: required `## Evidence Standard` + `## Do Not` sections, templates for each,
agent-specific Do Not additions, and the canonical section order.

### Persona-wide style changes belong in SOUL, not user memory
If the user says a response style is **who the agent should be** rather than a one-user preference
(e.g. "you should answer conclusion-first", "this is your style", "don't store this as my preference"),
update the active agent's `SOUL.md` instead of saving it to user memory. Use memory only when the
preference is actually user-specific and should follow that person across different agents.

---

## Pitfalls

- After rename: patch `name:` in frontmatter too — directory name ≠ name field
- `skill_manage(action='delete')` may return "not found" if dir name ≠ frontmatter name — use `terminal("rm -rf ...")` as fallback
- Descriptions: no person names — `user says`, not `Hunter says`
- One-time fixes → GBrain, not a skill
- Circular symlink: bash `ln -sf $PATH/$skill $PATH/$skill` self-references. Always use Python `os.symlink()` with absolute target paths if you intentionally use symlinks.
- Agent profile skills are NOT backed up by nightly brain sync — lost on profile delete
- **Default operational pattern for shared skills = canonical source + per-profile copies.** Keep the maintained source under `~/.hermes/skills/`, then copy into each profile's `skills/` directory for runtime use.
- **Symlink-based sharing is optional and best treated as a local experiment / fast-propagation mode, not the main production pattern** for multi-agent package workflows. One mistaken edit changes every linked profile at once.
- **Distributing a skill to multiple agents = copy, not symlink.** The canonical pattern is `cp -r skill-dir ~/.hermes/profiles/[agent]/skills/skill-dir`. For package distribution, always use direct copies in `artifacts/agents/<agent>/skills/` or `artifacts/shared-skills/<skill>/`.
- **`skill-creator` is the new authoritative skill-building reference** — `references/anthropic-skill-guide.md` is deprecated. Any skill that still loads the old guide via `file_path='references/anthropic-skill-guide.md'` should be patched to `skill_view(name='skill-creator')` instead.
- **Writing to another agent's profile requires `cross_profile=True`** — `write_file` and `patch` tools block cross-profile writes by default. When creating or updating a skill in `~/.hermes/profiles/<agent>/skills/`, always pass `cross_profile=True`. This is a soft guard (not a security boundary), but will hard-block without it.
- **Infrastructure skills need to exist independently in EACH agent profile** — do not assume shared skills or package copies are loaded at runtime. If Leo needs `openmail` and Iris needs `openmail`, write both. They can differ in scope (e.g. Leo = send+read, Iris = read-only).
