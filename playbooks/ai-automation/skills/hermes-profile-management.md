---
name: hermes-profile-management
description: Manage Hermes Agent profiles — inspect, move cron jobs between profiles, strip gateway config, and reset auth/state. Use when reorganizing profiles, migrating cron jobs, or doing a clean gateway reset.
tags: [hermes, profiles, cron, gateway, config]
---

# Hermes Profile Management

## Profile Layout

```
~/.hermes/                        # default profile
~/.hermes/profiles/<name>/        # named profiles
```

Each profile has: config.yaml, cron/, skills/, memories/, sessions/, auth.json, state.db, gateway.pid, etc.

## Reading jobs.json (Permission Gotcha)

jobs.json is owned by the_owner and not world-readable. Direct `cat` fails as root.

```bash
# Copy first, then read
sudo -u the_owner cat ~/.hermes/cron/jobs.json > /tmp/jobs_backup.json

# Then parse with python3
python3 << 'EOF'
import json
with open('/tmp/jobs_backup.json') as f:
    data = json.load(f)
jobs = data.get('jobs', [])   # NOTE: top-level key is "jobs", not a list
# Internal key is "id" (not "job_id" — that's what the cronjob tool exposes)
for j in jobs:
    print(j['id'], j['name'])
EOF
```

## Moving Cron Jobs Between Profiles

1. Read full job data from source profile's jobs.json (use sudo -u trick above)
2. Filter target jobs by `id`
3. Write to destination profile's cron/jobs.json as `{"jobs": [...]}`
4. Remove from source using `cronjob(action='remove', job_id=...)`

```python
import json

with open('/tmp/jobs_backup.json') as f:
    data = json.load(f)

target_jobs = [j for j in data['jobs'] if j['id'] in ['abc123', 'def456']]

with open('~/.hermes/profiles/busycow/cron/jobs.json', 'w') as f:
    json.dump({'jobs': target_jobs}, f, ensure_ascii=False, indent=2)
```

Then remove from default via the tool:
```python
cronjob(action='remove', job_id='abc123')
```

## Stripping Gateway Config (Full Reset)

### 1. Kill gateway processes
```bash
ps aux | grep -E "hermes|gateway" | grep -v grep
# Kill PIDs for gateway run processes (not the current CLI session or gbrain)
kill <pid1> <pid2> ...
```

### 2. Delete gateway state files
```bash
for dir in ~/.hermes ~/.hermes/profiles/aquaoptima ~/.hermes/profiles/busycow ~/.hermes/profiles/geokernel; do
  rm -fv "$dir/gateway.pid" "$dir/gateway.log" "$dir/gateway_state.json" \
         "$dir/channel_directory.json" "$dir/feishu_seen_message_ids.json" \
         "$dir/interrupt_debug.log"
  rm -rfv "$dir/pairing"
done
```

### 3. Delete auth + state DB
```bash
for dir in ~/.hermes ~/.hermes/profiles/aquaoptima ~/.hermes/profiles/geokernel; do
  rm -fv "$dir/auth.json" "$dir/auth.lock" \
         "$dir/state.db" "$dir/state.db-shm" "$dir/state.db-wal"
done
```

### 4. Strip platform config from config.yaml files

