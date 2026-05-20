---
name: lark-mcp-setup
description: Set up lark-mcp as a native MCP server in Hermes config. Covers correct binary path, credentials, known pitfalls (two app IDs, libsecret warning, Method not found), and Feishu quota diagnosis.
version: 1.0.0
metadata:
  hermes:
    tags: [Lark, Feishu, MCP, Integrations]
    related_skills: [native-mcp, lark-bitable-schema-setup]
---

# Lark MCP Setup

Adds lark-mcp as a native MCP server so Hermes can call Lark Base/Doc/Wiki/IM tools directly.

## Binary Location

lark-mcp is installed under the Hermes node runtime, not on system PATH.
Two possible locations (check which exists):

  ~/.nvm/versions/node/v22.15.0/bin/lark-mcp  (confirmed working 2026-05-15)
  ~/.hermes/node/bin/lark-mcp                 (older location)

Do NOT use `which lark-mcp` — it will show not found. Always use the full path.

The preferred approach is to use a wrapper script at ~/.hermes/lark-mcp-wrapper.sh

## config.yaml Entry

Add under mcp_servers in ~/.hermes/config.yaml:

```yaml
mcp_servers:
  lark:
    command: ~/.hermes/lark-mcp-wrapper.sh
```

Contents of ~/.hermes/lark-mcp-wrapper.sh:
```bash
#!/bin/bash
exec ~/.nvm/versions/node/v22.15.0/bin/lark-mcp mcp \
  -a {{LARK_APP_ID}} \
  -s <app_secret> \
  -d https://open.larksuite.com
```
Make sure the wrapper is executable: `chmod +x ~/.hermes/lark-mcp-wrapper.sh`

CRITICAL: Do NOT use `-t base,doc,wiki,im`. The `-t` flag in v0.5.1 does NOT accept
comma-separated module names — it passes the entire string as a single allowTools entry,
which matches nothing and results in 0 tools registered. Omitting `-t` uses defaultToolNames
which includes 19 tools covering bitable/docx/im/wiki — exactly what's needed.

The "Method not found" error in logs is caused by 0 tools registered (empty capabilities
in the initialize response). Fix: remove `-t` from args.

## Lark Bitable Record Deletion

The `lark-mcp` tool (v0.5.1) does NOT include a delete record tool — only create/update/search.
To delete records, call the Lark REST API directly via `execute_code`.

### Required setup (3 layers, all must pass):

**Layer 1 — API Scope**
Add `bitable:record:delete` (or `bitable:app`) to the App's Permissions & Scopes in
open.larksuite.com developer console. Then **publish a new app version** — adding scope alone
is NOT enough. The publish step is mandatory for scopes to take effect.

**Layer 2 — File Permission**
The App must have **「可管理」(full_access)** on the specific Bitable document.
「可編輯」(edit) is NOT sufficient for delete — delete requires manage-level permission.
Set this in the Bitable's share settings, not in the developer console.

**Layer 3 — Call pattern**
```python
import urllib.request, json, urllib.error

# Get token
req = urllib.request.Request(
    "https://open.larksuite.com/open-apis/auth/v3/app_access_token/internal",
    data=json.dumps({"app_id": "{{LARK_APP_ID}}", "app_secret": "{{LARK_APP_SECRET}}Y"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req, timeout=10) as resp:
    token = json.loads(resp.read())["app_access_token"]

# Delete record
APP_TOKEN = "{{LARK_APP_TOKEN}}"
TABLE_ID  = "{{TABLE_ID}}"
record_id = "recXXXXXX"

url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"}, method="DELETE")
with urllib.request.urlopen(req, timeout=10) as resp:
    result = json.loads(resp.read())
    # result["code"] == 0 means success
```

### Error codes
- `91403` Forbidden → file permission issue (need 可管理, not just 可編輯)
- `403` HTTP → either scope not published or file permission insufficient
- Both can appear even after adding scope, if the app version wasn't published



There are TWO separate Lark/Feishu apps in use:

  App 1 (Gateway platform — Feishu bot messaging):
    app_id:     cli_a97bd21895f89e18
    env var:    FEISHU_APP_ID / FEISHU_APP_SECRET in ~/.hermes/.env

  App 2 (lark-mcp wrapper — Base/Doc/Wiki API access, Lark 國際版):
    app_id:     {{LARK_APP_ID}}
    secret:     {{LARK_APP_SECRET}}Y
    domain:     https://open.larksuite.com
    wrapper:    ~/.hermes/lark-mcp-wrapper.sh

  NOTE: Previous App 2 was cli_a97aab1888f8de17 (Feishu版, wrong). Replaced 2026-05-07
  with {{LARK_APP_ID}} (Lark 國際版, open.larksuite.com).

These are different apps with different permissions. Using the wrong one causes
"app unauthorized" (code 10014) or "app secret invalid".

