---
name: google-workspace
description: >
  Use Gmail, Google Calendar, Drive, Sheets, and Docs via the gws CLI.
  Use when user asks to send an email, check calendar, read/write a Google Doc or Sheet,
  search Drive, or manage Google contacts. Requires gws binary and valid OAuth token.
version: 2.0.0
author: Nous Research
license: MIT
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials (downloaded from Google Cloud Console)
metadata:
  hermes:
    tags: [Google, Gmail, Calendar, Drive, Sheets, Docs, Contacts, Email, OAuth, gws]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [himalaya]
---

# Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, and Docs — powered by `gws` (Google's official Rust CLI). The skill provides a backward-compatible Python wrapper that handles OAuth token refresh and delegates to `gws`.

## Architecture

```
google_api.py  →  gws_bridge.py  →  gws CLI
(argparse compat)  (token refresh)    (Google APIs)
```

- `setup.py` handles OAuth2 (headless-compatible, works on CLI/Telegram/Discord)
- `gws_bridge.py` refreshes the Hermes token and injects it into `gws` via `GOOGLE_WORKSPACE_CLI_TOKEN`
- `google_api.py` provides the same CLI interface as v1 but delegates to `gws`

## References

- `references/gmail-search-syntax.md` — Gmail search operators (is:unread, from:, newer_than:, etc.)

## Scripts

- `scripts/setup.py` — OAuth2 setup (run once to authorize)
- `scripts/gws_bridge.py` — Token refresh bridge to gws CLI
- `scripts/google_api.py` — Backward-compatible API wrapper (delegates to gws)

## Prerequisites

Install `gws`:

```bash
cargo install google-workspace-cli
# or via npm (recommended, downloads prebuilt binary):
npm install -g @googleworkspace/cli
# or via Homebrew:
brew install googleworkspace-cli
```

Verify: `gws --version`

## First-Time Setup

The setup is fully non-interactive — you drive it step by step so it works
on CLI, Telegram, Discord, or any platform.

Define a shorthand first:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
GWORKSPACE_SKILL_DIR="$HERMES_HOME/skills/productivity/google-workspace"
PYTHON_BIN="${HERMES_PYTHON:-python3}"
if [ -x "$HERMES_HOME/hermes-agent/venv/bin/python" ]; then
  PYTHON_BIN="$HERMES_HOME/hermes-agent/venv/bin/python"
fi
GSETUP="$PYTHON_BIN $GWORKSPACE_SKILL_DIR/scripts/setup.py"
```

### Step 0: Check if already set up

```bash
$GSETUP --check
```

If it prints `AUTHENTICATED`, skip to Usage — setup is already done.

### Step 1: Triage — ask the user what they need

**Question 1: "What Google services do you need? Just email, or also
Calendar/Drive/Sheets/Docs?"**

- **Email only** → Use the `himalaya` skill instead — simpler setup.
- **Calendar, Drive, Sheets, Docs (or email + these)** → Continue below.

**Partial scopes**: Users can authorize only a subset of services. The setup
script accepts partial scopes and warns about missing ones.

**Question 2: "Does your Google account use Advanced Protection?"**

- **No / Not sure** → Normal setup.
- **Yes** → Workspace admin must add the OAuth client ID to allowed apps first.

### Step 2: Create OAuth credentials (one-time, ~5 minutes)

Tell the user:

> 1. Go to https://console.cloud.google.com/apis/credentials
> 2. Create a project (or use an existing one)
> 3. Enable the APIs you need (Gmail, Calendar, Drive, Sheets, Docs, People)
> 4. Credentials → Create Credentials → OAuth 2.0 Client ID → Desktop app
> 5. Download JSON and tell me the file path

```bash
$GSETUP --client-secret /path/to/client_secret.json
```

### Step 3: Get authorization URL

```bash
$GSETUP --auth-url
```

Send the URL to the user. After authorizing, they paste back the redirect URL or code.

### Step 4: Exchange the code

```bash
$GSETUP --auth-code "THE_URL_OR_CODE_THE_USER_PASTED"
```

### Step 5: Verify

```bash
$GSETUP --check
```

Should print `AUTHENTICATED`. Token refreshes automatically from now on.

## Usage

All commands go through the API script:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
GWORKSPACE_SKILL_DIR="$HERMES_HOME/skills/productivity/google-workspace"
PYTHON_BIN="${HERMES_PYTHON:-python3}"
if [ -x "$HERMES_HOME/hermes-agent/venv/bin/python" ]; then
  PYTHON_BIN="$HERMES_HOME/hermes-agent/venv/bin/python"
fi
GAPI="$PYTHON_BIN $GWORKSPACE_SKILL_DIR/scripts/google_api.py"
```

