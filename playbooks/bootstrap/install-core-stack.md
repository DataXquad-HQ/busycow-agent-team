# Install Core Stack

This playbook is for an agent or operator bringing up the **core BusyCow stack** after a basic Hermes installation already exists.

## What this creates

- Hermes Agent configured as the local runtime
- Core integration wiring for Lark and GBrain
- Initial identity files ready to be filled or copied from artifacts
- A verified base environment that later agent rollouts can build on

---

## Prerequisites

- Linux VM is available
- `hermes` CLI already installed
- required cloud credentials are ready where applicable
- you have this package repo locally available

---

## Steps

### 1. Verify Hermes exists

```bash
hermes --version
hermes doctor
```

### 2. Run the initial Hermes setup

```bash
hermes setup
```

### 3. Configure Lark / Feishu if this deployment uses it

```bash
hermes setup lark
```

### 4. Configure GBrain

```bash
hermes setup gbrain
gbrain init
```

### 5. Verify the base environment

```bash
hermes skills list
hermes doctor
```

---

## Artifacts you may need next

- agent SOULs and skills → `../../artifacts/agents/`
- schemas → `../../artifacts/schemas/`
- knowledge base templates → `../../artifacts/knowledge-base-templates/`

---

## Next integration playbooks

- Twenty CRM → `../integrations/twenty-crm/SETUP.md`
- Hermes runtime docs → `../integrations/hermes/README.md`
- GBrain docs → `../integrations/gbrain/README.md`
- Hindsight docs → `../integrations/hindsight/README.md`
