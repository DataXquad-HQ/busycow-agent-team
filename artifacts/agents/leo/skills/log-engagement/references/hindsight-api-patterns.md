# Hindsight API Patterns — Verified 2026-06-15

Base URL: `http://localhost:8888`
Auth: None (local)

---

## Create a Bank

```bash
# ❌ WRONG — POST returns "Method Not Allowed"
curl -X POST http://localhost:8888/v1/default/banks ...

# ✅ CORRECT — use PUT with bank_id in the path
curl -X PUT http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "name": "{{COMPANY_NAME}} Pipeline Memory",
    "mission": "Description of what this bank stores and why.",
    "disposition": {"skepticism": 3, "literalism": 3, "empathy": 3}
  }'
```

## List All Banks

```bash
curl http://localhost:8888/v1/default/banks
```

Returns array with `bank_id`, `name`, `fact_count`, `last_document_at`.

## Store a Memory

```bash
curl -X POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{
      "content": "CompanyName — 2026-06-15: Had discovery call. Outcome: interested but CFO not looped in yet. Blocker: need CFO intro. Next: Hunter to ask primary contact to arrange intro — by June 20.",
      "tags": ["opportunity", "company-name", "opportunity"]
    }]
  }'
```

## Recall Memories (Semantic Search)

```bash
curl -X POST http://localhost:8888/v1/default/banks/{{ORG_PREFIX}}-pipeline/memories/recall \
  -H "Content-Type: application/json" \
  -d '{"query": "CompanyName opportunity — background and blockers", "top_k": 5}'
```

---

## Bank Design Decisions

### Why `{{ORG_PREFIX}}-pipeline` is a separate bank (not `{{ORG_PREFIX}}-internal`)

`{{ORG_PREFIX}}-internal` is designed for cross-agent handoffs and team-level operational decisions.
If Leo, Iris, Maya all write to `{{ORG_PREFIX}}-internal`, opportunity-level context gets mixed with
unrelated team ops — recall signal degrades.

`{{ORG_PREFIX}}-pipeline` is:
- Opportunity-scoped: every entry is about a specific Opportunity or Partnership
- Multi-agent readable (Leo writes, but any agent can recall)
- Clean signal: only sales context, nothing else

### Bank inventory (as of 2026-06-15)

| Bank | Facts | Purpose |
|---|---|---|
| `{{ORG_PREFIX}}-pipeline` | 0 (new) | Opportunity contextual memory — C4/C5 primary bank |
| `{{ORG_PREFIX}}-global` | 54 | Company-level facts, portfolio, team structure |
| `{{ORG_PREFIX}}-human-[rep-name]` | 12 | Hunter's style and priorities |
| `{{ORG_PREFIX}}-human-[manager-name]` | 16 | Kevin's style and priorities |
| `{{ORG_PREFIX}}-agent-iris` | 10 | Iris working memory |
| `{{ORG_PREFIX}}-agent-leo` | 0 | Leo private working memory |
| `{{ORG_PREFIX}}-internal` | 0 | Cross-agent team ops |
