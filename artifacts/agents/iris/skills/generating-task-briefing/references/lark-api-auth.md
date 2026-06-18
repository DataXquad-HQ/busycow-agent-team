# Lark API Auth — Task Tracker

## Credentials (Feishu — open.feishu.cn)
- App ID: `cli_a97aab1888f8de17`
- Secret: `neUkvvYlfjJoaMhtB7GgA6pktgt0fM7n`

> ⚠️ **Domain note**: `open.larksuite.com` returns `10014 app unauthorized` for this app.
> The correct domain is `open.feishu.cn`. However, prefer `lark-cli --as bot` which abstracts this.

## Preferred: lark-cli (no manual token needed)
```bash
lark-cli api POST /open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search \
  --as bot \
  --data '{"page_size": 100}' > /tmp/tasks_raw.json
```

## Manual token (fallback, feishu.cn only)
```bash
curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id": "cli_a97aab1888f8de17", "app_secret": "neUkvvYlfjJoaMhtB7GgA6pktgt0fM7n"}'
# Returns: {"tenant_access_token": "t-xxxx", "expire": 7200}
```

## Search Records (manual curl)
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search" \
  -H "Authorization: Bearer {TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"page_size": 100}' > /tmp/tasks_raw.json
# Paginate: use data.page_token when data.has_more=true
```