### Gmail

```bash
$GAPI gmail search "is:unread" --max 10
$GAPI gmail get MESSAGE_ID
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail send --to user@example.com --subject "Report" --body "<h1>Q4</h1>" --html
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
```

### Calendar

```bash
$GAPI calendar list
$GAPI calendar create --summary "Standup" --start 2026-03-01T10:00:00+01:00 --end 2026-03-01T10:30:00+01:00
$GAPI calendar create --summary "Review" --start ... --end ... --attendees "alice@co.com,bob@co.com"
$GAPI calendar delete EVENT_ID
```

### Drive

```bash
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5
```

#### Shared Drive operations (requires direct REST API — gws CLI does not support Shared Drives)

Use `urllib.request` directly with the Drive v3 API. Key difference from My Drive: every request needs
`supportsAllDrives=true`, `includeItemsFromAllDrives=true`, and `corpora=drive` + `driveId`.

```python
import sys, os, json, urllib.request, urllib.parse, time
sys.path.insert(0, f"{os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))}/skills/productivity/google-workspace/scripts")
from gws_bridge import get_valid_token

token = get_valid_token()
DRIVE_ID = "0AMV9-bYAvS7GUk9PVA"  # last segment of the Shared Drive URL

def gapi(method, path, body=None, params_dict=None):
    base = f"https://www.googleapis.com/drive/v3/{path}"
    if params_dict:
        base += "?" + urllib.parse.urlencode(params_dict)  # MUST use urlencode — spaces in q= cause InvalidURL
    data = json.dumps(body).encode() if body else None
    headers = {"Authorization": f"Bearer {token}"}
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def list_folder(folder_id):
    """List contents of a folder in the Shared Drive."""
    params = {
        "driveId": DRIVE_ID,
        "includeItemsFromAllDrives": "true",
        "supportsAllDrives": "true",
        "corpora": "drive",
        "q": f"'{folder_id}' in parents",
        "fields": "files(id,name,mimeType,parents)",
        "pageSize": "100",
        "orderBy": "name"
    }
    return gapi("GET", "files", params_dict=params).get("files", [])

def create_folder(name, parent_id):
    r = gapi("POST", "files", {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]},
             {"supportsAllDrives": "true"})
    return r["id"]

def move(file_id, new_parent_id, old_parent_id):
    """Move a file/folder within Shared Drive — must pass both addParents and removeParents."""
    return gapi("PATCH", f"files/{file_id}", {}, {
        "addParents": new_parent_id,
        "removeParents": old_parent_id,
        "supportsAllDrives": "true",
        "fields": "id,name"
    })

def rename(file_id, new_name):
    return gapi("PATCH", f"files/{file_id}", {"name": new_name}, {"supportsAllDrives": "true"})

# List all Shared Drives the OAuth account has access to:
drives = gapi("GET", "drives", {"pageSize": "20"})
for d in drives.get("drives", []):
    print(d["name"], d["id"])
```

**Critical pitfalls for Shared Drive API:**
- ❌ `urllib.request` raises `InvalidURL: URL can't contain control characters` if you build `?q='folder_id' in parents` by string concatenation — spaces in `in parents` cause it. **Always use `urllib.parse.urlencode(params_dict)` to build the query string.**
- ❌ Using wrong OAuth app ID → `403 Forbidden` on write ops. Shared Drive writes require the app that **owns** the Drive. Use `cli_a97bd21895f89e18` (Hermes-BusyCow) for the BusyCow Shared Drive, NOT `{{LARK_APP_ID}}` (lark-mcp app).
- ❌ `move()` without `removeParents` leaves the file in both locations — always pass both.
- ✅ `gapi drive search` CLI wrapper does NOT work for Shared Drives — always use direct REST.
- ✅ To get Shared Drive ID: it's the last path segment of the Drive URL, e.g. `drive.google.com/drive/folders/0AMV9-bYAvS7GUk9PVA` → ID = `0AMV9-bYAvS7GUk9PVA`
- ✅ To list Shared Drives available to the account: `GET /drive/v3/drives`

#### Shared Drive restructuring workflow (confirmed pattern — BusyCow Drive 2026-05-20)

