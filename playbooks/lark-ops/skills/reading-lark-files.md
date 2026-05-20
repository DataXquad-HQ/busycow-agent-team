---
name: reading-lark-files
description: >
  Download and read files (xlsx, pdf, docx, etc.) shared via Lark/Feishu file links.
  Use when user shares a cjpg0xp67g6h.jp.larksuite.com/file/TOKEN URL and asks to read,
  analyse, or extract data from it.
version: 1.0.0
author: Hermes
---

# Reading Lark Files

## Trigger

User shares a URL like `https://cjpg0xp67g6h.jp.larksuite.com/file/FspvbmieHoO6BexTcDDjDCpvpUc`
and asks to read/analyse the file.

## Step 1 — Get the Lark App Credentials

The correct credentials are in the **Hermes config.yaml** (NOT the `.env` FEISHU_APP_ID):

```bash
grep -A8 'lark-mcp-wrapper' ~/.hermes/config.yaml
# OR
cat ~/.hermes/lark-mcp-wrapper.sh
```

The wrapper script contains: `-a <APP_ID> -s <APP_SECRET>`
These are the credentials that work. The `FEISHU_APP_ID` / `FEISHU_APP_SECRET` in `.env` are a **different app** and will return `app secret invalid`.

## Step 2 — Get a Tenant Access Token

```python
import json, urllib.request

APP_ID = "{{LARK_APP_ID}}"       # from lark-mcp-wrapper.sh
APP_SECRET = "{{LARK_APP_SECRET}}Y"   # from lark-mcp-wrapper.sh
DOMAIN = "https://open.larksuite.com"

token_payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request(
    f"{DOMAIN}/open-apis/auth/v3/tenant_access_token/internal",
    data=token_payload,
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=10) as r:
    tenant_token = json.loads(r.read()).get("tenant_access_token", "")
```

## Step 3 — Download the File

**CRITICAL PITFALL:** Use `/drive/v1/files/{token}/download` — NOT `/drive/v1/medias/{token}/download`.

- ✅ `https://open.larksuite.com/open-apis/drive/v1/files/{file_token}/download` → **works**
- ❌ `https://open.larksuite.com/open-apis/drive/v1/medias/{file_token}/download` → **403 Forbidden**

```python
file_token = "FspvbmieHoO6BexTcDDjDCpvpUc"   # from URL path

dl_req = urllib.request.Request(
    f"{DOMAIN}/open-apis/drive/v1/files/{file_token}/download",
    headers={"Authorization": f"Bearer {tenant_token}"}
)
with urllib.request.urlopen(dl_req, timeout=30) as r:
    content_disp = r.headers.get("Content-Disposition", "")
    data = r.read()

# Parse filename from Content-Disposition
import re
m = re.search(r'filename="(.+?)"', content_disp)
filename = m.group(1) if m else "lark_file.bin"

with open(f"/tmp/{filename}", "wb") as f:
    f.write(data)
```

## Step 4 — Read the File

### Excel / XLSX

```python
import openpyxl

# Read with formulas (data_only=False) AND with computed values (data_only=True)
wb_form = openpyxl.load_workbook(f"/tmp/{filename}", data_only=False)
wb_vals  = openpyxl.load_workbook(f"/tmp/{filename}", data_only=True)

print("Sheets:", wb_form.sheetnames)
```

### PDF

Use `web_extract` or `pymupdf` — see `ocr-and-documents` skill.

### DOCX

```python
import docx
doc = docx.Document(f"/tmp/{filename}")
text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
```

## Pitfalls

- **Wrong app credentials**: `FEISHU_APP_ID` in `.env` ≠ the lark-mcp app. Always read credentials from `lark-mcp-wrapper.sh` or config.yaml.
- **Wrong download endpoint**: `/medias/` → 403. Must use `/files/`.
- **Filename with spaces**: Save to `/tmp/` with quotes, or replace spaces before saving to avoid shell issues.
- **data_only=True in openpyxl**: Returns `None` for cells that were never calculated (only cached values from last Excel save). Always load both `data_only=False` (formulas) and `data_only=True` (values) to get full picture.
- **Very large sheets**: CF-type sheets can extend to column FX (180 cols) and 300 rows. Use `iter_rows` with explicit bounds.