```python
import re, os

configs = [
    '~/.hermes/config.yaml',
    '~/.hermes/profiles/aquaoptima/config.yaml',
    '~/.hermes/profiles/busycow/config.yaml',
    '~/.hermes/profiles/geokernel/config.yaml',
]

platform_sections = ['telegram', 'feishu', 'slack', 'discord', 'signal', 'mattermost', 'whatsapp', 'qqbot']
gateway_keys = ['TELEGRAM_HOME_CHANNEL', 'GATEWAY_ALLOW_ALL_USERS']

for path in configs:
    with open(path) as f:
        content = f.read()
    original = content

    # Remove platform sections (multi-line blocks)
    for s in platform_sections:
        content = re.sub(rf'^{s}:\n(?:  [^\n]*\n)*', '', content, flags=re.MULTILINE)
        content = re.sub(rf'^{s}: \{{\}}\n', '', content, flags=re.MULTILINE)

    # Remove top-level gateway keys
    for key in gateway_keys:
        content = re.sub(rf'^{key}:.*\n', '', content, flags=re.MULTILINE)

    # Remove mis-placed flush_memories in mcp_servers
    content = re.sub(
        r'  flush_memories:\n    provider: auto\n    model: \'\'\n    base_url: \'\'\n    api_key: \'\'\n    timeout: 30\n',
        '', content
    )

    # Fix platform_toolsets — stripping leaves it empty, restore cli-only
    content = re.sub(
        r'^platform_toolsets:\s*\n(?!  \S)',
        'platform_toolsets:\n  cli:\n  - hermes-cli\n',
        content, flags=re.MULTILINE
    )

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f"CLEANED: {path}")
```

## Finding Lark/Feishu App IDs per Profile

Each profile's Lark Bot identity is stored in its `.env` file:

```bash
grep FEISHU_APP_ID ~/.hermes/.env
grep FEISHU_APP_ID ~/.hermes/profiles/busycow/.env
grep FEISHU_APP_ID ~/.hermes/profiles/aquaoptima/.env
grep FEISHU_APP_ID ~/.hermes/profiles/geokernel/.env
```

config.yaml does NOT contain feishu config — it's all in `.env`.
Connected chats are in `channel_directory.json` under `platforms.feishu`.
Approved users are in `pairing/feishu-approved.json`.

## Rescheduling Cron Jobs in Named Profiles

The `cronjob` tool only operates on the **default profile's** jobs.json.
To update schedules in a named profile (busycow, aquaoptima, etc.), edit the JSON directly:

```python
import json

path = '~/.hermes/profiles/busycow/cron/jobs.json'
with open(path) as f:
    data = json.load(f)

# Map job id → new schedule
changes = {
    '44233711aa33': {'expr': '0 19 * * *',   'display': '03:00 TWN daily'},
    '8753f489f389': {'expr': '0 20 * * 6#1', 'display': '04:00 TWN first Saturday'},
}

for job in data['jobs']:
    if job['id'] in changes:
        job['schedule']['expr'] = changes[job['id']]['expr']
        job['schedule']['display'] = changes[job['id']]['display']

with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

For the **default profile**, use the `cronjob` tool directly:
```python
cronjob(action='update', job_id='1da29709b48b', schedule='0 18 * * *')
```

## Night-Shift Scheduling Strategy (Hunter's Preference)

Hunter often works late into the night. LLM-heavy cron jobs should run in the **02:00–06:00 TWN window** (UTC 18:00–22:00) — not 22:00–23:00 TWN which is still active work time.

**Rule of thumb:**
- 🟢 Keep at working hours: CRM morning reports (09:00), human-facing reminders
- 🌙 Move to 02:00–06:00 TWN: content generation, blog writing, GBrain ingest, intelligence gathering
- Stagger jobs 30 min apart to avoid resource contention

**UTC equivalents for TWN 02:00–06:00:**

| TWN | UTC cron | Use for |
|-----|---------|---------|
| 02:00 | `0 18 * * *` | Quick ingest jobs (StandupLog, Tasks) |
| 02:30 | `30 18 * * *` | Second quick ingest (stagger from above) |
| 03:00 | `0 19 * * *` | Daily content/intelligence scan |
| 04:00 | `0 20 * * *` | Monthly heavy jobs (stakeholder intel) |
| 05:00 | `0 21 * * *` | Blog generation, weekly synthesis |

**Monthly first-Saturday pattern** (for heavy monthly jobs — runs over weekend, report ready Monday morning):
```
0 20 * * 6#1   # 04:00 TWN first Saturday of month
```

## Moving Cron Jobs: NEVER use `cp` to overwrite jobs.json

`cp source/jobs.json ~/.hermes/cron/jobs.json` **overwrites and destroys** existing default jobs.
Always merge instead:

```python
import json

