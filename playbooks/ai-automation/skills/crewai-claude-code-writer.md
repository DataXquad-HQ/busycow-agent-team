---
name: crewai-claude-code-writer
description: >
  Use when building a CrewAI crew that needs to write files, build Google Sheets,
  generate code, or execute multi-step build tasks. Wires Claude Code CLI as the
  Sheet Writer / Builder agent inside the crewai Docker container. Solves the
  max_iter exhaustion problem — instead of 50+ tiny tool calls, one Claude Code
  task = one complete build script = done. Required pattern for any CrewAI crew
  that builds Google Sheets or generates substantial code artifacts.
version: 1.0.0
author: BusyCow/Hermes
metadata:
  hermes:
    tags: [CrewAI, Claude-Code, Google-Sheets, agent, builder, tool]
---

# CrewAI + Claude Code CLI — Sheet Writer Pattern

## When NOT to Use This Skill

**If your data is fully known at build time (static arrays, verified numbers) — skip the crew entirely.**
Pre-write Python build scripts on the host, copy to container, run directly:
```bash
docker cp ./scripts/. crewai:/workspace/scripts/
docker exec -e HERMES_HOME=/workspace crewai python3 /workspace/scripts/build_cf.py
```
This runs in **8 seconds** with zero agent overhead and zero token cost beyond Hermes itself.

**Rule of thumb:**
- Data is known → pre-write scripts, run directly, skip CrewAI entirely
- Need LLM to reason about structure/formulas → use CrewAI + ClaudeCodeTool
- Never use CrewAI just as an orchestration layer when you already know what to write

**Token cost reality check (May 2026 [your product] session):**
- A looping crew run (14 task starts, max_iter exhaustion) costs ~$5–10 per session
- Anthropic has NO programmatic usage API — check costs at console.anthropic.com → Usage tab
- Each CrewAI call with 8k context + conversation history ≈ 20k input + 4k output tokens
- A well-behaved run (1 call per tab, ~10 tabs) costs < $1

## Why This Exists

CrewAI agents calling write APIs row-by-row exhaust `max_iter` before finishing.
Root cause analysis from [your product] Financial Forecast build (May 2026):
- Writer called `write_values` 126 times (one row at a time) → hit max_iter=15 → stuck
- Fix: Claude Code CLI receives a full build task, writes a Python script, executes it → ONE tool call = entire sheet tab

## Architecture

```
CrewAI Crew
  ├── CFO Agent (claude-sonnet-4-5)       → validates numbers, produces spec
  ├── Model Architect (claude-sonnet-4-5) → designs structure, tab layout
  ├── Claude Code Writer (ClaudeCodeTool) → receives complete spec, writes
  │     └── Runs: claude -p "build this sheet..." inside crewai container
  │           └── Claude Code writes Python → executes it → sheet is built
  └── Auditor Agent (claude-sonnet-4-5)   → reads back cells, PASS/FAIL report
```

## Prerequisites

### Install Claude Code inside crewai container (one-time)

```bash
# Verify node + npm available
docker exec crewai node --version   # need v18+
docker exec crewai npm --version

# If node/npm missing, install first:
docker exec crewai apt-get install -y nodejs npm

# Install Claude Code CLI
docker exec -e ANTHROPIC_API_KEY=$(grep '^ANTHROPIC_API_KEY=' ~/.hermes/.env | cut -d'=' -f2-) \
  crewai npm install -g @anthropic-ai/claude-code

# Verify
docker exec -e ANTHROPIC_API_KEY=... crewai claude --version
# Expected: 2.1.x (Claude Code)

# Smoke test
docker exec -e ANTHROPIC_API_KEY=... crewai bash -c \
  'claude -p "print only: WORKS" 2>&1 | tail -1'
# Expected: WORKS
```

## ClaudeCodeTool — Drop-in CrewAI Tool

```python
import os, subprocess, json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HERMES_HOME   = "/workspace"

class ClaudeCodeInput(BaseModel):
    task: str = Field(..., description=(
        "Complete self-contained task for Claude Code. Must include: "
        "(1) exact Python script to write, "
        "(2) all data/values inline (no external file reads), "
        "(3) expected output to verify success. "
        "Claude Code will write the script to /tmp/ and execute it."
    ))

class ClaudeCodeTool(BaseTool):
    name: str = "claude_code_builder"
    description: str = (
        "Delegates a complete build task to Claude Code CLI. "
        "Use this for ANY task that requires writing more than 10 rows to Google Sheets, "
        "generating a Python script, or executing a multi-step build. "
        "Pass the COMPLETE specification as a single task string — Claude Code will "
        "write and execute a Python script to completion. "
        "ONE call = entire tab or entire file. Never call this multiple times for the same tab."
    )
    args_schema: type[BaseModel] = ClaudeCodeInput

    def _run(self, task: str) -> str:
        # Escape single quotes in task for shell safety
        safe_task = task.replace("'", "'\"'\"'")
        
        cmd = (
            f"docker exec "
            f"-e ANTHROPIC_API_KEY={ANTHROPIC_KEY} "
            f"-e HERMES_HOME={HERMES_HOME} "
            f"-e PYTHONPATH={HERMES_HOME} "
            f"-w /workspace "
            f"crewai bash -c "
            f"'claude --dangerously-skip-permissions -p \"{safe_task}\" 2>&1'"
        )
        
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=300
            )
            output = result.stdout.strip()
            if result.returncode != 0:
                return f"ERROR (exit {result.returncode}): {result.stderr[:500]}"
            return output[-2000:] if len(output) > 2000 else output  # return tail
        except subprocess.TimeoutExpired:
            return "TIMEOUT: Claude Code took >5 minutes. Check if task is too large — split into smaller tabs."
        except Exception as e:
            return f"ERROR: {e}"
```

