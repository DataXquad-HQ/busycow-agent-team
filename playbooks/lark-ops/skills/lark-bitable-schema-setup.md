---
name: lark-bitable-schema-setup
description: >
  Create Lark/Feishu Bitable apps, tables, and fields via API.
  Covers field type codes, known API limitations (auto-number, cross-table links),
  Drive permissions for sharing, user lookup, and file upload.
  Use when building a new Bitable database schema from scratch via Hermes.
triggers:
  - "create bitable"
  - "build lark base schema"
  - "lark bitable table fields"
  - "feishu base setup"
  - "create invoice quotation base"
---

# Lark Bitable Schema Setup via API

## Auth

⚠️ **Two different app IDs exist — use the one from `config.yaml`, NOT from `.env`:**
- `config.yaml` lark MCP args → `cli_a97bd21895f89e18` + secret `u5zHR2nk0PeEAAtOZOuVSfCW60O4IX3W` ✅ **Use this**
- `.env` FEISHU_APP_ID → `cli_a97aab1888f8de17` ❌ returns `app unauthorized` (10014)

⚠️ **`FEISHU_DOMAIN` env var is just `lark`** — always hardcode the domain, do NOT read from env.

⚠️ **Domain depends on which region the org was created in:**
- `open.larksuite.com` — international Lark (most BusyCow / BusyCow bases)
- `open.feishu.cn` — China / Feishu region (e.g. [your product] / MTR-AVIS bases)
- **Wrong domain = `1254045 FieldNameNotFound`** on Bitable writes (token call returns 200 on both, but API calls fail). If writes fail with 1254045 and field names are correct, **switch the domain**.

⚠️ **`execute_code` sandbox has no network access** — ALWAYS use `terminal` for Lark API calls, never `execute_code`.

⚠️ **`bitable:app` write scope** — if field creation returns HTTP 403 `code 91403`, the app is missing the `bitable:app` scope. Fix: Lark Developer Console → app → Permissions & Scopes → search `bitable:app` → check "View, comment, edit and manage Base" → Save → publish new version. Takes 1-2 min to propagate. Note: read operations (get meta, list fields) may still succeed without this scope via MCP user token — 403 only surfaces on write operations via tenant token.

```python
import json, urllib.request, os

# Always use config.yaml app credentials, not .env
APP_ID = 'cli_a97bd21895f89e18'
APP_SECRET = 'u5zHR2nk0PeEAAtOZOuVSfCW60O4IX3W'
DOMAIN = 'open.larksuite.com'  # always hardcode — FEISHU_DOMAIN env var is just 'lark', unusable
payload = json.dumps({'app_id': APP_ID, 'app_secret': APP_SECRET}).encode()
req = urllib.request.Request(
    f'https://{DOMAIN}/open-apis/auth/v3/tenant_access_token/internal',
    data=payload, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as resp:
    TOKEN = json.loads(resp.read())['tenant_access_token']
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}

def api(method, path, body=None):
    url = f'https://{DOMAIN}/open-apis{path}'
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise Exception(f'HTTP {e.code}: {e.read().decode()[:300]}')
    if result.get('code') != 0:
        raise Exception(f'API error: {result}')
    return result.get('data', {})
```

## Step 1: Create Bitable App

```python
app_data = api('POST', '/bitable/v1/apps', {
    "name": "My Base Name",
    "folder_token": ""   # empty = root folder
})
APP_TOKEN = app_data['app']['app_token']
```

## Step 2: Get / Rename Default Table

A new Bitable always has one default table. Fetch it and rename rather than creating fresh:

```python
tables_data = api('GET', f'/bitable/v1/apps/{APP_TOKEN}/tables')
default_table_id = tables_data['items'][0]['table_id']
api('PATCH', f'/bitable/v1/apps/{APP_TOKEN}/tables/{default_table_id}', {"name": "MyTable"})
```

## Step 3: Create Additional Tables

```python
inv_data = api('POST', f'/bitable/v1/apps/{APP_TOKEN}/tables', {
    "table": {"name": "Invoice"}
})
INV_TABLE_ID = inv_data['table_id']
```

## Step 4: Add Fields

```python
def add_field(table_id, name, field_type, property=None):
    body = {"field_name": name, "type": field_type}
    if property:
        body["property"] = property
    try:
        result = api('POST', f'/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields', body)
        return result.get('field', {}).get('field_id')
    except Exception as e:
        print(f"❌ {name}: {e}")
        return None
```

## ⚠️ Field Update: Use PUT not PATCH

`PATCH /bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}` → **HTTP 404** (broken)
`PUT  /bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}` → **Works correctly**

```python
def update_field(table_id, field_id, name, field_type, property=None):
    body = {"field_name": name, "type": field_type}
    if property: body["property"] = property
    r = api('PUT', f'/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields/{field_id}', body)
    return r.get('code') == 0
```

## ⚠️ Record Update: Also use PUT not PATCH

Same pattern for records:
`PATCH /bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}` → **HTTP 404**
`PUT  /bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}` → **Works correctly**

```python
def update_record(table_id, record_id, fields):
    r = api('PUT', f'/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records/{record_id}',
        {"fields": fields})
    return r.get('code') == 0
```

## ⚠️ Single Select / Multi Select record values: plain string, NOT dict

When writing a Single Select (type 3) value into a record, pass the option name as a **plain string**.
Wrapping it in `{"text": "..."}` returns error **1254062** and silently writes nothing.

```python
# ❌ FAILS — error 1254062, no data written:
api('PUT', f'/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}',
    {"fields": {"Status": {"text": "✅ Active"}}})

# ✅ CORRECT — plain string:
api('PUT', f'/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}',
    {"fields": {"Status": "✅ Active"}})
```

Same rule applies when **adding a new Select option** to the field schema — use `PUT` on the field with the full options list (including existing ones + the new one). The new option's `id` will be auto-assigned:

```python
fields_resp = api('GET', f'/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields')
status_field = next(f for f in fields_resp['data']['items'] if f['field_name'] == 'Status')
existing_opts = status_field.get('property', {}).get('options', [])
existing_opts.append({"name": "📝 Draft", "color": 4})  # color 4 = purple
api('PUT', f'/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields/{status_field["field_id"]}', {
    "field_name": "Status",
    "type": 3,
    "property": {"options": existing_opts}
})
```

## Field Type Reference

| Type Code | Field Type | Notes |
|-----------|-----------|-------|
| 1 | Text (multiline) | Plain text |
| 2 | Number | Add `"property": {"formatter": "0.00"}` |
| 3 | Single Select | Add `"property": {"options": [{"name": "X", "color": N}]}` |
| 4 | Multi Select | Same property as single select |
| 5 | Date / DateTime | Add `"property": {"date_formatter": "yyyy/MM/dd"}` — **write as millisecond integer timestamp, NOT ISO string** |
| 7 | Checkbox | |
| 11 | Person | |
| 13 | Phone | |
| 15 | URL | |
| 19 | Lookup | |
| 1001 | Link (cross-table) | ⚠️ API broken — do manually in UI |
| 1005 | Auto Number | ⚠️ API broken — do manually in UI |

### Select option colors (0–10)
0=grey, 1=blue, 2=green, 3=red, 4=purple, 5=yellow, 6=orange, 7=teal, 8=pink, 9=brown, 10=indigo

