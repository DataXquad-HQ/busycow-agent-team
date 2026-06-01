---
name: lark-docx-writer
description: Create and write structured Lark/Feishu Docs (docx) via API. Covers document creation, block types (heading1/2/3, paragraph, bullet), and writing content programmatically. Use when asked to create a Lark document with structured content (headings, bullets, paragraphs).
version: 1.0.0
author: BusyCow/BusyCow
metadata:
  hermes:
    tags: [Lark, Feishu, Docs, Document, API, Writing]
---

# Lark Docx Writer

Create and write structured Lark/Feishu documents (docx) via the open API.

## Auth

Same tenant access token pattern as all Lark APIs:

```python
import urllib.request, json, os

env = open(os.path.expanduser("~/.hermes/.env")).read()
app_id, app_secret = "", ""
for line in env.split("\n"):
    if line.startswith("FEISHU_APP_ID="): app_id = line.split("=",1)[1].strip()
    if line.startswith("FEISHU_APP_SECRET="): app_secret = line.split("=",1)[1].strip()

req = urllib.request.Request(
    "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
    headers={"Content-Type": "application/json"}, method="POST"
)
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read()).get("tenant_access_token", "")
```

## Step 1: Create Document

```python
doc_payload = {"title": "你的文件標題"}
req = urllib.request.Request(
    "https://open.larksuite.com/open-apis/docx/v1/documents",
    data=json.dumps(doc_payload).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())

doc_id = data["data"]["document"]["document_id"]
# URL: https://bytedance.larkoffice.com/docx/{doc_id}
```

## Step 2: Add Blocks

Use `doc_id` as both the document ID and the root `parent_id` for top-level blocks.

To **append** (add at end), omit `index`. To **insert at a specific position**, pass `"index": N` in the body — blocks are zero-indexed within the parent's children list.

```python
def add_block(parent_id, block_type_int, payload, index=None):
    body = {"children": [{"block_type": block_type_int, **payload}]}
    if index is not None:
        body["index"] = index
    req = urllib.request.Request(
        f"https://open.larksuite.com/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    children = data.get("data", {}).get("children", [])
    return children[0].get("block_id") if children else None
```

You can also pass a **batch of blocks** in one call (more efficient for large inserts):

```python
def insert_blocks_at(parent_id, index, children_list):
    """Insert multiple blocks at a specific index in one API call."""
    body = {"children": children_list, "index": index}
    req = urllib.request.Request(
        f"https://open.larksuite.com/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
```

**Index stability warning:** When inserting at multiple positions in the same document, insert from **higher index to lower** — or re-fetch block list between calls — to avoid index shift invalidating subsequent insertions.

## Block Type Reference

| Block Type | Integer Code | Payload Key |
|------------|-------------|-------------|
| Paragraph (plain text) | 2 | `"text"` |
| Heading 1 | 3 | `"heading1"` |
| Heading 2 | 4 | `"heading2"` |
| Heading 3 | 5 | `"heading3"` |
| Bullet list item | 12 | `"bullet"` |
| Ordered list item | 13 | `"ordered"` |
| Code block | 14 | `\"code\"` |
| Image | 27 | `\"image\"` |

## Helper Functions

```python
def heading1(parent_id, text):
    return add_block(parent_id, 3, {
        "heading1": {"elements": [{"text_run": {"content": text}}]}
    })

def heading2(parent_id, text):
    return add_block(parent_id, 4, {
        "heading2": {"elements": [{"text_run": {"content": text}}]}
    })

def heading3(parent_id, text):
    return add_block(parent_id, 5, {
        "heading3": {"elements": [{"text_run": {"content": text}}]}
    })

def paragraph(parent_id, text):
    return add_block(parent_id, 2, {
        "text": {"elements": [{"text_run": {"content": text}}]}
    })

def bullet(parent_id, text):
    return add_block(parent_id, 12, {
        "bullet": {"elements": [{"text_run": {"content": text}}]}
    })
```

## Usage Pattern

```python
root_id = doc_id  # top-level parent = doc_id itself

heading1(root_id, "第一章")
paragraph(root_id, "這是說明文字")
heading2(root_id, "1.1 子章節")
bullet(root_id, "第一個要點")
bullet(root_id, "第二個要點")
paragraph(root_id, "")  # blank line spacer
```

