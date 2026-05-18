# Sales Playbook — Setup

Run this after `core/SETUP.md` is complete.

This setup:
1. Creates the **Sales CRM Base** in Lark with 5 tables
2. Installs 5 sales skills
3. Registers skills in the Skills Registry

---

## Step 1 — Create Sales CRM Base

Call the Lark API to create a new Bitable app named "Sales CRM":

```
Create Lark Bitable app: "Sales CRM"
```

Then create the following tables inside this app:

### Table 1: Accounts
| Field | Type | Notes |
|-------|------|-------|
| Account Name | Text (primary) | Company full name |
| Short Name | Text | Internal alias |
| Country | Single Select | e.g. Taiwan / Hong Kong / Malaysia |
| Client Type | Multi Select | Direct / Reseller / Partner / End User |
| Industry | Text | |
| Website | URL | |
| Source | Single Select | How they came into pipeline |
| Business Line | Multi Select | Which products are relevant |
| Notes | Text | |

### Table 2: Contacts
| Field | Type | Notes |
|-------|------|-------|
| Contact Name | Text (primary) | |
| Company | DuplexLink → Accounts | |
| Role / Title | Text | |
| Decision Role | Single Select | Buyer / User / Influencer / Blocker / Champion |
| Phone | Phone | |
| Email | Email | |
| Preferred Channel | Single Select | WhatsApp / Email / Phone |
| LinkedIn | URL | |
| Notes | Text | |

### Table 3: Opportunities
| Field | Type | Notes |
|-------|------|-------|
| Order ID | Text (primary) | Format: OPP-YYYY-SHORTNAME-001 |
| Client | Text | Company name |
| Stage | Single Select | Lead / Qualified / Proposal / Negotiation / Closed Won / Closed Lost |
| Type | Single Select | New Business / Upsell / Renewal / Partnership |
| Product Line | Single Select | |
| Description | Text | |
| Total Contract Value | Number | |
| Next Action | Text | |
| Owner | Text | |
| Notes | Text | |

### Table 4: Partnership
| Field | Type | Notes |
|-------|------|-------|
| ID | Text (primary) | Format: P001, P002... |
| Name | Text | Partner company name |
| Stage | Single Select | Prospect / Qualifying / Agreement / Active / On Hold / Inactive |
| Type | Multi Select | Reseller / Distributor / Referral / Technology / OEM |
| Country | Single Select | |
| Description | Text | Running narrative log |
| Account | DuplexLink → Accounts | |
| Activities | DuplexLink → Activities | |

### Table 5: Activities
| Field | Type | Notes |
|-------|------|-------|
| Summary | Text (primary) | One-line description |
| Account | Text | Company name |
| Contact | Text | Person name |
| Type | Single Select | Call / Meeting / Demo / Email / WhatsApp / Site Visit / Other |
| Client Response | Text | What they said / their reaction |
| Stage Advanced? | Checkbox | Did the deal move forward? |
| Next Action | Text | What needs to happen next |
| Date | DateTime | When it happened |
| Owner | Text | Who conducted the interaction |

After creating, save to Memory:
```
Memory entry: "Sales CRM Base: [app_token] | Accounts: [id] | Contacts: [id] | Opportunities: [id] | Partnership: [id] | Activities: [id]"
```

---

## Step 2 — Install Sales Skills

Fetch and install each skill:

```
1. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/sales/skills/capturing-sales-intel.md
2. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/sales/skills/logging-sales-activities.md
3. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/sales/skills/managing-sales-pipeline.md
4. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/sales/skills/managing-partnership-pipeline.md
5. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/sales/skills/generating-quotations.md
```

---

## Step 3 — Register in Skills Registry

Add each skill to the Skills Registry (from Core Playbook):

| Name | Source | Category |
|------|--------|----------|
| capturing-sales-intel | our own | Sales |
| logging-sales-activities | our own | Sales |
| managing-sales-pipeline | our own | Sales |
| managing-partnership-pipeline | our own | Sales |
| generating-quotations | our own | Sales |

---

## Step 4 — Verify

- "Show me my accounts table" → agent should query the Accounts table
- "Log a quick call with [name]" → should trigger `logging-sales-activities`
- "Add a new contact" → should trigger `capturing-sales-intel`

---

## Done

Your Sales CRM is ready. Example interactions:

> "剛跟 [公司] 的 [姓名] 開了個會，他們對我們的產品很有興趣"
> "幫我記一個新客戶：[公司名]，在香港做 RFID 的"
> "Onnet 這個 partner 現在什麼狀況？"
> "幫我出一份 quotation 給 [客戶]"
