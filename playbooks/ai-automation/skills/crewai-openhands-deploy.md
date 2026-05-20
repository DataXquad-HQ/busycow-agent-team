---
name: crewai-openhands-deploy
description: >
  Deploy CrewAI + OpenHands as a self-hosted AI dev stack via Docker Compose,
  wire them together over the Docker internal network, install the integration
  BaseTool, and inject LLM API keys. Covers verified image tags, pitfalls
  encountered in deployment, OpenHands V1 REST API polling pattern, and the
  CrewAI BaseTool wrapper for calling OpenHands. Use when deploying or
  re-deploying this stack on any Linux VM.
---

# CrewAI + OpenHands — Self-Hosted Deployment

## Verified Versions (May 2026)

| Tool | Version | Image |
|------|---------|-------|
| CrewAI | `1.14.4` | `python:3.11-slim` + pip |
| OpenHands | `1.7.0` | `ghcr.io/openhands/openhands:1.7.0` |

---

## Deployment Location

Files live at `~/ai-agents/` on the host:
```
~/ai-agents/
├── docker-compose.yml
├── .env                        # actual keys (gitignored)
├── .env.example                # template
└── crewai_openhands/
    ├── openhands_tool.py       # CrewAI BaseTool wrapping OpenHands REST
    ├── main.py                 # example Crew (Planner→Coder→Reviewer)
    └── requirements.txt
```

---

## Step 1 — Pull Images

```bash
# OpenHands only (large image, pull first)
docker pull ghcr.io/openhands/openhands:1.7.0

# CrewAI uses python:3.11-slim + pip install at runtime — no pre-pull needed
```

## Step 2 — docker-compose.yml

```yaml
services:
  crewai:
    image: python:3.11-slim
    container_name: crewai
    restart: unless-stopped
    volumes:
      - crewai_workspace:/workspace
      - ./crewai_openhands:/workspace/crewai_openhands
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - LLM_MODEL=${LLM_MODEL:-anthropic/claude-sonnet-4-5}
      - LLM_API_KEY=${LLM_API_KEY:-}
      - OPENHANDS_URL=http://openhands:3000
      - OPENHANDS_API_KEY=${OPENHANDS_API_KEY:-}
    working_dir: /workspace
    command: >
      bash -c "
        pip install -q 'crewai[tools]==1.14.4' requests &&
        echo '✅ CrewAI 1.14.4 installed' &&
        tail -f /dev/null
      "
    depends_on:
      - openhands
    healthcheck:
      test: ["CMD", "python", "-c", "import crewai; print(crewai.__version__)"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s

  openhands:
    image: ghcr.io/openhands/openhands:1.7.0
    container_name: openhands
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - openhands_workspace:/opt/workspace
    environment:
      - LOG_ALL_EVENTS=true
      - LLM_API_KEY=${LLM_API_KEY:-}
      - LLM_MODEL=${LLM_MODEL:-anthropic/claude-sonnet-4-5}
    extra_hosts:
      - "host.docker.internal:host-gateway"
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:3000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 120s

volumes:
  crewai_workspace:
  openhands_workspace:
```

## Step 3 — .env file

```bash
# Read Hermes key and write to .env
ANTHROPIC_KEY=$(grep "^ANTHROPIC_API_KEY=" ~/.hermes/.env | cut -d'=' -f2-)
cat > ~/ai-agents/.env << EOF
ANTHROPIC_API_KEY=${ANTHROPIC_KEY}
LLM_API_KEY=${ANTHROPIC_KEY}
LLM_MODEL=anthropic/claude-sonnet-4-5
OPENHANDS_API_KEY=
EOF
```

## Step 4 — Start

```bash
cd ~/ai-agents && docker compose up -d
```

## Step 4b — Configure LLM in OpenHands Web UI (MANDATORY)

⚠️ **You must do this before running any CrewAI crews.** env vars alone are not enough in 1.7.0.