## ⚠️ Known API Limitations (Confirmed Broken)

### Auto-Number fields (type 1005) — DO NOT USE via API
Returns `HTTP 400` regardless of property format tried. Workaround: create as Text (type 1), instruct user to change to Auto-Number in the UI and set the format `Q-001` / `INV-001`.

```python
# ❌ FAILS — both formats tried and both give 400:
add_field(table_id, "Quote ID", 1005, {
    "auto_serial": {"type": "custom", "options": [...]}
})

# ✅ WORKAROUND:
add_field(table_id, "Quote ID", 1)   # create as text, change type in UI
```

### Cross-table Link fields (type 1001) — DO NOT USE via API
Returns `HTTP 400` with error `1254093 CreatedTimeFieldPropertyError`. Must be created manually in the UI.

```python
# ❌ FAILS — both property key formats give 400:
add_field(inv_table_id, "關聯 Quote", 1001, {"table_id": QUOTE_TABLE_ID, "multiple": False})
add_field(inv_table_id, "關聯 Quote", 1001, {"linked_table_id": QUOTE_TABLE_ID})

# ✅ WORKAROUND: Tell user to manually add "Link" field in UI, select the source table
```

## Step 5: Set Permissions (Drive API)

### Quickest method — MCP tool (no curl needed)

When Hermes has the Lark MCP server available, use `mcp_lark_drive_v1_permissionMember_create` directly:

```python
# Add user to a Bitable — perm: "view" | "edit" | "full_access"
mcp_lark_drive_v1_permissionMember_create(
    data={"member_id": "{{USER_OPEN_ID}}",
          "member_type": "openid", "perm": "edit", "type": "user"},
    params={"type": "bitable"},
    path={"token": "Ms3dbQu4xag6p5ssasfjymFYpPb"}
)
```

Returns `{}` (empty dict) on success — this is correct, NOT an error.

**Known open_ids:**
- Hunter: `{{USER_OPEN_ID}}`
- Kevin: `{{USER_OPEN_ID}}`
- DX Developer bot (`cli_aa8c6865f439de15`): `{{USER_OPEN_ID}}`

## Granting a 3rd-Party App Bot Access to a Base

When someone gives you a `cli_xxx` app_id (and optionally its secret), and wants that bot to have Base access:

1. **Do NOT use the app_id directly** as `member_id` — Lark will return `1063001 Invalid parameter`
2. **Do NOT use random token strings** (like app secrets) as open_ids — same error
3. The correct flow: get the bot's `open_id` via its own `/bot/v3/info` endpoint, then grant

```python
import json, urllib.request

# Step 1: Get tenant token using the 3rd-party app credentials
app_id = "cli_aa8c6865f439de15"
app_secret = "their_app_secret"
domain = "open.larksuite.com"  # or open.feishu.cn depending on org region

req = urllib.request.Request(
    f"https://{domain}/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
    headers={"Content-Type": "application/json"}, method="POST"
)
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read())["tenant_access_token"]

# Step 2: Get the bot's open_id
req2 = urllib.request.Request(
    f"https://{domain}/open-apis/bot/v3/info",
    headers={"Authorization": f"Bearer {token}"}, method="GET"
)
with urllib.request.urlopen(req2) as resp:
    bot_info = json.loads(resp.read())
open_id = bot_info["bot"]["open_id"]
print(f"Bot open_id: {open_id}")  # e.g. {{USER_OPEN_ID}}
```

3. Then grant access using your own MCP tool or API with the `open_id`

**Note**: Even with the correct open_id, `mcp_lark_drive_v1_permissionMember_create` may return `1063002 Permission denied` if your app (Hermes bot) is not the owner of the Base. In that case, the user must grant access manually via the Lark Base UI: open Base → Share → search by bot/app name → set permission.

### Via curl (fallback)

Use Drive permissions endpoint with `type=bitable` (for the whole app) or `type=file` (for uploaded files):

```python
def add_base_admin(app_token, open_id):
    body = {"member_type": "openid", "member_id": open_id, "perm": "full_access"}
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f'https://open.larksuite.com/open-apis/drive/v1/permissions/{app_token}/members'
        f'?type=bitable&need_notification=false',
        data=data, headers=HEADERS, method='POST')
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

# Add all org members
for uid in ['ou_xxx', 'ou_yyy']:
    add_base_admin(APP_TOKEN, uid)
```

## Finding User open_ids in the Org

The BusyCow app does NOT have `contact:user.id:readonly` scope. Workaround: list the department to get open_ids.

```python
# Lists all users in the root department (dept_id=0)
r = api('GET', '/contact/v3/users/find_by_department?user_id_type=open_id&department_id=0&page_size=50')
users = r.get('data', {}).get('items', [])
for u in users:
    print(u['open_id'])  # open_id available but name/email NOT returned without contact scope
```

**Known org open_ids (BusyCow/BusyCow):**
- Hunter: `{{USER_OPEN_ID}}`
- Kevin (CEO): `{{USER_OPEN_ID}}`
- Hermes-BusyCow bot: `{{USER_OPEN_ID}}`

**Get your bot's own open_id** (useful to confirm identity or grant self permissions via owner):
```python
r = api('GET', '/bot/v3/info')
BOT_OPEN_ID = r['bot']['open_id']
```

Note: `contact:user.id:readonly` scope not available — user name/email cannot be fetched via API. Use department listing and add all members to be safe.

## Uploading Files to Drive (DOCX/PDF)

```python
def upload_file(filepath, filename, mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'):
    with open(filepath, 'rb') as f:
        file_data = f.read()
    boundary = 'FeishuBoundary12345'
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file_name"\r\n\r\n{filename}\r\n'
        f'--{boundary}\r\nContent-Disposition: form-data; name="parent_type"\r\n\r\nexplorer\r\n'
        f'--{boundary}\r\nContent-Disposition: form-data; name="parent_node"\r\n\r\n\r\n'
        f'--{boundary}\r\nContent-Disposition: form-data; name="size"\r\n\r\n{len(file_data)}\r\n'
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: {mime}\r\n\r\n'
    ).encode() + file_data + f'\r\n--{boundary}--\r\n'.encode()
    req = urllib.request.Request(
        'https://open.larksuite.com/open-apis/drive/v1/files/upload_all',
        data=body,
        headers={'Authorization': f'Bearer {TOKEN}',
                 'Content-Type': f'multipart/form-data; boundary={boundary}'},
        method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# Result contains file_token for sharing
r = upload_file('~/MyDoc.docx', 'MyDoc.docx')
file_token = r['data']['file_token']
print(f"https://bytedance.larkoffice.com/file/{file_token}")
```

## Downloading Files from Lark Drive

```python
FILE_TOKEN = 'W6L4bTuwdoIYJMxmmnhjVL00pOg'
req = urllib.request.Request(
    f'https://open.larksuite.com/open-apis/drive/v1/files/{FILE_TOKEN}/download',
    headers=HEADERS)
with urllib.request.urlopen(req, timeout=30) as resp:
    content_disp = resp.headers.get('Content-Disposition', '')
    content_type = resp.headers.get('Content-Type', '')
    data = resp.read()
    # filename is in content_disp, content-type tells you the format
    # e.g. Content-Disposition: attachment; filename="Q-2026-001_AIEdge.pdf"
with open('/tmp/downloaded_file', 'wb') as f:
    f.write(data)
```