## Get Feishu Chat ID List (bonus utility)

Useful for finding deliver targets:

```python
req = urllib.request.Request(
    "https://open.larksuite.com/open-apis/im/v1/chats?page_size=50",
    headers={"Authorization": f"Bearer {token}"}, method="GET"
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
for item in data.get("data", {}).get("items", []):
    print(f"{item.get('name')} -> {item.get('chat_id')}")
```

## Document URL

```
https://bytedance.larkoffice.com/docx/{doc_id}
```

## Deleting Blocks

To delete a range of blocks, use `batch_delete` on the **parent** block, specifying `start_index` and `end_index` (exclusive):

```python
# Step 1: Get all blocks to find parent and indices
req = urllib.request.Request(
    f"https://open.larksuite.com/open-apis/docx/v1/documents/{doc_id}/blocks?page_size=500",
    headers={"Authorization": f"Bearer {token}"}, method="GET"
)
with urllib.request.urlopen(req) as resp:
    items = json.loads(resp.read()).get("data", {}).get("items", [])

# Step 2: Find parent block and index of the block you want to delete
for item in items:
    children = item.get("children", [])
    if "TARGET_BLOCK_ID" in children:
        parent_id = item.get("block_id")
        start_idx = children.index("TARGET_BLOCK_ID")
        count = 4  # number of consecutive blocks to delete
        break

# Step 3: Delete by parent + index range
body = {"start_index": start_idx, "end_index": start_idx + count}
req = urllib.request.Request(
    f"https://open.larksuite.com/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children/batch_delete",
    data=json.dumps(body).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="DELETE"
)
with urllib.request.urlopen(req) as resp:
    print(json.loads(resp.read()))
```

**⚠️ Do NOT use** `DELETE /docx/v1/documents/{doc_id}/blocks/batch_delete` — that endpoint returns 404. The correct URL is on the **parent block's children**.

## Image Blocks

Images require a two-step process: upload the file to Feishu Drive, then insert the image block.

### Step 1: Upload image via curl (most reliable)

```bash
TOKEN="your_tenant_access_token"
DOC_ID="your_doc_id"

curl -s -X POST \
  "https://open.larksuite.com/open-apis/drive/v1/medias/upload_all" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=png" \
  -F "file_name=image.png" \
  -F "size=$(wc -c < /path/to/image.png)" \
  -F "parent_type=docx_image" \
  -F "parent_node=$DOC_ID" \
  -F "file=@/path/to/image.png;type=image/png"
# Returns: {"code":0,"data":{"file_token":"U8TEbXXXXX"},...}
```

⚠️ **`parent_type=docx_image` and `parent_node=<doc_id>` are REQUIRED** — omitting them causes HTTP 400.

### Step 2: Insert image block

```python
image_block = {
    "block_type": 27,
    "image": {
        "file_token": "U8TEbXXXXX"   # ⚠️ field is "file_token", NOT "token"
    }
}
insert_blocks_at(doc_id, index, [image_block])
```

⚠️ **`file_token` not `token`** — using `"token"` returns HTTP 400 "invalid param".  
⚠️ Do NOT pass `width`/`height` in the block body — also causes 400. Lark auto-sizes.

---

## Patching Existing Block Text

To update the text content of an existing block (without deleting/re-inserting):

```python
def patch_text(block_id, new_text, bold=False):
    style = {"bold": bold} if bold else {}
    body = {
        "update_text_elements": {
            "elements": [{"text_run": {"content": new_text, "text_element_style": style}}]
        }
    }
    req = urllib.request.Request(
        f"https://open.larksuite.com/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="PATCH"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
```

Use `patch_text` when restructuring existing docs — far cheaper than delete+re-insert.

---

## Restructuring Existing Documents (Edit Strategy)

When making multiple edits to an existing document (delete sections, replace content, insert new blocks):

1. **Always fetch fresh block list** before each edit — indices shift after every delete/insert
2. **Delete from HIGH index to LOW** when removing multiple non-contiguous ranges — prevents index invalidation
3. **Prefer `patch_text` over delete+re-insert** for content changes — preserves block_id and is faster
4. **Batch deletes** using `batch_delete` with `start_index`/`end_index` range for consecutive blocks
5. **Re-fetch between operations** if editing more than 2–3 blocks to avoid stale indices

