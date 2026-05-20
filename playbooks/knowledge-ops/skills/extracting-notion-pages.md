---
name: extracting-notion-pages
description: Extract content from private Notion pages using the Notion API and convert to markdown. Use when user shares Notion URLs that require authentication, or asks to migrate Notion content to another platform (Lark, GBrain, etc.). Token stored in memory.
version: 1.0.0
metadata:
  hermes:
    tags: [Notion, Migration, Markdown, Knowledge Base]
    related_skills: [lark-docx-writer, managing-team-knowledge]
---

# Extracting Notion Pages

Use the Notion Integration Token (stored in memory) to fetch private pages via the Blocks API and convert to markdown.

## Credentials

Notion API token is stored in Hermes memory. Header pattern:
```
Authorization: Bearer ntn_...
Notion-Version: 2022-06-28
Content-Type: application/json
```

## Core Pattern

Use `execute_code` with the blocks API — `web_extract` cannot access private Notion pages.

```python
import json
from hermes_tools import terminal

NOTION_TOKEN = "ntn_..."  # from memory
HEADERS = f'-H "Authorization: Bearer {NOTION_TOKEN}" -H "Notion-Version: 2022-06-28"'

def get_blocks(block_id):
    result = terminal(f'curl -s {HEADERS} "https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"')
    return json.loads(result["output"])

def extract_text(rich_text_arr):
    return "".join([rt.get("plain_text", "") for rt in rich_text_arr])
```

## Block Type → Markdown Mapping

```python
def blocks_to_markdown(blocks, indent=0):
    lines = []
    prefix = "  " * indent
    for block in blocks:
        btype = block.get("type")
        content = block.get(btype, {})

        if btype == "heading_1":
            lines.append(f"\n# {extract_text(content.get('rich_text', []))}\n")
        elif btype == "heading_2":
            lines.append(f"\n## {extract_text(content.get('rich_text', []))}\n")
        elif btype == "heading_3":
            lines.append(f"\n### {extract_text(content.get('rich_text', []))}\n")
        elif btype == "paragraph":
            text = extract_text(content.get("rich_text", []))
            lines.append(f"{prefix}{text}\n" if text else "")
        elif btype == "bulleted_list_item":
            text = extract_text(content.get("rich_text", []))
            lines.append(f"{prefix}- {text}")
            if block.get("has_children"):
                children = get_blocks(block["id"])
                if "results" in children:
                    lines.append(blocks_to_markdown(children["results"], indent+1))
        elif btype == "numbered_list_item":
            text = extract_text(content.get("rich_text", []))
            lines.append(f"{prefix}1. {text}")
            if block.get("has_children"):
                children = get_blocks(block["id"])
                if "results" in children:
                    lines.append(blocks_to_markdown(children["results"], indent+1))
        elif btype == "toggle":
            text = extract_text(content.get("rich_text", []))
            lines.append(f"\n**{text}**")
            if block.get("has_children"):
                children = get_blocks(block["id"])
                if "results" in children:
                    lines.append(blocks_to_markdown(children["results"], indent+1))
        elif btype == "quote":
            text = extract_text(content.get("rich_text", []))
            lines.append(f"{prefix}> {text}")
        elif btype == "callout":
            text = extract_text(content.get("rich_text", []))
            emoji = content.get("icon", {}).get("emoji", "📌")
            lines.append(f"\n> {emoji} {text}\n")
        elif btype == "divider":
            lines.append("\n---\n")
        elif btype in ("column_list", "column"):
            if block.get("has_children"):
                children = get_blocks(block["id"])
                if "results" in children:
                    lines.append(blocks_to_markdown(children["results"], indent))
        elif btype == "table_of_contents":
            pass  # skip TOC
        elif btype == "child_page":
            lines.append(f"{prefix}📄 [{content.get('title', '')}]")

    return "\n".join(lines)
```

## Extracting Page ID from URL

Notion page URLs end with the page ID (last 32 hex chars, with or without hyphens):
```
https://www.notion.so/Brand-Identity-3450837e356a815d923fcf9eb8c2fa44
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ page_id
```

Strip hyphens if present: `page_id.replace("-", "")`

## Migrating to Lark Docs

After extracting markdown, use `mcp_lark_docx_builtin_import` to create Lark Docs:

```python
mcp_lark_docx_builtin_import(data={
    "file_name": "Page Title",
    "markdown": markdown_content
})
# Returns: {"result": {"token": "...", "url": "https://...larksuite.com/docx/..."}}
```

Batch all 5 pages in parallel (no dependencies between them).

## Pitfalls

### GCP Checklist / Empty Sections in Notion
Notion toggle blocks with empty children (e.g. checklists not yet filled in) come back
as `has_children: true` but with 0 results or placeholder text only.
Preserve them with `*(To be filled in)*` placeholders — don't silently drop them.

### Notion Page vs Block ID
The page URL ID IS the block ID for the root-level blocks call.
No separate "page" API needed — just call `/blocks/{page_id}/children`.

### Lark Wiki — Apps Cannot Be Added as Space Members (Platform Limitation)

This is a hard Lark platform limitation, not a permissions/scope issue:

- **Lark Wiki Space UI only allows adding people, not Apps** — there is no option to search for or add an App in the Space Members UI.
- Even after granting `wiki:wiki` scope, API calls return `permission denied: node permission denied` because the App is not in the Space member list.
- `GET /wiki/v2/spaces` only returns Spaces the App is already a member of — it cannot discover or join new Spaces.
- There is no API endpoint that allows an App to add itself to a Wiki Space it is not already in (chicken-and-egg).

**The only working solution: user manually moves Docs into Wiki**
- In Lark: right-click each Doc → Move → select the BusyCow Wiki Space
- Takes ~30 seconds per doc, no API needed
- After the doc is in Wiki, the App can still edit its content via the docx token (doc content API doesn't need Wiki membership)

**What the App CAN do after docs are in Wiki:**
- Edit doc content via `mcp_lark_docx_builtin_import` or block API using the docx token
- The Wiki is just the navigation shell — content edits go through the doc API, not the wiki API

The MCP tool `mcp_lark_wiki_v2_space_getNode` uses App 1 (`cli_a97bd21895f89e18`).
For direct API calls, use App 2 token (`{{LARK_APP_ID}}` + secret from lark-mcp-setup skill).
Neither can access a Wiki Space they weren't manually added to at Space creation time.
