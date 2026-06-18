---
name: packaging-to-github
description: Use when publishing skills, agent setups, schemas, knowledge bases, or capability docs to the busycow-agent-package GitHub repo — so any agent or client can install them. Covers universalization (strip internal data), sanitization scan, repo structure, and push workflow.
triggers:
  - "push to github"
  - "publish playbook"
  - "package for clients"
  - "put on github"
  - "publish skill"
  - "push to package"
  - "package agent"
  - "sync agent to repo"
  - "push soul to github"
  - "genericize and push"
version: "3.0"
author: [Business Line]
---

# Packaging to GitHub

Use this when publishing **anything reusable** to `busycow-agent-package`:
- **Skills** — agent procedural memory (SKILL.md + scripts + references)
- **Setup** — Hermes profiles, SOUL.md, MEMORY.md, USER.md templates
- **Schema** — Lark Bitable table/field definitions (SCHEMA.md)
- **Knowledge** — GBrain pages, decision logs, architecture docs
- **Capability Docs** — agent capability documents (what an agent can do, how to trigger it)

## What busycow-agent-package Is

`busycow-agent-package` is the **universal agent team framework** — a reusable blueprint for deploying the full [Business Line] agent stack at any company. Formerly named `busycow-playbooks` / `busycow-agent-team` (both deleted Jun 2026).

Local clone: `/mnt/disks/data/busycow-agent-package/`

It is built to be copied. When onboarding a new client or spinning up a new company instance, pull from this repo and fill in the company-specific layer. The package itself stays generic — no internal data, no hardcoded IDs, no product names.

**Current package model:**
- `guidelines/` = human-readable specs
- `playbooks/` = agent-readable setup / migration / verification instructions
- `artifacts/` = concrete installable assets

When discussing package structure with the sales rep, lead with the conclusion first, keep intermediate detail brief, and only expand on follow-up.

**Report-back style for the sales rep (mandatory):**
- Default to a very short update.
- Use this order: **(1) conclusion, (2) 2–4 brief bullets, (3) one short next-step suggestion**.
- Do **not** paste long file-by-file change lists, exhaustive intermediate reasoning, or large blocks of rewritten content unless explicitly asked.
- If many files changed, summarize by class of change (e.g. "genericized Iris package", "pushed cron routing fix") instead of enumerating every edit.

**What it contains:**
- `guidelines/` — human-readable specs and architecture
- `playbooks/` — agent-readable operational instructions (setup, rollout, migration, verification)
- `artifacts/agents/<agent>/` — genericized SOULs, skills, cron docs, and agent setup assets
- `artifacts/shared-skills/` — canonical shared skills that can be copied into multiple profiles
- `artifacts/schemas/` — structural data schemas (CRM, task board field definitions)
- `artifacts/knowledge-base-templates/` — templates for a client's own knowledge base / GBrain source repo
- `SETUP.md` — lightweight entrypoint that routes humans and agents to the correct layer

**Authoritative rule:** if any older example in this skill still mentions `agent-teams/`, `context/schemas/`, `knowledge-base-setup/`, or `third-party-tools/` as active package paths, follow the v2 structure above instead. Those older names are legacy.

**Layering rule:**
- `guidelines/` answers **why the system is designed this way**
- `playbooks/` answers **how an agent should perform setup or migration**
- `artifacts/` contains **the actual files that get installed or copied**

- Company-specific data (client names, real pricing, internal decisions) → `dx-gbrain/internal/`
- Live credentials or API keys → never committed anywhere
- Task state or session output → nowhere (ephemeral)
- Shared skills infrastructure (deleted Jun 2026) — each agent has its own real skill dirs

---

## Repo Scope

This skill is **only** for the external package repo:

| Repo | Local path | Purpose |
|---|---|---|
| `{{ORG_GITHUB_NAMESPACE}}/busycow-agent-package` | `/mnt/disks/data/busycow-agent-package/` | Universal agent framework — `guidelines/`, `playbooks/`, and `artifacts/` for client-ready deployment packaging |

**Do not use this skill for internal knowledge writes to `dx-gbrain`.**
That route belongs to `operating-dx-gbrain-vault`.

**Rule:**
- reusable / client-installable / generalized → `packaging-to-github`
- internal durable knowledge / vault update → `operating-dx-gbrain-vault`

## References

- `references/agent-architecture-principles.md` — design principles for SOUL.md, agent operating models, three-layer capability structure, hire framework, event-driven triggers. Load when designing new agent playbooks or SOUL.md templates.
- `references/package-structure-v2.md` — authoritative three-layer package model (`guidelines/`, `playbooks/`, `artifacts/`) and the legacy-path migration map. Follow this when packaging or relocating files.

---

## What Gets Packaged — Decision Table

| Artifact type | Source location | Target in repo | Notes |
|---|---|---|---|
| Env key management | `~/.hermes/shared.env` + `sync-shared-env.sh` | `playbooks/integrations/hermes/` or `artifacts/templates/` | shared.env.example + profile.env.example + script — NEVER commit real .env |
| Skill (SKILL.md + support files) | `~/.hermes/skills/<cat>/<skill>/` | `artifacts/shared-skills/<skill>/` | Copy entire folder — SKILL.md + scripts/ + references/ + templates/. Skills are **folders**, not flat .md files |
| Agent-specific skill | `~/.hermes/profiles/<agent>/skills/<skill>/` | `artifacts/agents/<agent>/skills/<skill>/` | Same folder structure; universalize before pushing |
| SOUL.md | `~/.hermes/profiles/<name>/SOUL.md` | `artifacts/agents/<agent>/SOUL.md` | Strip product/client names |
| MEMORY.md / USER.md | `~/.hermes/profiles/<name>/memories/` | `artifacts/templates/` | Strip all specifics |
| CRM / DB schema | From SCHEMA.md or structural definition | `artifacts/schemas/<system>.md` | Replace all IDs with `{{PLACEHOLDERS}}`; keep field types + relation patterns |
| Background knowledge | Prose docs (company, products, glossary) | `guidelines/reference/` or `artifacts/knowledge-base-templates/` | Put explanatory material in guidelines; installable templates in artifacts |
| GBrain knowledge page | GBrain `put_page` export | `guidelines/reference/` or a domain-specific playbook support file | Strip entity-specific takes/timelines; keep design principles |
| Third-party tool install | Docker Compose + README | `playbooks/integrations/<tool>/` | README.md + SETUP.md + docker-compose.yml (template form) |
| Core tool doc | Per-tool README | `playbooks/integrations/<tool>/README.md` | What it is, how it integrates, setup steps |
| Agent capability doc | Lark Doc or local file | `guidelines/deployed-agents/<agent>-spec.md` or `guidelines/reference/` | Human-readable capability and build mapping docs belong in guidelines |

