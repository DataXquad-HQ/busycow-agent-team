# Schemas

Structural data definitions for the operational systems agents read and write.

Each file in this directory defines the schema for one system: object types, field names, field IDs, and usage conventions.

## Files

| File | System | Purpose |
|---|---|---|
| `crm.md` | Twenty CRM | Opportunity, contact, company object schemas |
| `task-board.md` | Lark Base | Task tracker field definitions and IDs |

## Convention

- Use `{{PLACEHOLDER}}` for any instance-specific IDs
- Each schema file documents both the object structure and how agents are expected to use it
- When a field is added or changed in a live instance, update the schema here too
