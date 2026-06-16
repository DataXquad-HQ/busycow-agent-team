# Auto-Initiative & Auto-Goal Logic

## Step 1 — Classify the task
Extract: Business Line, Type, Theme keywords (client name, project name, activity)

## Step 2 — Match to existing Initiative
Fuzzy-match on business line + keywords:

| Signal | Initiative | New Record ID |
|--------|-----------|----|
| HKRFID / PM系統 | HKRFID — PM 系統資料遷移 | `recvk51nMLCRAR` |
| 逢甲 / 交流會 | 逢甲大學交流會 | `recvk51osFWgxW` |
| James / 消防 / GeoKernel reseller | GeoKernel Taiwan — James 消防應用 | `recvk51p9B43OO` |
| GTM / recurring revenue | BusyCow GTM & 商業策略調整 | `recvk51pUslqnR` |
| OnNet / Malaysia | BusyCow x OnNet — Malaysia Resale | `recvk51rfDfBCF` |
| 臺水 / 工程進度 | BusyCow x 臺水 — 工程進度追蹤 | `recvk51rTtaVl8` |
| 內部系統 / pipeline / automation | DataXquad 內部系統 & Pipeline 優化 | `recvk51syPo68J` |
| AquaOptima | AquaOptima — AI Agent 導入規劃 | `recvk51qAwDvxt` |
| MTR / patrol / robot | HK MTR Patrol Robots 2026 | `recvk51tdv4Kzo` |
| Vikings / Odoo | The Vikings x Odoo 導入評估 | `recvk51tSKBeIP` |
| 產品化 / 模板 / 訂閱 Add-on | BusyCow — 產品化策略：模板銷售 + 訂閱 Add-on | `recvkSyGtVtIJr` |

- **>80% confidence** → link silently, mention inline: "→ 歸入 [Initiative Name]"
- **Ambiguous** → ask once: "這個任務我打算歸入 [X] 或 [Y]，哪個對？"
- **No match** → propose new Initiative (see Step 4)

## Step 3 — Map Initiative to Goal
| Business Line | Goal Record ID |
|---------------|----------------|
| BusyCow | `recvk50RBz2xk5` |
| GeoKernel | `recvk50S1aUBia` |
| AquaOptima | `recvk50SoAHGfD` |
| DataXquad | `recvk50SSQ0qSD` |

Always set Goal field (`fldQ5gGqoy`) when creating an Initiative.

## Step 4 — Create new Initiative if needed
1. Propose: Name, Type, Business Line, Target Finished
2. Say: "這是新的 Initiative，建議建立「[Name]」，歸入 [Goal]。確認後我來建。"
3. Wait for confirmation, then create and record for the session.
