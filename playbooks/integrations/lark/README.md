# Lark / Feishu

## What it is

Lark (international) / Feishu (China) is the team workspace. It is the
primary communication and coordination layer for the agent team.

In the packaged BusyCow deployment, **Lark CLI is a required companion to the
Lark integration**. It is not optional glue code. It is the operational surface
used to bind the app, enforce identity policy, troubleshoot permission issues,
and cover actions that are awkward or unavailable through Hermes gateway / MCP
alone.

---

## Role in the stack

| Layer | Role |
|---|---|
| Hermes gateway | Messaging runtime — the agent receives and sends chat messages |
| Lark app | The bot identity and app-level permission container |
| `lark-cli` | App binding, identity policy, auth inspection, permission troubleshooting, and direct operational access |

---

## Packaging policy

### Default mode

For a standard BusyCow deployment, bind `lark-cli` to the **same Lark app used
by the Hermes runtime**, then operate it in **bot-default, non-restricted** mode.

This keeps bot as the normal operating path while avoiding unnecessary policy
friction.

### Why

- The app identity is stable and centrally managed
- Bot-mode behavior is easier to package and reproduce
- Bot remains the default posture without hard-disabling user-mode tools
- Agents can still send messages, update operational records, and manage docs
  that the app already has permission to access

### What this means

- Normal package behavior assumes **bot identity first**
- `--as user` is an **exception path**, not the default
- If a deployment needs user-level actions later, the operator can still use
  them deliberately without first changing strict-mode

---

## Key settings

Record these settings in the target deployment:

| Setting | Required value / pattern | Why it matters |
|---|---|---|
| Lark app binding | Same app as Hermes runtime | Keeps CLI and agent runtime on one permission surface |
| Workspace | Shared deployment workspace name (for example `hermes`) | Makes all agents read the same `lark-cli` config / token store |
| `default-as` | `bot` | Makes bot the default identity for direct CLI use |
| `strict-mode` | `off` | Keeps the CLI flexible while still preserving `bot` as the default identity |
| App scopes | Must include the bot-level scopes the workflow needs | App permission is the real gate in bot mode |
| Resource access | Bot must be added to required chats / docs / bases | Bot mode cannot access resources it was never granted |

---

## Required setup sequence

### 1. Create or select the deployment app

Create one Lark app for the deployment, or select the already-approved app that
Hermes will use.

### 2. Bind `lark-cli` to that app

```bash
lark-cli config init --new
```

Bind it into the shared workspace used by the deployment.

### 3. Enforce bot-default operation

```bash
lark-cli config default-as bot
lark-cli config strict-mode off
```

### 4. Verify the policy landed

```bash
lark-cli config default-as
lark-cli config strict-mode
lark-cli auth status --verify
lark-cli config show
```

Expected outcomes:
- `default-as: bot`
- `strict-mode: off`
- bot identity is `ready`
- the config is stored in the intended shared workspace

---

## Operational rule

**Use `lark-cli` as the package's operator-facing control plane for Lark.**

Use it for:
- binding the Lark app
- checking bot readiness
- inspecting scopes
- diagnosing permission failures
- enforcing identity policy
- direct operational actions when Hermes gateway / MCP is not the right surface

Do not assume Hermes messaging alone replaces `lark-cli`.

---

## Exception path: deliberate user-mode operations

If a deployment truly needs user-level actions later, keep `default-as=bot` but
run user auth and user-mode commands deliberately.

Example:

```bash
# bot remains the default posture
lark-cli config default-as bot
lark-cli config strict-mode off

# only when the operator explicitly wants user-level access
# lark-cli auth login --scope "..."
# lark-cli ... --as user
```

This should still be treated as an exception workflow, not the default package
model.

---

## Common failure modes in bot-default deployments

| Symptom | Likely cause | Fix |
|---|---|---|
| CLI asks for user auth | a user-mode command is being run, or the workflow genuinely needs user scopes | keep `default-as=bot`; only authorize user mode when explicitly intended |
| Bot cannot access a doc / base / chat | Resource not shared with the app / bot | add the bot or grant the app access |
| Permission denied despite bot mode | Missing app scope | add scope in developer console and publish the app update |
| Different agents see different CLI state | They are not sharing the same workspace | standardize the deployment workspace name |

---

## What this package assumes

This package assumes:

- Lark is part of the deployment's operating system
- `lark-cli` is installed and used intentionally
- the CLI is bound to the same app as Hermes
- bot mode is the default operating posture, while strict-mode stays off for flexibility

If a client wants a different policy, document that as a deployment-specific
override rather than silently drifting from the package default.
