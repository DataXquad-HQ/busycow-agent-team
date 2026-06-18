# Vault Draft Workflow — Drafting GBrain Vault Content from Internal Docs

## When to Use

When one or more GBrain vault files are empty/placeholder and the user asks Leo
to "create a draft" based on existing source documents. Common sources:
- `revenue-strategy-[year].md` (council output)
- `product.md`
- `strategy.md`
- Any rich internal doc in the same BL folder

## Workflow

1. **Read all non-empty source docs in the BL folder first** — in parallel
   (`strategy.md`, `product.md`, `revenue-strategy-*.md`). Never draft from memory alone.

2. **Write draft files to disk** via `write_file` to the vault path
   (`[GBRAIN_VAULT]/internal/business-lines/[bl]/[file].md`).
   GBrain MCP sync will pick them up.

3. **Frontmatter convention for drafts** — always include:
   ```yaml
   ---
   status: draft
   last_updated: YYYY-MM-DD
   source: [source doc name(s)] + "Hunter ([date] session)" if info came from conversation
   review_needed: true
   ---
   ```

4. **Present a summary table** to the user showing what you drafted and what needs review.
   Include specific review questions — not "check everything" but targeted gaps
   (e.g. "Is partner-led confirmed as primary motion, or is there a direct track?").

5. **Apply corrections as patches** — when the user provides corrections mid-session
   (e.g. "vendor is now out, we own the source code"), apply as `patch` calls to
   individual sections. Do NOT rewrite the full file for incremental corrections.

6. **Update `source:` in frontmatter** when conversation-provided context changes the content.
   Add `Hunter ([date] session)` as a source alongside the doc reference.

## Pitfall — `status: work-in-progress` pages in GBrain MCP

Pages with `status: work-in-progress` in frontmatter exist in GBrain but contain
no actionable data (all TBD). Do NOT confuse "page exists in GBrain" with
"page has content". Always check `compiled_truth` for actual content before
relying on a vault page for outreach or scouting context.

## Files to Draft per BL (example using your active BL slug)

| File | Source docs | Key content |
|---|---|---|
| `icp.md` | revenue-strategy | 3 ICP tiers, green/red flags, disqualification signals |
| `gtm.md` | revenue-strategy | Market entry motion, channel structure, growth levers, what we don't do |
| `market.md` | revenue-strategy | TAM/SAM/SOM, country breakdowns, competitive landscape, buying cycle |
| `overview.md` | product.md + revenue-strategy | Status, product tiers, pricing, IP, partners, milestones |

## Strategy Shift Mid-Session

When the user provides a correction that changes the strategic positioning of a product
(e.g. "vendor is out, we own the code now", "this is no longer a primary business",
"partner role has changed"), update the vault files BEFORE updating CRM records.

Reason: CRM opportunity/partnership writes reference the product positioning. If you write
CRM records first with stale positioning, the overview and statusSummary fields will be wrong.

**Order of operations on a strategy shift:**
1. Update `overview.md` (status, current situation)
2. Update `strategy.md` (strategic intent, motions)
3. Update `gtm.md` (channel structure, growth levers, rules)
4. Update `market.md` (entry points, partner routes)
5. Update `product.md` (current status field, partner table)
6. THEN write CRM records with the correct context

**What to patch vs what to rewrite:**
- Single fact changed (vendor out, role upgraded) → `patch` the affected paragraph/field
- Whole strategy reoriented (BusyCow → not primary business) → rewrite the `strategy.md` file
- Partner table changed → patch the specific row in `overview.md` and `gtm.md`

## What NOT to Invent

- Do not fabricate pricing, TAM numbers, partner names, or deal structures
  unless they appear in source docs
- If a section is genuinely unknown, write `TBD` with a note — do not guess
- Flag any section that relies on a single source that may be outdated
