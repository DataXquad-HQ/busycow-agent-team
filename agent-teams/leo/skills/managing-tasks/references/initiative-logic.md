# Auto-Initiative & Auto-Goal Logic

## Step 1 — Classify the task
Extract: Business Line, Type, Theme keywords (client name, project name, activity)

## Step 2 — Match to existing Initiative
Fuzzy-match on business line + keywords:

| Signal | Initiative | New Record ID |
|--------|-----------|---|
| HKRFID / PM system | HKRFID — PM System Data Migration | `recvk51nMLCRAR` |
| Fengjia / exchange event | Fengjia University Exchange Event | `recvk51osFWgxW` |
| James / fire safety / GeoKernel reseller | GeoKernel Taiwan — James Fire Safety Application | `recvk51p9B43OO` |
| GTM / recurring revenue | BusyCow GTM & Commercial Strategy Adjustment | `recvk51pUslqnR` |
| OnNet / Malaysia | BusyCow x OnNet — Malaysia Resale | `recvk51rfDfBCF` |
| Taiwan Water / engineering progress | BusyCow x Taiwan Water — Engineering Progress Tracking | `recvk51rTtaVl8` |
| Internal systems / pipeline / automation | {{COMPANY_NAME}} Internal Systems & Pipeline Optimisation | `recvk51syPo68J` |
| AquaOptima | AquaOptima — AI Agent Onboarding Plan | `recvk51qAwDvxt` |
| MTR / patrol / robot | HK MTR Patrol Robots 2026 | `recvk51tdv4Kzo` |
| Vikings / Odoo | The Vikings x Odoo Onboarding Assessment | `recvk51tSKBeIP` |
| Productisation / templates / subscription add-on | BusyCow — Productisation Strategy: Template Sales + Subscription Add-on | `recvkSyGtVtIJr` |

- **>80% confidence** → link silently, mention inline: "→ Assigned to [Initiative Name]"
- **Ambiguous** → ask once: "I'm planning to file this task under [X] or [Y] — which is correct?"
- **No match** → propose new Initiative (see Step 4)

## Step 3 — Map Initiative to Goal
| Business Line | Goal Record ID |
|---------------|----------------|
| BusyCow | `recvk50RBz2xk5` |
| GeoKernel | `recvk50S1aUBia` |
| AquaOptima | `recvk50SoAHGfD` |
| {{COMPANY_NAME}} | `recvk50SSQ0qSD` |

Always set Goal field (`fldQ5gGqoy`) when creating an Initiative.

## Step 4 — Create new Initiative if needed
1. Propose: Name, Type, Business Line, Target Finished
2. Say: "This is a new Initiative. I propose creating \"[Name]\", filed under [Goal]. Confirm and I'll create it."
3. Wait for confirmation, then create and record for the session.
