# Finance Playbook

Skills for financial modeling, forecasting, invoice generation, and investor-grade reporting.

## Skills

| Skill | What it does |
|---|---|
| `building-investor-financial-model` | Build investor-grade financial forecasts for B2G/SaaS — multi-scenario Python model + Google Sheets |
| `gsheets-formula-model` | Build live formula-driven financial models in Google Sheets with tab-to-tab linkage and scenario switcher |
| `generating-invoices` | Generate invoices from Lark Base data, fill Google Doc template, export PDF, upload to Drive |

## Prerequisites

- **Core playbook installed**
- **Google Workspace configured** — see `core/skills/google-workspace.md`
- **For invoices**: Lark Base with a Quotation table + Google Doc invoice template in Drive
- **numpy-financial** installed in Hermes venv (`pip install numpy-financial`)

## Use Cases

- Seed / Series A fundraising model with revenue projections, unit economics, sensitivity analysis
- Live Google Sheet that auto-recalculates when you change assumptions
- Agent-generated invoices from accepted quotations — fills template, exports PDF, links back to CRM
