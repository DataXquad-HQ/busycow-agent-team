# Third-Party Tools

Every tool in the BusyCow stack — what it does, how agents use it, and setup notes.

## Tools

| Tool | Directory | Role in the stack |
|---|---|---|
| Lark / Feishu | `lark/` | Workspace — IM, task board, docs, calendar |
| Twenty CRM | `twenty-crm/` | Pipeline — deals, contacts, companies, stages |
| Hermes Agent | `hermes/` | Agent runtime — skills, cron, memory, tools |
| GBrain | `gbrain/` | Knowledge graph — entity facts, decisions, intel |
| Hindsight | `hindsight/` | Episodic memory — interaction history, soft signals |

## What each file contains

Each tool directory has:
- **README.md** — what the tool does, how it fits in the stack, how agents use it day-to-day
- **SETUP.md** (where relevant) — installation and configuration steps
