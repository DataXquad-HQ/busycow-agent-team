# Founder Brain Dump Pattern

## When This Applies

The Sales Rep gives a long verbal update covering multiple companies, people, opportunities, and strategic shifts in one message — rather than introducing a single contact. Common after a period of offline activity, a strategy review session, or when the user is "getting Leo up to speed."

## How to Handle

### Step 1 — Extract and categorise before writing anything

Parse the message mentally into buckets:
- **Strategy changes** → GBrain vault files (`internal/business-lines/[bl]/`)
- **New companies** → CRM Company + GBrain `external/entities/companies/`
- **New people** → CRM Person + GBrain `external/entities/people/`
- **New opportunities** → CRM Opportunity
- **New partnerships** → CRM Partnership
- **Context/history** → Hindsight `{{ORG_PREFIX}}-pipeline`

Do NOT start writing until you have the full picture. If the message is ambiguous on ONE critical point (e.g. deal type, partner role), ask that one question first.

### Step 2 — Audit CRM before creating

Always search for existing records before creating new ones. Brain dumps often reference companies already in CRM under partial names (e.g. "SkyDyn" for "Sky Dynamics"). Pattern:
```
for each entity in brain dump:
    search CRM with like "%partial_name%"
    if found: update existing record
    if not found: create new
```

### Step 3 — Write in dependency order

1. Companies (no dependencies)
2. People (depend on Company)
3. Partnerships (depend on Company, optional Person)
4. Opportunities (depend on Company, optional Person)
5. Tasks (depend on Opportunity/Partnership)
6. GBrain pages (independent, can parallelise with CRM)
7. Hindsight memories (last — summarises everything)

### Step 4 — Batch scripts for bulk CRM writes

For 5+ CRM mutations, write a Python script to `/mnt/disks/data/hermes/profiles/leo/workspace/` and run it. Do not do mutations one-by-one via terminal curl — too slow and error-prone. Script template: load token from `.env`, define `gql()` helper, print results with clear section headers.

### Step 5 — Report back in a summary table

After all writes, present:
- What was created/updated in each system (CRM / GBrain / Hindsight)
- Any gaps (missing contact person, incomplete data)
- Time-sensitive items needing tasks

## Common Pitfalls in Brain Dumps

- **One person, two companies** — e.g. Stanley Ng is CEO of AI Cities but primary BD contact via MapKing. Link person to their primary company; note the secondary company in `notes` and GBrain page.
- **Duplicate person stubs** — search by name before creating. If a stub exists (blank jobTitle, no company), enrich it rather than creating a second record, then delete the stub.
- **Strategy shift embedded in an ops update** — if the user signals a change in how a product is positioned or prioritised (e.g. "BusyCow is no longer primary"), update GBrain vault files (`overview.md`, `strategy.md`) before writing CRM records so the ICP and GTM context is current.
- **GBrain vault files may be empty** — when internal business line files are blank stubs, draft them from whatever source docs exist (revenue strategy, product.md) before the session ends. Mark as `status: draft, review_needed: true`.
