---
name: capturing-to-gbrain
description: >
  Use when a piece of information from a conversation is worth preserving as
  long-term knowledge. Triggers put_page and/or extract_facts. Do NOT use for
  ephemeral task state — those stay in Memory or nowhere.
triggers:
  - user explicitly says to save something permanently
  - new person or company encountered
  - key decision reached
  - new market or competitor intel shared
  - agent judges information is durable and reusable
---

# Capturing to GBrain

## When to Store

| ✅ Store | ❌ Don't Store |
|---------|--------------|
| New person / company / partner | One-session task state |
| Strategic decision made | Intermediate debug steps |
| Validated fact about product or market | Things already in Memory |
| Relationship context (who knows who) | Raw meeting transcripts |
| Key insight worth finding later | Ephemeral numbers that change weekly |

**Heuristic:** Would a future session benefit from this being searchable? If yes → store.

---

## Page Types & Slug Conventions

| Content | Type | Slug |
|---------|------|------|
| Company | `company` | `companies/name` |
| Person | `person` | `people/firstname-lastname` |
| Partner | `company` | `partners/name` |
| Decision | `note` | `decisions/YYYY-MM-DD-topic` |
| Market intel | `concept` | `market/topic` |
| Competitor | `concept` | `competitors/name` |
| Analysis | `analysis` | `projects/name-analysis` |

---

## Operations

### 1. New or updated page → `mcp_gbrain_put_page`
```yaml
---
title: "Page Title"
type: company  # company | person | concept | note | analysis
tags: [tag1, tag2]
---

Body — concise, factual, wiki-style. No filler.
```

### 2. Extract structured facts → `mcp_gbrain_extract_facts`
Use after put_page when content contains claims or commitments.
Pass the page body or relevant conversation turn as `turn_text`.

### 3. Add dated event → `mcp_gbrain_add_timeline_entry`
Use when something happened on a specific date.
Always include `date` (YYYY-MM-DD), `summary`, optional `detail`.

### 4. Link pages → `mcp_gbrain_add_link`
Use when a relationship between entities is established.
Common types: `works_at`, `partner_of`, `founded`, `invested_in`

---

## Workflow

1. Does this meet the threshold above?
2. Check if page exists: `mcp_gbrain_query` or `mcp_gbrain_get_page`
3. If exists → `put_page` to update
4. If new → `put_page` with full frontmatter
5. Extract facts if content has structured claims
6. Add timeline entry if something happened on a specific date
7. Add links if relationships are established
8. Confirm: "Saved to GBrain: `slug`"

---

## Pitfalls
- Slugs: lowercase, hyphens only — no spaces, no non-Latin characters
- `type` must be one of: `company`, `person`, `concept`, `note`, `analysis`
- Don't duplicate what's already in Memory verbatim
- Keep `extract_facts` turn_text focused — not a 5000-word dump
