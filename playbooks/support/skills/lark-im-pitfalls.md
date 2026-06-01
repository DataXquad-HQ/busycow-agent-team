---
name: lark-im-pitfalls
version: 1.0.0
description: "Pitfalls and scope requirements for Lark IM message access — bot vs user identity, reading user-sent files, and attachment search. Load alongside lark-im when fetching group history or user-shared files."
tags: [lark, im, pitfalls, permissions]
---

# Lark IM — Pitfalls & Scope Reference

Supplement to `lark-im` skill. Contains hard-won pitfalls discovered in production.

---

## ⚠️ Gateway Silent in Group — Bot Not a Member

**Symptom**: Approved user messages a group, gateway shows zero log activity for that chat_id — no skip, no drop, complete silence.

**Cause**: The Hermes bot was never invited into the group (or was removed). The Feishu event subscription only delivers events to bots that are members of the chat.

**Diagnosis** — check membership via bot token:
```python
import urllib.request, json
with open("~/.hermes/.env") as f:
    env = dict(line.strip().split("=",1) for line in f if "=" in line and not line.startswith("#"))
r = urllib.request.urlopen(urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": env["FEISHU_APP_ID"], "app_secret": env["FEISHU_APP_SECRET"]}).encode(),
    headers={"Content-Type": "application/json"}, method="POST"
), timeout=10)
token = json.loads(r.read())["tenant_access_token"]
chat_id = "oc_XXXXXXXX"
req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members?member_id_type=open_id&page_size=50",
    headers={"Authorization": f"Bearer {token}"}
)
for m in json.loads(urllib.request.urlopen(req, timeout=10).read()).get("data",{}).get("items",[]):
    print(m.get("member_id"), m.get("name"))
```

**Fix**: If bot's open_id is absent → invite the bot in Feishu UI (Members → Add → search bot by name). No gateway restart needed.

---

## ⚠️ Bot Identity Only Returns Bot-Sent Messages

**Pitfall**: `+chat-messages-list --as bot` (and the MCP tool `mcp_lark_im_v1_message_list`) **silently returns only bot messages** — not user messages. The response looks completely valid (50 items, `has_more: true`) but contains zero human-sent content.

**How to detect the problem**: Inspect senders — all items will have `sender_type=app` or `sender.id_type=app_id`. If you see *only* `sender_type=app`, you are reading only bot output.

**Root cause**: The app's bot identity does not have a scope covering `im:message.group_msg` for user messages.

**Fix — read user messages in a group**:
```bash
# Re-auth with the required scopes
lark-cli auth login --scope "im:message.group_msg:get_as_user im:message.p2p_msg:get_as_user contact:user.base:readonly"

# Then fetch with user identity
lark-cli im +chat-messages-list --chat-id <oc_xxx> --as user
```

---

## ⚠️ File/Attachment Search Requires `search:message` Scope (User Only)

To find files or PDFs shared by humans in a group:
```bash
# Re-auth first
lark-cli auth login --scope "search:message"

# Then search by attachment type
lark-cli im +messages-search --chat-id <oc_xxx> --include-attachment-type file --as user
```

- `+messages-search` is **user-only** (`--as bot` not supported for message search)
- `--include-attachment-type` accepts: `file`, `image`, `video`, `link`

---

## ⚠️ MCP `mcp_lark_im_v1_message_list` Has the Same Bot-Only Limitation

The MCP tool uses the same bot token as `--as bot`. When the bot hasn't been granted user-message read scopes, it returns the same bot-only result set. Use `lark-cli --as user` after re-auth for reliable group history access.

---

## Scope Quick Reference

| Task | Identity | Required Scopes |
|------|----------|-----------------|
| Read user messages in group | `--as user` | `im:message.group_msg:get_as_user` |
| Read P2P messages | `--as user` | `im:message.p2p_msg:get_as_user` |
| Search messages with attachments | `--as user` | `search:message` |
| Resolve sender names | `--as user` | `contact:user.base:readonly` |
| Download a file from a message | `--as bot` or `--as user` | `im:resource` |
