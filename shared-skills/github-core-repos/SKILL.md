---
name: github-core-repos
version: 1.0.0
description: "Use when any agent needs to read, write, or sync the internal GitHub core knowledge repos (busycow-playbooks, dataxquad-core, aquaoptima-core). Covers SSH access, git pull/push, and GBrain sync."
triggers:
  - "read from github"
  - "update the playbook"
  - "push to core repo"
  - "sync to gbrain"
  - "pull latest from repo"
  - "update capabilities doc"
  - "write to dataxquad-core"
  - "write to aquaoptima-core"
---

# GitHub Core Repos — Access & Sync

## Context

All Hermes profiles run under the same Linux user (`hunter_lin`) on the VM.
SSH is already configured — no setup needed per profile.

**SSH config (`~/.ssh/config`):**
```
Host github.com
  HostName github.com
  User git
  IdentityFile /home/hunter_lin/.ssh/github_geokernel
  IdentitiesOnly yes
```

**Verify SSH works:**
```bash
ssh -T git@github.com
# Expected: Hi hunterlin1997! You've successfully authenticated...
```

---

## Repos

| Repo | Local Path | Purpose |
|---|---|---|
| `busycow-playbooks` | `~/busycow-playbooks` | Agent capabilities, setup SOPs, playbooks |
| `dataxquad-core` | `~/dataxquad-core` | DataXquad company knowledge |
| `aquaoptima-core` | `~/aquaoptima-core` | AquaOptima company knowledge |

All three are registered as GBrain sources (federated). Agents query via GBrain — not by cloning.

---

## Reading Content

**Preferred — query GBrain (no git needed):**
```python
mcp_gbrain_query(query="<your question>", source_id="busycow-playbooks")
mcp_gbrain_query(query="<your question>", source_id="dataxquad-core")
mcp_gbrain_query(query="<your question>", source_id="aquaoptima-core")
```

**Direct read (for full file):**
```bash
cat ~/busycow-playbooks/agent-teams/maya/CAPABILITIES.md
cat ~/dataxquad-core/strategy/company-strategy.md
cat ~/aquaoptima-core/partners/partner-strategy.md
```

**List all files in a repo:**
```bash
find ~/busycow-playbooks -name "*.md" | sort
```

---

## Writing / Updating Content

### Step 1 — Pull latest before editing
```bash
cd ~/busycow-playbooks && git pull origin main
# or
cd ~/dataxquad-core && git pull origin main
cd ~/aquaoptima-core && git pull origin main
```

### Step 2 — Edit the file
Use `write_file` or `patch` tool to edit the markdown file directly.

### Step 3 — Commit and push
```bash
cd ~/busycow-playbooks   # (or whichever repo)
git add -A
git commit -m "update: <what changed and why>"
git push origin main
```

### Step 4 — Sync to GBrain
```bash
gbrain sync --repo ~/busycow-playbooks
gbrain sync --repo ~/dataxquad-core
gbrain sync --repo ~/aquaoptima-core
```

Only sync the repo you just updated — no need to sync all three every time.

---

## Commit Message Convention

```
feat: add <new file or section>
update: <what changed> based on <trigger>
fix: correct <what was wrong>
decision: <YYYY-MM-DD> <topic>
```

---

## Pitfalls

- **Never edit files directly in GBrain** for content that lives in a GitHub repo — edit the file, push, then sync. GBrain is the read layer, GitHub is the write source.
- **Always `git pull` before editing** — if another agent or human pushed since your last pull, you'll get a conflict.
- **Don't put credentials or tokens in any of these repos** — even though they're private.
- **GBrain sync lag** — after push, run `gbrain sync` immediately if the agent needs the content right away. Otherwise the nightly cron picks it up.
- **SSH key is at `~/.ssh/github_geokernel`** — if you see `Permission denied (publickey)`, verify this file exists and `~/.ssh/config` points to it.