1. **Scan first** — `list_folder(DRIVE_ID)` for root, then recurse per folder. Save all IDs to `/tmp/drive_id_map.json`.
2. **Create new folders** — `create_folder(name, parent_id)`. Save new IDs to `/tmp/drive_new_ids.json`.
3. **Rename root folders** — `rename(file_id, new_name)` before moving children to avoid confusion.
4. **Move in order** — move projects first (they reference other folders), then templates, then leaf files.
5. **`time.sleep(0.3)`** between move calls to avoid rate limit errors.
6. **Verify** — re-run `list_folder` tree after moves to confirm structure.

**BusyCow Drive naming convention (approved 2026-05-20):**
- Root level: `[DX] Folder` prefix for company-wide folders (floats to top, signals "shared by all BLs")
- Root level: bare name for Business Line folders (`[your product]`, `BusyCow`, `[your product]`, `Distify`)
- Inside each BL: `00_Core`, `01_Sales & Marketing`, `02_Commercial`, `03_Clients`, `90_Inbox`, `Archived`
- `[DX] Projects/` at root — all time-bound projects regardless of BL, named `[BL] Project Name YYYY`
- `[DX] Operations/` — Invoices, Quotations, Templates, Contracts (cross-BL ops)
- `[DX] Company/` — company-level pitch, legal, brand (formerly empty `BusyCow/` folder)

#### List files in a folder (by folder ID from URL)

Use `--raw-query` with the `parents in` syntax. The folder ID is the last segment of the Google Drive URL.

```bash
FOLDER_ID="1U7KwezW-igc45KkNTnSKxRwnZfmaEQgA"
$GAPI drive search "'$FOLDER_ID' in parents" --raw-query --max 50
```

PITFALL: `gws_bridge.py drive files list --params '{"q": "..."}' ` does NOT work for folder queries — returns empty or 400 Invalid Value. Always use the `$GAPI drive search ... --raw-query` wrapper for folder listing.

#### Download a .docx / binary file from Drive

Files stored as `.docx` (not native Google Docs) CANNOT be exported via `files export` — that API only works for native Docs/Sheets/Slides and returns error: `fileNotExportable`. Use `files get` with `alt=media` instead:

```python
import json, os
from hermes_tools import terminal

hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
skill_dir = f"{hermes_home}/skills/productivity/google-workspace"
python_bin = f"{hermes_home}/hermes-agent/venv/bin/python"
gbridge = f"{python_bin} {skill_dir}/scripts/gws_bridge.py"

file_id = "FILE_ID_HERE"
params = json.dumps({"fileId": file_id, "alt": "media"})
# IMPORTANT: output path must be RELATIVE — gws rejects absolute paths with a validation error
terminal(f"cd /tmp && {gbridge} drive files get --params '{params}' -o myfile.docx")
```

PITFALL: If you pass an absolute path like `-o /tmp/myfile.docx`, gws rejects it with: `--output resolves to ... which is outside the current directory`. Always `cd` to the target dir first and use a relative filename.

#### Read a Google Doc shared via public link (no auth required)

When a Google Doc is shared as "Anyone with the link can view", you can export it directly via curl **without OAuth** — the export URL is public:

```bash
DOC_ID="1afrXCOjR_D5itEGeTuei_wMEDWjdtX68"
curl -s -L -o /tmp/doc.txt "https://docs.google.com/document/d/${DOC_ID}/export?format=txt"
# Other formats: format=docx, format=pdf, format=html
```

PITFALL: `browser_navigate` to the export URL triggers a download and returns an error (`Download is starting`) — use curl instead.

PITFALL: The Google Docs API (`gws docs get DOC_ID`) requires the Docs API to be enabled in Google Cloud Console. If you get a 403 "Google Docs API has not been used", use the curl export approach above for public docs, or enable the API at https://console.developers.google.com/apis/api/docs.googleapis.com/overview.

PITFALL: **Google Sheets stored as .xlsx (Office format) cannot be read via the Sheets API** — the API returns `400: This operation is not supported for this document. The document must not be an Office file.` when calling `spreadsheets.get` or `spreadsheets.values.get`. These files show `rtpof=true` in their share URL. To read them: download via `drive files get --params '{"fileId": "ID", "alt": "media"}'` then parse with openpyxl. If the file returns 404, it's not in the authorized user's Drive (shared-only files are invisible to the API — user must add to their Drive first).

PITFALL: `drive files export` only works for **native Google Docs** (Docs/Sheets/Slides created inside Google Drive). If the file is a `.docx` upload, it returns `fileNotExportable`. Use `drive files get --params '{"fileId": "...", "alt": "media"}'` for uploaded binary files.

PITFALL: `drive files get` (metadata or media) returns 404 if the file was shared with you via a public link but is not in your Drive. The Drive API only sees files the authenticated user owns or has been explicitly added to their Drive.

