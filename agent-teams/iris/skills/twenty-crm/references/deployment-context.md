# Twenty CRM — Deployment Context (DataXquad)

## Instance details

| Item | Value |
|------|-------|
| Install path | `/mnt/disks/data/twenty/` |
| Docker containers | `twenty-server-1`, `twenty-db-1` |
| Internal URL | `http://localhost:3001` |
| Tailscale URL | `http://100.118.240.101:3001` (browser only — never in agent code) |
| Admin email | `hunter.lin@distify.ai` |
| API Key name | `Hermes` (expires 2126) |
| API Key ID | `529a4913-cc22-4e1b-b8ee-52a53c4c5d3c` |
| Workspace ID | `a352ccf9-ed5f-40d3-910f-706074dc3877` |

## Standard object metadata IDs (from DB)

| Object | Metadata ID |
|--------|-------------|
| company | `10c93af8-1586-44f5-9554-e862dea90c01` |
| person | `a278e81b-bf75-4ce9-9398-cbea2f8e5b9a` |
| opportunity | `ab82bc92-fe4b-471f-bed8-7f89e9a4d63b` |

## Custom object IDs

| Object | ID |
|--------|----|
| partner | `f50bbdce-3732-414d-bcb3-8cd6abd5f6c2` |
| quotation | `1ecb1a71-de9b-4ef5-9471-06159482d409` |
| quotationItem | `26662ed7-b75a-417c-9833-f531e1fdb5b3` |
| invoice | `fd480fa5-824d-4a4a-96a6-dc2687a24fb7` |
| invoiceItem | `e5919d5c-1bcd-425f-897d-1f99b0ac98c0` |

## Playbooks repo

Universalized ({{PLACEHOLDER}}) version of this skill lives at:
`https://github.com/DataXquad-HQ/busycow-playbooks/blob/main/shared-skills/twenty-crm.md`

CRM schema (object/field definitions) at:
`https://github.com/DataXquad-HQ/busycow-playbooks/blob/main/structural-data/crm/SCHEMA.md`

Install guide at:
`https://github.com/DataXquad-HQ/busycow-playbooks/blob/main/third-party-tools/twenty-crm/SETUP.md`

## Access rule rationale

Agents always run on the same VM as Twenty. Using localhost:3001 avoids:
- Tailscale round-trip latency
- Cloudflare tunnel overhead + egress cost
- External auth surface exposure

This rule must survive any future tunnel URL changes — the internal address is stable.
