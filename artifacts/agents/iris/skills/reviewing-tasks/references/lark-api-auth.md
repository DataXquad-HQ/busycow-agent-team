# Lark API Auth — Task Tracker

## Credentials (Lark international — open.larksuite.com)
- App ID: `cli_a97aab1888f8de17`
- Secret: `neUkvvYlfjJoaMhtB7GgA6pktgt0fM7n`

## Get Token (bash)
```bash
curl -s -X POST 'https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id": "cli_a97aab1888f8de17", "app_secret": "neUkvvYlfjJoaMhtB7GgA6pktgt0fM7n"}'
# Returns: {"tenant_access_token": "t-xxxx", "expire": 7200}
```

## Search Records (bash)
```bash
curl -s -X POST "https://open.larksuite.com/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search" \
  -H "Authorization: Bearer {TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"page_size": 100}'
# Paginate: use data.page_token when data.has_more=true
```