## Agent Definition

```python
from crewai import Agent

writer_agent = Agent(
    role="Sheet Builder & Code Executor",
    goal=(
        "Receive a complete build specification and delegate it entirely to "
        "Claude Code CLI via the claude_code_builder tool. ONE tool call per tab. "
        "Never write data manually — always use claude_code_builder."
    ),
    backstory=(
        "You are a senior engineer who delegates all build work to Claude Code. "
        "Your job is to compose a clear, complete task specification and pass it "
        "to Claude Code in ONE call. Claude Code handles all execution. "
        "You NEVER call write_values directly. You NEVER loop row by row."
    ),
    verbose=True,
    allow_delegation=False,
    llm="anthropic/claude-sonnet-4-5",
    max_iter=8,   # Only needs a few iterations: 1 per tab + verification
    tools=[claude_code_tool],
)
```

## Task Specification Template

The task string passed to ClaudeCodeTool must be fully self-contained:

```python
CLAUDE_CODE_TASK_TEMPLATE = """
You are Claude Code running inside a Python environment.
Write and execute a Python script that builds one tab of a Google Sheet.

CONTEXT:
- Google token at: /workspace/google_token.json  
- gws_bridge.py at: /workspace/gws_bridge.py
- Sheet ID: {sheet_id}
- Tab to build: {tab_name}

YOUR TASK:
Write /tmp/build_{tab_safe}.py with this exact content, then execute it:

```python
import sys, requests, json, subprocess
sys.path.insert(0, '/workspace')
from gws_bridge import get_valid_token

SID = "{sheet_id}"
token = get_valid_token()
H = {{"Authorization": f"Bearer {{token}}", "Content-Type": "application/json"}}

data = {values_2d_array}

r = requests.post(
    f"https://sheets.googleapis.com/v4/spreadsheets/{{SID}}/values:batchUpdate",
    headers=H,
    json={{"valueInputOption": "USER_ENTERED", "data": [{{"range": "'{tab_name}'!A1", "values": data}}]}},
    timeout=30
)
print("Written:", r.json().get("totalUpdatedCells"), "cells")

# Verify key cells
v = requests.get(
    f"https://sheets.googleapis.com/v4/spreadsheets/{{SID}}/values/'{tab_name}'!A1:B3",
    headers=H, timeout=10
).json().get("values", [])
print("Verify A1:", v[0][0] if v and v[0] else "EMPTY")
```

Execute: python3 /tmp/build_{tab_safe}.py
Report the output including "Written: X cells" and the verify result.
"""
```

## Complete Crew Pattern

```python
from crewai import Crew, Process

crew = Crew(
    agents=[cfo_agent, architect_agent, writer_agent, auditor_agent],
    tasks=[
        task_spec,           # CFO: produces complete build spec with all data arrays
        task_architecture,   # Architect: creates spreadsheet + tabs, returns sheet_id
        task_build_cf,       # Writer (Claude Code): builds CF tab in 1 call
        task_build_pl,       # Writer (Claude Code): builds P&L tab in 1 call
        task_build_rest,     # Writer (Claude Code): builds remaining tabs
        task_audit,          # Auditor: reads back key cells, PASS/FAIL
    ],
    process=Process.sequential,
    verbose=True,
)
```

## Task Design Rules for Claude Code Writer

1. **One tab per task** — `task_build_cf`, `task_build_pl`, etc. Never bundle multiple tabs in one task.
2. **All data inline** — embed the complete 2D values array directly in the task string. No file reads.
3. **Include verification** — always ask Claude Code to read back 3 key cells after writing.
4. **Timeout 300s** — Claude Code needs up to 5 min for large tabs. Set `timeout=300` in subprocess.run.
5. **Use `--dangerously-skip-permissions`** — required for non-interactive execution in Docker.

## Key Differences vs Direct Tool Calling

| Approach | Iterations Used | Failure Mode | Result |
|----------|----------------|--------------|--------|
| Old: write_values row-by-row | 126 calls → max_iter hit | Stuck mid-tab | Incomplete |
| New: ClaudeCodeTool | 1 call per tab | None (Claude Code handles errors internally) | Complete |

## Docker Container Requirements

