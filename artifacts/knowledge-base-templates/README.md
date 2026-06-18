# Knowledge Base Setup

This folder contains the templates for setting up your company's internal knowledge base. Copy these into your own knowledge base repo and fill them in.

## Structure

```
artifacts/knowledge-base-templates/
├── company/                  ← Fill in once — company-wide content
│   ├── overview.md           ← Who you are, what you do, founding story
│   ├── team.md               ← Core team, roles, org structure
│   ├── portfolio.md          ← All business lines at a glance
│   ├── brand-messaging.md    ← Voice, tone, positioning
│   └── key-contacts.md       ← Key external relationships
│
└── business-lines/
    └── [bl-name]/            ← Copy this folder once per business line
        ├── overview.md       ← What this BL does, why it exists
        ├── strategy.md       ← Current direction, priority markets, targets
        ├── icp.md            ← Ideal Customer Profile
        ├── product.md        ← Features, value props, objection handling
        ├── gtm.md            ← GTM motion: channels, sequences, pricing
        └── market.md         ← Competitive landscape, industry trends
```

## How to Use

1. Create your knowledge base repo (GitHub, private)
2. Copy `company/` and fill in all files
3. For each business line: copy `business-lines/[bl-name]/`, rename the folder, fill in all files
4. Register the repo as a GBrain source (see `../../guidelines/02-knowledge-and-memory-spec.md`)

## Design Principle

**One folder per business line.** Every BL has its own complete knowledge package — strategy, ICP, product, GTM, market. Agents query by BL slug, so nothing bleeds across.

Company-level content (`company/`) is shared across all BLs and agents. Business line content is scoped.