## Copying Skills to Agent Profiles

**No shared skills, no symlinks.** Each agent profile has its own real skill dirs. If two agents need the same skill, duplicate it directly into each profile's `skills/` directory.

```python
import os, shutil

def copy_skill_clean(src_dir, dest_dir, skill_name):
    """Copy a skill directory — skip cyclic symlinks (same-name-as-skill symlinks inside the dir)"""
    os.makedirs(dest_dir, exist_ok=True)
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dst_item = os.path.join(dest_dir, item)
        if os.path.islink(src_item):
            continue  # skip ALL symlinks — avoids cyclic refs
        if os.path.isfile(src_item):
            shutil.copy2(src_item, dst_item)
        elif os.path.isdir(src_item):
            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)

# Example: copy lark-im to leo
copy_skill_clean(
    "~/.agents/skills/lark-im",
    "~/.hermes/profiles/leo/skills/lark-im",
    "lark-im"
)
```

**Why skip all symlinks:** Lark skills at `~/.agents/skills/` contain a same-name cyclic symlink inside their directory (e.g. `lark-im/lark-im → ~/.hermes/skills/lark-im`). `cp -rL` fails on these. Python `os.walk` with symlink filtering is the safe pattern.

---

## Architecture Principles

**Three core pillars** — every deployment runs all three:
1. **Lark / Feishu** — workspace comms, databases (Bitable), documents
2. **Google Workspace** — external email, calendar, Drive, Sheets, Docs
3. **GBrain** — long-term knowledge graph (entities, decisions, intel)

**Tasks are business-anchored.** No standalone Task Tracker. Tasks live inside the business Base (Sales & Ops, Finance, etc.) and link via DuplexLink to Opportunities/Partnerships/Initiatives. This is a hard architectural rule — do not propose a separate Task Tracker.

**GBrain setup includes system prompt refinement.** Installing GBrain also means appending routing rules to `~/.hermes/SOUL.md` so the agent auto-writes entities/decisions to GBrain without being asked.

## Knowledge Repos (company-specific, private)

For company-specific private knowledge bases (not the public playbooks repo), use this pattern:

**Repos created:**
- `{{ORG_GITHUB_NAMESPACE}}/dataxquad-core` — {{COMPANY_NAME}} company core (~/dataxquad-core)
- `{{ORG_GITHUB_NAMESPACE}}/aquaoptima-core` — [Business Line] company core (~/aquaoptima-core)

**Canonical directory structure:**
```
<company>-core/
├── README.md           ← repo purpose + reading order
├── product/            ← what the product is
├── market/             ← ICP, expansion roadmap
├── partners/           ← partner strategy + registry
├── strategy/           ← company strategy, OKRs, milestones
├── team/               ← roster, RACI, entity info
├── operations/         ← live sites, SLA, deployment
└── decisions/          ← key decisions (YYYY-MM-DD-topic.md)
```

Files are tagged `v0.1 — team to update` on first creation. Each file is standalone markdown — no cross-file dependencies. Agents read these directly via `cat` or via GBrain sync.

## Repo Structure (current package model)
```
busycow-agent-package/
├── README.md
├── SETUP.md
├── guidelines/                 ← human-readable specs
│   ├── deployed-agents/
│   └── reference/
├── playbooks/                  ← agent-readable operational instructions
│   ├── bootstrap/
│   └── integrations/
└── artifacts/                  ← actual installable / copyable assets
    ├── agents/
    ├── shared-skills/
    ├── schemas/
    └── knowledge-base-templates/
```

**Core rule:** Human reads guidelines, agent runs playbooks, system installs artifacts.

### Two-phase packaging rule

When packaging an agent that is still being actively built for internal use, use a **two-phase flow**:

1. **DX-use completeness first** — make the agent package self-contained enough to run for the current company, even if some copied skills still come from the shared runtime layer.
2. **Genericization second** — once the artifact set is complete, run a dedicated cleanup pass to strip internal names, IDs, paths, Chinese text, and company-specific examples.

Do not prematurely optimize for client-generic packaging if doing so blocks making the agent whole for current internal use.

### Agent completeness rule

If an agent spec says a capability depends on a set of skills, and the goal is to package that agent as a runnable artifact, the package must not rely only on the reader *assuming* those shared skills exist elsewhere. For an internal-use package, copy the required shared skills into `artifacts/agents/<agent>/skills/` so the deploy layer is explicit and self-contained. You can genericize them afterward.

---

## Workflow

### Step 1 — Identify what to package

Before starting, classify the artifact:

**Skill** → `skill_view(name)` to get full content + linked files  
**SOUL.md / MEMORY.md / USER.md** → `read_file(~/.hermes/profiles/<name>/SOUL.md)`  
**Schema** → query Lark Bitable field definitions via `lark-cli base` or read existing SCHEMA.md  
**GBrain knowledge page** → `mcp_gbrain_get_page(slug)` to export  
**Capability Doc** → `read_file` or fetch from Lark Doc  

### Step 2 — Universalize

Apply these rules in ORDER (broader patterns first):

| Remove | Replace with |
|--------|-------------|
| Hardcoded Lark base/table IDs (`tbl[A-Za-z0-9]{8,}`) | `{{TABLE_ID}}` |
| Hardcoded field IDs (`fld[A-Za-z0-9]{8,}`) | `{{FIELD_ID}}` |
| User open_ids (`ou_[a-f0-9]{20,}`) | `{{USER_OPEN_ID}}` |
| API tokens (Lark, Notion, Google) | `{{API_TOKEN}}` or remove |
| Google Doc / Drive IDs | `{{GOOGLE_DOC_TEMPLATE_ID}}` |
| IP addresses | `{{SERVER_IP}}` |
| Internal product names ([Business Line], [Business Line], [Business Line]) | `[Product]` or `[your product lines]` |
| Specific client/partner names ([Client], Onnet, etc.) | `[Client]` or `[Partner]` |
| Personal names / usernames (the sales rep, hunter_lin) | `the owner` or omit |
| Personal file paths (/home/username, ~/.hermes) | `~/.hermes` |
| Internal business logic (billing entity rules, commission %) | Generic equivalent or remove |
| Company name {{COMPANY_NAME}} | [Business Line] (as publisher) |
| Lark App ID (`cli_[a-z0-9]{16,}`) | `{{LARK_APP_ID}}` |
| Lark App Secret | `{{LARK_APP_SECRET}}` |