# Load destination (default profile)
with open('~/.hermes/cron/jobs.json') as f:
    dest = json.load(f)

# Load source (busycow profile)
with open('~/.hermes/profiles/busycow/cron/jobs.json') as f:
    src = json.load(f)

# Merge: add source jobs that don't already exist in destination
existing_ids = {j['id'] for j in dest['jobs']}
for job in src['jobs']:
    if job['id'] not in existing_ids:
        dest['jobs'].append(job)

with open('~/.hermes/cron/jobs.json', 'w') as f:
    json.dump(dest, f, ensure_ascii=False, indent=2)
```

## lark-mcp is Unnecessary When terminal is Available

The `@larksuiteoapi/lark-mcp` MCP server is **not needed** if the gateway has terminal toolset.
With terminal, call the Feishu API directly via Python/curl:

```python
import requests

# Get tenant access token
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', json={
    'app_id': 'cli_a97aab1888f8de17',
    'app_secret': 'YOUR_SECRET'
})
token = r.json()['tenant_access_token']

# Read/write Bitable
headers = {'Authorization': f'Bearer {token}'}
requests.get(f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables', headers=headers)
```

lark-mcp also has a known incompatibility: it returns `"capabilities": {}` (empty) during
MCP initialize handshake regardless of protocol version, causing Hermes MCP client to fail
on `tools/list` with `Method not found`. Skip it entirely.

To enable Feishu API access in the gateway, just add `hermes-cli` to platform_toolsets:

```yaml
platform_toolsets:
  feishu:
    - mcp
    - hermes-cli   # ← adds terminal/execute_code/file tools
```

## Disk Health & Emergency Cleanup

### Quick Disk Check
```bash
df -h /                          # overall usage
du -sh ~/.hermes/*/              # top-level breakdown
du -sh ~/.hermes/profiles/*/     # per-profile sizes
du -sh ~/.hermes/hermes-agent/*/ # agent internals
```

### Known Space Hogs (in order of size)
| Path | Typical Size | Notes |
|------|-------------|-------|
| `~/.hermes/hermes-agent/venv/` | 6+ GB | Python venv — do NOT delete |
| `~/.hermes/profiles/<name>/node/` | 1-2 GB each | Each profile gets its own Node.js copy |
| `~/.hermes/hermes-agent/node_modules/` | 200+ MB | |
| `~/.hermes/sessions/` | 200-400 MB | Accumulates `.jsonl` files over time |
| `~/.hermes/profiles/<name>/sessions/` | 20-50 MB each | |

Deleting unused profiles (especially aquaoptima, geokernel) can free 1-2 GB each just from the bundled Node copy.

### Session Cleanup (Pitfalls)
Sessions are `.jsonl` files, NOT `.json`. `find -name "*.json"` will miss them entirely.

```bash
# WRONG — misses session files
find ~/.hermes/sessions/ -name "*.json" -mtime +30 -delete

# CORRECT — target .jsonl
find ~/.hermes/sessions/ -name "*.jsonl" -mtime +30 -delete
```

`mtime +30` means strictly MORE than 30 days old — files exactly 30 days old are NOT deleted.
To delete by filename date prefix (safer, more predictable):

```bash
cd ~/.hermes/sessions/
ls *.jsonl | awk '$0 < "20260430"' | xargs rm -f
```

Keep at least the last 2 weeks of sessions — they power `session_search`.

### Disk-Full Cascade Failure Pattern
When disk hits ~100%, the following cascade occurs on GCP VMs:

1. Docker container veth interfaces start erroring / containers crash-loop
2. `snapd` watchdog timeout (snapd can't write state)
3. SSH starts returning "send failure packet" / "Connection reset by peer"  
4. `systemd-journald` watchdog timeout — **this is the point of no return**
5. GCP OSConfigAgent loses metadata server connectivity (networking stack broken)
6. `oslogin_cache_refresh` fails — SSH login impossible (can't resolve users)
7. VM requires hard reboot from GCP Console to recover

Warning threshold: keep disk below 85%. At 90%+ start cleaning. At 95%+ expect instability.

### Disk Cleanup Priority Order
1. Delete unused profiles: `rm -rf ~/.hermes/profiles/<name>` (can free 1-2 GB/profile)
2. Old sessions: `find ~/.hermes/sessions/ -name "*.jsonl" -mtime +30 -delete`
3. Rotated system logs: `find /var/log -name "*.gz" -delete && find /var/log -name "*.1" -delete`
4. Image cache: `rm -rf ~/.hermes/image_cache/*`
5. APT cache: `sudo apt-get clean`

## Migrating ~/.hermes to a Separate Disk (Symlink Method)

Use when adding a new data disk (e.g. 200GB SSD on GCP) to free up the system disk.
The symlink approach is transparent — all paths, cron jobs, and gateway configs continue
working without any changes.

### Prerequisites

1. New disk is attached and formatted (GCP auto-mounts to `/mnt/disks/data`)
2. Ensure fstab entry exists for the new disk so it mounts on reboot:

```bash
UUID=$(sudo blkid -s UUID -o value /dev/sdb)
# If not already present, add:
echo "UUID=$UUID /mnt/disks/data ext4 discard,defaults,nofail 0 2" | sudo tee -a /etc/fstab
# Verify only one entry:
grep "19bbf\|disks/data" /etc/fstab
```

GCP usually adds this automatically with `discard,defaults,nofail` — check before adding.

### Migration Steps

```bash
# 1. Create destination
mkdir -p ~/.hermes

# 2. Rsync everything (takes ~3-5 min for 9GB, ~55 MB/s on internal GCP disk)
rsync -a --info=progress2 ~/.hermes/ ~/

# 3. Verify destination looks complete
du -sh ~/
ls ~/ | head -10

# 4. Atomic cut-over (backup old, create symlink)
mv ~/.hermes ~/.hermes.bak
ln -s ~/.hermes ~/.hermes

# 5. Verify
ls -la ~/.hermes   # should show: .hermes -> ~/.hermes

# 6. Restart gateway services (see section below)

# 7. After confirming everything works, delete backup
rm -rf ~/.hermes.bak
```

### Restarting Gateway Services

Gateways are managed by **systemd user services**, NOT pm2 or manual nohup.

```bash
# List the service files
ls ~/.config/systemd/user/hermes*.service

# Restart all gateways
systemctl --user restart hermes-gateway hermes-gateway-aquaoptima hermes-gateway-busycow hermes-gateway-geokernel

# Verify all running
systemctl --user status hermes-gateway hermes-gateway-aquaoptima hermes-gateway-busycow hermes-gateway-geokernel --no-pager | grep -E "●|Active:"
```

Expected output: all show `Active: active (running)`.

Do NOT use `pkill -f gateway` during migration — it will also kill the current CLI session
(the CLI session process shares the same venv Python binary path match pattern).
Use `systemctl --user restart` instead.

### Expected Disk Result

| Disk | Before | After |
|------|--------|-------|
| System (sda, 60GB) | 96% | ~55-60% |
| Data (sdb, 200GB) | empty | ~5% (9GB) |

## Pitfalls

- jobs.json top-level structure is `{\"jobs\": [...]}` not a bare array
- Internal job key is `id`, but `cronjob(action='list')` returns it as `job_id`
- After regex-stripping platform sections, `platform_toolsets:` becomes an empty key — must patch it back to `cli: hermes-cli`
- `flush_memories` sometimes gets mis-placed inside `mcp_servers` block — clean it out
- busycow profile may lack runtime dirs (auth, state.db, bin, node, etc.) if gateway was never run — those get created on first `gateway run`
- pairing is a directory, not a file — use `rm -rf`, not `rm -f`
