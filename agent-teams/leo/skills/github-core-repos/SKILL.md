---
name: github-core-repos
version: 1.0.0
description: "Use when any agent needs to read, write, or sync the internal GitHub core knowledge repos (busycow-agent-package, dx-internal-wiki, aquaoptima-core). Covers SSH access, git pull/push, and GBrain sync."
triggers:
  - "read from github"
  - "update the playbook"
  - "push to core repo"
  - "sync to gbrain"
  - "pull latest from repo"
  - "update capabilities doc"
  - "write to dx-internal-wiki"
  - "write to aquaoptima-core"
  - "update internal wiki"
---

# GitHub Core Repos — Access & Sync

## References

- `references/dx-internal-wiki-architecture.md` — full directory structure, document template pattern, ROLE.md format, knowledge flow diagram, and terminology rules for the dx-internal-wiki repo.

---

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

| Repo | GitHub | Local Path | Purpose |
|---|---|---|---|
| `busycow-agent-package` | `DataXquad-HQ/busycow-agent-package` | `/mnt/disks/data/busycow-agent-package` | Agent team packaging for distribution to other orgs |
| `dx-internal-wiki` | `DataXquad-HQ/dx-internal-wiki` | `/mnt/disks/data/dx-internal-wiki` | DataXquad internal company handbook (human-readable Layer 1) |
| `aquaoptima-core` | `DataXquad-HQ/aquaoptima-core` | `/mnt/disks/data/aquaoptima-core` | AquaOptima company knowledge |

⚠️ **All repos must live on the external SSD (`/mnt/disks/data/`), NOT under `~/` (system disk, 90% full) and NOT under `/mnt/disks/data/hermes/` (Hermes internal).** They are independent repos that live alongside hermes on the SSD.

**dx-internal-wiki is Layer 1 of the knowledge stack** — the human-readable source of truth. Written by Iris after key decisions/conversations. Agents read via GBrain distillation (not directly). Structure: `strategy/`, `context/`, `decisions/`, `systems/`.

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
cat /mnt/disks/data/busycow-agent-package/agent-teams/maya/CAPABILITIES.md
cat /mnt/disks/data/dx-internal-wiki/decisions/2026-06-15-knowledge-layer-architecture.md
cat /mnt/disks/data/aquaoptima-core/partners/partner-strategy.md
```

**List all files in a repo:**
```bash
find /mnt/disks/data/busycow-agent-package -name "*.md" | sort
find /mnt/disks/data/dx-internal-wiki -name "*.md" | sort
```

---

## Writing / Updating Content

### Step 1 — Pull latest before editing
```bash
cd /mnt/disks/data/busycow-agent-package && git pull origin main
cd /mnt/disks/data/dx-internal-wiki && git pull origin main
cd /mnt/disks/data/aquaoptima-core && git pull origin main
```

### Step 2 — Edit the file
Use `write_file` or `patch` tool to edit the markdown file directly.

### Step 3 — Commit and push
```bash
cd /mnt/disks/data/dx-internal-wiki   # (or whichever repo)
git add -A
git commit -m "update: <what changed and why>"
git push origin main
```

**Git identity for Iris commits:**
```bash
git config user.email "iris@dataxquad.com"
git config user.name "Iris"
```

### Step 4 — Sync to GBrain
```bash
gbrain sync --repo /mnt/disks/data/dx-internal-wiki
gbrain sync --repo /mnt/disks/data/busycow-agent-package
gbrain sync --repo /mnt/disks/data/aquaoptima-core
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

## GBrain as the Agent Read Layer

Agents should NEVER `git clone` a repo to read content. The correct read path is:

```
GitHub repo → git pull (local clone) → gbrain sync → mcp_gbrain_query
```

1. All core repos are registered as GBrain sources (federated=true)
2. Agents query via `mcp_gbrain_query(query="...", source_id="busycow-playbooks")`
3. For full file reads: `cat ~/busycow-playbooks/agent-teams/maya/CAPABILITIES.md`
4. After any push, run `gbrain sync --repo ~/<repo>` to update GBrain immediately

**Registering a new repo as a GBrain source:**
```python
mcp_gbrain_sources_add(id="<id>", name="<Name>", path="/home/hunter_lin/<repo>", federated=True)
```
Then: `gbrain sync --repo ~/<repo>`

**Current registered sources:**
| Source ID | Local Path | Purpose |
|---|---|---|
| `busycow-agent-package` | `/mnt/disks/data/busycow-agent-package` | Agent capabilities, distribution package |
| `dx-internal-wiki` | `/mnt/disks/data/dx-internal-wiki` | DataXquad company handbook (Layer 1) |
| `aquaoptima-core` | `/mnt/disks/data/aquaoptima-core` | AquaOptima company knowledge |

## Pitfalls

- **Agent-specific skills are NOT synced to GitHub.** The `syncing-brain-memory` cron only pushes GBrain vault + `MEMORY.md`/`USER.md`. Skills in `~/.hermes/profiles/<name>/skills/` are NOT included. Deleting a profile = permanently losing those skills. Back up manually before any profile delete: `cp -r ~/.hermes/profiles/<name>/skills /tmp/<name>_skills_backup`.
- **Never edit files directly in GBrain** for content that lives in a GitHub repo — edit the file, push, then sync. GBrain is the read layer, GitHub is the write source.
- **Always `git pull` before editing** — if another agent or human pushed since your last pull, you'll get a conflict.
- **Don't put credentials or tokens in any of these repos** — even though they're private.
- **GBrain sync lag** — after push, run `gbrain sync` immediately if the agent needs the content right away. Otherwise the nightly cron picks it up.
- **SSH key is at `~/.ssh/github_geokernel`** — if you see `Permission denied (publickey)`, verify this file exists and `~/.ssh/config` points to it.
- **Old repo names are gone** — `busycow-playbooks`, `busycow-agent-team`, `dataxquad-core` are all deleted/renamed. Use current names: `busycow-agent-package` and `dx-internal-wiki`. Neither lives under `hermes/` — both are at `/mnt/disks/data/<name>/`.
- **Terminology: Opportunity not Deal** — prose uses "Opportunity" to match Twenty CRM. CRM field names (`dealType`, `dealId`) and skill directory names (`deal-progressing/`) stay unchanged.
- **`gbrain sync` paths use absolute paths** — `gbrain sync --repo /mnt/disks/data/dx-internal-wiki`, not `~/` shortcuts. The `~` may not resolve correctly in some contexts.
