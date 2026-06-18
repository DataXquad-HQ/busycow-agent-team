# Legacy Base Goals/Initiatives → Lark Default Tasks OKR Migration

Use this when DataXquad wants to retire or de-emphasize the old Base-backed planning structure but keep its strategic content.

## Target structure

- **OKR / planning list (default Lark Tasks)**
  - top-level task = former Base **Goal**
  - subtask = former Base **Initiative**
- **Execution list (default Lark Tasks)**
  - operational work only
  - link each execution task back to planning via custom fields such as `Objective` and `KR`

Do **not** keep writing live execution into the old Base if the team has already declared default Lark Tasks the execution system of record.

## Migration pattern

1. Read legacy Base `Goals` and `Initiatives`.
2. Convert each **Goal** into a top-level task in the OKR list.
   - Task title = human-readable goal title
   - Description should preserve:
     - business line
     - status
     - success metric
     - original notes
   - Due date can carry over from Base target date if present.
3. Convert each **Initiative** into a subtask under its parent Goal.
   - Preserve:
     - business line
     - linked goal name
     - type
     - status
     - notes
     - target finished date when present
4. If the new OKR list already contains placeholder tasks, **reuse and patch** them instead of creating duplicates.
5. Rebuild the execution-task mapping only **after** the planning/OKR structure is cleaned up.

## Important Lark Task API behavior

`tasklists.tasks` can return tasks that are also visible as subtasks in the same list.

So when validating hierarchy:
- do **not** assume every item returned by `tasklists.tasks` is a top-level OKR item
- check `parent_task_guid` via `task.tasks.get`
- or call `task.subtasks.list` on known parent goals to reconstruct the intended Goal → Initiative tree

In other words: **the authoritative hierarchy is `parent_task_guid`, not the flat task-list response alone**.

## Execution mapping pattern

After migration:
- keep execution tasks in a separate list
- use custom fields (for example `Objective`, `KR`) to map execution work back to planning
- rename custom-field options from placeholder labels to real company language before remapping tasks

Good pattern:
- Objective option = goal-level label
- KR option = initiative / workstream label

## Pitfalls

- Do not preserve fake placeholder OKRs once real company goals exist.
- Do not map execution tasks before the goal/initiative vocabulary is stabilized.
- Do not treat all rows from `tasklists.tasks` as top-level goals.
- Do not create duplicate initiatives if an existing placeholder task can be patched and re-parented.
- Do not force a mathematically strict OKR format too early; `Goal + Initiative` can be the correct transitional shape when the company first needs alignment with real work.

## Recommended output to user

Keep the migration summary short:
- how many goals were migrated
- how many initiatives were attached
- whether execution tasks were remapped
- what still needs manual review
