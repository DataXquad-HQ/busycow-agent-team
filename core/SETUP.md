# Core Playbook — Setup

Run this once after `setup/SETUP.md` is complete.

This setup:
1. Creates the **Skills Registry** Lark Base
2. Creates the **Cron Registry** Lark Base
3. Installs the 5 core skills

---

## Step 1 — Create Skills Registry Base in Lark

Call the Lark API to create a new Bitable app named "Hermes Registry":

```
Create Lark Bitable app: "Hermes Registry"
```

Inside this app, create a table called **Skills** with these fields:

| Field | Type |
|-------|------|
| Name | Text (primary) |
| Description | Text |
| Source | Single Select: `our own` / `hermes` / `3rd-party` |
| Category | Single Select: `Sales` / `Finance` / `System` / `Internal` / `Utility` / `Marketing` |
| Status | Single Select: `Active` / `Deprecated` |

Then create a second table called **Cron Jobs** with these fields:

| Field | Type |
|-------|------|
| Name | Text (primary) |
| Schedule | Text |
| Destination | Text |
| Status | Single Select: `Active` / `Paused` / `Disabled` |
| Last Run | DateTime |
| Notes | Text |

After creating, confirm the app token and both table IDs, then save to Memory:
```
Memory entry: "Hermes Registry Base: [app_token] | Skills: [table_id] | Cron Jobs: [table_id]"
```

---

## Step 2 — Install Core Skills

Fetch and install each skill by loading the raw URL:

```
1. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/managing-skills.md
2. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/managing-cron-jobs.md
3. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/maintaining-gbrain.md
4. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/maintaining-memory.md
5. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/capturing-to-gbrain.md
```

For each URL: fetch the content and save as a skill using `skill_manage(action='create')`.

---

## Step 3 — Register Core Skills in Skills Registry

After installing, add each skill to the Skills Registry Base:

| Name | Source | Category |
|------|--------|----------|
| managing-skills | hermes | System |
| managing-cron-jobs | hermes | System |
| maintaining-gbrain | hermes | System |
| maintaining-memory | hermes | System |
| capturing-to-gbrain | hermes | System |

---

## Step 4 — Verify

- "List my installed skills" → should show the 5 core skills
- "What's in the Skills Registry?" → should return the 5 entries in Lark

---

## Next Step

Choose a business playbook:
- Sales: `https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/sales/SETUP.md`