```python
# Safe pattern for multi-step edits:
items, children = get_children()          # fresh fetch
del_range(30, 35)                         # delete high range first
time.sleep(0.3)
items, children = get_children()          # re-fetch
del_range(10, 12)                         # then lower range
time.sleep(0.3)
items, children = get_children()          # re-fetch again
patch_text(children[8], "new text")       # patch by block_id from fresh list
```

---

## Matplotlib with CJK Text (for infographic generation)

When generating infographics with Chinese text to embed in Lark docs:

```python
import matplotlib.font_manager as fm

# WenQuanYi Zen Hei — available on Ubuntu/Debian
wqy_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
fm.fontManager.addfont(wqy_path)
prop = fm.FontProperties(fname=wqy_path)
plt.rcParams['font.family'] = prop.get_name()

# Then pass prop= to all text calls:
ax.text(x, y, "中文字", fontproperties=prop)
ax.legend(..., prop=prop)
```

Without this, all CJK glyphs render as empty boxes (tofu) with DejaVu Sans (matplotlib default).

---

## Transferring Document Ownership

```python
body = {
    "member_type": "openid",   # ⚠️ must be "openid", NOT "userid" — userid returns 400
    "member_id": "ou_xxxxxxxx"  # the target user's open_id
}
req = urllib.request.Request(
    f"https://open.larksuite.com/open-apis/drive/v1/permissions/{doc_id}/members/transfer_owner?type=docx&need_notification=false",
    data=json.dumps(body).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    print(json.loads(resp.read()))  # {"code": 0, "data": {}, "msg": "Success"}
```

## Moving Documents to a Folder

Use `POST /drive/v1/files/{file_token}/move` to move a doc into a folder:

```python
body = {"type": "docx", "folder_token": "TARGET_FOLDER_TOKEN"}
req = urllib.request.Request(
    f"https://open.larksuite.com/open-apis/drive/v1/files/{doc_id}/move",
    data=json.dumps(body).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
```

**Required scopes:** `drive:drive` AND `space:document:move` — the BusyCow default app does NOT have these. Without them, the API returns `99991672 Access denied`.

**Cross-tenant move is impossible via API.** If the target folder URL has a different subdomain (e.g., `cjpg0xp67g6h.jp.larksuite.com`) from your app's tenant, the move will always fail — the folder belongs to a different Lark org. The only path is for the user to manually drag-and-drop in their browser, or duplicate the doc inside their org.

**Same-tenant workaround if scope is missing:** Add `drive:drive` scope to the app in the Lark developer console, then retry. Or ask the user to move manually (right-click → Move in Lark Drive UI — takes 30 seconds).

---

## Which App Credentials to Use

Lark Docx write access depends on which **Feishu app** is a collaborator on the document. The default BusyCow app (`~/.hermes/.env`) will return **HTTP 403** on write calls if the document was created under the [Product] (or another) tenant/app.

**Rule:** Match credentials to the document's owning app/profile:
- [Product] docs → use `~/.hermes/profiles/aquaoptima/.env` credentials
- BusyCow docs → use `~/.hermes/.env` credentials
- If you get 403 on write but read succeeds, switch to the correct profile's `.env`

```python
# [Product] profile example
env_path = os.path.expanduser("~/.hermes/profiles/aquaoptima/.env")
env = open(env_path).read()
app_id, app_secret = "", ""
for line in env.split("\n"):
    if line.startswith("FEISHU_APP_ID="): app_id = line.split("=",1)[1].strip()
    if line.startswith("FEISHU_APP_SECRET="): app_secret = line.split("=",1)[1].strip()
```

**Diagnosis pattern:** If you can `GET` blocks (code 0) but `POST` children returns 403 → wrong app credentials, not a scope issue.

## Large Batch Inserts (>20 blocks) Fail With HTTP 400

When inserting 20+ blocks in a single `POST children` call, Lark returns HTTP 400 with no useful error body — even when the same call works with fewer blocks. The fix is to split into chunks of **15 blocks max** and insert sequentially, adjusting the `index` after each chunk:

