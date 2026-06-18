# Lark Channel Management — Pitfalls

## Adding Members to a Chat

**Symptom:** `lark-cli im chat.members create` fails with `missing_scope: im:chat.members:write_only`

**Cause:** This scope is not included in the default `lark-cli auth login` flow.

**Fix:**
```bash
lark-cli auth login --scope "im:chat.members:write_only im:chat:read"
```
Then retry with `--as user`.

**Note:** Bot identity (`--as bot`) is blocked by strict-mode on this install. Always use `--as user`.

---

## Channels Created via MCP Have No Human Members

When a group chat is created via `mcp_lark_im_v1_chat_create`, the bot is the creator/owner but **no human members are added automatically**. The channel shows 0 members until humans are explicitly added.

After creating a channel, always:
1. Add all required human members via `lark-cli im chat.members create`
2. Verify membership with `lark-cli im chat.members get`

---

## Resolving Human open_id for Adding

Don't use email lookup — it often fails for internal users. Instead:
1. Get members from any existing channel both humans are in:
   ```bash
   lark-cli im chat.members get --params '{"chat_id": "oc_<known_channel>"}' --as user
   ```
2. Match by name in the returned list to get `member_id` (open_id format)

[Founder 1]'s open_id: `{{LARK_USER_OPEN_ID}}`
[Founder 2]'s open_id: `{{LARK_USER_OPEN_ID}}`