```
crewai container needs:
  ✅ python3 (already in python:3.11-slim)
  ✅ requests (pip install requests)
  ✅ nodejs v18+ (apt-get install nodejs)
  ✅ npm (apt-get install npm)
  ✅ claude CLI (npm install -g @anthropic-ai/claude-code)
  ✅ ANTHROPIC_API_KEY env var
  ✅ /workspace/gws_bridge.py (for Google auth)
  ✅ /workspace/google_token.json (OAuth token)
```

Verify all at once:
```bash
docker exec -e ANTHROPIC_API_KEY=... crewai bash -c '
  python3 --version &&
  python3 -c "import requests; print(requests.__version__)" &&
  node --version &&
  npm --version &&
  claude --version &&
  ls /workspace/gws_bridge.py /workspace/google_token.json
'
```

## Killing a Runaway Crew

If the crew loops or needs to be stopped:
```bash
# On host — kill the crew main.py process
pkill -f "main.py" && pkill -f "financial_crew"

# Inside container — kill all claude processes
docker exec crewai pkill -f "claude" 2>/dev/null || true
docker exec crewai pkill -f "python.*main" 2>/dev/null || true

# Nuclear option — restart the container (loses in-progress work)
docker restart crewai

# Verify clean
docker exec crewai bash -c "ps aux | grep -E 'claude|crew|main' | grep -v grep"
```

Log files land in `/tmp/crew_*.log` inside the container. Check sizes to see how far it got:
```bash
docker exec crewai bash -c "ls -lh /tmp/crew*.log; grep -c 'Task Started' /tmp/crew*.log"
```

## Pitfalls

1. **`--dangerously-skip-permissions` is required** — without it, Claude Code prompts for confirmation and hangs
2. **Shell quoting**: single quotes in the task string break the bash -c command. Use `.replace("'", "'\"'\"'")` to escape, or write task to a temp file and pass as `claude --dangerously-skip-permissions -p "$(cat /tmp/task.txt)"`
3. **Better: write task to file** — avoids all quoting issues:
   ```python
   with open('/tmp/cc_task.txt', 'w') as f: f.write(task)
   # then: docker exec crewai claude --dangerously-skip-permissions -p "$(cat /tmp/cc_task.txt)"
   ```
4. **Timeout 300s minimum** — Claude Code needs up to 5 min for large tabs. Set `timeout=300` in subprocess.run.
5. **Output truncation** — Claude Code output can be long. Read last 2000 chars for the result.
6. **Token refresh** — `gws_bridge.get_valid_token()` refreshes automatically. No manual token management needed.
7. **Container persistence** — `npm install -g` inside container is lost on restart unless added to docker-compose. Add to requirements or use a custom image.
8. **crewai[anthropic] still required** — base CrewAI for the CFO/Auditor agents still needs `pip install crewai[anthropic]`.
9. **max_iter=8 for writer** — with Claude Code, writer only needs: 1 receive spec + 1 call per tab + 1 verify. 8 is enough for 4 tabs.
10. **Claude binary path differs by context** — on the host it's at `~/node/bin/claude`; inside the crewai container it's at `/usr/local/bin/claude`. Never use bare `claude` — always resolve the full path:
    ```python
    claude_bin = "~/node/bin/claude"
    if not os.path.exists(claude_bin):
        claude_bin = "/usr/local/bin/claude"
    ```
11. **`--dangerously-skip-permissions` is BLOCKED when running as root** — container runs as root by default. Drop this flag entirely; `claude -p` works fine as root without it.
11. **Write task file INSIDE container via stdin pipe** — never write to host `/tmp/` and reference it from container. Use `docker exec -i crewai bash -c "cat > /tmp/task.txt"` with `input=task` to pipe the task string into the container first, then reference `/tmp/task.txt` in the claude command.
13. **CRITICAL: Run crew on HOST or fix tool to not use docker exec** — If crew script runs INSIDE the crewai container, `subprocess(["docker", "exec", "crewai", ...])` fails with `[Errno 2] No such file: 'docker'` because docker CLI is not installed inside the container. Two valid patterns:
    - **Pattern A (preferred)**: Run crew inside container. ClaudeCodeTool calls `claude` directly (no docker exec). Since the crew IS inside the container, claude is already at `/usr/local/bin/claude`.
    - **Pattern B**: Run crew on host. ClaudeCodeTool uses `docker exec crewai claude ...`. Requires crewai Python package installed on host.
    - Pattern A is simpler — just write task to `/tmp/file.txt` and call `subprocess.run(["bash", "-c", 'claude -p "$(cat /tmp/file.txt)" 2>&1'])` directly.

12. **Verified working pattern (May 2026)**:
    ```python
    write_cmd = ["docker", "exec", "-i", "crewai", "bash", "-c", "cat > /tmp/cc_task.txt"]
    subprocess.run(write_cmd, input=task, text=True, timeout=10)
    cmd = ["docker", "exec", "-e", f"ANTHROPIC_API_KEY={KEY}", "crewai",
           "bash", "-c", 'claude -p "$(cat /tmp/cc_task.txt)" 2>&1']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    ```