**Schema-specific rules:**
- Replace every table name that's product-specific → `[Module Name]` (keep structural names like Tasks, Activities, Contacts)
- Replace every option value that's business-specific (e.g. `[Business Line]`, `[Business Line]`) → `[Value]`
- Keep field types, link directions, and relationship patterns — these are the reusable structural knowledge

**GBrain knowledge page rules:**
- Remove entity-specific takes, timelines, and fact rows that reference internal clients/products
- Keep decision rationale, design principles, and architectural patterns — these generalize
- Remove `## Facts` fences entirely if they contain specifics
- Keep `## Summary`, `## Key Principles`, `## How It Works` sections

**Capability Doc rules:**
- Keep the capability name, trigger description, input/output format, and workflow steps
- Replace specific Lark base/table references with `{{PLACEHOLDER}}`
- Remove example data that references real clients or deals

**Key insight:** Apply broad patterns (`tbl[A-Za-z0-9]{8,}`, `ou_[a-f0-9]{20,}`) FIRST in code, BEFORE specific named replacements. Broad patterns catch everything; named patterns handle remaining context.

### Step 2a — Copy skills from agent profile to package (rsync pattern)

Use `rsync` to copy skill directories — it handles nested `references/`, `scripts/`, `templates/` correctly and skips dotfiles automatically:

```bash
# Copy one skill
rsync -a \
  --include="*/" --include="SKILL.md" --include="*.md" --include="*.py" --include="*.json" \
  --exclude="*" \
  ~/.hermes/profiles/leo/skills/log-engagement/ \
  /mnt/disks/data/busycow-agent-package/artifacts/agents/leo/skills/log-engagement/

# Copy all skills in a profile (skip bundled manifest + usage files)
rsync -a \
  --include="*/" --include="SKILL.md" --include="*.md" --include="*.py" --include="*.json" \
  --exclude=".bundled_manifest" --exclude=".curator_state" --exclude=".usage*" \
  ~/.hermes/profiles/leo/skills/ \
  /mnt/disks/data/busycow-agent-package/artifacts/agents/leo/skills/
```

**Why rsync over Python `shutil`:** rsync skips dotfiles and internal Hermes state files (`.bundled_manifest`, `.curator_state`, `.usage.json`) by default with the include/exclude filter. No need to enumerate exceptions manually. Also handles nested directories cleanly without the cyclic symlink risk of `cp -r`.

### Step 2b — Genericize agent files (SOUL.md, skills, cron) with Python

Use Python regex — apply broad ID patterns first, then named strings:

```python
import re

def genericize(content):
    replacements = [
        # Broad ID patterns first
        (r'oc_[a-z0-9]{20,}', '{{LARK_CHAT_ID}}'),
        (r'cli_[a-z0-9]{16,}', '{{LARK_APP_ID}}'),
        (r'om_[a-z0-9]{40,}', '{{OPENMAIL_API_TOKEN}}'),
        # Hindsight banks
        (r'{{ORG_PREFIX}}-pipeline', '{{HINDSIGHT_PIPELINE_BANK}}'),
        (r'{{ORG_PREFIX}}-global', '{{HINDSIGHT_GLOBAL_BANK}}'),
        (r'dx-agent-[a-z]+', '{{HINDSIGHT_AGENT_BANK}}'),
        (r'dx-internal', '{{HINDSIGHT_INTERNAL_BANK}}'),
        (r'dx-human-[a-z]+', '{{HINDSIGHT_HUMAN_BANK}}'),
        # Channel names, emails
        (r'\[DX\] [A-Za-z ]+', '{{CHANNEL_NAME}}'),
        (r'[a-z-]+@openmail\.sh', '{{AGENT_EMAIL}}'),
        # Company/people names
        (r'{{COMPANY_NAME}}', '{{COMPANY_NAME}}'),
        (r'\bthe sales rep\b', '{{SALES_REP_NAME}}'),
        (r'\bthe manager\b', '{{FOUNDER_NAME}}'),
    ]
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    return content
```

When walking skill directories, skip all symlinks (Lark skills have cyclic same-name symlinks):
```python
for root, dirs, files in os.walk(src):
    dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
    for f in files:
        if os.path.islink(os.path.join(root, f)):
            continue
        # process file
```

### Step 3 — Sanitization scan (mandatory before push)

```python
import re, os

CONFIDENTIAL_PATTERNS = [
    (r'tbl[A-Za-z0-9]{8,}', 'hardcoded table ID'),
    (r'fld[A-Za-z0-9]{8,}', 'hardcoded field ID'),
    (r'ou_[a-z0-9]{20,}', 'hardcoded open_id'),
    (r'oc_[a-z0-9]{20,}', 'hardcoded chat ID'),
    (r'ntn_[A-Za-z0-9]+', 'Notion token'),
    (r'LARK_APP_(?:ID|SECRET)=[^\n{]', 'Lark credential'),
    (r'MtvNbgCH[A-Za-z0-9]+', 'hardcoded Lark app token (Sales CRM)'),
    (r'SfMJbDOB[A-Za-z0-9]+', 'hardcoded Lark app token (Task Tracker)'),
    (r'529a4913-cc22-4e1b-b8ee-52a53c4c5d3c', 'Twenty API Key ID'),
    (r'a352ccf9-ed5f-40d3-910f-706074dc3877', 'Twenty Workspace ID'),
    (r'Iris@{{COMPANY_NAME}}2026', 'Twenty admin password'),
    (r'hunter\.lin@distify\.ai', 'internal admin email'),
    (r'100\.118\.240\.101', 'Tailscale IP (use {{SERVER_TAILSCALE_IP}})'),
    (r'\b{{COMPANY_NAME}}\b(?!-HQ)', 'company name {{COMPANY_NAME}}'),
    (r'\b([Business Line]|[Business Line]|[Business Line])\b', 'internal product name'),
    (r'/home/[a-z_]+', 'personal path'),
    (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP address'),
    (r'[a-z]+@dataxquad\.com', 'internal email'),
    (r'\bhunter_lin\b', 'personal username'),
    (r'\b([Client]|AICities|Onnet|HeadWorker|VoiceBot)\b', 'internal partner name'),
]

def scan(directory):
    issues = {}
    for root, _, files in os.walk(os.path.expanduser(directory)):
        if '.git' in root:
            continue
        for filename in files:
            if not filename.endswith('.md'):
                continue
            filepath = os.path.join(root, filename)
            with open(filepath) as f:
                content = f.read()
            file_issues = []
            for pattern, label in CONFIDENTIAL_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    file_issues.append(f"  ⚠️  {label}: {list(set(matches))[:3]}")
            if file_issues:
                issues[filepath] = file_issues
    return issues

issues = scan("/mnt/disks/data/busycow-agent-package")
if not issues:
    print("✅ All clean — safe to push.")
else:
    for f, problems in issues.items():
        print(f"📄 {f}")
        for p in problems:
            print(p)
```

