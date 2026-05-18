---
name: managing-skills
description: >
  Create, rename, update, or delete Hermes skills — following naming and
  description best practices — and sync all changes to the Skills Registry
  in the Hermes Registry Lark Base.
  Use when user asks to add, rename, update, delete, or audit skills.
triggers:
  - "add a skill"
  - "create a skill"
  - "rename skill"
  - "delete skill"
  - "update skill description"
  - "新增 skill"
  - "刪除 skill"
  - "改 skill 名字"
---

# Managing Skills

## Naming Rules
- **Format**: lowercase, hyphens only — `processing-pdfs`, `managing-databases`
- **Form**: gerund (verb+ing noun) — `tracking-tasks` ✅, `task-tracker` ❌
- **Tool names**: keep as-is — `mcporter`, `himalaya`, `whisper` ✅
- **Avoid**: `helper`, `utils`, `tools`, `data`, `files`

## Description Rules
- Lead with trigger condition: "Use when user says..."
- Include what it does AND when to use it
- **Bad**: "A framework for X that covers Y and Z"
- **Good**: "Use when user says 'generate invoice' — creates Lark Base record, fills template, exports PDF"

## When to Create vs Not
**Create** if: workflow has 3+ steps, has pitfalls/quirks, will be triggered repeatedly
**Don't create** if: one-time fix, single API call, knowledge belongs in GBrain

## Source Classification
| Source | When |
|--------|------|
| `our own` | Built by the team for specific workflows |
| `hermes` | Bundled with Hermes at install |
| `3rd-party` | External tools (Whisper, Marp, etc.) |

## Workflow

### Create
1. `skill_manage(action='create', name='gerund-name', category='...', content='...')`
2. Immediately sync to Skills Registry Lark Base:
   - Fields: Name, Description, Source, Category (Type)
   - Type options: `Sales` / `Finance` / `System` / `Internal` / `Utility` / `Marketing`

### Rename
1. Read old content: `skill_view(name='old-name')`
2. `skill_manage(action='edit', name='old-name', content='...')` — write full content with new `name:` in frontmatter
3. Move directory: `terminal("mv ~/.hermes/skills/.../old-name ~/.hermes/skills/.../new-name")`
4. Update Lark Base record: find by old Name, update Name and Description

### Update Description
1. `skill_manage(action='patch', name='...', old_string='...', new_string='...')`
2. Update Description field in Lark Base record

### Delete
1. `skill_manage(action='delete', name='...')`
2. Delete record from Lark Base (search by Name → get record_id → delete)

## Lark Base
- App token and table IDs: stored in Memory as "Hermes Registry Base"
- Fields: Name (text), Description (text), Source (single select), Category (text)

## Pitfalls
- After rename: patch `name:` inside SKILL.md to match directory name
- `skill_manage(action='delete')` fails if directory name ≠ `name:` field — use `terminal("rm -rf ...")` as fallback
- Keep descriptions generic — use `user says`, not people's names
- Don't save one-time fixes as skills — put them in GBrain instead