Note: `GET /drive/v1/files/{token}` (metadata) returns 404 even for valid tokens — use download directly.

## Extracting Text from a Downloaded PDF

After downloading a Lark Drive file as PDF, use **pymupdf** (`fitz`) to extract text — confirmed working on server (no GUI needed). `pdftotext` CLI is NOT installed; `web_extract` cannot read local files.

```python
import fitz  # pymupdf — available as `import fitz`

doc = fitz.open('/tmp/downloaded_file.pdf')
for i, page in enumerate(doc):
    text = page.get_text()
    print(f"=== Page {i+1} ===")
    print(text)
```

**Full workflow — download + extract from Lark Drive file token:**

```python
import json, urllib.request, fitz

FILE_TOKEN = 'L6GtbD1y0oTwkUx3OOwjj5Kapof'
# ... (auth setup as above) ...

# 1. Download
req = urllib.request.Request(
    f'https://{DOMAIN}/open-apis/drive/v1/files/{FILE_TOKEN}/download',
    headers={'Authorization': f'Bearer {TOKEN}'})
with urllib.request.urlopen(req, timeout=30) as resp:
    content_type = resp.headers.get('Content-Type', '')
    data = resp.read()
ext = 'pdf' if 'pdf' in content_type.lower() else 'docx'
path = f'/tmp/lark_file.{ext}'
with open(path, 'wb') as f:
    f.write(data)

# 2. Extract text (PDF only)
if ext == 'pdf':
    doc = fitz.open(path)
    full_text = '\n'.join(page.get_text() for page in doc)
    print(full_text)
```

**Pitfalls:**
- `web_extract` with `file://` URLs is blocked — always use `fitz` or `pdfminer` in terminal
- `vision_analyze` does not accept PDF files — convert to image first if needed
- `pdftotext` CLI is not installed on the server
- `pdfminer` is also available but `fitz` (pymupdf) is simpler and faster

## BusyCow Sales & Operations Base (consolidated 2026-05-14)

All CRM + Financial + Sales tables merged into one Base:

- **App Token**: `{{LARK_APP_TOKEN}}`
- **URL**: https://cjpg0xp67g6h.jp.larksuite.com/base/{{LARK_APP_TOKEN}}

| Table | ID |
|---|---|
| 💰 Revenue Tracker | `{{TABLE_ID}}` |
| 💸 Expenses | `{{TABLE_ID}}` |
| 📊 Monthly Summary | `{{TABLE_ID}}` |
| ⚙️ Product Config | `{{TABLE_ID}}` |
| 🏢 Company Entities | `{{TABLE_ID}}` |
| 👥 Clients 客戶 | `{{TABLE_ID}}` |
| 🏭 Vendors | `{{TABLE_ID}}` |
| 🧾 Invoices | `{{TABLE_ID}}` |
| 📋 Deals | `{{TABLE_ID}}` |
| 📄 Agreements | `{{TABLE_ID}}` |
| 📝 Quotation | `{{TABLE_ID}}` |
| 📝 Quotation Items | `{{TABLE_ID}}` |
| 📝 Invoice Items | `{{TABLE_ID}}` |
| 👤 Contacts | `{{TABLE_ID}}` |
| 🤝 Partnership | `{{TABLE_ID}}` |
| 📅 Activities | `{{TABLE_ID}}` |
| 📋 Goals | `{{TABLE_ID}}` |
| 📋 Initiatives | `{{TABLE_ID}}` |
| 📋 Tasks | `{{TABLE_ID}}` |

Tasks DuplexLinks: `fldxTM0Op2` → Opportunity, `flderan4Kb` → Partnership (added 2026-05-19)
Opportunity back field: `fld2Fp7U7A` (📋 Tasks-Opportunity)
Partnership back field: `fldSugbXyk` (📋 Tasks-Partnership)

**Old Invoice/Quotation Base** (`KeyubOCo7aRusLs9lQXj3TnDp7c`) — deprecated, returns "note has been deleted".

### Quotation Field IDs
| Field | ID |
|-------|----|
| Quote ID (text) | fldDB1yNF1 |
| Client (select) | fld4bWQTHM |
| 建立日期 | fldEtDy4O4 |
| 有效期限 | fldFUAPWKX |
| 項目明細 | fldBccJjOo |
| 小計 (USD) | fld14rJNR1 |
| 稅額 (USD) | fld226COOA |
| 總金額 (USD) | fldslGaXgA |
| 幣別 | fldVnMg18p |
| 狀態 | fldovMBkdb |
| 負責人 | fld0Flg0u9 |
| Doc 連結 | fldPKmbutI |
| 備註 | fldOEOoACC |

### Invoice Field IDs
| Field | ID |
|-------|----|
| Invoice ID (text) | fld3jgITh4 |
| Client | fldalECAbp |
| 開票日期 | fld2uviPvO |
| 付款截止 | fldiZEhjLo |
| 金額 (USD) | fldisMV2Hd |
| 幣別 | fldLR80uVz |
| 付款狀態 | fldvVdOGZx |
| 付款日期 | fldncAuNO2 |
| 付款方式 | flddDKp5YH |
| 負責人 | fldjFNkr9J |
| Doc 連結 | fldoZAwMJq |
| 備註 | fldve2aNv0 |

## BusyCow Invoice Template Style

Extracted from `DX Invoice IP106 CLP IoT Sensors.pdf` (file token: `W6L4bTuwdoIYJMxmmnhjVL00pOg`):