**Known false positives to ignore:**
- `LARK_APP_SECRET=***` in README Step 0c — example text, not a real secret
- English words starting with `rec` — NOT Lark record IDs

**Do not push if scan returns any real issues. Fix first.**

### Step 4 — Write files to repo

Save each universalized file to the correct location under the current package repo root (`/mnt/disks/data/busycow-agent-package/` or `<repo-root>/`).

### Step 4a — Sync deployed-agent spec and artifact layer together

When an agent was refined locally and you are packaging the update, do **not** publish only the new skill folders.
Treat the package update as a synchronized bundle across:

- `guidelines/deployed-agents/<agent>-spec.md`
- `artifacts/agents/<agent>/SOUL.md`
- `artifacts/agents/<agent>/skills/`
- `artifacts/agents/<agent>/skills/README.md`
- `artifacts/agents/<agent>/cron/jobs.json`
- `artifacts/agents/<agent>/cron/README.md`

**Rule:** if the live profile changed any of these truths, the package copy must change in the same pass:
- capability map changed → update the deployed-agent spec and SOUL capability list
- skill inventory changed → update `skills/README.md`
- cron delivery or recovery behavior changed → update both `cron/jobs.json` and `cron/README.md`
- a shared-core skill changed locally → sync the matching copy under `artifacts/shared-skills/` too

For Leo-style reporting jobs, this means the package must keep the spec, the agent artifact, and the shared `routing-report-delivery` copy aligned on:
- full human report vs short backend receipt
- paused-job recovery (`list` → `resume` / `run` / `update`)
- which channel gets the business report vs the backend receipt

### Shared-skill sync rule
When the **canonical shared skill set** changes locally, the package repo must be updated as a package-facing mirror of that model.

At minimum, sync these layers together:
- `artifacts/shared-skills/<skill>/` for each shared canonical skill
- `artifacts/shared-skills/README.md` to reflect the current shared-core baseline
- `guidelines/05-mandatory-skills.md` if the mandatory baseline changed
- any deployed-agent spec or artifact README that still names an old shared skill or old routing concept

Do **not** publish internal-only operating skills just because they are canonical locally. Example: `operating-dx-gbrain-vault` stays internal and should not be exported into the client package.

**Skills with support files:** Each internal skill is a folder. Copy the whole directory:
```bash
cp -r ~/.hermes/skills/<cat>/<skill>/ <repo-root>/artifacts/shared-skills/<skill>/
```
Then universalize every file inside (SKILL.md + references/ + scripts/).

**Skills are NEVER flat .md files in the repo** — always folders, even if the only file is SKILL.md:
```
artifacts/shared-skills/twenty-crm/SKILL.md       ✅
artifacts/shared-skills/twenty-crm.md             ❌  (old flat format, do not use)
```

**GBrain knowledge pages:** Export via `mcp_gbrain_get_page`, universalize, write to `playbooks/<domain>/knowledge/<slug>.md`. Add a `## Install Note` section at the top explaining how to import: `gbrain import <file>` or manually via `put_page`.

**Capability docs / agent specs:** Human-readable capability and build-mapping docs belong in `guidelines/deployed-agents/<agent>-spec.md`. Runtime behavior belongs in `artifacts/agents/<agent>/SOUL.md`. Do not create standalone `CAPABILITY.md` files unless a deployment explicitly introduces them.

### Step 5 — Push
```bash
cd /mnt/disks/data/busycow-agent-package
git add -A
git commit -m "feat/refactor: [description of what was added or changed]"
git push origin main
```

### Step 6 — Confirm client URLs
```
https://raw.githubusercontent.com/{{ORG_GITHUB_NAMESPACE}}/busycow-agent-package/main/[path]/SETUP.md
```
After push: `curl -s [raw URL] | head -5` to verify accessible.

---

## Installation Order (client-facing)

```
Phase 0: Human steps (manual)
  1. VM + Hermes install
  2. Lark org + Hermes App
  3. Lark Dev Console → enable permissions (messenger / base / docs / contact)
  4. hermes setup lark → get Lark user ID approved
  5. Tavily API key → hermes config set search.tavily_api_key YOUR_KEY
  6. (optional) hermes setup google-workspace

Phase 1: setup/SETUP.md      → SOUL.md + MEMORY.md + USER.md
Phase 2: core/SETUP.md       → GBrain + Lark MCP + Google Workspace + Hermes Registry
Phase 3: playbooks/X/SETUP.md → business Base schema + skills + chat groups + cron jobs
```

---

## SETUP.md Format (agent-executable)

Every SETUP.md must be written as **step-by-step agent instructions**, not human prose.

Required sections:
1. What this setup creates (bullet list)
2. Numbered steps with exact API calls or fetch URLs
3. Verify section (how to confirm it worked)
4. Next step (what to run next)

Must be **idempotent** — running twice should not corrupt the workspace.

---

## Multi-Agent Package Structure

When packaging a full multi-agent system, align it to the current three-layer repo model:

