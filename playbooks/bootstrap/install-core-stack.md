# Install Core AI Colleague Stack

> Audience: Default Hermes or an operator running commands with Default Hermes guidance.
> Scope: prepare the shared AI colleague infrastructure after base Hermes already exists.

This playbook must run before installing individual AI colleagues.

---

## 0. Stop Conditions

Stop and report the gap if any of these are true:

- base Hermes CLI is not available
- the package repository is not readable
- no human owner or approval owner is known
- credentials are required but no approved credential handoff exists
- the target organization name is unknown
- a requested external write would happen without an approval rule

---

## 1. Confirm Base Hermes

Run:

```bash
hermes --version
hermes doctor
hermes profile list
```

Record:

- Hermes version
- current default profile
- any doctor warnings
- package repository path

Do not hide warnings. If a warning affects install safety, stop and ask the human owner.

---

## 2. Confirm Target Deployment Metadata

Collect or confirm:

| Field | Required? | Notes |
|---|---|---|
| organization slug | yes | used for paths, banks, logs, and naming |
| human owner | yes | accountable owner |
| approval owner | yes | approves high-risk actions |
| workspace root | yes | default: `/srv/ai-colleagues/workspaces/` |
| GBrain sources | yes, may be missing | mark missing if not ready |
| Hindsight endpoint/banks | yes, may be missing | mark missing if not ready |
| structured systems | yes, may be empty | CRM, Plane, approvals, logs |
| communication channel | optional | Lark/Feishu or other delivery surface |

If values are missing, create an install gap report rather than guessing.

---

## 3. Create Workspace Root

Default path:

```bash
sudo mkdir -p /srv/ai-colleagues/workspaces
sudo mkdir -p /srv/ai-colleagues/shared
sudo mkdir -p /srv/ai-colleagues/logs
```

If the target environment uses another root, record the override.

Expected shared docs or directories:

```text
/srv/ai-colleagues/shared/approval-policy.md
/srv/ai-colleagues/shared/tool-action-log-policy.md
/srv/ai-colleagues/shared/context-routing-policy.md
/srv/ai-colleagues/logs/routine-runs/
/srv/ai-colleagues/logs/tool-actions/
/srv/ai-colleagues/logs/evaluations/
```

If these files are not present in artifacts yet, draft them as missing runtime artifacts and do not claim the stack is complete.

---

## 4. Configure GBrain Assumptions

Confirm whether GBrain is available.

If available, record:

- endpoint or MCP name
- sources
- schema pack
- source-level access rules
- home write source convention
- canonical/evidence separation

Recommended V1 sources:

```text
shared
customers
partners
product-eng
internal
```

Minimum verification:

```bash
hermes mcp list
```

Then use the deployment's approved GBrain verification command or MCP call.

Stop if an AI colleague requires canonical knowledge that does not exist and no review path is defined.

---

## 5. Configure Hindsight Assumptions

Confirm whether Hindsight is available as the external memory provider.

For each role-owning colleague, the target model is:

- one personal Hindsight bank
- memory mode: `hybrid`
- auto-recall enabled
- auto-retain enabled for personal bank unless explicitly overridden
- shared/domain bank writes governed

Core stack should define the bank naming convention before agents are installed.

Recommended naming pattern:

```text
{{org_slug}}/agents/{{profile_name}}
{{org_slug}}/shared/{{domain}}
```

If Hindsight is missing, record the gap and install agents in disabled or draft state only.

---

## 6. Identify Structured Systems of Record

Create or confirm the systems that own operational truth.

Examples:

| System | Owns |
|---|---|
| CRM | accounts, contacts, deals, stages, owners |
| Plane or task system | work items, blockers, cycles |
| approval table/system | approval state |
| routine run log | autonomous routine history |
| tool action log | external tool action audit |
| evaluation log | evaluator and human review results |

If a requested AI colleague needs operational state and no system of record exists, stop before activation.

---

## 7. Configure Communication Integration

If the deployment uses Lark/Feishu, continue with:

```text
../integrations/lark/README.md
```

Minimum checks, if `lark-cli` exists:

```bash
lark-cli auth status --verify
lark-cli config default-as bot
```

If communication is not ready, record it as a delivery gap. Do not enable routines that require outbound delivery.

---

## 8. Verify Core Stack

Run or confirm:

```bash
hermes doctor
hermes skills list
hermes mcp list
```

Then produce a core stack status summary:

| Area | Status | Notes |
|---|---|---|
| Hermes runtime | pass / warn / fail | |
| workspace root | pass / warn / fail | |
| GBrain | pass / missing / partial | |
| Hindsight | pass / missing / partial | |
| structured systems | pass / missing / partial | |
| approvals | pass / missing / partial | |
| logs | pass / missing / partial | |
| communication | pass / missing / partial | |

---

## 9. Next Step

If the core stack is ready or explicitly accepted as partial by the human owner, continue with:

```text
playbooks/bootstrap/install-agent-package.md
```

Do not install or activate role-owning colleagues until core gaps are either fixed or explicitly accepted for a draft-only install.