PITFALL: `web_extract("file:///tmp/...")` is **blocked** — the tool rejects local file:// URLs as "private network address". To read downloaded PDFs, use `pymupdf` via terminal instead:
```python
from hermes_tools import terminal
r = terminal("""
source ~/.hermes/hermes-agent/venv/bin/activate && python3 -c "
import pymupdf
doc = pymupdf.open('/tmp/file.pdf')
for i, page in enumerate(doc):
    print(f'--- Page {i+1} ---')
    print(page.get_text())
"
""")
print(r['output'])
```
`pymupdf` is available in the Hermes venv. Works for all PDFs including scanned ones (with embedded text).

PITFALL: `drive files copy` returns 404 if the template file is not in the authenticated user's Drive — even if it's publicly shared. The file must be owned by or explicitly shared (edit/view) with the OAuth account. Ask the user to share the file with the OAuth account's email, or use `Make a copy` in Google Docs UI first.

PITFALL: Google Docs API (`docs batchUpdate`) requires the **`documents`** scope (not `documents.readonly`) and the **Docs API must be enabled** in Google Cloud Console. If 403: enable at https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=PROJECT_ID

PITFALL: OAuth scopes for full Invoice workflow require `drive` (not `drive.readonly`) and `documents` (not `documents.readonly`). Update setup.py SCOPES list and re-run `--auth-url` + `--auth-code` flow to get new token with write scopes.

#### Extract text from downloaded .docx files

`python-docx` (`import docx`) is available in the Hermes venv:

```python
import docx

doc = docx.Document("/tmp/myfile.docx")
text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
print(text)
```

### Contacts

```bash
$GAPI contacts list --max 20
```

### Sheets

```bash
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

### Docs

```bash
$GAPI docs get DOC_ID
```

### Patching Calendar Events (attendees, etc.)

**PITFALL: `gws calendar events patch` does NOT correctly handle array fields like `attendees`** — it stringifies the array instead of sending it as JSON. Use the Google Calendar REST API directly via Python instead:

```python
import json, os, sys, urllib.request

hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
skill_dir = f"{hermes_home}/skills/productivity/google-workspace"
sys.path.insert(0, f"{skill_dir}/scripts")
from gws_bridge import get_valid_token

access_token = get_valid_token()
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

EVENT_ID = "your_event_id"
body = {
    "attendees": [
        {"email": "alice@example.com"},
        {"email": "bob@example.com"}
    ]
}
data = json.dumps(body).encode()
req = urllib.request.Request(
    f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{EVENT_ID}?sendUpdates=all",
    data=data, headers=headers, method="PATCH"
)
with urllib.request.urlopen(req, timeout=15) as resp:
    result = json.loads(resp.read())
    print(result.get("attendees"))
```

Pass `?sendUpdates=all` to notify attendees of the change.

### Direct gws access (advanced)

For operations not covered by the wrapper, use `gws_bridge.py` directly:

```bash
GBRIDGE="$PYTHON_BIN $GWORKSPACE_SKILL_DIR/scripts/gws_bridge.py"
$GBRIDGE calendar +agenda --today --format table
$GBRIDGE gmail +triage --labels --format json
$GBRIDGE drive +upload ./report.pdf
$GBRIDGE sheets +read --spreadsheet SHEET_ID --range "Sheet1!A1:D10"
```

## Output Format

All commands return JSON via `gws --format json`. Key output shapes:

- **Gmail search/triage**: Array of message summaries (sender, subject, date, snippet)
- **Gmail get/read**: Message object with headers and body text
- **Gmail send/reply**: Confirmation with message ID
- **Calendar list/agenda**: Array of event objects (summary, start, end, location)
- **Calendar create**: Confirmation with event ID and htmlLink
- **Drive search**: Array of file objects (id, name, mimeType, webViewLink)
- **Sheets get/read**: 2D array of cell values
- **Docs get**: Full document JSON (use `body.content` for text extraction)
- **Contacts list**: Array of person objects with names, emails, phones

Parse output with `jq` or read JSON directly.

## Invoice Generation via Google Docs Template

Pattern confirmed working (2026-05-15):

1. **Template must be in the authorized user's My Drive** — shared-only files return 404 on copy even with full Drive scope. User must "Make a copy" or share the file with the authorized Google account.
2. **Copy template**: `drive files copy --params '{"fileId": "TEMPLATE_ID", "name": "New Name"}'`
3. **Fill placeholders**: `docs batchUpdate` with `replaceAllText` requests
4. **Export PDF**: `drive files get export?mimeType=application/pdf`
5. **Enable Google Docs API** in Google Cloud Console before first use — `403 Google Docs API has not been used` otherwise

```python
# Full working pattern
access_token = refresh_google_token()
H = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

