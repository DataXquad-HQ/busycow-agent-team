# Twenty CRM — Self-Hosted Setup

## What this creates

- Twenty CRM running via Docker Compose on port 3001
- PostgreSQL data volume persisted on the VM
- Admin account + API key for Hermes agent access

## Requirements

- Docker + Docker Compose v2 installed on the VM
- Port 3001 available (not firewalled internally)
- (Optional) Cloudflare Tunnel for external browser access

---

## Steps

### 1. Create install directory

```bash
mkdir -p ~/twenty && cd ~/twenty
```

### 2. Download config files

```bash
curl -o .env \
  https://raw.githubusercontent.com/twentyhq/twenty/refs/heads/main/packages/twenty-docker/.env.example

curl -o docker-compose.yml \
  https://raw.githubusercontent.com/twentyhq/twenty/refs/heads/main/packages/twenty-docker/docker-compose.yml
```

### 3. Configure .env

Open `.env` and set:

```bash
ENCRYPTION_KEY=$(openssl rand -base64 32)        # generate and paste
PG_DATABASE_PASSWORD=$(openssl rand -base64 16)  # generate and paste
SERVER_URL=http://localhost:3001

# If exposing externally via Cloudflare Tunnel:
# SERVER_URL=https://crm.{{YOUR_DOMAIN}}
```

### 4. Start Twenty

```bash
docker compose up -d
```

Wait ~30 seconds, then verify:

```bash
curl -sf http://localhost:3001/healthz && echo "UP"
```

### 5. Create admin account

Open `http://localhost:3001` (or via Tailscale) in a browser.
Complete onboarding: create workspace + admin user.

Record these values — you'll need them for the skill:

```
Admin email:    {{TWENTY_ADMIN_EMAIL}}
Admin password: {{TWENTY_ADMIN_PASSWORD}}
```

### 6. Generate API key for Hermes

1. Log in to Twenty UI
2. **Settings → API & Webhooks → API Keys → Generate API Key**
3. Name it `Hermes`, set expiry to a far future date
4. Copy the full JWT token (shown only once)

```bash
echo "<paste token here>" > /tmp/twenty_token.txt
```

Record:

```
API Key ID:    {{TWENTY_API_KEY_ID}}      (visible in Settings UI)
Workspace ID:  {{TWENTY_WORKSPACE_ID}}   (Settings → General)
```

### 7. Install the Hermes skill

Copy the full shared skill directory into your Hermes shared skills layer:

```bash
cp -r <repo-root>/artifacts/shared-skills/twenty-crm ~/.hermes/skills/core/twenty-crm
```

Replace all `{{PLACEHOLDER}}` values in the skill with your actual credentials.

### 8. Verify agent access

```python
import requests
TOKEN = open('/tmp/twenty_token.txt').read().strip()
r = requests.post(
    "http://localhost:3001/graphql",
    json={"query": "{ companies { edges { node { id name } } } }"},
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
)
print(r.json())
# Expected: {"data": {"companies": {"edges": []}}}
```

---

## Maintenance

```bash
# Upgrade Twenty
cd ~/twenty
docker compose pull && docker compose up -d

# Backup database
docker exec twenty-db-1 pg_dump -U twenty default > backup_$(date +%Y%m%d).sql

# Restart server (clears schema cache after object/field changes)
docker compose restart twenty-server-1
# Wait ~2 min for NestJS boot, then: curl -sf http://localhost:3001/healthz
```

---

## Next step

→ `<repo-root>/artifacts/shared-skills/` — install shared skills into Hermes profiles