```python
def push_small(doc_id, children_list, index=None, chunk_size=15):
    current_idx = index
    for i in range(0, len(children_list), chunk_size):
        chunk = children_list[i:i+chunk_size]
        body = {"children": chunk}
        if current_idx is not None:
            body["index"] = current_idx
        req = urllib.request.Request(
            f"https://open.larksuite.com/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            r = json.loads(resp.read())
        if r.get("code") != 0:
            print(f"Error: {r.get('msg')}")
        if current_idx is not None:
            current_idx += len(chunk)
        time.sleep(2.5)
```

This was validated at 67 and 66 blocks inserted successfully via 5 chunks each.

## Fast-Path: `mcp_lark_docx_builtin_import` for Whole-Document Recreation

When you need to recreate or duplicate an entire document (e.g., creating a new version with amendments), `mcp_lark_docx_builtin_import` is far faster than block-by-block writing. Pass the full document as markdown — it creates a new Lark Doc with a single API call.

```python
# Via MCP tool (no manual auth needed):
mcp_lark_docx_builtin_import(data={
    "file_name": "Short name ≤27 chars",   # ⚠️ HARD LIMIT: 27 characters max
    "markdown": "# Title\n\n## Section\n\nContent..."
})
# Returns: {"result": {"token": "NewDocID", "url": "https://..."}}
```

**⚠️ `file_name` is limited to 27 characters** — passing a longer name returns HTTP 422 validation error. Shorten aggressively (e.g., `"[Product] Apr'26 Update v2"` not `"[Product] Investor Update — Apr '26 (Updated)"`).

**When to use this vs. block API:**
- Use `builtin_import` when: creating a new version/copy of a document, content is fully known upfront, document is medium-sized (no 50-block chunks needed)
- Use block API when: editing an existing document in-place, inserting at specific positions, or adding images

**Credential note:** `mcp_lark_docx_builtin_import` uses the default BusyCow app credentials. If writing to an [Product]-owned doc, you still need the [Product] profile credentials for block-level edits — but `builtin_import` creates a new doc under the BusyCow app's accessible space.

---

## Finding Previously-Worked-On Lark Doc IDs

When Lark search fails (UAT token expired, app token limitations) and you need to find a document worked on in a past session:

1. **Use `session_search` first** — past session summaries often contain doc IDs and full URLs
2. GBrain (`mcp_gbrain_search`) for docs that were indexed into the brain
3. `mcp_lark_docx_builtin_search` with `useUAT: false` only (UAT tokens expire frequently)

```python
# Preferred fallback:
session_search(query="[Product] investor update document")
# Returns past session summaries that typically include:
# - doc ID (e.g., KhJsdxgNeog9n5xhBv2j5O19pWH)
# - full URL (e.g., https://cjpg0xp67g6h.jp.larksuite.com/docx/...)
# - which app profile was used for write access
```

---

## Hyperlink Preservation When Reimporting Documents

**Critical pitfall:** `mcp_lark_docx_v1_document_rawContent` returns **plain text only** — all hyperlinks are stripped. If you read a doc with `rawContent` and then reimport it via `builtin_import`, all embedded links will be lost.

### Recovery Workflow

When a user notices links are missing after a reimport:

1. **Take a screenshot of the original doc** using browser or ask user to share a screenshot — identify all blue hyperlinked text
2. **Web search for each linked entity** to find the official URL (company websites, LinkedIn profiles, government portals, etc.)
3. **Confirm with user** before rebuilding — present a table of `linked text → URL found` and ask if correct
4. **Rebuild with markdown links** — `[Link Text](https://url)` in markdown becomes a clickable hyperlink in the imported Lark doc

```markdown
<!-- Example: preserve links in markdown for builtin_import -->
- **Malaysia — [Abbaco Controls](https://abbacocontrols.com.my/) (Sales & Technical Partner):** ...
- [**世曦工程**](https://www.ceci.com.tw/) — Taiwan's major engineering consultants firm
```

### Prevention

When reimporting any Lark doc that may contain hyperlinks:
- **Always ask the user first** if the original document has embedded links
- If yes, get the original doc link and use browser/screenshot to capture them before proceeding
- Alternatively, ask the user to list all links explicitly before you reimport

### URL recovery by entity type

| Entity type | Best source |
|---|---|
| Company website | Web search `"Company Name" official site` |
| Individual consultant | LinkedIn search |
| Government/utility body | Web search `"org name" official website` |
| Already-known entities | User memory or GBrain |

## Sandbox Context Reset — Use File-Based Scripts for Multi-Step Edits

