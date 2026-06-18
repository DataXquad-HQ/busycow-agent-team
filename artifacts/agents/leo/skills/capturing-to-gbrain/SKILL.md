---
name: capturing-to-gbrain
description: >
  Use when a piece of information from a conversation is worth preserving as
  long-term knowledge — either because the agent judges it valuable, or the user
  explicitly says to save it to GBrain. Triggers put_page and/or extract_facts.
  Do NOT use for ephemeral task state or one-session fixes — those go in Memory
  or GBrain notes at most.
triggers:
  - "存進 GBrain"
  - "記進長期記憶"
  - "save to brain"
  - "put in gbrain"
  - user explicitly says to remember something permanently
  - agent judges information meets the threshold below
version: "1.0"
author: {{COMPANY_NAME}}/BusyCow
---

# Capturing to GBrain

## Auto-Trigger Events (no user prompt needed)

The following events ALWAYS trigger GBrain writes, without being asked:

| Event | Action |
|-------|--------|
| New contact or company saved to Lark | `put_page people/` or `companies/` |
| Opportunity stage changes | `add_timeline_entry` on company page |
| Partnership stage changes | `add_timeline_entry` on partner page |
| Key decision made in conversation | `put_page decisions/YYYY-MM-DD-topic` |
| Client expresses clear signal (positive/negative/budget/timeline) | `extract_facts` |
| New market / competitor intel shared | `put_page` + `extract_facts` |

These are SOP steps embedded in other skills (`capturing-sales-intel`, `logging-sales-activities`, `managing-partnership-pipeline`). This skill handles standalone captures.

---

## When to Trigger (Agent Judgment — Standalone)

Store when the information is **durable and reusable across future sessions**:

| ✅ Store | ❌ Don't Store |
|---------|--------------|
| New person / company / partner encountered | One-session task state |
| Strategic decision made | Intermediate debug steps |
| Validated fact about a product, market, or competitor | Ephemeral numbers that change weekly |
| New system/process established (e.g. new skill, new cron job design) | Things already in Hermes Memory |
| Key insight from a conversation that would take time to reconstruct | Raw meeting transcripts |
| Relationship context (who knows who, who owns what) | Lark record IDs (those live in Memory) |

**Heuristic:** Would a future session benefit from this being searchable? If yes → store.

---

## Page Types & Slug Conventions

| Content | Type | Slug Pattern |
|---------|------|-------------|
| Company / product | `company` | `busycow/aquaoptima`, `partners/onnet` |
| Person | `person` | `people/daniel-onnet` |
| Strategic analysis | `analysis` | `busycow/busycow-1m-arr-strategy-2026` |
| Market intelligence | `concept` | `market/taiwan-water-utilities` |
| Decision log | `note` | `decisions/YYYY-MM-DD-topic` |
| Competitor intel | `concept` | `competitors/salesforce` |
| Partnership strategy | `concept` | `partnerships/aquaoptima-partner-strategy` |
| System / process doc | `concept` | `systems/hermes-memory-architecture` |
| Venture studio / fund | `company` | `companies/dataxquad-venture-studio` |
| Fund portfolio map | `company` | Nest inside the studio page; use a Portfolio section with a markdown table (Company / Stage / Key Target). Do NOT create separate pages for grooming-stage companies — wait until they have a CEO or active raise. |

---

## Operations to Use

### 1. New or updated page → `mcp_gbrain_put_page`
```yaml
---
title: "Page Title"
type: company  # company | person | concept | note | analysis | system
tags: [tag1, tag2]
---

# Page Title

Body content — compiled truth goes here. Be concise, factual, wiki-style.
No filler. No "as of today" hedging — use timeline for dated entries.
```

### 2. Extract structured facts → `mcp_gbrain_extract_facts`
Use after put_page when the content contains claims, preferences, or commitments.
Pass the page body as `turn_text`. Also use for raw conversation turns with dense facts.

### 3. Add dated event → `mcp_gbrain_add_timeline_entry`
Use when something happened on a specific date (meeting, decision, milestone).
Always include `date` (YYYY-MM-DD), `summary`, optional `detail` and `source`.

### 4. Link pages → `mcp_gbrain_add_link`
Use when a relationship between two entities is established.
Common types: `works_at`, `invested_in`, `advises`, `founded`, `partner_of`

---

## Workflow

1. **Decide** — does this meet the threshold above?
2. **Check if page exists** — `mcp_gbrain_query` or `mcp_gbrain_get_page` to avoid duplicates
3. **If exists** → `put_page` to update (GBrain merges/overwrites)
4. **If new** → `put_page` with full frontmatter
5. **Extract facts** if content has structured claims
6. **Add timeline entry** if something happened on a specific date
7. **Add links** if relationships to other pages are established
8. Confirm to user: "已存入 GBrain：`slug`"

---

## Drafting Vault Content from Internal Docs

When vault files are empty/placeholder, Leo can draft them from existing source documents.
See `references/vault-draft-workflow.md` for the full procedure.

Key conventions:
- Always use `status: draft` + `review_needed: true` frontmatter on drafted files
- Add `source:` field naming the source doc(s) + `Hunter ([date] session)` if conversation context was used
- Apply user corrections as targeted `patch` calls — never rewrite a full file for incremental changes
- `status: work-in-progress` pages in GBrain MCP contain no actionable data — check `compiled_truth`, not just existence

## Pitfalls

- Slugs are lowercase, hyphens only — no spaces, no Chinese characters
- `type` must be one of: `company`, `person`, `concept`, `note`, `analysis`, `system`
- Don't duplicate what's already in Hermes Memory verbatim — GBrain is for structured knowledge, not settings/credentials
- `extract_facts` uses Haiku under the hood — keep `turn_text` focused, not a 5000-word dump
- Always confirm to user after storing so they know it happened

## CLI Fallback When MCP put_page Fails

If `mcp_gbrain_put_page` fails (e.g. embedding dimension mismatch, MCP transport error), fall back to the CLI immediately — do not retry MCP:

**Known error signatures:**
- `expected 768 dimensions, not 1536` — embedding model mismatch between GBrain config and the currently loaded embedding model. MCP layer is broken; CLI bypasses it.
- `internal_error` with no further detail — transport or DB issue; same CLI fallback applies.

```bash
# Write the page content to a temp file, then pipe it to gbrain put
cat > /tmp/<slug-name>.md << 'EOF'
---
title: "Page Title"
type: concept
tags: [tag1, tag2]
---

# Page Title

Body content here.
EOF

gbrain put <slug/path> --type <type> < /tmp/<slug-name>.md
```

The CLI writes directly to the brain database and bypasses the MCP embedding layer. This is the reliable fallback for any MCP write failure.

**If CLI is also unavailable** (not in PATH, gbrain binary missing): fall back to Memory for the most critical facts (key numbers, names, triggers, milestones) using a compact single-line entry. Memory is the last resort — keep it under 300 chars and point to a future GBrain write. Do not skip capture entirely just because GBrain MCP is broken.
