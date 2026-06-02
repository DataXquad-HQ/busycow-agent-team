# Core Playbook — Setup

Run this after `setup/SETUP.md` is complete.

This setup installs the **three core pillars** of the BusyCow stack:
1. **GBrain** — long-term knowledge graph + Hermes system prompt refinement
2. **Lark MCP** — native Lark tool access for the agent
3. **Google Workspace** — external email, calendar, Drive (optional)

Then it opens the **Hermes Dashboard** and installs all core skills.

---

## Step 1 — Initialize GBrain

GBrain is the long-term knowledge graph. All entities (people, companies, decisions, intel) live here.

### 1a. Install GBrain

Follow the GBrain installation guide:
```
https://github.com/nous-research/gbrain — follow README install steps
```

Confirm GBrain is running:
```bash
gbrain status
```

### 1b. Refine Hermes System Prompt

Append the GBrain routing rules to `~/.hermes/SOUL.md` so Hermes knows to read from and write to GBrain automatically. Add the following block:

```markdown
## GBrain Knowledge Routing

Before every response, silently check:
- Is a person, company, deal, or decision mentioned? → query GBrain first, write to GBrain after
- Is new intel being shared? → extract_facts to GBrain before responding
- Is a key decision being made? → put_page decisions/YYYY-MM-DD-topic to GBrain

Auto-write triggers (no user prompt needed):
- New contact or company → put_page people/ or companies/
- Opportunity or partnership stage change → add_timeline_entry
- Key decision reached → put_page decisions/
- Market or competitor intel → put_page + extract_facts

Query routing:
- Entity facts (who/what) → GBrain first
- Past workflow (how we did something) → session_search first
- Need both → GBrain then session_search
```

### 1c. Configure GBrain Source

Set the GBrain home directory in Hermes config:
```bash
hermes config set gbrain.home ~/.gbrain
```

Verify GBrain is accessible from Hermes:
```
Ask Hermes: "What's in my GBrain?"
→ Should return brain stats or empty brain confirmation
```

---

## Step 2 — Configure Lark MCP

This gives Hermes native Lark tool access (Bitable, Docs, Messaging) via MCP.

Fetch and follow the Lark MCP setup skill:
```
Fetch: https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/lark-mcp-setup.md
Install as skill, then follow its instructions.
```

After setup, verify:
```
Ask Hermes: "List my Lark chats"
→ Should return a list of groups/chats
```

---

## Step 3 — Google Workspace (optional)

Skip this step if you don't use Gmail / Google Calendar / Google Drive.

Fetch and follow the Google Workspace setup skill:
```
Fetch: https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/google-workspace.md
Install as skill, then follow its setup instructions to authenticate gws CLI.
```

After setup, verify:
```bash
gws gmail list
# Should return recent emails
```

---

## Step 4 — Open Hermes Dashboard

The Hermes Dashboard is the primary interface for inspecting skills, cron jobs, memory, and agent activity. This is a required step — open the port before proceeding.

### 4a. Start the Dashboard

```bash
hermes dashboard
```

By default, the dashboard runs on **port 9119**.

### 4b. Open the Port (if on a cloud VM)

If your Hermes instance runs on a remote VM (GCP, AWS, etc.), open port 9119 in your firewall or security group:

**GCP example:**
```bash
gcloud compute firewall-rules create hermes-dashboard \
  --allow tcp:9119 \
  --source-ranges 0.0.0.0/0 \
  --description "Hermes Dashboard"
```

**Or restrict to your IP only (recommended):**
```bash
gcloud compute firewall-rules create hermes-dashboard \
  --allow tcp:9119 \
  --source-ranges <YOUR_IP>/32 \
  --description "Hermes Dashboard"
```

### 4c. Verify

Open in your browser:
```
http://<YOUR_VM_IP>:9119
```

You should see the Hermes Dashboard with:
- **Skills** tab — all installed skills, searchable
- **Cron Jobs** tab — scheduled jobs, status, last run
- **Memory** tab — persistent memory entries
- **Sessions** tab — recent agent sessions

> **Note:** Skills and cron jobs are managed directly through the Dashboard. No separate Lark Base registry is needed.

---

## Step 5 — Install Core Skills

Fetch and install each skill by loading the raw URL and calling `skill_manage(action='create')`:

```
1. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/hermes-agent.md
2. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/maintaining-gbrain.md
3. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/maintaining-memory.md
4. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/capturing-to-gbrain.md
5. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/google-workspace.md
6. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/lark-mcp-setup.md
7. https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/core/skills/native-mcp.md
```

After installing, verify in the Dashboard (port 9119) that all 7 skills appear under the **Skills** tab.

---

## Step 6 — Verify

- "What's in my GBrain?" → should return brain stats
- "List my installed skills" → should show 7 core skills (also visible in Dashboard)
- "List my Lark chats" → should return chat list (Lark MCP working)
- Dashboard at `http://<YOUR_VM_IP>:9119` → Skills + Cron tabs populated
- (If Google Workspace): `gws gmail list` → should return emails

---

## Next Step

Choose a business playbook:
- Sales & Ops: `https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/sales/SETUP.md`
- Internal Ops: `https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/internal-ops/SETUP.md`
- Knowledge Ops: `https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/knowledge-ops/SETUP.md`
