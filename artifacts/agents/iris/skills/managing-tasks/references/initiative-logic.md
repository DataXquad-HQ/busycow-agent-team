# Auto-Initiative & Auto-Goal Logic

## Step 1 — Classify the task
Extract: Business Line, Type, Theme keywords (client name, project name, activity)

## Step 2 — Match to existing Initiative
Fuzzy-match on business line + keywords:

| Signal | Initiative | New Record ID |
|--------|-----------|----|
| HKRFID / PM system | HKRFID — PM system migration | `recvk51nMLCRAR` |
| university / exchange event | university exchange event | `recvk51osFWgxW` |
| James / fire-response / [Product B] reseller | [Product B] Taiwan — James fire-response use case | `recvk51p9B43OO` |
| GTM / recurring revenue | [Product A] GTM & commercial strategy reset | `recvk51pUslqnR` |
| OnNet / Malaysia | [Product A] x OnNet — Malaysia Resale | `recvk51rfDfBCF` |
| water utility / engineering progress | [Product A] x water utility — engineering progress tracking | `recvk51rTtaVl8` |
| internal systems / pipeline / automation | [Org] internal systems & pipeline optimization | `recvk51syPo68J` |
| [Portfolio Company] | [Portfolio Company] — AI Agent deployment plan | `recvk51qAwDvxt` |
| MTR / patrol / robot | HK MTR Patrol Robots 2026 | `recvk51tdv4Kzo` |
| Vikings / Odoo | The Vikings x Odoo evaluation | `recvk51tSKBeIP` |
| productization / templates / subscription add-ons | [Product A] — productization strategy: templates + subscription add-ons | `recvkSyGtVtIJr` |

- **>80% confidence** → link silently, mention inline: "→ Assigned to [Initiative Name]"
- **Ambiguous** → ask once: "I think this task belongs under [X] or [Y]. Which is right?"
- **No match** → propose new Initiative (see Step 4)

## Step 3 — Map Initiative to Goal
| Business Line | Goal Record ID |
|---------------|----------------|
| [Product A] | `recvk50RBz2xk5` |
| [Product B] | `recvk50S1aUBia` |
| [Portfolio Company] | `recvk50SoAHGfD` |
| [Org] | `recvk50SSQ0qSD` |

Always set Goal field (`fldQ5gGqoy`) when creating an Initiative.

## Step 4 — Create new Initiative if needed
1. Propose: Name, Type, Business Line, Target Finished
2. Say: "This looks like a new initiative. I suggest creating "[Name]" under [Goal]. Confirm and I will create it."
3. Wait for confirmation, then create and record for the session.