When making multiple sequential block patches to a Lark doc (especially budget tables with many cells), the `execute_code` sandbox context resets between calls, losing variables like `items`, `root_children`, `token`, etc.

**Solution: Write the full script to `/tmp/script.py` and run with `terminal()`**

```python
# Write once
write_file("/tmp/patch_doc.py", full_script_content)

# Run with terminal
terminal("~/.hermes/hermes-agent/venv/bin/python /tmp/patch_doc.py", timeout=60)
```

This is especially important when:
- Patching 10+ blocks in sequence
- Searching for block IDs and then patching in the same session
- Budget table cells (many blocks with identical text like "700,000" that need context to disambiguate)

**Block ID discovery pattern for tables:**
Table cells don't appear in `root_children` (idx=-1). Find them by searching ALL `items` for matching text:

```python
for b in items:
    txt = get_text(b)
    if "700,000" in txt:
        print(f"bid={b['block_id']} | {txt!r}")
```

Then patch by exact `block_id` — never by text match alone when multiple blocks share the same text.

## ⚠️ Permissions After Import

After calling `mcp_lark_docx_builtin_import`, the created Doc is NOT accessible to the owner by default.
Always call `mcp_lark_drive_v1_permissionMember_create` immediately after:
```json
{
  "path": { "token": "<docx_token>" },
  "params": { "type": "docx" },
  "data": {
    "member_type": "openid",
    "member_id": "{{USER_OPEN_ID}}",
    "perm": "edit"
  }
}
```

## Creating Documents Directly Inside a Wiki (wiki node API)

Use this when you need docs to live inside a Wiki space (navigable from Wiki UI), not just in My Space.

### Step 1: Get space_id and parent node token

```python
# Use mcp_lark_wiki_v2_space_getNode with the wiki root node token
# Returns: node["space_id"] and node["node_token"] (use as parent_node_token)
```

### Step 2: Create wiki node

```python
SPACE_ID = "7633698708932054554"       # from space_getNode
PARENT_NODE = "Udd0w5Ve6iMmjbkEMjRjAdk5pDf"  # wiki root node token

body = {
    "obj_type": "docx",
    "parent_node_token": PARENT_NODE,
    "title": "Document Title",
    "node_type": "origin"              # ⚠️ REQUIRED — omitting returns 400 field_validation_failed
}
req = urllib.request.Request(
    f"https://open.larksuite.com/open-apis/wiki/v2/spaces/{SPACE_ID}/nodes",
    data=json.dumps(body).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    r = json.loads(resp.read())

node_token = r["data"]["node"]["node_token"]
doc_id     = r["data"]["node"]["obj_token"]   # use this for all docx block API calls
```

### Step 3: Fill content using the normal block API

Use `doc_id` (= `obj_token`) for all subsequent `POST /docx/v1/documents/{doc_id}/blocks/...` calls — exactly the same as a regular docx.

### Step 4: Grant access to the owner

Wiki nodes created by the App are not visible to the owner by default. Always call:

```python
body = {"member_type": "openid", "member_id": "{{USER_OPEN_ID}}", "perm": "edit"}
req = urllib.request.Request(
    f"https://open.larksuite.com/open-apis/drive/v1/permissions/{doc_id}/members?type=docx",
    data=json.dumps(body).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
```

### Listing existing wiki nodes (to check before creating duplicates)

```python
req = urllib.request.Request(
    f"https://open.larksuite.com/open-apis/wiki/v2/spaces/{SPACE_ID}/nodes?parent_node_token={PARENT_NODE}&page_size=20",
    headers={"Authorization": f"Bearer {token}"}, method="GET"
)
with urllib.request.urlopen(req) as resp:
    nodes = json.loads(resp.read()).get("data", {}).get("items", [])
for n in nodes:
    print(f"[{n['node_token']}] {n['title']} → doc: {n['obj_token']}")
```

**Always list first before creating** — duplicate wiki nodes cannot be deleted via API (DELETE returns `node not found` regardless of payload). If duplicates are created, user must delete them manually in Lark Wiki UI (right-click → Delete).

### Wiki node pitfalls