1. Open `http://localhost:3000`
2. Go to **Settings → LLM**
3. Set **Model**: `claude-sonnet-4-5` (or your model)
4. Set **API Key**: your Anthropic key
5. Click **Save**

This writes `/root/.openhands/settings.json` via the correct code path so `get_user_settings()` returns a non-None value at request time.

## Step 4c — Install crewai[anthropic] in crewai container

```bash
docker exec crewai pip install -q "crewai[anthropic]==1.14.4"
```

Required to avoid `ImportError: Anthropic native provider not available`.

## Step 5 — Verify

```bash
# Both containers healthy?
docker ps

# CrewAI has key + can reach OpenHands?
docker exec crewai python -c "
import os, requests
print('crewai:', __import__('crewai').__version__)
print('key:', os.getenv('ANTHROPIC_API_KEY','')[:15] + '...')
r = requests.get('http://openhands:3000/health', timeout=5)
print('OpenHands health:', r.status_code, r.text)
"
```

## Step 6 — OpenHands Web UI

Open `http://localhost:3000` → Settings → LLM:
- Model: `claude-sonnet-4-5` (or your model)
- API Key: same key as `LLM_API_KEY`

---

## Integration Architecture

```
You → CrewAI (Planner / Coder / Reviewer agents)
              │
              │  HTTP REST — Docker internal network
              │  http://openhands:3000
              ▼
         OpenHands (sandboxed code execution)
         → writes files, runs tests, opens PRs
```

Both containers are on the same Docker network (`ai-agents_default`).
CrewAI calls OpenHands via the internal hostname `openhands` — no port-forwarding needed.

---

## OpenHands V1 REST API Pattern (self-hosted)

**No auth token needed for self-hosted** — `LocalhostCORSMiddleware` handles it.
Only needed for `app.all-hands.dev` Cloud.

```
POST /api/v1/app-conversations   → returns { id: "start_task_id" }
GET  /api/v1/app-conversations/start-tasks?ids=TASK_ID
     poll until status == "READY" → get app_conversation_id
GET  /api/v1/app-conversations?ids=CONVERSATION_ID
     poll until execution_status in {finished, error, stuck, waiting_for_confirmation}
```

⚠️ **V0 API (`/api/conversations`) was removed April 2026 — use V1 only.**

---

## CrewAI BaseTool Wrapper (openhands_tool.py)

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests, time

TERMINAL_STATES = {"finished", "error", "stuck", "waiting_for_confirmation"}

class OpenHandsTaskInput(BaseModel):
    task: str = Field(..., description="Natural language coding task.")
    repository: str = Field(default=None, description="Optional GitHub repo slug.")