```
guidelines/
  deployed-agents/
    <agent>-spec.md

playbooks/
  bootstrap/
  integrations/

artifacts/
  agents/
    <agent>/
      SOUL.md
      skills/
      cron/
  shared-skills/
  schemas/
  knowledge-base-templates/
```

**SOUL.md packaging rules:**
- Never include specific deal names, client names, or product names → `[Product]`, `[Client]`, `[Partner]`
- Never include Lark table IDs or App Tokens → `{{LARK_APP_TOKEN}}`, `{{TABLE_ID_TASKS}}`
- Always include: Role, How You Work, Authority & Boundaries, context sources, and the tools / systems the agent relies on

**Schema packaging rule:** structural schemas belong in `artifacts/schemas/`. Human-readable explanation of why a schema exists belongs in `guidelines/` or the relevant integration playbook.

---

## Parallelising Large Batches

**Do NOT use `delegate_task` for bulk packaging** — subagents time out (~80s) on large reads.

**Use `execute_code` with a batch Python script instead:**
```python
skill_mapping = {
    'core/skills/hermes-agent.md': 'core/skills/hermes-agent.md',
    # ... all mappings
}
for dest_rel, src_rel in skill_mapping.items():
    content = read_skill(os.path.join(SKILLS_ROOT, src_rel))
    content = universalize(content)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w') as f:
        f.write(content)
```

---

## Agent Package Structure Rules

These rules govern how `artifacts/agents/<agent>/` should look in the package — learned from Leo packaging 2026-06-16.

### Skills directory must be flat
Skills in `artifacts/agents/<agent>/skills/` must sit at the **root of that folder**, not inside a subfolder. No `crm/`, `core/`, or category subfolders inside an agent's skills dir. A visitor opening the skills folder must see all skills immediately — no extra click required.

```
✅  artifacts/agents/leo/skills/twenty-crm/SKILL.md
✅  artifacts/agents/leo/skills/log-engagement/SKILL.md
❌  artifacts/agents/leo/skills/crm/twenty-crm/SKILL.md   ← subfolder = hidden, wrong
```

If the live profile uses category subfolders for its own organisation, flatten when copying to the package:
```bash
# Flatten crm/ subfolder to skills/ root
for dir in artifacts/agents/leo/skills/crm/*/; do
  mv "$dir" "artifacts/agents/leo/skills/$(basename $dir)"
done
rmdir artifacts/agents/leo/skills/crm/
```

### Skills README must match actual contents
The `skills/README.md` must list every skill currently in the folder, with a one-line description and which Capability it serves. After any add/remove/rename, update the README in the same commit. Two-table structure:
- **BD Capabilities** — skills that implement the agent's named capabilities (C1–C6 etc.)
- **Infrastructure Skills** — tools and systems the agent uses across all capabilities

### SOUL.md Knowledge Sources — no product names
The Knowledge Sources table must contain zero company-specific product names ([Business Line], [Business Line], [Business Line], [Business Line], [Business Line], etc.). The correct pattern is one generic template row:

```markdown
| Product Wiki — [Your Product] | `wiki/products/{{PRODUCT_SLUG}}` | Value prop, use cases, customer types. Add one row per product/service line. | 📝 Pending |
```

Never six rows with our product names. If the previous genericization script left product names in the first column while replacing the slugs, that is **not** fully genericized — fix the first column too.

### Genericization is complete only when ALL three columns are clean
In any table row: if the resource name column still says "[Business Line]" or any internal product name, the row is not genericized even if the slug column has `{{PRODUCT_SLUG}}`. Check every column independently.

### Internal-use package completeness rule

When packaging an agent for **your own DX runtime first** (before full client genericization), do not leave core capabilities only in the shared skill registry.

If the agent spec says the agent depends on a skill to perform its active non-future scope, the package should carry an explicit copy under:
- `artifacts/agents/<agent>/skills/<skill>/`

This is different from merely having the skill available somewhere in the live Hermes install.

Use this distinction:
- **runtime capability exists** = the shared/local Hermes library has the skill
- **package completeness exists** = the agent artifact itself carries the skill layer needed to satisfy the spec

For an internal-use packaging pass, prefer a **self-contained agent artifact**:
1. read the deployed-agent spec
2. list all non-future skills named under active capabilities
3. copy those skill folders into `artifacts/agents/<agent>/skills/`
4. keep any truly agent-specific skills there as well
5. update `skills/README.md` so it explicitly says which skills are Iris-specific vs copied capability skills vs external tool dependencies
6. add an agent `SETUP.md` if the artifact layer did not already have one

Do not tell yourself "the shared layer already has it" and stop there — that leaves the package incomplete.

### Agent SETUP.md — canonical structure

Every `artifacts/agents/<agent>/SETUP.md` must follow this structure. It is a client-facing onboarding guide, not just a README.

**Required sections in order:**
1. **Overview table** — all steps with type (self-hosted / cloud SaaS / cloud API / configuration / content) and estimated time
2. **One section per step** — numbered, with exact shell commands or UI instructions
3. **Placeholder reference table** — every `{{PLACEHOLDER}}` in the agent's files listed with what to put there
4. **Verify everything** — shell commands to confirm each system is reachable and wired up
5. **Next steps after setup** — what to do first once the agent is running

**Step order convention:**
1. Core infrastructure (Hermes + GBrain) → reference `../../SETUP.md`
2. Self-hosted services first (CRM, Hindsight)
3. Cloud API credentials (OpenMail, GitHub SSH, Tavily, Anthropic)
4. Profile creation + SOUL.md + .env + config.yaml
5. Skills installation
6. Cron job creation
7. Memory seeding (GBrain pages + Hindsight banks)

**Placeholder table must include every `{{TOKEN}}`** found across SOUL.md, skills/, and cron/jobs.json — not just the obvious ones. Scan before writing:
```bash
grep -roh '{{[A-Z_]+}}' artifacts/agents/<agent>/ | sort -u
```

**Hindsight bank creation** — include the exact `curl` commands to create all required banks, one per bank. Banks must exist before cron jobs run.

**Cron jobs** — the `jobs.json` is a reference template only; it is NOT directly importable into Hermes. The SETUP.md must explain this and show the CLI pattern for manually creating each job.

---

### Tools section in SOUL.md — not a separate file

Tool access is documented **inside SOUL.md** only — no separate `tools.md`. SOUL.md is always loaded; a separate file would not be. Every SOUL.md must have a Tools section with exactly three subsections:

