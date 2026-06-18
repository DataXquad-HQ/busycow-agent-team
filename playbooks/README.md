# Playbooks

This layer is for **agents**.

A playbook is an operational runbook that tells an agent how to perform a task against this package and a target environment.
Playbooks answer: **what should the agent do, in what order, and how does it verify success?**

## Rules

- Playbooks are executable instructions, not architecture essays
- Playbooks may reference files in `artifacts/`
- Playbooks should include verification and fallback steps
- If a file is primarily explanatory rather than operational, it belongs in `guidelines/`

---

## Structure

```text
playbooks/
├── README.md
├── bootstrap/
│   └── install-core-stack.md
└── integrations/
    ├── README.md
    ├── hermes/
    ├── gbrain/
    ├── hindsight/
    ├── lark/
    └── twenty-crm/
```

---

## Current Entry Points

| Path | Use when |
|---|---|
| `bootstrap/install-core-stack.md` | bringing up the core stack after base Hermes exists |
| `integrations/` | setting up or understanding a specific system integration |

---

## Relationship to Artifacts

Playbooks tell the agent **what to do**.
Artifacts provide the **actual files** to install, copy, or adapt.