- **`node_type: "origin"` is required** — omitting it returns `99992402 field validation failed`
- **Wiki node deletion is NOT supported via API** — `DELETE /wiki/v2/spaces/{space_id}/nodes/{node_token}` always returns 400. Only deletable via Lark UI.
- **`time.sleep(5)` after node creation before first push** — same as regular docx creation; the doc needs time to provision
- **Run `list_nodes` before creating** — if a script is interrupted and re-run, it will create duplicate nodes with identical titles; there is no upsert/idempotent option

---

## Client Reference Files

- [`references/hkrfid-org-structure.md`](references/hkrfid-org-structure.md) — [Client] org chart, role cards, KPIs, and [Product] legacy project portfolio (35 projects). Load when creating any [Client] document.

## ⚠️ Pre-flight: `docx:document:create` scope

When using `lark-cli docs +create --api-version v2` (the lark-doc skill), you may hit a `missing_scope: docx:document:create` error even if bot/user identity is otherwise ready. This scope is **not granted by default**.

**Fix — use the `--no-wait --json` split-flow** (never block-wait in agent context):

```bash
# Step 1: initiate (returns immediately)
lark-cli auth login --scope "docx:document:create" --no-wait --json
# → get device_code + verification_url

# Step 2: generate QR (path must be relative — cd first)
cd ~ && lark-cli auth qrcode "<verification_url>" --output lark_auth_qr.png
# → send MEDIA:~/lark_auth_qr.png to user, END the turn

# Step 3: after user confirms auth
lark-cli auth login --device-code <device_code>

# Step 4: retry docs +create
```

Do NOT run `lark-cli auth login` without `--no-wait` in agent context — it blocks and the user never sees the URL.

## ⚠️ Pitfalls

1. **Wiki spaces API returns 400** — `GET /wiki/v2/spaces` requires wiki admin scope. Use the docx API directly instead; docs are created in the user's default My Space.
2. **Root parent_id = doc_id** — To add top-level blocks, use `doc_id` as the `parent_id`. Do NOT try to fetch the root block ID separately; it equals the doc_id.
3. **Write to file first** — For long documents, write the Python script to `/tmp/script.py` and run with `python3 /tmp/script.py`. Inline `-c` breaks on f-strings with nested quotes.
4. **Block type integers are exact** — Wrong integer silently creates wrong block type. Use the table above.
5. **Empty paragraph as spacer** — Use `paragraph(root_id, \"\")` to add visual spacing between sections.
6. **Rate limits** — Each `add_block` call is one API request. For large documents (50+ blocks), add a small `time.sleep(0.1)` between calls to avoid 429 errors.
11. **App-level quota exhaustion after heavy writing** — Writing a large document (100+ blocks across multiple scripts in the same session) can exhaust the entire App's API quota, causing ALL API calls (even GET `/chats`) to return 429 for 5–30 minutes. This is NOT per-call rate limiting — the whole App is throttled. Symptoms: even a simple `GET /im/v1/chats` returns 429. Fix: wait 5–30 minutes. Prevention: use the single-file batch-push approach (one `push()` per section, `time.sleep(0.35)` between calls) to minimise total API calls — this completes a ~120 block document in ~40 calls instead of 120+.
15. **Multi-document sessions exhaust quota faster than single-doc sessions** — Creating 3+ large docs (250+ blocks each) in the same session will hit the App quota wall mid-way through the last doc, even with `time.sleep(2)` between pushes. The quota is App-wide per day, not per-document. Mitigation: (a) create all docs first (just titles, no content), then fill sequentially with generous delays; (b) if quota hits mid-doc, check block count with `GET /blocks?page_size=50`, identify missing sections, resume after 30-minute wait; (c) for sessions with 3+ large docs, use `time.sleep(3)` between pushes and `time.sleep(5)` immediately after `create_doc()`.
16. **`time.sleep(5)` after `create_doc()` is mandatory for multi-doc sessions** — Without a pause after document creation, the first `push()` call reliably returns HTTP 400 even though the document was created successfully. The API needs time to fully provision the document before accepting block writes. `time.sleep(4-5)` eliminates this failure mode entirely.
12. **`mcp_lark_docx_builtin_import` requires `drive:drive` or `docs:document:import` scope** — the built-in import MCP tool will return error code 99991672 if the Feishu app doesn't have these scopes. Do NOT fall back to it as an alternative to block-by-block writing — it requires extra admin scope setup. Stick with the block API approach.
13. **Rate-limited mid-fill recovery pattern** — If the app hits 429 mid-document (document partially filled), do NOT re-run the full script. The document was already created; just wait 5–30 minutes then continue from where you left off. Check current block count with `GET /docx/v1/documents/{doc_id}/blocks?page_size=50` to find the last written position before resuming. To find missing sections by heading: iterate the block list and collect all h2 (`block_type=4`) text — compare against the expected section list to identify gaps. Then use `insert_at(index, blocks)` with the correct index to backfill, re-fetching the block list between each insertion to get updated indices.
14. **Conservative delay for reliability** — In production use `time.sleep(2)` between `push()` calls (not 0.35) when filling large documents to avoid triggering App-level throttling. The 0.35s delay is the minimum; 2s is safer for documents > 50 blocks. For sessions writing 3+ large documents, use `time.sleep(3)` between pushes — the quota pressure compounds across documents.
9. **Large documents (100+ blocks) will timeout** — A single Python script writing 100+ blocks via individual API calls will exceed the 180s terminal timeout. Solution: split into multiple `/tmp/fill_doc_partN.py` scripts (~25–30 blocks per part), run sequentially. Create the document first, capture `doc_id`, then pass it as a constant into each part script.
10. **Batch-push pattern is far more efficient** — Instead of one `add_block` call per block, group an entire section into one `push(children_list)` call. This reduces API round-trips by ~10x and avoids timeouts on medium-sized documents (30–80 blocks). Use `time.sleep(0.35)` between `push()` calls (not between individual blocks):
7. **Block delete uses parent+index, not block_id directly** — You must find the parent block and the target's index in `children[]`, then call `batch_delete` on the parent's children endpoint. See Deleting Blocks section above.
8. **Ownership transfer: use `openid` not `userid`** — Passing `member_type: \"userid\"` returns HTTP 400. Use `member_type: \"openid\"` with the user's `ou_xxx` ID.