```markdown
## Tools

### Always Available (interactive sessions + cron)
| Tool | Endpoint / Access | Skill | Used for |
|---|---|---|---|
| Twenty CRM | `http://localhost:3001/graphql` | `twenty-crm` | All pipeline reads/writes |
| Hindsight | `http://localhost:8888` | — (direct API) | Contextual memory |
| GBrain | MCP (`mcp_gbrain_*`) | `capturing-to-gbrain` | Knowledge graph |
| Web search | Built-in (`web_search` → Tavily) | — | Enrichment, research |

### Cron sessions (restricted toolset: web, terminal, file)
MCP tools (GBrain) are NOT available in cron. Any capability requiring MCP
must run in an interactive session or delegate via task.

### Not available to this agent
- Code execution
- Image generation
- File system writes outside `workspace/`
```

This is the single authoritative declaration of what the agent can access. The deployer reads it to know what to enable in `config.yaml`. The agent reads it to know what not to attempt.

---

### Language: 100% English for international packages
All content in `artifacts/agents/` — SOUL.md, every SKILL.md, every reference file, README.md, cron README.md, and jobs.json prompts — must be in English. No Chinese prose anywhere. This applies even to trigger phrases in SKILL.md frontmatter.

**Scan for Chinese before every push:**
```bash
grep -rlP '[\x{4e00}-\x{9fff}]' artifacts/agents/ --include="*.md" --include="*.json"
```
Any hit = block the push and translate first.

**Bulk translation pattern** (when many files have Chinese):
Use the Anthropic API directly via Python — faster and more reliable than delegate_task for large file counts:
```python
import anthropic, re, os

client = anthropic.Anthropic(api_key=load_key())
CJK = re.compile(r'[\u4e00-\u9fff]')

SYSTEM = """You are a technical translator. Translate ALL Chinese prose, headings, table cells, bullet points, trigger phrases, and descriptions to English.
Rules:
- Keep ALL fenced code blocks (``` ... ```) EXACTLY unchanged.
- Keep inline backtick code exactly unchanged.
- Keep all {{PLACEHOLDER}} tokens exactly as-is.
- Keep all Markdown formatting intact.
- For YAML frontmatter: translate only description: and triggers: values. Keep all keys unchanged.
- Translate faithfully — preserve full meaning.
Return ONLY the translated content."""

def translate_file(path):
    content = open(path).read()
    if not CJK.search(content):
        return  # skip — no Chinese
    msg = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=8000,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Translate:\n\n{content}"}],
    )
    translated = msg.content[0].text
    if len(translated) > len(content) * 0.4:  # sanity check
        open(path, 'w').write(translated)