If lark-mcp fails to authenticate, confirm which app_id/secret the wrapper uses
vs what's in .env — they are intentionally separate.

## Lark 國際版 vs Feishu

lark-mcp 預設連 Feishu (open.feishu.cn)。要連 Lark 國際版需加 `-d` 參數：

  -d https://open.larksuite.com

App 必須在 open.larksuite.com 建立（非 open.feishu.cn）。
Hunter 用的是 Lark 國際版 ({{LARK_APP_ID}})，Gateway Feishu bot 是另一個 app。



Quick sanity check (should return initialize response):

  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}' \
    | timeout 5 ~/.hermes/node/bin/lark-mcp mcp \
      -a cli_a97aab1888f8de17 -s <secret> -t base,doc,wiki,im -l zh

Expected: JSON response with serverInfo.name = "Feishu/Lark MCP Server"

## Known Warnings (Safe to Ignore)

  [WARN] Failed to initialize encryption: libsecret-1.so.0: cannot open shared object file
  [WARN] Builtin User Access Token Store will be disabled

These appear because libsecret is not installed on this Linux host. lark-mcp falls back
to memory store. App-credential-based auth (cli_* + secret) still works fine.

## Why "Method not found" in Logs

The old lark-mcp wrapper was listed in a previous gateway config attempt but not in
mcp_servers properly. "Method not found" in errors.log means the MCP server connected
but an unsupported RPC method was called — usually from a version mismatch or
incomplete tool list call. Re-adding via mcp_servers with correct args fixes this.

## Group Message Behavior — @mention Required

In Feishu/Lark **group chats**, the bot only responds when it is **@mentioned**.
Messages sent in a group without @mention are silently ignored.

- DM (private chat): responds to all messages ✅
- Group chat + `@Hermes-BusyCow`: responds ✅
- Group chat without @mention: **ignored** ❌

This is controlled by the gateway adapter (`feishu.py` line 6: "group @mention-gated").
It is NOT a bug — it is by design to avoid responding to every group message.

### Group Policy Config

The `FEISHU_GROUP_POLICY` env var in `~/.hermes/.env` controls who can interact in groups:

| Value | Behavior |
|-------|----------|
| `open` | Anyone in the group can trigger the bot (via @mention) |
| `allowlist` | Only users in `FEISHU_ALLOWED_USERS` can trigger the bot |
| `admin_only` | Only admins can trigger |
| `disabled` | Bot ignores all group messages |

Default is `allowlist`. For open group access, set `FEISHU_GROUP_POLICY=open`.

Per-group overrides are possible via `group_rules` in config.yaml:

```yaml
# Under the feishu platform section in config.yaml
group_rules:
  {{CHAT_ID}}:   # chat_id
    policy: open
```

After changing group policy, restart the gateway:
```bash
hermes gateway restart
```

### Finding the Bot's Chat List

To check which groups the bot is already in:

```python
mcp_lark_im_v1_chat_list(params={"page_size": 50})
```

Returns all chats with their `chat_id` — use this to find the correct `chat_id` for `group_rules` config.

## Feishu Quota Exceeded (code 99991403)

When you see:
  Send failed: [99991403] This month's API call quota has been exceeded

This is a monthly API quota on the Feishu app tier, NOT a connectivity issue.
The gateway can still receive messages but cannot send replies or add reactions.

Workaround: Switch to Telegram as primary platform until Feishu quota resets.
The gateway supports both simultaneously — Telegram (polling) stays functional
even when Feishu send is blocked.

Telegram allowlist is in ~/.hermes/.env:
  TELEGRAM_ALLOWED_USERS=7341314810,7699699350

Add user IDs there to grant access. Get a user's ID by messaging @userinfobot on Telegram.

## Bitable Record Delete — Not Supported

lark-mcp v0.5.1 does NOT include a delete record tool. The tool list only has:
- `bitable_v1_appTableRecord_create`
- `bitable_v1_appTableRecord_search`
- `bitable_v1_appTableRecord_update`

Calling the Lark REST delete endpoint directly (`DELETE /bitable/v1/apps/.../records/:id`)
returns **403 Forbidden** because the App (`{{LARK_APP_ID}}`) is missing the
`bitable:record:delete` permission scope.

**To enable delete:**
1. Go to [open.larksuite.com](https://open.larksuite.com) developer console
2. Find App `{{LARK_APP_ID}}`
3. Permissions & Scopes → add `bitable:app` or `bitable:record:delete`
4. Publish a new App version

**Until then:** the only workaround is marking unwanted records `Done: true` — they
disappear from active views but are not physically removed.

## After Config Change

Restart the gateway to pick up new mcp_servers:

  hermes gateway restart
  # or kill the PID and run: hermes gateway run --replace &
