---
name: writing-blog-post
description: >
  Write a BusyCow blog post from a content intelligence briefing suggestion.
  Use when user replies "寫第N個", "write article", or "幫我寫這篇" after
  receiving a content briefing. Produces a 800–1200 word Traditional Chinese
  article and saves it to the Blog DB.
triggers:
  - "寫第N個"
  - "write article"
  - "幫我寫這篇"
  - "write blog post"
  - "產生文章"
---

# Writing Blog Post

## Blog Base
- **DB Token:** `3480837e`
- Tags zh: `AI趨勢` / `應用情境` / `實際案例` / `導入指南`
- Tags en: `AI Trends` / `Use Cases` / `Case Studies` / `Implementation Guide`
- Always fill: Title, Tags, Status=草稿, Date=today, Slug

## Steps
1. `web_extract` the source article in full
2. `mcp_gbrain_query("BusyCow positioning target audience")` for tone context
3. Write article — see `references/article-structure.md`
4. Save to Blog DB via Lark Base MCP tool
5. Reply: ✅ 已存入 Blog Posts：{標題}（狀態：草稿）

## References
- `references/article-structure.md` — structure, tone, CTA rules