## Adding Screenshots to an Existing Document (Retroactive Image Insertion)

When a doc already exists and you need to insert screenshots at specific locations (e.g., adding UI screenshots to a user guide after the text is written):

### Step 1: Audit all root-level block indices

Run this to map every root block's index, type, and text — so you know exactly where to insert:

```python
def get_all_blocks():
    req = urllib.request.Request(
        f"https://open.larksuite.com/open-apis/docx/v1/documents/{doc_id}/blocks?page_size=500",
        headers={"Authorization": f"Bearer {token}"}, method="GET"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read()).get("data", {}).get("items", [])

blocks = get_all_blocks()
block_by_id = {b["block_id"]: b for b in blocks}

root_block = next(b for b in blocks if b["block_id"] == doc_id)
root_children = root_block.get("children", [])

def get_block_text(b):
    for key in ["heading1","heading2","heading3","text","bullet","ordered"]:
        obj = b.get(key, {})
        if obj:
            elements = obj.get("elements", [])
            return "".join(e.get("text_run",{}).get("content","") for e in elements)
    return ""

for i, child_id in enumerate(root_children):
    b = block_by_id.get(child_id, {})
    print(f"  [{i:3d}] type={b.get('block_type',?):2d}  {get_block_text(b)[:60]!r}")
```

This prints the full index map. Use it to identify the exact index after each section heading where the screenshot should go.

### Step 2: Upload images via curl subprocess (most reliable for multipart)

```python
import subprocess, os

def upload_image(path, name, token, doc_id):
    size = os.path.getsize(path)
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://open.larksuite.com/open-apis/drive/v1/medias/upload_all",
        "-H", f"Authorization: Bearer {token}",
        "-F", "file_type=png",
        "-F", f"file_name={name}.png",
        "-F", f"size={size}",
        "-F", "parent_type=docx_image",
        "-F", f"parent_node={doc_id}",
        "-F", f"file=@{path};type=image/png",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    if data.get("code") != 0:
        print(f"Upload error: {data}")
        return None
    return data["data"]["file_token"]
```

⚠️ Use `subprocess.run` with `curl` for multipart uploads — `urllib.request` multipart is error-prone. `curl -F` is battle-tested.

### Step 3: Insert image + caption at target index (HIGH → LOW order)

