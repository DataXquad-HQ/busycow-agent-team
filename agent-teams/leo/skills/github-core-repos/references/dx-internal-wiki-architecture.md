# dx-internal-wiki Content Architecture

## What it is

`dx-internal-wiki` is the human-readable Layer 1 of the DataXquad knowledge stack. Iris writes here after key decisions/conversations. Agents read via GBrain (Iris extracts and syncs).

## Directory Structure

```
dx-internal-wiki/
├── README.md                   ← includes BusyCow relationship + three-layer flow diagram
├── agents/
│   ├── README.md               ← delegation map + funnel ownership table
│   └── <agent>/ROLE.md         ← role, responsibilities, metrics, boundaries, tools
├── context/                    ← company context — the inputs agents need to operate
│   ├── README.md               ← table of all docs with status + primary agent reader
│   ├── company-background.md   ← company history, business model, milestones
│   ├── team.md                 ← human team roster, roles, decision authority, contact prefs
│   ├── product-overview.md     ← products list; links to /products/<name>/ for depth
│   ├── brand-messaging.md      ← tone, key messages, tagline, elevator pitch
│   ├── key-contacts.md         ← external stakeholders with sensitivity + engagement rules
│   ├── sales-strategy.md       ← Leo's primary input: ICP, goals, strategy, pipeline benchmarks
│   ├── icp.md                  ← standalone ICP (detailed version)
│   └── gtm-strategy.md         ← GTM strategy for Maya
├── decisions/                  ← YYYY-MM-DD-topic.md per decision
├── strategy/
│   └── org-framework.md        ← org structure + revenue funnel
└── systems/README.md           ← tool usage docs (GBrain, Hindsight, Twenty, Lark, GitHub)
```

## Document Template Pattern

New installs: copy templates from `busycow-agent-package/wiki-setup/` into `context/`.

Each template includes:
- A header note explaining what it is and who uses it
- Structured code blocks with `[bracket]` placeholders
- `⚠️` callouts for special actions (e.g. create /products/ subfolder)

| Template | Primary agent reader | Priority |
|---|---|---|
| `company-background.md` | All agents | First |
| `team.md` | All agents | First |
| `product-overview.md` | Leo, Maya | First |
| `sales-strategy.md` | Leo | First (Pipeline Health Check input) |
| `brand-messaging.md` | Maya, Leo | Before content creation |
| `key-contacts.md` | Leo, Iris | Before outreach |

## ROLE.md Format (for agents/ directory)

Each agent ROLE.md follows this structure:
1. **Role** — one paragraph, what they own, what they are NOT
2. **Position in the Org** — table of functions and owners
3. **Core Responsibilities** — grouped by theme, bullet points
4. **What [Agent] Owns** — metric table (the numbers they track)
5. **Boundaries** — what they handle, what human handles, what they do NOT do
6. **Funnel Position** — ASCII flow diagram
7. **Tools** — table of tools, purposes

## Knowledge Flow

```
Conversation (human + Iris)
    ↓ Iris writes after key decisions
dx-internal-wiki (GitHub, human-readable)
    ↓ Iris extracts with mcp_gbrain_put_page / extract_facts
GBrain (agent-queryable, daily operations)
    ↓ agents act on GBrain context
Hindsight (episodic memory — what happened)
```

Agents query GBrain for daily ops. They do NOT read the wiki directly.
If GBrain has no answer → agent asks Iris → Iris reads wiki and updates GBrain.

## Terminology Rules

- Sales pipeline objects: **Opportunity** (not Deal) — matches Twenty CRM object names
- Exception: CRM field names (`dealType`, `dealId`) and skill dir names (`deal-progressing/`) are technical identifiers — do not rename
- Company objects: Company, People, Opportunity (matching Twenty CRM exactly)