| Element | Value |
|---------|-------|
| Accent color | Orange `#F5A623` |
| Table header bg | Dark navy `#2C3E50`, white text |
| Data rows | White, no borders, light `#EEEEEE` bottom rule per row |
| Total values | Orange bold |
| Signature font | Segoe Script (or Dancing Script) |
| Body font | Calibri |
| Invoice ID style | 22pt bold orange |
| Layout | 3-col header (logo \| BR# \| address), right-aligned totals, 2-col footer (payment \| terms) |

Word template placeholder format: `{{FIELD_NAME}}` — e.g. `{{INVOICE_ID}}`, `{{CLIENT_NAME}}`, `{{TOTAL}}`, `{{CURRENCY}}`.

Saved templates:
- Invoice: `https://bytedance.larkoffice.com/file/JqOybygPzoT2UDxmSMBjjr8Ypbb`
- Quotation: `https://bytedance.larkoffice.com/file/IVnbbgDHVoT2nvxjHH9jRTYxpDd`
- Local: `~/DataXquad_Invoice_Template.docx`, `~/DataXquad_Quotation_Template.docx`
- Build script: `~/build_invoice_template.py` (run with `uv run --with python-docx python3 build_invoice_template.py`)

## Writing Lark Sheets (Spreadsheet API)

### Create a Spreadsheet

```python
r = api('POST', '/sheets/v3/spreadsheets', {"title": "My Spreadsheet"})
SHEET_TOKEN = r['data']['spreadsheet']['spreadsheet_token']
```

### Add / Rename Sheets

```python
# Rename default sheet
api('PUT', f'/sheets/v3/spreadsheets/{ST}/sheets/{sheet_id}', {"title": "Quotation (EN)"})

# Add new sheet
r = api('POST', f'/sheets/v3/spreadsheets/{ST}/sheets', {"title": "報價單 (中文)"})
new_id = r['data']['sheet']['sheet_id']
```

### Write Values — Always use batch_update to avoid timeouts

**Single-cell ranges must be written as `B3:B3` not `B3`** — the Lark API rejects bare single-cell references like `"3739a4!B3"` with `"wrong range"` error. Always expand: `B3` → `B3:B3`.

```python
import re
def fix_range(rng):
    if ':' not in rng:
        m = re.match(r'^([A-Z]+)(\d+)$', rng)
        if m: return f"{rng}:{rng}"
    return rng
```

**`batch_update` silently fails** — `PUT /sheets/v2/spreadsheets/{token}/values_batch_update` returns `code: None` (not 0) and writes nothing. Despite appearing to succeed, the cells remain empty. **Always use single-range writes** instead:

```python
# ❌ BROKEN — batch silently writes nothing:
api('PUT', f'/sheets/v2/spreadsheets/{ST}/values_batch_update', {
    "valueRanges": [{"range": f"{sid}!A1:H1", "values": [[...]]}]
})

# ✅ WORKS — single write per range:
api('PUT', f'/sheets/v2/spreadsheets/{ST}/values', {
    "valueRange": {"range": f"{sid}!A1:H1", "values": [[...]]}
})
```

**DO NOT** loop many individual `write_values` calls without batching the ranges within each call — each is a separate HTTP round-trip. Group related rows into single wide ranges when possible:

```python
def write(sheet_token, sheet_id, rng, values):
    """Single range write — the only confirmed-working write method."""
    import re
    # Expand single-cell refs: B3 → B3:B3
    if ':' not in rng:
        m = re.match(r'^([A-Z]+)(\d+)$', rng)
        if m: rng = f"{rng}:{rng}"
    req = urllib.request.Request(
        f'https://open.larksuite.com/open-apis/sheets/v2/spreadsheets/{sheet_token}/values',
        data=json.dumps({"valueRange": {"range": f"{sheet_id}!{rng}", "values": values}}).encode(),
        headers=H, method='PUT')
    r = json.loads(urllib.request.urlopen(req, timeout=12).read())
    if r.get('code') != 0:
        print(f"  WARN {rng}: {r.get('msg','?')}")
    return r.get('code') == 0

# Write template rows — call once per distinct range needed:
write(ST, sid, "A1:H1", [["BusyCow", "", "", "", "", "", "", "Company info"]])
write(ST, sid, "A3:H3", [["", "QUOTATION #", "{{QUOTE_ID}}", "", "", "Issued on", "{{ISSUED_DATE}}", ""]])
# Single-cell refs must be written as ranges:
write(ST, sid, "C3:C3", [["{{QUOTE_ID}}"]])   # ✅ works
# write(ST, sid, "C3", ...)                   # ❌ fails with "wrong range"
```

**Formulas** work normally in value writes:
```python
("A12:H12", [[1, "", "", "", "piece", "", "=IF(D12=\"\",\"\",D12*F12)", ""]])
```

### Set Column Widths

```python
def set_col_width(sheet_id, col_idx_0based, width_px):
    api('PUT', f'/sheets/v2/spreadsheets/{ST}/dimension_range', {
        "dimension": {
            "sheetId": sheet_id,
            "majorDimension": "COLUMNS",
            "startIndex": col_idx_0based,
            "endIndex": col_idx_0based + 1
        },
        "dimensionProperties": {"pixelSize": width_px}
    })
```

### Styles API — Correct Endpoint and Field Names (confirmed 2026-05-02)

**IMPORTANT**: The endpoint is `/style` (singular) NOT `/styles` (plural). The plural form always returns 404.

```python
# ✅ CORRECT endpoint:
PUT /sheets/v2/spreadsheets/{token}/style

# ❌ WRONG — always 404:
PUT /sheets/v2/spreadsheets/{token}/styles
```

**Requires** the `sheets:spreadsheet:style` scope on the Lark app. Must be added in Lark Developer Console → Permissions, then republish the app version before it takes effect.

```python
def sty(sheet_token, sid, rng, style_dict):
    """Apply style to a range. All field names verified against Lark API."""
    req = urllib.request.Request(
        f'https://open.larksuite.com/open-apis/sheets/v2/spreadsheets/{sheet_token}/style',
        data=json.dumps({"appendStyle": {
            "range": f"{sid}!{rng}",
            "style": style_dict
        }}).encode(),
        headers=H, method='PUT')
    r = json.loads(urllib.request.urlopen(req, timeout=12).read())
    return r.get('code') == 0
```

**Verified field names** (many are different from what you'd expect):

| Property | Correct key | ❌ Wrong key | Values |
|----------|-------------|-------------|--------|
| Background color | `backColor` | `backgroundColor` | `"#RRGGBB"` — **must include `#`** |
| Font color | `font.foreColor` | `font.color` | `"#RRGGBB"` or `"RRGGBB"` (both work) |
| Font size | `font.size` | `font.fontSize` | Integer only — `fontSize` always fails! |
| Bold | `font.bold` | — | `True` / `False` |
| Italic | `font.italic` | — | `True` / `False` |
| Horizontal align | `horiAlign` | `hAlign` | `"LEFT"`, `"CENTER"`, `"RIGHT"` |
| Vertical align | `vertAlign` | `vAlign` | `"TOP"`, `"MIDDLE"`, `"BOTTOM"` |

**Critical pitfalls**:
- `backColor` **must** have `#` prefix — `"FFFFFF"` fails, `"#FFFFFF"` works
- `font.size` NOT `font.fontSize` — `fontSize` always returns `"invalid fontSize"` error
- `horiAlign` / `vertAlign` NOT `hAlign` / `vAlign` — wrong names return HTTP 400
- Font `bold` cannot be combined with `backColor` in the same style dict when the cell is merged — apply them in separate calls
- Rate limit: run ops sequentially with `time.sleep(0.05)` minimum between calls; parallel requests get throttled to 0 success

**Working style helper**:

```python
GOLD="#C9922A"; NAVY="#2C3E50"; LGRAY="#F2F2F2"; MGRAY="#DDDDDD"
WHITE="#FFFFFF"; GRAY="#888888"; DKGRAY="#444444"; GOLD_L="#FDF3E3"

def f(size=None, bold=None, color=None, italic=None):
    """Build font dict — uses font.size (not font.fontSize)"""
    d = {}
    if size   is not None: d["size"] = size        # NOT fontSize!
    if bold   is not None: d["bold"] = bold
    if color  is not None: d["foreColor"] = color  # with # prefix
    if italic is not None: d["italic"] = italic
    return {"font": d} if d else {}

def bg(color): return {"backColor": color}         # color WITH # prefix
def ha(a): return {"horiAlign": a}                 # not hAlign
def va(a): return {"vertAlign": a}                 # not vAlign

def merge_dicts(*dicts):
    result = {}
    for d in dicts: result.update(d)
    return result

# Example — navy header row:
sty(ST, sid, "A11:G11", merge_dicts(
    bg(NAVY),
    f(bold=True, color=WHITE),
    ha("CENTER"),
    va("MIDDLE")
))
# Gold total amount cell:
sty(ST, sid, "G24:G24", merge_dicts(bg(NAVY), f(14, True, GOLD), ha("RIGHT")))
```

**Tip**: If you get HTTP 400 `"Invalid parameter type in json: Bold"` on a merged cell, apply font and background in separate calls:
```python
sty(sid, "G3:H3", {"backColor": "#FDF3E3"})
time.sleep(0.1)
sty(sid, "G3:H3", {"font": {"bold": True, "foreColor": "#2C3E50"}})
```

**Performance**: Sequential with `time.sleep(0.05)` handles ~66 style ops in ~45 seconds. Run as background process for large templates. Do NOT run in parallel — all calls fail due to rate limiting.

### Sheet Drive Permissions — use `type=sheet` not `type=spreadsheet`

```python
# ✅ CORRECT — type=sheet for spreadsheet files
req = urllib.request.Request(
    f'https://open.larksuite.com/open-apis/drive/v1/permissions/{SHEET_TOKEN}/members'
    f'?type=sheet&need_notification=false',
    data=json.dumps({"member_type":"openid","member_id":uid,"perm":"full_access"}).encode(),
    headers=HEADERS, method='POST')

# ❌ WRONG — type=spreadsheet → HTTP 400
```

### BusyCow Master Template (created 2026-05-01)

- **Token**: `Qv8fsmDoIhDpyAtfRGujqjwZpBh`
- **URL**: https://bytedance.larkoffice.com/sheets/Qv8fsmDoIhDpyAtfRGujqjwZpBh
- EN sheet ID: `3739a4` — "Quotation (EN)"
- ZH sheet ID: `u8haSV` — "報價單 (中文)"
- Build script: `~/build_template_step1.py`

**Placeholder cells** (Hermes fills when copying for a new quote):
| Cell | Content |
|------|---------|
| C3 | `{{QUOTE_ID}}` |
| G3 | `{{ISSUED_DATE}}` |
| G4 | `{{VALID_UNTIL}}` |
| B7 | `{{CLIENT_NAME}}` |
| F7 | `{{PROJECT_NAME}}` |
| B8 | `{{CLIENT_COMPANY}}` |
| F8 | `{{PROJECT_DESC}}` |
| B9 | `{{CLIENT_ADDRESS}}` |
| A12:G21 | Line items: A=#, B=Model, C=Desc, D=Qty, E=Unit, F=UnitPrice, G=auto-formula |
| G23 | Tax amount (default 0) |

## Reading Lark Sheets (Spreadsheet API)

Use sheet token from URL (`/sheets/SHEET_TOKEN`). The sheet ID in the range is a **6-char alphanumeric string** — NOT `"0"`.

```python
SHEET_TOKEN = 'Y32JskEz3hZzvnts2FejygnPpXc'

# Step 1: get real sheet IDs
r = api('GET', f'/sheets/v3/spreadsheets/{SHEET_TOKEN}/sheets/query')
for s in r['data']['sheets']:
    sid = s['sheet_id']    # e.g. '0RWNnA', NOT '0'
    title = s.get('title', '')

# Step 2: read values — use real sheet ID in range
r2 = api('GET', f'/sheets/v2/spreadsheets/{SHEET_TOKEN}/values/{sid}!A1:Z50')
rows = r2['data']['valueRange']['values']
```

**Pitfall**: Using `"0"` as sheet ID → `code: 90215 "not found sheetId"`. Always query sheet IDs first.

**Rich-text cells** return a list of segment dicts: `[{'text': '...', 'segmentStyle': {'bold': True, ...}}]` — extract `.get('text', '')` from each segment.

**Date cells** return Excel serial numbers (e.g. `45735` = 2025-03-19). Convert with:
```python
from datetime import date, timedelta
excel_epoch = date(1899, 12, 30)
actual_date = excel_epoch + timedelta(days=int(serial_num))
```

## Lark Base Workspace — What it can and cannot do
- Workspace = folder/container for multiple Bases — useful for organization only
- **Cannot** do cross-Base link fields (1-way or 2-way) — links only work within same Base
- Adding a Base to Workspace requires: Manage permission on the Base + Edit permission on the storage location
- Add from Base homepage (⋯ → Add to Base Workspace) is most reliable — NOT from inside Workspace
- Workspace API is NOT publicly available (404 on all endpoints as of 2026-05)

## Bulk Table/Field Cleanup (remove emoji + CJK, add emoji prefix)
When cleaning a Base (removing Chinese, removing old emoji, adding category emoji):

1. **Scan first** — collect all renames before executing, save to /tmp
2. **Background process** — run rename in background to avoid 60s timeout
3. **`DataNotChange` (code 1254606) = already clean** — safe to ignore
4. **Table rename**: `PATCH /bitable/v1/apps/{app}/tables/{table_id}` `{"name": "new"}`
5. **Field rename**: `PUT` (not PATCH) on fields endpoint, must include `type` even for rename-only

```python
import re
def clean(name):
    name = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf\uff00-\uffef]+', '', name)
    name = re.sub(r'[^\x00-\x7F]+', '', name)
    name = re.sub(r'\s*[/\-_]\s*$', '', name).strip()
    name = re.sub(r'^\s*[/\-_]\s*', '', name).strip()
    return re.sub(r'\s+', ' ', name).strip()
```

**Emoji prefix pattern** (Hunter prefers this for grouping):
- 💼 = Sales tables (Clients, Contacts, Deals, Activities, Quotation...)
- 💰 = Finance tables (Invoices, Revenue, Expenses...)
- ⚙️ = Config tables (Company Entities, Product Config, Vendors...)

## BusyCow Invoice/Quotation Base (Confirmed IDs)

- **App Token**: `KeyubOCo7aRusLs9lQXj3TnDp7c`
- **URL**: https://bytedance.larkoffice.com/base/KeyubOCo7aRusLs9lQXj3TnDp7c
- **Quotation Table**: `{{TABLE_ID}}` — Quote ID / Client / 建立日期 / 有效期限 / 項目明細 / 小計 / 稅額 / 總金額 / 幣別 / 狀態 / 負責人 / Doc 連結 / 備註
- **Invoice Table**: `{{TABLE_ID}}` — Invoice ID / 關聯Quote(manual) / Client / 開票日期 / 付款截止 / 金額 / 幣別 / 付款狀態 / 付款日期 / 付款方式 / 負責人 / Doc 連結 / 備註

**BusyCow org member open_ids** (confirmed 2026-05-01):
- `{{USER_OPEN_ID}}` — Hunter (session user / owner)
- `{{USER_OPEN_ID}}` — org member 1
- `{{USER_OPEN_ID}}` — org member 2

All three have `full_access` on the Invoice/Quotation Base.

## GBrain Import Limitation

`gbrain import <path>` requires a **directory**, not a single file:
```bash
# ❌ FAILS — not a directory
gbrain import ~/vault/myfile.md

# ✅ WORKS — import the containing folder
gbrain import ~/vault/Projects/ --no-embed
```
Workaround for single files: place the file in its own subfolder, then import that folder.

## Bulk Permission Grant for All Drive Files

To grant a user full_access to all files in the org root (and known bases):
1. List root files: `GET /drive/v1/files?folder_token=&page_size=50`
2. For each file, call `POST /drive/v1/permissions/{token}/members?type={ftype}&need_notification=false`
   with `{"member_type": "openid", "member_id": HUNTER_OPEN_ID, "perm": "full_access"}`
3. `type` must match doc type: `bitable`, `docx`, `file`, `folder`, `sheet`
4. Files not visible to current bot (owned by another bot) will return 403 — handle separately via ownership transfer

**Table name emojis**: Users may find emoji prefixes in table/base names annoying. Default to clean text names (Accounts, Contacts, Deals) unless the user explicitly wants emoji.

## Bitable Ownership Problem & Migration Playbook

When a Bitable was created by a **different/old bot** (you can't edit permissions, get 403 on everything):
- The old bot's tenant token will return `code 10014 app unauthorized` if the app was deauthorized
- The new bot **cannot grant itself access** — only the owner can add members
- **Ownership CAN be transferred via API** — use `transfer_owner` endpoint (confirmed working 2026-05-11):

```python
# Use the CURRENT owner's app credentials to get a token, then call:
resp = requests.post(
    f'https://open.feishu.cn/open-apis/drive/v1/permissions/{app_token}/members/transfer_owner?type=bitable',
    headers=headers,
    json={
        'member_type': 'openid',
        'member_id': 'ou_TARGET_OPEN_ID',  # new owner's open_id
    }
)
# Returns: 200 {"code": 0, "data": {}, "msg": "Success"}
```

**Note**: The `type` param goes in the **query string**, not the body. Returns empty `data` on success.

**Best solution if transfer fails: recreate the base from scratch**, migrate data programmatically.

### Migration Playbook

```python
# Step 1 — Backup all data from old base (read-only, works without write scope)
all_data = {}
for name, tid in old_tables.items():
    records = []
    page_token = None
    while True:
        path = f'/bitable/v1/apps/{OLD_TOKEN}/tables/{tid}/records?page_size=100'
        if page_token: path += f'&page_token={page_token}'
        r = api('GET', path)
        records.extend(r.get('data', {}).get('items', []))
        if not r.get('data', {}).get('has_more'): break
        page_token = r.get('data', {}).get('page_token')
    all_data[name] = records

# Step 2 — Create new base (owned by new bot), grant users access
r = api('POST', '/bitable/v1/apps', {"name": "Base Name"})
NEW_TOKEN = r['data']['app']['app_token']
api('POST', f'/drive/v1/permissions/{NEW_TOKEN}/members?type=bitable&need_notification=false',
    {"member_type": "openid", "member_id": HUNTER_OPEN_ID, "perm": "full_access"})

# Step 3 — Create tables, add fields (see field creation steps above)

# Step 4 — Migrate records using batch_create (NOT one-by-one — too slow)
# CRITICAL: Lark API returns all Number field values as STRINGS in GET responses.
# You MUST cast them to float before writing back, or get NumberFieldConvFail.

def get_field_map(table_id):
    r = api('GET', f'/bitable/v1/apps/{NEW_TOKEN}/tables/{table_id}/fields?page_size=100')
    return {f['field_name']: f['type'] for f in r.get('data', {}).get('items', [])}

def coerce(val, ftype):
    if val is None or val == '': return None
    if ftype == 2:  # Number — API returns as string, must cast
        try: return float(str(val).replace(',', ''))
        except: return None
    if ftype == 5:  # DateTime — pass millisecond timestamp as int
        if isinstance(val, (int, float)): return int(val)
        return None
    if ftype in (1, 3, 4): return str(val) if val else None
    if ftype == 7: return bool(val)
    return val

def batch_migrate(records, new_table_id, extra_fields_fn=None):
    fm = get_field_map(new_table_id)
    batch = []
    for rec in records:
        fields = {}
        for k, v in rec.get('fields', {}).items():
            if k not in fm: continue
            c = coerce(v, fm[k])
            if c is not None: fields[k] = c
        if extra_fields_fn: fields.update(extra_fields_fn(rec.get('fields', {})))
        if fields: batch.append({"fields": fields})
    # Send in chunks of 50
    for i in range(0, len(batch), 50):
        r = api('POST', f'/bitable/v1/apps/{NEW_TOKEN}/tables/{new_table_id}/records/batch_create',
                {"records": batch[i:i+50]})
        time.sleep(0.3)
```

**Key pitfalls in migration:**
- `NumberFieldConvFail` — all number values come back as strings from GET; always `float(str(val))`
- **DateTime fields MUST be written as millisecond integer timestamps** — ISO strings (e.g. `"2026-05-13T12:00:00+00:00"`) are silently ignored and the field is left blank. Convert with `int(datetime.fromisoformat(iso_str.replace("Z", "+00:00")).timestamp() * 1000)`.
- DateTime primary fields — backup stores as millisecond int timestamp; pass as-is (int)
- `FieldNameDuplicated` on retry — means field was already created (previous run); safe to ignore
- `batch_create` is ~10x faster than one-by-one; always use it for migration
- `time.sleep(0.08)` between individual creates, `0.3` between batch chunks

## DuplexLink Fields — API Behavior (Confirmed 2026-05-19)

DuplexLink (type 21) is the correct type for cross-table bidirectional links within the same Base.

### Creating DuplexLink via API
```python
# Add DuplexLink on table A pointing to table B
r = add_field(TABLE_A_ID, "Initiatives", 21, {
    "table_id": TABLE_B_ID,
    "multiple": True
})
# Lark auto-creates a back field on TABLE_B with a generated name like "📋 Goals-Initiatives"
# The back field name is NOT configurable via API — check it with GET /fields
```

### Back field name — always verify after creation
```python
# Get the auto-generated back field name on the target table
cmd = f'curl -s "https://open.larksuite.com/open-apis/bitable/v1/apps/{APP}/tables/{TABLE_B_ID}/fields" -H "Authorization: Bearer {token}"'
# Look for type=21 field — it will have a name like "📋 TableA-FieldName"
# You MUST use this exact name when writing links from the target side
```

### Writing DuplexLink values — use plain array of strings
```python
# ✅ CORRECT — plain array of record ID strings:
update_record(TABLE_ID, record_id, {"Initiatives": ["recXXX", "recYYY"]})

# ❌ FAILS (code 1254074) — dict format:
update_record(TABLE_ID, record_id, {"Initiatives": {"link_record_ids": ["recXXX"]}})
```

### DuplexLink cannot be set during record CREATE
```python
# ❌ FAILS (code 1254074) — cannot set DuplexLink in records/batch_create or records POST:
create_record(TABLE_ID, {"Name": "Test", "Initiatives": ["recXXX"]})

# ✅ CORRECT — two-step: create first, then update with link:
new_id, code = create_record(TABLE_ID, {"Name": "Test"})  # no link
update_record(TABLE_ID, new_id, {"Initiatives": ["recXXX"]})  # add link after
```

### DuplexLink update must go through the PRIMARY side
When Goals has the primary DuplexLink field pointing to Initiatives:
- Update Goals record → set `{"Initiatives": ["recA", "recB"]}` → **works ✅**
- Update Initiatives record → set `{"📋 Goals-Initiatives": ["recGoal"]}` → **fails 1254074 ❌**
- Always update from the table that **owns** the primary DuplexLink field

### Person field in batch_create
```python
# ❌ FAILS (UserFieldConvFail) — plain string:
{"Responsible Person": ["ou_xxx"]}

# ✅ CORRECT — array of objects:
{"Responsible Person": [{"id": "ou_xxx"}]}
```

### Batch create (batch_create) is supported and fast
```python
# Up to 50 records per call:
r = api('POST', f'/bitable/v1/apps/{APP}/tables/{TABLE_ID}/records/batch_create',
    {"records": [{"fields": f} for f in records_list[:50]]})
new_ids = [rec['record_id'] for rec in r.get('data', {}).get('records', [])]
```

### Deleting a Bitable Base
```python
# Via Drive API — requires owner permission:
api('DELETE', f'/drive/v1/files/{APP_TOKEN}?type=bitable')
# Returns 403 "operate node no permission" if current bot is not the owner
# Solution: transfer ownership first (see Ownership Transfer section), then delete
```

---

## Deleting Bitable Records

**Batch delete** (`DELETE /bitable/v1/apps/{app}/tables/{table}/records/batch_delete`) uses body key `records` (list of record IDs). However it returns `1254043 RecordIdNotFound` if any ID in the batch is stale or was recently created in the same session. **Delete one-by-one to be safe:**

```python
for rid in ids_to_delete:
    r = api('DELETE', f'/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records/{rid}')
    print(f"Delete {rid}: {r.get('code')} {r.get('msg')}")
    time.sleep(0.1)
```

To find empty/placeholder records created by default when a new Base is made:
```python
resp = api('GET', f'/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records?page_size=50')
records = resp.get('data', {}).get('items', [])
empty_ids = [r['record_id'] for r in records if not r.get('fields', {}).get('YourPrimaryField')]
```

## Renaming the Primary (Title) Field

New Bitables have a primary field called `"Text"` by default. Rename it with `PUT`:

```python
# GET fields first to find primary field ID
resp = api('GET', f'/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields')
primary = next(f for f in resp['data']['items'] if f.get('is_primary'))
primary_id = primary['field_id']

# Rename with PUT (not PATCH)
api('PUT', f'/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields/{primary_id}',
    {"field_name": "Job Name", "type": 1})
```

Also delete the default unused fields (Single option type=3, Date type=5, Attachment type=17) that Lark adds automatically:
```python
default_trash = [f['field_id'] for f in resp['data']['items']
                 if not f.get('is_primary') and f['field_name'] in ('Single option','Date','Attachment')]
for fid in default_trash:
    api('DELETE', f'/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields/{fid}')
    time.sleep(0.2)
```

## API Quota Limits — Starter vs Pro

Error `99991403 "This month's API call quota has been exceeded"` means the org has hit its monthly Basic API cap.

| Plan | Monthly Basic API Quota |
|------|------------------------|
| Starter | 10,000 calls/month (shared across ALL apps in the org) |
| Pro / Basic / Enterprise | Unlimited |

- Quota resets on the 1st of each month
- Changing the URL or permissions does NOT fix this — only upgrading the plan or waiting for reset
- Every read AND write call counts toward the quota
- Cron jobs running daily can easily burn through 10,000 calls within a month
- **Recommendation**: If Hermes is actively managing Lark Bases + running daily crons, upgrade to Pro ($12/user/month)

## BusyCow Sales & Operations Base (rebuilt 2026-05-15)

- **App Token**: `{{LARK_APP_TOKEN}}`
- **URL**: https://cjpg0xp67g6h.jp.larksuite.com/base/{{LARK_APP_TOKEN}}
- Merged from: Financial Tracker + CRM (Y9fhbly8RaHxcFsjz4pj1fb5p2c — deleted)

| Table | ID |
|-------|-----|
| 👥 Clients 客戶資料 | `{{TABLE_ID}}` |
| 🤝 Deals | `{{TABLE_ID}}` |
| 🧾 Invoices 發票 | `{{TABLE_ID}}` |
| 📋 Quotation 報價單 | `{{TABLE_ID}}` |
| 📝 Quotation Items | `{{TABLE_ID}}` |
| 📝 Invoice Items | `{{TABLE_ID}}` |
| 💰 Revenue Tracker | `{{TABLE_ID}}` |
| 💸 Expenses | `{{TABLE_ID}}` |
| 📊 Monthly Summary | `{{TABLE_ID}}` |
| 🏢 Company Entities | `{{TABLE_ID}}` |
| 🏭 Vendors | `{{TABLE_ID}}` |
| 📄 Agreements | `{{TABLE_ID}}` |
| 👤 Contacts 聯絡人 | `{{TABLE_ID}}` |
| 🤝 Partnership | `{{TABLE_ID}}` |
| 📅 Activities | `{{TABLE_ID}}` |

## Lark Base Workspace

- Workspace API is **NOT publicly available** (returns 404) — cannot add bases programmatically
- Must add bases to Workspace manually in UI: open Workspace → "+ Add Base"
- Workspace URL: https://cjpg0xp67g6h.jp.larksuite.com/base/workspace/E7eqskTG8pjCrHciiJxjevAdptd
- Benefit: cross-Base link fields work within same Workspace

- **App Token**: `{{LARK_APP_TOKEN}}`
- **URL**: https://bytedance.larkoffice.com/base/{{LARK_APP_TOKEN}}
- Owner: Hermes-BusyCow bot (`cli_a97bd21895f89e18`)
- Hunter + Kevin have `full_access`

| Table | ID |
|-------|----|
| 💰 Revenue Tracker 收入追蹤 | `{{TABLE_ID}}` |
| 💸 Expenses 支出 | `{{TABLE_ID}}` |
| 📊 Monthly Summary & Cash Flow | `{{TABLE_ID}}` |
| ⚙️ Product Config 產品配置 | `{{TABLE_ID}}` |
| 🏢 Company Entities 法人資料 | `{{TABLE_ID}}` |
| 👥 Clients 客戶資料 | `{{TABLE_ID}}` |
| 🏭 Vendors 供應商 | `{{TABLE_ID}}` |
| 🧾 Invoices 發票 | `{{TABLE_ID}}` |
| 📋 Orders 合約訂單 | `{{TABLE_ID}}` |

**Entity logic**: [your product]/[your product] → TW - ATA Limited 應科聯; BusyCow/[your product]/Others → SG - BusyCow Pte. Ltd. (default for overseas income = SG, Taiwan income = TW unless instructed otherwise)

**Invoice / Order naming convention:**
- Invoice: `INV-{SG|TW}-{YYYY}-{MM}` e.g. `INV-TW-2026-007` (month = billing month, entity = issuing entity)
  - Same month multiple clients: append `-A`, `-B` e.g. `INV-TW-2026-007-[Client]`
- Order/Contract: `ORD-{YYYY}-{CLIENT_SHORT}-{SEQ}` e.g. `ORD-2026-[Client]-001`
- Quotation (pre-sign): `QUO-{YYYY}-{CLIENT_SHORT}-{SEQ}`

**Order → Invoice relationship**: One signed Order links to N Invoices via `Related Quote #` field (text). Each invoice = one billing period. This is the correct pattern for instalment contracts.

**Company Entities pre-populated:**
- SG: BusyCow Pte. Ltd. | UEN 202414515G | DBS Bank SWIFT DBSSSGSG | Acc 0721151979
- TW: ATA Limited 應科聯有限公司 | 統編 9063 1464 | Taipei Fubon SWIFT TPBKTWTPXXX | USD Acc 83110000387935 | NTD Acc 82110000093580

## Transferring Ownership from a Deactivated Bot (Confirmed 2026-05-14)

When a Bitable/Doc is owned by an old bot that was deactivated:
- Re-enable the old app in Lark Developer Console first (get its App Secret from Credentials tab)
- Use the old bot's tenant_access_token to call `transfer_owner` — this is the only way
- Old bot's open_id: call `/bot/v3/info` with old token to get it
- New bot's open_id: call `/bot/v3/info` with new token to get it
- Transfer endpoint: `POST /drive/v1/permissions/{token}/members/transfer_owner?type={ftype}`
  - Body: `{"member_type": "openid", "member_id": NEW_BOT_OPEN_ID}`
  - `type` is the **doc type** in the query string (`bitable`, `docx`, `sheet`, `file`, `folder`)
- After transfer, new bot owns the file and can delete or grant permissions normally
- Delete a bitable: `DELETE /drive/v1/files/{token}?type=bitable`
- Once done, re-disable the old app

**Pitfall**: f-string with backslash inside expression causes SyntaxError in Python < 3.12.
Always extract the value before the f-string:
```python
# ❌ SyntaxError:
print(f"{'ok' if code==0 else f'err {result.get(\"msg\")}'}")

# ✅ Fine:
msg = 'ok' if code == 0 else f'err {result.get("msg")}'
print(f"[{msg}] {name}")
```

**Hermes-BusyCow old bot** (cli_a97aab1888f8de17): open_id = `{{USER_OPEN_ID}}`

## Cross-Profile Permission Grant (Confirmed 2026-05-11)

When you need to grant a **different Hermes profile's bot** access to a Bitable owned by another profile:

1. **Get the target bot's open_id** using its own app credentials:
```python
import requests

# Target app (the one you want to GRANT access TO)
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal',
    json={'app_id': 'cli_TARGET_APP_ID', 'app_secret': 'TARGET_SECRET'})
app_token = r.json()['app_access_token']

r2 = requests.get('https://open.feishu.cn/open-apis/bot/v3/info',
    headers={'Authorization': f'Bearer {app_token}'})
target_open_id = r2.json()['bot']['open_id']
# e.g. '{{USER_OPEN_ID}}'
```

2. **Use the OWNER's app credentials** to grant access:
```python
# Owner app (the one that owns the Bitable)
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': 'cli_OWNER_APP_ID', 'app_secret': 'OWNER_SECRET'})
owner_token = r.json()['tenant_access_token']

headers = {'Authorization': f'Bearer {owner_token}', 'Content-Type': 'application/json'}

# Grant full_access — member_type must be 'openid', type must match (user for bot open_ids)
resp = requests.post(
    f'https://open.feishu.cn/open-apis/drive/v1/permissions/{BITABLE_APP_TOKEN}/members?type=bitable',
    headers=headers,
    json={'member_type': 'openid', 'member_id': target_open_id, 'perm': 'full_access', 'type': 'user'}
)
```

3. **Then transfer ownership** if desired (so you don't need the owner profile again):
```python
resp = requests.post(
    f'https://open.feishu.cn/open-apis/drive/v1/permissions/{BITABLE_APP_TOKEN}/members/transfer_owner?type=bitable',
    headers=headers,  # still using OWNER's token
    json={'member_type': 'openid', 'member_id': target_open_id}
)
```

**Pitfalls:**
- First attempt using `member_type: 'openid'` with the app's `cli_xxx` ID (not open_id) returns `400 Invalid parameter` — always use the bot's `open_id` from `/bot/v3/info`
- The `type` param in the permission grant URL is the **document type** (`bitable`), not the member type
- `member_type: 'openid'` + `type: 'user'` is the correct combo for bot open_ids

**BusyCow known bot open_ids:**
- Hermes-BusyCow (`cli_a97bd21895f89e18`): `{{USER_OPEN_ID}}`
- BusyCow profile (`cli_a97aab1888f8de17`): owner of older Bases

## Task Management Base (BusyCow — created 2026-05-07)

- **App Token**: `{{LARK_APP_TOKEN}}`
- **Tasks Table**: `{{TABLE_ID}}`
- **Projects Table**: `{{TABLE_ID}}`
- **URL**: https://cjpg0xp67g6h.jp.larksuite.com/base/{{LARK_APP_TOKEN}}
- Covers all 4 business lines: BusyCow, [your product], [your product], [your product]
- Hunter + Kevin shared; Hermes maintains it (weekly rhythm, no manual maintenance needed)
- **Owner**: Hermes-BusyCow (`{{USER_OPEN_ID}}`) — transferred from BusyCow profile on 2026-05-11

**Tasks fields**: Task Name, Status (Not Started/In Progress/Blocked/Done/Cancelled), Deadline, Business Line, Responsible Person, Priority (🔴High/🟡Medium/🟢Low), Description, Next Action, Notes, Source, Created Date, Task Type (Sales/Product/Ops/Legal/Admin/Comms), Project (link)

**Projects fields**: set up by user — includes Project Name, Business Line, Status, Owner, Target Week, Notes

## Hermes Cron Registry Base (created 2026-05-01, restructured 2026-05-05)

A registry of all Hermes automation jobs, grouped by product line:

- **App Token**: `OircbPodaawVZlsQP2vjThkQp6b`
- **Table**: `{{TABLE_ID}}` — "Cron Jobs"
- **URL**: https://cjpg0xp67g6h.jp.larksuite.com/base/OircbPodaawVZlsQP2vjThkQp6b
- **Admins**: Hunter (`ou_9ba57313`) — full_access

**Current fields (simplified 2026-05-05):**
Job Name (primary) | Job ID | Product Line | Schedule (TWN) | What It Does | Output / Delivery | Status | Deliver To

`Product Line` select options: 🐄 BusyCow, 💧 [your product], 🏢 BusyCow, ⚙️ System
`Status` select options: ✅ Active, ⏸️ Paused, ❌ Disabled, 📝 Draft

**Removed fields (2026-05-05):** Profile, Agent/Tool, Type, Cron Expression, Window, Purpose, Notes
— All cron jobs now run under Hermes; Profile tracking no longer needed.

## Manual Steps Required After API Setup

Always remind user to do these in the Bitable UI:
1. **Auto-Number fields** — change `Quote ID` / `Invoice ID` from Text to Auto-Number, set format `Q-001` / `INV-001`
2. **Cross-table link** — add \"Link\" field in Invoice table manually, select Quotation table as source

## Lark Base Workspace — Confirmed Limitations

- **Workspace is a folder only** — does NOT enable cross-base link fields (1-way or 2-way)
- Cross-base linking is officially NOT supported in Lark Base (confirmed in official docs 2026-01-09)
- To add a Base to Workspace: need **Manage permission on the base** + **Edit permission on the storage location (Drive folder)**
- Best way to add: from **Base homepage** → `⋯` next to the base → **Add to Base Workspace** (bypasses Drive folder permission issue)
- Workspace API (bitable/v1/workspaces) returns 404 — not publicly supported via API, UI only

## Ownership Transfer — Confirmed Behavior

- `transfer_owner` returns code 0 (success) but Workspace UI may still show permission denied
- Root cause: transfer succeeds for the Base itself, but Drive storage location permissions are separate
- If transfer keeps failing (403), the base is likely owned by a different/old bot — need that bot's credentials
- `old_owner_action: remove_role` param can be passed but does not affect success rate

## Invoice No. Naming Convention (BusyCow/BusyCow)

- Format: `IN-{YYYY}{MM}{NNN}` e.g. `IN-202605001`
- Monthly reset, 3-digit sequence starting 001
- Previous incorrect format `INV-TW-2026-Q001-SNS` was project-specific, not the standard