```python
def insert_at(index, children_list, token, doc_id):
    body = {"children": children_list, "index": index}
    req = urllib.request.Request(
        f"https://open.larksuite.com/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        r = json.loads(resp.read())
    if r.get("code") != 0:
        print(f"ERROR: {r}")
    time.sleep(2.5)

def img_block(file_token):
    return {"block_type": 27, "image": {"file_token": file_token}}

def caption(text):
    return {"block_type": 2, "text": {"elements": [{"text_run": {"content": text}}]}}

def sp():
    return {"block_type": 2, "text": {"elements": [{"text_run": {"content": ""}}]}}

# Insert a screenshot + caption group (4 blocks: sp + image + caption + sp)
def insert_screenshot(index, file_token, caption_text, token, doc_id):
    insert_at(index, [sp(), img_block(file_token), caption(caption_text), sp()], token, doc_id)
```

### Step 4: Insert all screenshots from HIGHEST to LOWEST index

**Critical:** If inserting at multiple positions, always go high-to-low so earlier insertions don't shift the indices of later targets.

```python
# Example: inserting at indices 279, 255, 180, 165, 139
# Process in descending order:
insert_screenshot(279, tokens["settings"],     "▲ Settings page — ...", token, doc_id)
insert_screenshot(255, tokens["alerts"],       "▲ Alert History — ...", token, doc_id)
insert_screenshot(180, tokens["add_camera"],   "▲ Add Camera form — ...", token, doc_id)
insert_screenshot(165, tokens["cameras_list"], "▲ Cameras list — ...", token, doc_id)
insert_screenshot(139, tokens["dashboard"],    "▲ Dashboard — ...", token, doc_id)
```

Each `insert_screenshot` adds 4 blocks, so if you process high→low, none of the lower indices are affected by the insertions above.

### Verified working: 371-block document, 5 screenshots inserted cleanly in one pass.

---

## Efficient Batch-Push Pattern (for medium/large documents)

Instead of calling `add_block` once per block, pass an entire section as a `children` list in one API call. This is ~10x faster and avoids timeout on large docs:

```python
def blk(btype, text):
    key_map = {2:"text", 3:"heading1", 4:"heading2", 5:"heading3", 12:"bullet", 13:"ordered"}
    k = key_map[btype]
    return {"block_type": btype, k: {"elements": [{"text_run": {"content": text}}]}}

def push(children_list):
    """Send a batch of blocks to the doc root in one API call."""
    body = {"children": children_list}
    req = urllib.request.Request(
        f"https://open.larksuite.com/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        r = json.loads(resp.read())
    if r.get("code") != 0:
        print("ERROR:", r)
    time.sleep(0.35)  # rate limit buffer between push() calls

# Convenience shorthands
def sp(): return blk(2, "")
def h1(t): return blk(3, t)
def h2(t): return blk(4, t)
def h3(t): return blk(5, t)
def p(t):  return blk(2, t)
def b(t):  return blk(12, t)
def hr():  return blk(2, "────────────────────────────────────────────────────────")

# Usage: group a whole section into one push() call
push([
    h1("第一章"),
    p("說明文字"),
    h2("1.1 子章節"),
    b("第一個要點"),
    b("第二個要點"),
    sp(),
    hr(),
])
```

## Large Document Strategy (100+ blocks)

When a document has 100+ blocks, **split the script** into multiple `/tmp/fill_doc_partN.py` files to avoid terminal timeouts (180s limit):

1. **Part 0** — Create the doc, capture `doc_id`, print it
2. **Part 1…N** — Each part hardcodes the `doc_id` as a constant and writes ~25–30 blocks via `push()` calls
3. Run sequentially: `python3 fill_doc_part1.py && python3 fill_doc_part2.py && ...`
4. Each part re-authenticates (token TTL is 2h, safe for sequential runs)
5. **Prefer single-file over split-file when possible** — A single script using batch `push()` with `time.sleep(0.35)` can complete ~120 blocks within the 180s timeout (verified). Split into parts only if the document exceeds ~150 blocks or if individual `push()` calls are very large.

```python
# Template for each part script
DOC_ID = "XxxxxxxxxxxYYYYYY"  # captured from part 0

# ... auth code ...

push([h1("章節標題"), p("內容..."), sp()])
push([h2("子標題"), b("要點一"), b("要點二"), sp()])
# ~25-30 blocks per push group, ~5-8 push() calls per part script
```
