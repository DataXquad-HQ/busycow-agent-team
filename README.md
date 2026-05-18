# BusyCow Playbooks

Agent-ready setup and skill bundles for BusyCow clients.

## Stack

All playbooks assume this stack:
- **[Hermes Agent](https://github.com/DataXquad-HQ/hermes-agent)** — AI agent runtime
- **[Lark / Feishu](https://www.larksuite.com)** — Data backend (Bitable bases)
- **[GBrain](https://github.com/DataXquad-HQ/gbrain)** — Long-term knowledge base (SSOT)

---

## Installation Order

```
Step 0: Prerequisites   (manual — do this before anything else)
Step 1: setup/          (Hermes + GBrain config)
Step 2: core/           (system skills + management bases)
Step 3: playbooks/X/    (pick one or more business playbooks)
```

Tell your agent the raw GitHub URL for each `SETUP.md` and it will run the setup automatically.

---

## Step 0 — Prerequisites (Manual)

Complete these before running any SETUP.md.

### 0a. Install Hermes Agent
Follow the [Hermes installation guide](https://github.com/DataXquad-HQ/hermes-agent#installation).

### 0b. Install GBrain
Follow the [GBrain installation guide](https://github.com/DataXquad-HQ/gbrain#installation).

### 0c. Connect Hermes to Lark

1. Go to [Lark Open Platform](https://open.larksuite.com/) → **Create App** → Self-Built App
2. Under **Permissions & Scopes**, enable:
   - `bitable:app` (read + write)
   - `im:message` (send messages)
   - `im:chat` (read chat list)
3. Under **App Credentials**, copy **App ID** and **App Secret**
4. Add to `~/.hermes/.env`:
   ```
   LARK_APP_ID=your_app_id
   LARK_APP_SECRET=your_app_secret
   ```
5. Publish the app in your Lark workspace (Admin approval may be required)
6. Verify: ask your agent "list my Lark chats" — it should return results

### 0d. Verify GBrain is running
Ask your agent: "What's the GBrain brain identity?" — it should return version and page count.

---

## Folder Structure

```
busycow-playbooks/
├── setup/              ← Stack config (SOUL.md + Memory templates)
├── core/               ← Core Playbook (must install before business playbooks)
└── playbooks/
    ├── sales/          ← Sales CRM playbook
    ├── finance/        ← (coming soon)
    └── content/        ← (coming soon)
```

---

## Quick Install (copy-paste to your agent)

```
Step 1 — Setup:
Run this setup: https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/setup/SETUP.md

Step 2 — Core:
Run this setup: https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/SETUP.md

Step 3 — Sales Playbook:
Run this setup: https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/sales/SETUP.md
```
