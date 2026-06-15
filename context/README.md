# Context Schemas

Data schema definitions for the structural data layer — the operational systems agents read and write.

Each file in this directory defines the schema for one system: object types, field names, field IDs, and usage conventions.

## Files

| File | System | Purpose |
|---|---|---|
| `crm.md` | Twenty CRM | Deal, contact, company object schemas |
| `task-board.md` | Lark Base | Task tracker field definitions and IDs |

## Convention

- Use `{{PLACEHOLDER}}` for any instance-specific IDs (Lark Base IDs, app tokens, etc.)
- Each schema file documents both the object structure and how agents are expected to use it
- When a field is added or changed in a live instance, update the schema here too
