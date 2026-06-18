# Twenty CRM

[Twenty](https://twenty.com) is an open-source CRM with a developer-first
architecture. We self-host it on the same VM as Hermes.

## Why self-hosted

- Full data ownership, no SaaS lock-in
- GraphQL API at `localhost:3001` — zero egress latency for agents
- Custom objects and fields without tier restrictions
- MCP server at `localhost:3001/mcp` for direct Hermes integration

## Agent access (all profiles)

```
http://localhost:3001/graphql   ← data CRUD
http://localhost:3001/metadata  ← schema management
http://localhost:3001/mcp       ← MCP server
http://localhost:3001/healthz   ← health check
```

Never use Tailscale IP or Cloudflare URL in agent code.
See `../../../artifacts/shared-skills/twenty-crm/SKILL.md` for the full Hermes skill.

## Directory contents

| File | What |
|------|------|
| `SETUP.md` | Docker Compose install + admin account + API key setup |

## CRM schema

→ `../../../artifacts/schemas/crm.md`