# 1. Copy
r = gapi('POST', f'https://www.googleapis.com/drive/v3/files/{TEMPLATE_ID}/copy',
    {'name': 'Invoice Name'})
doc_id = r['id']

# 2. Fill
requests = [{'replaceAllText': {
    'containsText': {'text': k, 'matchCase': True}, 'replaceText': v
}} for k, v in replacements.items()]
gapi('POST', f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate',
    {'requests': requests})

# 3. Export PDF
req = urllib.request.Request(
    f'https://www.googleapis.com/drive/v3/files/{doc_id}/export?mimeType=application/pdf',
    headers={'Authorization': f'Bearer {access_token}'})
with urllib.request.urlopen(req, timeout=30) as r:
    pdf_data = r.read()
```

**Scopes required**: `drive` (NOT `drive.readonly`) + `documents` (NOT `documents.readonly`)

## Patching Calendar Events (attendees, location, etc.)

The `gws calendar events patch` CLI **cannot handle array fields** — passing `attendees` as a repeated param stringifies it instead of sending a JSON array, leaving the original attendees unchanged.

Use the Google Calendar REST API directly for any PATCH that involves arrays:

```python
import json, os, sys, urllib.request

hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
skill_dir = f"{hermes_home}/skills/productivity/google-workspace"
sys.path.insert(0, f"{skill_dir}/scripts")
from gws_bridge import get_valid_token

access_token = get_valid_token()
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

EVENT_ID = "YOUR_EVENT_ID"
body = {
    "attendees": [
        {"email": "alice@example.com"},
        {"email": "bob@example.com"}
    ]
}
data = json.dumps(body).encode()
req = urllib.request.Request(
    f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{EVENT_ID}?sendUpdates=all",
    data=data, headers=headers, method="PATCH"
)
with urllib.request.urlopen(req, timeout=15) as resp:
    result = json.loads(resp.read())
    print([a["email"] for a in result.get("attendees", [])])
```

`sendUpdates=all` ensures all attendees receive the updated invite notification.

The `get_valid_token()` function (not `refresh_google_token`) is the correct import from `gws_bridge.py`.

## Rules

1. **Never send email or create/delete events without confirming with the user first.**
2. **"Calendar invite" always means Google Calendar** — even if the team uses Feishu/Lark for messaging. Default to Google Calendar unless the user explicitly says "Feishu Calendar" or "Lark Calendar".
2. **Check auth before first use** — run `setup.py --check`.
3. **Use the Gmail search syntax reference** for complex queries.
4. **Calendar times must include timezone** — ISO 8601 with offset or UTC.
5. **Respect rate limits** — avoid rapid-fire sequential API calls.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `NOT_AUTHENTICATED` | Run setup Steps 2-5 |
| `REFRESH_FAILED` | Token revoked — redo Steps 3-5 |
| `gws: command not found` | Install: `npm install -g @googleworkspace/cli` |
| `HttpError 403` | Missing scope — `$GSETUP --revoke` then redo Steps 3-5 |
| `HttpError 403: Access Not Configured` | Enable API in Google Cloud Console |
| `Request had insufficient authentication scopes` | Token has read-only scopes. Update `SCOPES` in `setup.py` (see below) then re-auth |
| Advanced Protection blocks auth | Admin must allowlist the OAuth client ID |

## ⚠️ Write Scopes — Default is Read-Only

The default setup script uses `drive.readonly` and `documents.readonly`. These are **insufficient** for:
- Copying a Google Doc (`drive files copy`)
- Creating new Docs
- Replacing text in a Doc (Docs API batchUpdate)
- Uploading files

To enable write access, update `SCOPES` in `setup.py`:

```python
# ❌ Read-only (default) — cannot copy/create/modify:
"https://www.googleapis.com/auth/drive.readonly",
"https://www.googleapis.com/auth/documents.readonly",

# ✅ Full access — required for Invoice/template workflows:
"https://www.googleapis.com/auth/drive",
"https://www.googleapis.com/auth/documents",
```

Then re-run auth:
```bash
$GSETUP --auth-url
# User clicks link, pastes back redirect URL
$GSETUP --auth-code "THE_REDIRECT_URL"
$GSETUP --check  # should show AUTHENTICATED
```

## Revoking Access

```bash
$GSETUP --revoke
```
