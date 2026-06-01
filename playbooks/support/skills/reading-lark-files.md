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

APP_ID = "cli_a96d2de81f3a1e17"       # from lark-mcp-wrapper.sh
APP_SECRET = "n7YzJ3vrJNCcA3CZGWbNwfczfOKzEkHY"   # from lark-mcp-wrapper.sh
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

## Which App to Use for File Downloads

Two apps exist with different permissions:
- `cli_a96d2de81f3a1e17` (lark-mcp app) — works for chat messages but returns **403 Forbidden** on file downloads
- `cli_a97bd21895f89e18` (Hermes bot app, in `.env` as `FEISHU_APP_ID`) — **works for file downloads**

Always try the Hermes bot app first for file downloads. Use `FEISHU_APP_SECRET` from `.env` (get actual value via `python3 -c "with open('~/.hermes/.env') as f: [print(l) for l in f if 'SECRET' in l]"`).

```python
# ✅ Use the Hermes bot app for file downloads
APP_ID     = "cli_a97bd21895f89e18"   # from .env FEISHU_APP_ID
APP_SECRET = "u5zHR2nk0PeEAAtOZOuVSfCW60O4IX3W"  # from .env FEISHU_APP_SECRET (read actual value)
```

## Porting a Lark/Feishu .xlsx to Google Sheets

To download a Lark file and upload it as a native Google Sheets spreadsheet (preserving formulas and named ranges):

```python
# Step 1: Download from Lark (see above)
# Step 2: Multipart upload to Google Drive with conversion
import os, sys, json, urllib.request, urllib.parse

skill_dir = f"{os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))}/skills/productivity/google-workspace"
sys.path.insert(0, f"{skill_dir}/scripts")
from gws_bridge import get_valid_token

token = get_valid_token()
DRIVE_ID = "{{SHARED_DRIVE_ID}}"   # BusyCow Shared Drive

with open("/tmp/[Product].xlsx", "rb") as f:
    file_data = f.read()

metadata = {
    "name": "My Spreadsheet",
    "mimeType": "application/vnd.google-apps.spreadsheet",  # ← converts to native Sheets
    "parents": [DRIVE_ID]
}

boundary = "upload_boundary"
body = (
    f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(metadata)}\r\n"
    f"--{boundary}\r\nContent-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
).encode() + file_data + f"\r\n--{boundary}--".encode()

params = urllib.parse.urlencode({"uploadType": "multipart", "supportsAllDrives": "true"})
req = urllib.request.Request(
    f"https://www.googleapis.com/upload/drive/v3/files?{params}",
    data=body,
    headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/related; boundary={boundary}"},
    method="POST"
)
with urllib.request.urlopen(req, timeout=60) as r:
    result = json.loads(r.read())
    print(f"Sheet ID: {result['id']}")
    print(f"https://docs.google.com/spreadsheets/d/{result['id']}/edit")
```

Google converts formulas and named ranges automatically on import. Exceptions:
- Custom Python/VBA functions (e.g. numpy_financial UDFs) → `#NAME?` errors
- Some complex array formulas may not convert perfectly

## Pitfalls

- **Wrong app credentials**: `FEISHU_APP_ID` in `.env` ≠ the lark-mcp app. Always read credentials from `lark-mcp-wrapper.sh` or config.yaml.
- **Wrong download endpoint**: `/medias/` → 403. Must use `/files/`.
- **Filename with spaces**: Save to `/tmp/` with quotes, or replace spaces before saving to avoid shell issues.
- **data_only=True in openpyxl**: Returns `None` for cells that were never calculated (only cached values from last Excel save). Always load both `data_only=False` (formulas) and `data_only=True` (values) to get full picture.
- **Very large sheets**: CF-type sheets can extend to column FX (180 cols) and 300 rows. Use `iter_rows` with explicit bounds.
