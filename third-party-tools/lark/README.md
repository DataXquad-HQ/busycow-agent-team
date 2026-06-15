# Lark / Feishu

## What it is

Lark (international) / Feishu (China) is the team workspace. It is the primary communication and coordination layer for the entire agent team.

## Role in the stack

| Feature | How we use it |
|---|---|
| IM (Instant Messaging) | Founders communicate with agents; agents receive tasks and return results |
| Bitable (Base) | Task tracker — the team's task board where all agent work is logged |
| Docs | Internal documents, meeting notes, client-facing materials |
| Calendar | Scheduling, meeting management |
| Drive | File storage for shared documents |
| Wiki | Not used — internal docs live in GitHub (`dx-internal-wiki`) |

## How agents use it

Every agent communicates through Lark IM. The task board (Lark Bitable) is the canonical record of what each agent is doing and what has been completed.

**Agents read from Lark:**
- Tasks assigned to them via the task board
- Messages and requests from founders or Iris

**Agents write to Lark:**
- Task status updates (in progress, done, blocked)
- Agent Notes — what was done, what was found, what needs human review
- Result for Human — the final human-readable output after completing a task

## Setup

Each agent requires its own Lark bot app with its own App ID and App Secret. Credentials are not shared between agents.

Steps:
1. Create a bot app in the Lark Developer Console: https://open.larksuite.com/
2. Enable required permissions: `im:message`, `bitable:app`, `docx:document`, `contact:user.base:readonly`
3. Add the App ID and App Secret to the agent's Hermes config under `mcp_servers.lark`
4. Add the bot to any groups or Bitables it needs to access

## Access convention

Agents use `lark-cli` in `--as user` mode for actions that require user-level access (e.g. writing to Bitable as the operator, not the bot).

Bot credentials go in the agent's `config.yaml`. User credentials go in the agent's `.env`.