class OpenHandsTool(BaseTool):
    name: str = "OpenHands Coding Agent"
    description: str = (
        "Delegates coding tasks to OpenHands — writes code, runs tests, "
        "fixes bugs, opens PRs. Returns final status."
    )
    args_schema: type[BaseModel] = OpenHandsTaskInput
    base_url: str = "http://openhands:3000"
    api_key: str = ""   # empty = self-hosted

    def _run(self, task: str, repository: str = None) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"initial_message": {"content": [{"type": "text", "text": task}]}}
        if repository:
            payload["selected_repository"] = repository

        resp = requests.post(f"{self.base_url}/api/v1/app-conversations",
                             headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        task_id = data.get("id")

        # Poll for READY
        conversation_id = None
        for _ in range(60):
            time.sleep(5)
            r = requests.get(f"{self.base_url}/api/v1/app-conversations/start-tasks",
                             headers=headers, params={"ids": task_id}, timeout=10)
            items = r.json().get("items", [r.json()])
            item = items[0] if items else {}
            if item.get("status") == "READY":
                conversation_id = item.get("app_conversation_id") or item.get("id")
                break
            elif item.get("status") == "ERROR":
                return f"❌ Start task failed: {item}"

        # Fallback: self-hosted may return conversation_id directly
        if not conversation_id:
            conversation_id = data.get("conversation_id") or data.get("app_conversation_id")
        if not conversation_id:
            return "❌ OpenHands never became READY (timeout)"

        # Poll for completion
        for _ in range(120):
            time.sleep(15)
            r = requests.get(f"{self.base_url}/api/v1/app-conversations",
                             headers=headers, params={"ids": conversation_id}, timeout=10)
            items = r.json().get("items", [r.json()])
            conv = items[0] if items else {}
            status = conv.get("execution_status", "")
            if status in TERMINAL_STATES:
                emoji = "✅" if status == "finished" else "⚠️"
                return f"{emoji} OpenHands: {status} | conversation: {conversation_id}"

        return f"⏱️ Timeout — check UI at {self.base_url} | conversation: {conversation_id}"
```

---

## Run an Example Crew

```bash
docker exec -it crewai python /workspace/crewai_openhands/main.py
# Input: Create a Python hello_world.py script
```

---

## End-to-End Readiness Check

Before claiming the stack works, run this verification:

```python
# docker exec crewai python -c "..."
import os, requests

# 1. Check CrewAI version + key
import crewai
print('crewai:', crewai.__version__)
key = os.getenv('ANTHROPIC_API_KEY', '')
print('key:', key[:15] + '...' if key else '❌ NOT SET')

# 2. Check OpenHands reachable from inside crewai container
r = requests.get('http://openhands:3000/health', timeout=5)
print('OpenHands /health:', r.status_code, r.text)
```

Key things to verify:
- `docker ps` shows **both containers healthy** (not just "Up")
- OpenHands `/health` returns `"OK"` from inside the crewai container
- `LLM_API_KEY` and `LLM_MODEL` are set in OpenHands env (`docker exec openhands env | grep LLM`)
- OpenHands Web UI at `http://localhost:3000` → Settings → LLM shows the key (set it there too — env var alone isn't enough for the UI flow)

---

## Running a Development Crew for a Project

**Rule: ALL software development tasks must go through CrewAI + OpenHands — never use `delegate_task` directly for coding work.**

### Standard 3-Agent Pattern (PM → Coder → Reviewer)

Write a crew script at `~/ai-agents/crewai_openhands/<project>_crew.py`, then:

```bash
# Copy into container and run in background
docker cp ~/ai-agents/crewai_openhands/<project>_crew.py crewai:/workspace/crewai_openhands/
docker exec crewai bash -c "cd /workspace && nohup python crewai_openhands/<project>_crew.py > /tmp/crew_<project>.log 2>&1 &"

# Monitor progress
docker exec crewai cat /tmp/crew_<project>.log | tail -60
```

### LLM Config for Agents

Use `llm=` string format — but **must install `crewai[anthropic]` extra** or you get:
`ImportError: Anthropic native provider not available`

```bash
docker exec crewai pip install -q "crewai[anthropic]==1.14.4"
```

Agent LLM string format:
```python
llm=f"anthropic/{os.getenv('LLM_MODEL', 'claude-sonnet-4-5').replace('anthropic/', '')}"
```

### Task Design Rules for OpenHands

Each task description sent to the Coder/Reviewer agent **must embed full context** because OpenHands runs in a sandbox that has no memory of previous calls:
- Absolute paths to project files
- How to activate the venv
- What Docker services are already running and on which ports
- Git remote URL and credential location
- Exact verification command to run after the change

Example task description snippet:
```
CRITICAL CONTEXT to include in every OpenHands task:
- Project root: ~/projects/myproject/
- Backend venv: cd ~/projects/myproject/backend && source venv/bin/activate
- Docker running: postgres on 5432, minio on 9000
- Git remote: https://github.com/DataXquad-HQ/myproject.git
- Credentials in ~/.git-credentials (no password prompt)
- Verify frontend: cd frontend && npm run build
```

### Monitoring with Hermes Cron

For long-running crews, set a cron job to monitor progress every 10 min:
```python
cronjob(action='create', schedule='10m', repeat=6, prompt="""
docker exec crewai cat /tmp/crew_<project>.log | tail -80
Report: which agent is active, whether OpenHands was called, any errors, final result if done.
""")
```

---

## OpenHands Settings Fix (v1.7.0)

**Critical**: Settings must be written to `/.openhands/settings.json` (NOT `~/.openhands/` or `/root/.openhands/`).
The server reads from `shared.config.file_store_path` = `/.openhands` at request time.

**Correct nested schema** (flat `llm_model` no longer works):
```python
docker exec openhands python3 -c "
import json, os
from openhands.core.config.app_config import AppConfig
from openhands.storage.files import FileStore
from openhands.server.settings import Settings, AgentSettings, LLMSettings

settings = Settings(
    agent_settings=AgentSettings(
        llm=LLMSettings(
            model='anthropic/claude-sonnet-4-5',
            api_key=os.environ.get('LLM_API_KEY', 'sk-ant-...'),
        )
    )
)
store = FileStore('/.openhands')
store.write('settings.json', settings.model_dump_json())
print('done')
"
```

**Port conflicts**: Prune old sandbox containers before starting tasks:
```bash
docker ps -a --filter "name=oh-agent-server" -q | xargs docker rm -f
```

**CrewAI crew max_iter**: Set `max_iter=8` for Tech Lead / QA agents, `max_iter=5` for PM Reporter. Too low (e.g. 3) causes empty LLM response crash.
For **API-writing agents** (agents that call external APIs like Google Sheets to write data row by row), `max_iter` must be ≥ 50. A writer agent building a 27-row monthly P&L will make 27+ tool calls if not explicitly told to batch — it will exhaust `max_iter=15` mid-tab and the crew "completes" with partial data. Fix: `max_iter=50` + BATCH RULE in task description (see pitfall below).

## Pitfalls

- **`docker.all-hands.dev` registry unreachable** — always use `ghcr.io/openhands/openhands:VERSION` instead
- **AutoGen → CrewAI swap**: if you previously deployed AutoGen Studio, stop/remove its container and delete the `autogen_data` volume before adding CrewAI to the same compose file. They share the `python:3.11-slim` base image — Docker will reuse the layer cache.
- **OpenHands shows `unhealthy` after 8+ hours** — the healthcheck wget probe can fail after long uptime even though the service is responding. Check with `curl http://localhost:3000/health` directly; if it returns `"OK"` the service is fine. The unhealthy status is a probe timing issue, not a real failure.
- **Self-hosted OpenHands needs no Bearer token** — leave `api_key=""` in the tool; auth only needed for Cloud (`app.all-hands.dev`)
- **Two-step polling required** — start-task → conversation_id → execution_status; you cannot skip the first poll
- **`waiting_for_confirmation` is blocking** — the agent is waiting for human input via UI; add a timeout in the tool
- **`selected_repository` causes ERROR** — passing `selected_repository` to `/api/v1/app-conversations` makes OpenHands try to clone from GitHub. For local file tasks, **never set `selected_repository`**. Tasks should use absolute local paths (e.g. `~/projects/gx-geoshare/`).
- **`WAITING_FOR_SANDBOX` must be treated as "keep polling"** — not as an error. The poll loop must handle `WAITING_FOR_SANDBOX`, `WORKING`, `PENDING`, and `""` as intermediate states, only stopping on `READY` or `ERROR`.
- **POST timeout must be 120s, not 30s** — OpenHands spins up a sandbox container per conversation; the initial POST to `/api/v1/app-conversations` can take 60-90s to respond from inside the crewai container. Set `timeout=120` on the POST call.
- **`assert settings is not None` — write settings.json to `/.openhands/` NOT `~/.openhands/`** — In OpenHands 1.7.0 self-hosted, `shared.config.file_store_path` is `/.openhands` (absolute root path), NOT `~/.openhands`. The server reads `settings.json` from `/.openhands/settings.json`. Writing to `/root/.openhands/settings.json` does NOT work even though expanduser resolves there. The fix: write a correctly-structured settings.json to `/.openhands/settings.json`. Use the Python API inside the container to get the correct nested format (NOT flat `llm_model`/`llm_api_key` — it changed to `agent_settings.llm.model`/`agent_settings.llm.api_key`):
```bash
ANTHROPIC_KEY=$(grep "^ANTHROPIC_API_KEY=" ~/.hermes/.env | cut -d'=' -f2-)
docker exec openhands python3 -c "
import json, os, asyncio
from openhands.app_server.settings.settings_models import Settings
key = '$ANTHROPIC_KEY'
data = {'language': 'en', 'v1_enabled': True, 'agent_settings': {'schema_version': 1, 'agent_kind': 'openhands', 'agent': 'CodeActAgent', 'llm': {'model': 'anthropic/claude-sonnet-4-5', 'api_key': key}}}
s = Settings(**data)
json_str = s.model_dump_json(context={'expose_secrets': True, 'persist_settings': True})
os.makedirs('/.openhands', exist_ok=True)
open('/.openhands/settings.json', 'w').write(json_str)
print('Done')
"
```
- **Also clear old sandbox containers before testing** — paused `oh-agent-server-*` containers accumulate and exhaust port ranges, causing `Bind for 0.0.0.0:PORT failed: port is already allocated`. Run: `docker ps -a --filter "name=oh-agent-server" --format "{{.Names}}" | xargs -r docker rm -f`
- **`crewai[anthropic]` extra required** — base `crewai==1.14.4` does not include the Anthropic native provider. Must install `crewai[anthropic]==1.14.4` or the agent instantiation fails with `ImportError: Anthropic native provider not available`.
- **OpenHands needs `/var/run/docker.sock`** — it spawns its own sandbox containers; missing this volume breaks execution
- **Env var names differ between tools**:
  - CrewAI reads `ANTHROPIC_API_KEY` (standard)
  - OpenHands reads `LLM_API_KEY` (generic) + `LLM_MODEL`
  - Set both in `.env`
- **`version:` key in compose** is obsolete — Docker Compose v2+ warns on it; remove or ignore
- **pip install takes ~90s** on first CrewAI startup — healthcheck `start_period: 120s` is required
- **Port conflicts when Dify is also on the VM**: Dify's nginx takes port 80/443 and its own internal port 3000 may conflict with OpenHands. Always map OpenHands to a distinct host port (`3000:3000`) and verify no other service is on it before deploying.
- **Gunicorn on port 5001 is not the same as Dify's user-facing URL**: Dify's API (gunicorn) binds `0.0.0.0:5001` internally but is only reachable via nginx reverse proxy on 80/443 — not directly from non-root processes. `curl http://127.0.0.1:5001/...` requires root/sudo. Use the nginx-proxied URL instead.
- **`DIFY_BASE_URL=http://localhost:3000` breaks silently after adding OpenHands**: OpenHands takes port 3000. If `.env` has `DIFY_BASE_URL=http://localhost:3000` from a previous Dify self-hosted install, all Dify API calls will hit OpenHands and return cryptic errors. Update `DIFY_BASE_URL` to the real Dify URL (e.g. `https://dataxquad-dify.zeabur.app`) as part of adding OpenHands to the stack.
- **`crewai[anthropic]` extra required** — plain `crewai[tools]` install causes `ImportError: Anthropic native provider not available` at agent instantiation. Always install `crewai[anthropic]==1.14.4` before running a crew.
- **f-string `{var}` in task descriptions causes `NameError` at import** — Task `description=f\"\"\"...\"\"\"` strings are Python f-strings. Any `{x}` notation used as a documentation placeholder (e.g. Excel formula patterns like `=SUM(A{r}:B{r})`, row references like `=Tab!C{row}`) is evaluated as a Python variable at module load time and raises `NameError: name 'r' is not defined`. Fix: use `[r]` or `<row>` notation for documentation placeholders, OR escape as `{{r}}`. Scan before running: `grep -n '{[a-z]}' crew_script.py | grep -v '#'`.

- **`claude-sonnet-4-6` does NOT work with CrewAI 1.14.4** — causes `anthropic.BadRequestError: 400 - This model does not support assistant message prefill. The conversation must end with a user message.` CrewAI's native Anthropic provider uses assistant prefill internally. Use `claude-sonnet-4-5` (confirmed working). Always test model compatibility with a simple crew before building a large one.

- **Multi-field Pydantic tool args fail silently with Anthropic native tools** — When a `BaseTool` has an `args_schema` with multiple required fields (e.g. `sheet_id`, `tab_name`, `data`), the Anthropic native tool-calling layer sometimes passes an empty dict `{}` — causing `Field required` validation errors that loop indefinitely. **Fix: use a single `input: str = Field(...)` that accepts a JSON string, and parse it inside `_run()`**. This is the most reliable pattern for CrewAI + Anthropic:
  ```python
  class SingleInput(BaseModel):
      input: str = Field(..., description="JSON string with all parameters")
  
  class MyTool(BaseTool):
      args_schema: type[BaseModel] = SingleInput
      def _run(self, input: str) -> str:
          p = json.loads(input)
          # use p["sheet_id"], p["range"], etc.
  ```

- **Pre-flight resource creation before crew kickoff** — For crews that need to create external resources (Google Sheets, databases, etc.) before agents can write to them, create the resource OUTSIDE the crew in a pre-flight step and inject the IDs into task descriptions. Avoids tool-call loops where the creation tool fails and blocks Task 1 from completing. Pattern:
  ```python
  # Pre-flight: create sheet, get ID
  sheet_info = create_spreadsheet_and_tabs(title, tab_names)
  json.dump(sheet_info, open("/tmp/sheet_info.json", "w"))
  # Inside container: agents read /tmp/sheet_info.json
  # Task descriptions embed: f"Sheet ID: {sheet_info['sheet_id']}"
  ```

- **`max_iter` too low causes `ValueError: Invalid response from LLM call - None or empty.`** — CrewAI agents that call OpenHands (which can take 10-30 min) need enough iterations. Default `max_iter=3` is always too low. Use `max_iter=8` for agents with tools, `max_iter=5` for synthesis-only agents. If you see the ValueError in the log, increase `max_iter` and restart.
- **`deliver=origin` fails in cron jobs** — Cron jobs run in an isolated session with no chat context, so `deliver=origin` cannot resolve the target and logs `no delivery target resolved`. Always pass an explicit deliver target when creating monitor crons: `deliver='feishu:CHAT_ID:THREAD_ID'` or `deliver='telegram:CHAT_ID:THREAD_ID'`. Never use `deliver=origin` for cron jobs.
- **`ps` not available in crewai container** — use `cat /proc/*/cmdline 2>/dev/null | tr '\0' ' ' | grep <script>` to check if a process is running.
- **Write crew scripts to host first, then `docker cp`** — the `/workspace/crewai_openhands/` directory in the container maps to `~/ai-agents/crewai_openhands/` on the host via volume mount, so `docker cp` or writing to the host path both work.
- **GitHub push from inside OpenHands** — credentials must be in `~/.git-credentials` on the host (not inside the container). Tell OpenHands the git remote is `https://github.com/DataXquad-HQ/<repo>.git` and that credentials are stored; it will use the host's git credential helper automatically when the project dir is mounted.
- **End-to-end pipeline readiness ≠ code readiness**: All code can pass syntax checks and unit tests while the full pipeline is still broken at the infrastructure level. Run the readiness check script against live services (Lark auth, Dify reachability, lark_writer running, test video present) before claiming the flow works end-to-end.

- **Crew may "complete" with partial output when Writer agent runs out of iterations** — CrewAI marks the crew as done even if the Writer agent exhausted `max_iter` mid-task (e.g. wrote P&L headers but not EBITDA/cash columns). The final output message will say something like "I have completed X, let me now do Y" — that means it ran out of iterations. **Fix: (1) increase Writer `max_iter` to 15+, (2) split large write tasks into smaller ones (one tab per task), (3) always verify via direct API read-back after crew completes, not just from the crew's own output message.**

- **`docker exec -d` is more reliable than `nohup ... &` for background crew launch** — Use `docker exec -d -e KEY=val container bash -c 'python script.py > /tmp/log 2>&1'` rather than a non-detached exec with `nohup`. The `-d` flag detaches cleanly and env vars inject correctly.

- **Crew cannot create Google Sheets reliably — always pre-flight** — Confirmed in practice: any tool that requires external resource creation (Google Sheets, DB, etc.) as the first agent action is fragile. The Architect agent got stuck in a 10-iteration loop failing to call `create_spreadsheet` because Anthropic native tools dropped the `title` field. **Always create the sheet, add tabs, and write the ID to `/tmp/sheet_info.json` BEFORE starting the crew. Agents only read + write data, never create resources.**

- **Google auth inside crewai container** — The `gws_bridge.py` token refresh works inside the container if: (1) `gws_bridge.py` and `google_token.json` are copied to `/workspace/` via `docker cp`, (2) `HERMES_HOME=/workspace` and `PYTHONPATH=/workspace` are set as env vars, (3) `google-auth` pip package is installed in the container. Token refresh is then a simple subprocess call to `python3 -c "from gws_bridge import get_valid_token; print(get_valid_token())"`.

- **Verified financial model numbers should be hardcoded, not re-derived in crew tasks** — When a verified source-of-truth dataset exists (e.g. numpy-financial pre-computed monthly EBITDA), hardcode those exact values into task descriptions or as Python lists in the crew script. Attempts to re-derive from component parts inside tasks will produce subtly wrong numbers (e.g. missing BD commission, wrong COGS formula). Lock the numbers; let agents focus on writing them correctly.

- **Writer agents MUST batch all rows in ONE API call — add explicit BATCH RULE to every write task** — Without explicit instruction, writer agents default to writing one row at a time (126 calls observed for a 27-row sheet). This burns `max_iter` in the first tab and leaves all subsequent tabs empty. The crew "completes" with a final message like "I have completed X, let me now do Y" — that means it ran out of iterations. **Fix: embed this at the top of every write task description:**
  ```
  ⚠️ CRITICAL BATCH RULE:
  You have max_iter=50 total. Call write_values ONCE per tab with ALL rows.
  Build the complete 2D array in your reasoning first, then make ONE call.
  NEVER call write_values more than twice per tab (once write, once verify).
  Input format: {"ranges": [{"range": "Tab!A1", "values": [[r1c1,r1c2,...],[r2c1,...],...]}]}
  ```
  Also set writer agent backstory to explicitly state this constraint.

- **Crew is the wrong tool for writing structured spreadsheets with known data — use direct API calls instead** — Confirmed across multiple attempts: when the data is already known (verified numbers, fixed schema), writing it directly via the Google Sheets REST API from Hermes/execute_code is faster, more reliable, and produces correct output. Crew agents add value for tasks requiring reasoning (designing formulas, auditing, generating content) — not mechanical data writes. Pattern: use crew for design + spec, then implement directly via API. Reserve crew for tasks where the agent needs to *figure out* what to write, not when you already know exactly what every cell should contain.

- **`delegate_task` also fails for long API-writing tasks** — Even the Hermes `delegate_task` subagent pattern hits the same wall: the subagent times out at 450s waiting for model response when asked to build a complex spreadsheet. The execute_code sandbox (50-call limit, 5-min timeout) is the right tool for bulk data writes — it runs Python directly without LLM round-trips per operation.
