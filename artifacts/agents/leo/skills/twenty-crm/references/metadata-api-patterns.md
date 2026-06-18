# Twenty CRM — Metadata API Patterns
*Verified: 2026-06-15*

## Endpoints
- Schema introspection: `POST http://localhost:3001/metadata`
- Data CRUD: `POST http://localhost:3001/graphql`

## Adding a Custom Field to an Existing Object

### Step 1 — Find the object metadata ID
The metadata `/objects` query returns max 10 at a time with no cursor/pagination support.
Use `filter: { id: { notIn: [...known_ids] } }` to paginate manually.

```python
# Page 1
result = meta('{ objects { edges { node { id nameSingular } } } }')

# Page 2 (exclude known IDs)
ids_json = json.dumps(known_ids)
result = meta(f'{{ objects(filter: {{ id: {{ notIn: {ids_json} }} }}) {{ edges {{ node {{ id nameSingular }} }} }} }}')
```

Known object IDs (as of 2026-06-15):
- `person`: `5ae439de-e1d6-40f1-846b-a4b482ad665a`
- `company`: `b77d396f-68cf-4ba4-a4ba-c423eed3a922`
- `opportunity`: `61788876-89f8-4ac5-be6d-3d2fb7111b3c`
- `partnership`: `7ef607fd-6b4d-4b87-ab96-60393f06af33`
- `engagement`: `5de654a0-96b3-484a-b80e-b35b5b276a6d`
- `outreachMessage`: `68c20f74-28b7-4768-af61-ad7b54fc279c`

### Step 2 — Create the field
Mutation is `createOneField` (NOT `createField`). `objectMetadataId` goes INSIDE `field`, not in `input`:

```python
mutation = {
    "query": """
mutation CreateField($input: CreateOneFieldMetadataInput!) {
  createOneField(input: $input) { id name label type }
}
""",
    "variables": {
        "input": {
            "field": {
                "type": "TEXT",           # TEXT | SELECT | DATE_TIME | RICH_TEXT | RELATION
                "name": "myField",        # camelCase
                "label": "My Field",
                "description": "...",
                "objectMetadataId": "OBJECT_UUID"
            }
        }
    }
}
```

### Step 3 — SELECT fields need options as JSON
Pass options via Python variables (not GraphQL literals) to avoid token redaction:

```python
mutation = {
    "query": "mutation CreateField($input: ...) { createOneField(input: $input) { id options } }",
    "variables": {
        "input": {
            "field": {
                "type": "SELECT",
                "name": "mySelect",
                "label": "My Select",
                "objectMetadataId": "OBJECT_UUID",
                "options": [
                    {"value": "OPTION_A", "label": "Option A", "color": "blue", "position": 0},
                    {"value": "OPTION_B", "label": "Option B", "color": "gray", "position": 1},
                ]
            }
        }
    }
}
```

### Step 4 — RELATION fields
```python
"variables": {
    "input": {
        "field": {
            "type": "RELATION",
            "name": "recipient",
            "label": "Recipient",
            "objectMetadataId": SOURCE_OBJECT_ID,
            "relationCreationPayload": {
                "type": "MANY_TO_ONE",
                "targetObjectMetadataId": TARGET_OBJECT_ID,
                "targetFieldLabel": "Outreach Messages",
                "targetFieldIcon": "IconMail"
            }
        }
    }
}
```

## Adding an Enum Value to an Existing SELECT Field

### Step 1 — Find the field ID
The `/fields` query also caps at 10. Use `filter: { objectMetadataId: { eq: "..." }, isCustom: { is: true } }` and paginate via `id: { notIn: [...known_ids] }`.

### Step 2 — Update with full options array (must include ALL existing options)
```python
update_mutation = {
    "query": "mutation UpdateField($input: UpdateOneFieldMetadataInput!) { updateOneField(input: $input) { id name options } }",
    "variables": {
        "input": {
            "id": "FIELD_UUID",
            # NOTE: objectMetadataId is NOT part of UpdateOneFieldMetadataInput
            "update": {
                "options": [
                    # include ALL existing options + new one
                    {"value": "EXISTING", "label": "Existing", "color": "blue", "position": 0},
                    {"value": "NEW_VALUE", "label": "New Value", "color": "purple", "position": 1},
                ]
            }
        }
    }
}
```

## Creating a Custom Object

```python
mutation = {
    "query": """
mutation {
  createOneObject(input: {
    object: {
      nameSingular: "myObject"
      namePlural: "myObjects"
      labelSingular: "My Object"
      labelPlural: "My Objects"
      description: "..."
      icon: "IconMail"
    }
  }) { id nameSingular }
}
"""
}
```
Returns the new object's metadata ID — save it immediately for subsequent field creation calls.

## Pitfalls
- **Mutation is `createOneField` not `createField`** — the error message helpfully suggests the right name
- **`objectMetadataId` goes inside `field`, not in `input`** — for create
- **`objectMetadataId` does NOT exist in `UpdateOneFieldMetadataInput`** — for update, only `id` + `update` are valid
- **`/objects` caps at 10, no cursor/after argument** — use notIn filter to paginate
- **`/fields` also caps at 10** — same workaround
- **BooleanFieldComparison uses `is`/`isNot`, not `eq`** — `isCustom: { is: true }` not `isCustom: { eq: true }`
- **SELECT options must include ALL existing options** — partial update replaces the whole array
- **RICH_TEXT fields use `bodyV2: { markdown: "..." }`** — NOT `body: "..."` and NOT `bodyV2: { blocks: [...] }`
