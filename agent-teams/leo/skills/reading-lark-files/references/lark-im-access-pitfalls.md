# Lark IM Access Pitfalls — Bot vs User Identity

Supplement for reading group messages and user-sent files from Lark/Feishu.
Absorbed from the `lark-im-pitfalls` skill.

---

## ⚠️ lark-cli Workspace Sharing — Shared Bot Identity

When multiple agent profiles share `LARK_CLI_WORKSPACE=hermes`, all lark-cli API calls use the same bot identity. Document edit history in Lark will show all agents as the same bot name — there is no per-agent attribution.

**This is acceptable** for most operational workflows. If per-agent edit attribution is required, each agent needs its own `lark-cli config bind` with a separate app.

To set up shared workspace for an agent:
```bash
echo "LARK_CLI_WORKSPACE=hermes" >> ~/.hermes/profiles/<agent>/.env
```

## ⚠️ Gateway Silent in Group — Bot Not a Member

**Symptom**: Approved user messages a group, gateway shows zero log activity for that chat_id — no skip, no drop, complete silence.

**Cause**: The Hermes bot was never invited into the group (or was removed). The Feishu event subscription only delivers events to bots that are members of the chat.

**Diagnosis** — check membership via bot token:
```python
import urllib.request, json
with open("/mnt/disks/data/hermes/.env") as f:
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

## ⚠️ `strict-mode bot` Blocks `auth login`

**Symptom**: `lark-cli auth login` returns:
```
command_denied: strict mode is "bot", only bot-identity commands are available
```

**Cause**: `strict-mode` is set to `bot`, which blocks all user-identity commands including `auth login`.

**Fix**:
```bash
lark-cli config strict-mode          # check current setting
lark-cli config strict-mode user     # user-only (confirm with user first)
lark-cli config strict-mode off      # no restriction (safest default)
```

**When to use each mode:**
- `user` — user wants file/doc ownership under their own identity (not bot)
- `bot` — agent-only operations, no human auth needed
- `off` — mixed usage (most common)

⚠️ Switching does NOT require re-bind or re-auth. Existing tokens are preserved.
⚠️ Always confirm with user before switching — it changes whose identity ALL lark-cli operations run under.
⚠️ Run `lark-cli update` BEFORE switching strict-mode — older installs may not have the command.
⚠️ User mode means file/doc ownership goes to the user (not the bot) — this is often the explicit goal when switching.

---

## Scope Quick Reference

| Task | Identity | Required Scopes |
|------|----------|-----------------|
| Read user messages in group | `--as user` | `im:message.group_msg:get_as_user` |
| Read P2P messages | `--as user` | `im:message.p2p_msg:get_as_user` |
| Search messages with attachments | `--as user` | `search:message` |
| Resolve sender names | `--as user` | `contact:user.base:readonly` |
| Download a file from a message | `--as bot` or `--as user` | `im:resource` |