```
Process files one at a time to avoid timeouts — do NOT pass 10+ files per delegate_task call.

### Lark/Feishu skills do NOT belong in international packages
`lark-*` skills (lark-im, lark-base, lark-task, lark-doc, lark-drive, lark-calendar, lark-contact, lark-shared, reading-lark-files) are Lark/Feishu-specific. Lark is a China/SEA-market tool. International deployments use Slack, Teams, or other IM — they have no use for Lark API skills.

**Do not include in `artifacts/agents/<agent>/skills/`:**
- Any `lark-*` skill
- `reading-lark-files`

These belong in the {{COMPANY_NAME}}-internal agent profiles only, not in the distributable package. If an agent's live profile has these, strip them when copying to the package.

---

## Third-Party Tool Registry (Leo stack)

When packaging Leo or any BD agent, the full tool list is:

| Tool | Hosting | Credentials | Required? |
|---|---|---|---|
| Hermes Agent | Self-hosted (VM) | — | ✅ |
| Twenty CRM | Self-hosted (Docker, port 3001) | `TWENTY_API_KEY` | ✅ |
| Hindsight | Self-hosted (Docker, port 8888) | None (local) | ✅ |
| GBrain | Self-hosted (Node, MCP) | Via MCP (local) | ✅ |
| OpenMail | Cloud (openmail.sh) | `OPENMAIL_API_KEY`, `OPENMAIL_INBOX_ID` | ✅ Leo |
| GitHub | Cloud (SSH key) | SSH key on VM | ✅ |
| Tavily | Cloud API (tavily.com) | `TAVILY_API_KEY` | ✅ Leo |
| Anthropic Claude | Cloud API | `ANTHROPIC_API_KEY` (in Hermes .env) | ✅ |
| Lark / Feishu | Cloud SaaS | App ID + App Secret | ⚙️ Optional (China/SEA) |

**Tavily usage by skill:**
- `enriching-accounts` — company news, website, LinkedIn for L1/L2 enrichment
- `prospect-scouting` — research companies on target list
- `checking-pipeline-health` — context on stalled opportunities
- `checking-pipeline-strategy` — market signals and competitor activity

Skills call `web_search` generically — Hermes routes to Tavily when `TAVILY_API_KEY` is set in the agent's `.env`. No skill changes needed to swap providers.

**GitHub SSH:** one key per VM, shared across all agent profiles (same Linux user). Configure once in `~/.ssh/config`. All agents on that VM inherit it automatically.

---

## Client Migration: Updating an Existing Install

When a client already has a previous version of the package installed, **do NOT wipe and reinstall**. Use targeted update instead.

### Targeted update (preferred)
- Remove stale skills: `rm -rf ~/.hermes/profiles/<agent>/skills/<stale-skill>`
- Replace updated SOUL.md: overwrite `~/.hermes/profiles/<agent>/SOUL.md` with the new version (fill placeholders)
- Update individual skills that changed: overwrite their SKILL.md + references/ in place
- Leave cron jobs, Hindsight memory, and CRM data untouched

### When to wipe and reinstall
Only wipe if: the agent profile structure changed fundamentally (e.g. bank taxonomy redesign), or the client's install is so broken that surgery is harder than restart. High cost — all Hindsight memory, cron jobs, and CRM links must be rebuilt.

### Who executes the migration
**Always route to the client's Iris (or the human operator), NOT the agent being updated.** Leo should never modify his own SOUL.md or skills — that's operator-layer work, not BD work. Write migration instructions as an Iris task briefing.

### Migration instruction format (for client's Iris)
```
You are running a Leo agent update. Steps:
1. Remove stale skills that are no longer part of the runtime set
2. Overwrite SOUL.md from [raw GitHub URL] (fill {{PLACEHOLDERS}} before saving)
3. Overwrite updated skills from [raw GitHub URL]
4. Verify: list ~/.hermes/profiles/leo/skills/ — confirm removed skills are gone
5. Confirm cron jobs still reference only existing skills
```

## Reporting Back to the User

When packaging, sanitizing, or pushing artifacts, keep the user-facing summary terse unless they ask for audit detail:
1. **Conclusion first** — packaged / pushed / cleaned or not
2. **Brief bullets only** — the smallest useful set of facts (e.g. scope, commit, repo state)
3. **One short next-step recommendation**

Do **not** paste long file-by-file change lists or broad sanitization dumps by default.

## Pitfalls

- **Cron jobs.json packaging** — `jobs.json` is a reference template, not a Hermes-importable file. Strip ALL runtime state before pushing: remove `id`, `completed`, `last_run_at`, `next_run_at`, `origin.chat_id`, `state`, `paused_at`. Replace all instance-specific values with `{{PLACEHOLDER}}`. Keep: `name`, `skills`, `schedule`, `deliver` (with placeholder), `enabled_toolsets`, `prompt` (genericized). The README must include a placeholder reference table so installers know what to fill in.

- ❌ **Old repo names** — `busycow-playbooks`, `busycow-agent-team`, `dataxquad-core`, `dx-internal-wiki`, `dx-internal-kb` are all deleted/renamed. Current repos: `busycow-agent-package` at `/mnt/disks/data/busycow-agent-package/`; `dx-gbrain` at `[GBRAIN_VAULT]/`. Neither lives under `hermes/`.
- **`dx-internal-kb` is fully DEPRECATED (2026-06-17)** — merged into `dx-gbrain`. Any reference to `dx-internal-kb` is stale. The canonical knowledge path is `[GBRAIN_VAULT]/internal/`.
- ❌ **shared-skills/ and _shared/ symlinks are gone** — entire shared skills architecture removed Jun 2026. Agent profiles have flat real dirs only. No `_shared/` symlinks, no `shared_skills/` registry. Duplicate skills per agent.
- ❌ **Retired example agent names** — not part of the current active roster. Keep the active agent list current in the package docs and remove outdated names when the framework changes.
- ❌ **Quinn deleted Jun 2026** — remove from all rosters.
- **`artifacts/schemas/` is the active schema path** — keep structural schemas there, not under `context/schemas/`.
- **`artifacts/knowledge-base-templates/` is the active template path** — do not reintroduce `knowledge-base-setup/` as the live package directory.
- **Do not reintroduce `context/` as a package content layer** — explanatory prose belongs in `guidelines/`, operational instructions in `playbooks/`, and installable assets in `artifacts/`.
- **SOUL.md is the runtime source of truth inside `artifacts/agents/`** — do not create standalone `CAPABILITY.md` files unless the deployment explicitly defines them.
- **Use "knowledge base" in package prose** — avoid reintroducing older `wiki` wording in new package-facing docs.
- **dx-internal-kb is DEPRECATED** — the entire knowledge base was merged into `dx-gbrain` on 2026-06-17. GBrain vault at `[GBRAIN_VAULT]/` is now the single source of truth. Structure: `internal/` (our knowledge) + `external/` (world knowledge). Do not reference `dx-internal-kb` or `dx-internal-wiki` anywhere.
- **guidelines/ reading order is numbered 01–04** — when adding new guideline files, maintain the reading order prefix. Current order: `01-infrastructure-spec.md` → `02-knowledge-and-memory-spec.md` → `03-gbrain-and-hindsight-spec.md` → `04-agent-spec-template.md`. The template is last (04), not first (00).
- **Agent specs use role-based names for agents too** — in client-facing specs, do not use internal agent names like "Growth Agent's personal name". Use role descriptions such as "Growth Agent", "Customer Success Agent", or "BD Lead Agent". Keep only framework-level role labels that are intentionally part of the package design.
- **`deployed-agents/` folder naming** — the subfolder under `guidelines/` for built agent specs is called `deployed-agents/` (not `existing-agents`, `active-agents`, or `team/`). README.md in that folder has two tables: Active Agents + Pending Agents.
- **deployed-agents/ subfolder under guidelines/** — agent specs for deployed agents live in `guidelines/deployed-agents/[agent]-spec.md`. Follow the 4-part template from `04-agent-spec-template.md`. Every spec needs a Build Mapping (Part 4) that links spec sections to actual Hermes artifacts. **ALWAYS use the template — do NOT write free-form specs.** The template exists for a reason: it enforces Part 1 (why the agent exists + the number it owns), Part 2 (context sources), Part 3 (capabilities + skills + crons + delivery channels), Part 4 (tools + credentials + build mapping), and a Status Tracker. A free-form spec that covers the same information is still wrong — it won't be scannable by clients or translatable to SOUL.md artifacts without the template structure. If you wrote a spec and it doesn't have four clearly labelled Parts, rewrite it before pushing.

- **Agent spec rewrite checklist before pushing to guidelines/deployed-agents/:** (1) Part 1 has 1a/1b/1c subheadings, (2) 1b has "The number it owns" row, (3) Part 2 has a context sources table AND a GBrain content status table, (4) Part 3 has 3a/3b/3c/3d subheadings with skills split into Capability/General, (5) Part 4 has build mapping table, (6) Spec Status tracker at bottom with per-section checkboxes. Missing any of these = incomplete spec.
- **guidelines/ content must be fully generic** — every file in `guidelines/` is client-facing. Any {{COMPANY_NAME}}-specific names ([Business Line], [Business Line], [Business Line], [Business Line] as product names, the sales rep, the manager, {{COMPANY_NAME}} company name, `dx-` bank prefixes, real paths, real Lark channel IDs like `oc_8c3706...`, real Hindsight bank names like `{{ORG_PREFIX}}-pipeline`, real GitHub org names like `{{ORG_GITHUB_NAMESPACE}}`) must be replaced with `[org]`, `[bl-name]`, `[Human 1]`, `[Human 2]`, `[org]-pipeline`, `[org]/[org]-gbrain`, `{{PLACEHOLDER}}` before committing. Partial genericization (slug column clean, name column still has real product name) is NOT acceptable — check every column of every table independently. Run the sanitization scan after every write — do not rely on memory of what you changed.
- **Terminology: use Opportunity not Deal** — all sales pipeline references use "Opportunity" to match Twenty CRM object names. Exception: technical CRM field names like `dealType`, `dealId`, `OpportunityDealTypeEnum` stay as-is (schema identifiers). Directory names like `deal-progressing/` stay as-is (technical identifiers). Only prose content uses Opportunity.
- **CRM schema in `artifacts/schemas/crm.md`** — structural CRM definitions belong under `artifacts/schemas/`. Always verify against the live system before trusting a copied schema doc.
- **Genericizing agent files** — SOUL.md and skills must be genericized with Python regex before push. Apply broad ID patterns (oc_*, cli_*, om_*) first, then named strings. Skip all symlinks when walking skill dirs (Lark skills have cyclic same-name symlinks inside). See `copy_skill_clean()` above.
- **Current package layout is `guidelines/` + `playbooks/` + `artifacts/`** — if you see older internal notes referring to `agent-teams/`, `context/schemas/`, `knowledge-base-setup/`, or `third-party-tools/` as current top-level package paths, treat them as legacy and map them through `references/package-structure-v2.md`.
- **CRM schema now lives under `artifacts/schemas/crm.md`** — structural schemas stay in `artifacts/schemas/`, not `context/schemas/`.
- **Knowledge-base templates live under `artifacts/knowledge-base-templates/`** — do not reintroduce `knowledge-base-setup/` as the active package path.
- **Use `guidelines/` and `playbooks/`, not `context/`, for package prose** — explanatory content belongs in `guidelines/`, operational instructions in `playbooks/`, and only installable assets in `artifacts/`.
- **Remote URL**: repo is at `git@github.com:{{ORG_GITHUB_NAMESPACE}}/busycow-agent-package.git`. If a clone still points at the old repo name, update it with `git remote set-url origin git@github.com:{{ORG_GITHUB_NAMESPACE}}/busycow-agent-package.git`.
  ```python
  # /tmp/create_repo.py
  import urllib.request, json
  env = {}
  with open("~/.hermes/.env") as f:
      for line in f:
          if "=" in line and not line.startswith("#"):
              k, v = line.split("=", 1)
              env[k.strip()] = v.strip()
  token = env.get("GITHUB_TOKEN", "")
  req = urllib.request.Request(
      "https://api.github.com/orgs/{{ORG_GITHUB_NAMESPACE}}/repos",
      data=json.dumps({"name": "repo-name", "private": True, "auto_init": True}).encode(),
      headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"},
      method="POST"
  )
  with urllib.request.urlopen(req) as resp:
      d = json.loads(resp.read())
      print("URL:", d.get("html_url")); print("private:", d.get("private"))
  ```
  Run: `python3 /tmp/create_repo.py`. Then: `git clone git@github.com:{{ORG_GITHUB_NAMESPACE}}/repo-name.git` (SSH, not HTTPS).
- **Making an existing repo private** — same Python pattern but PATCH to `/repos/<org>/<repo>` with `{"private": True}`. Shell heredoc approach fails with EOF/quote errors when the .env source is inline.
- **GitHub SSH remains shared at the VM level** — all profiles run under the same Linux user (`hunter_lin`), so `~/.ssh/config` and keys are automatically shared. No per-profile setup needed. Key in use: `~/.ssh/github_geokernel` pointing to `github.com`. Verify: `ssh -T git@github.com` → `Hi hunterlin1997!`.
- **Leo does not need a repo-operation skill for runtime knowledge lookup** — internal knowledge reads route through GBrain / the dx-gbrain vault flow, while external package publication routes through `packaging-to-github`.

- **HTTPS clone + SSH push → fatal: could not read Username** — `git clone https://github.com/...` sets the remote URL to HTTPS. Pushing requires credentials (GitHub removed password auth). Fix once with: `git remote set-url origin git@github.com:{{ORG_GITHUB_NAMESPACE}}/busycow-agent-package.git` — subsequent pushes use the SSH key already configured on the VM (`hunterlin1997` key). Verify SSH works first: `ssh -T git@github.com`.
- **Established knowledge repo structure** — `dataxquad-core` and `aquaoptima-core` use the same pattern: `README.md` + subdirs (`product/`, `market/`, `partners/`, `strategy/`, `team/`, `operations/`, `decisions/`). Each file is a standalone markdown knowledge doc tagged `v0.1 — team to update`. This is the canonical structure for any company-level knowledge repo.
- Run sanitization scan **every time**, even for small edits
- `{{PLACEHOLDER}}` format for all dynamic values — don't leave bare TODO comments
- SETUP.md must work as a **standalone agent instruction** — don't assume the agent has context from the README
- Raw GitHub URLs only for client install — `raw.githubusercontent.com`, not the HTML page
- Don't add Notion-based variants or other stacks — one stack only (Hermes + Lark + GBrain)
- After push, verify with: `curl -s [raw URL] | head -5`
- Sanitization scan: use `os.path.expanduser()` — bare `~` doesn't expand in Python's `os.walk`
- Internal server paths appear in two forms: `/home/the_owner/` AND `~/.hermes/` — use greedy pattern: `r'~/.hermes[^\s]*'` → `~/.hermes`
- Scan false positives: `LARK_APP_SECRET=***` in README is safe (example text)
- **SOUL.md templates must be universalized** — strip all specific deal/client/product names
- **GBrain pages:** only export structural patterns and decisions, never entity-specific timelines or fact rows
- **Capability Docs:** the trigger description is the most valuable part — make it concrete and specific
- **shared-skills/ files must be fully universalized** — all credentials/IDs use `{{PLACEHOLDER}}` format; the twenty-crm.md skill is the reference example
- **artifacts/schemas/ vs artifacts/agents/**: cross-agent schemas (CRM object definitions, DB schemas) go in `artifacts/schemas/`, NOT inside any agent's directory; artifacts/agents/ is for SOUL.md, capabilities, and agent-specific skills only
- **Remote URL**: repo is at `git@github.com:{{ORG_GITHUB_NAMESPACE}}/busycow-agent-package.git` — if a clone still points at the old repo name, update it with `git remote set-url origin git@github.com:{{ORG_GITHUB_NAMESPACE}}/busycow-agent-package.git`
