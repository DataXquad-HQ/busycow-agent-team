---
name: ai-pipeline-feasibility-study
description: Build a software-only feasibility study for an AI vision pipeline — validates the full data journey (video → detection → VLM analysis → SOP reasoning → quality gate → ticketing) without requiring physical hardware. Use when a client wants to de-risk an AI system before committing to hardware/deployment.
version: 1.0.0
author: BusyCow/BusyCow
metadata:
  hermes:
    tags: [AI, feasibility, vision, pipeline, YOLO, Dify, Lark, OpenRouter]
---

# AI Pipeline Feasibility Study

Use when you need to validate an AI vision pipeline end-to-end **without physical hardware** (robot, edge device, etc.). Replace the camera/edge with phone video files — everything downstream is identical to production.

## Core Principle

The riskiest parts of an AI vision system are **not** the hardware — they are:
1. Can the AI reliably classify the right things?
2. Does the reasoning layer produce actionable output?
3. Does the quality gate actually cut false positives?
4. What is the real end-to-end latency?

A phone MP4 replaces the robot camera for all of this. Hardware is commodity; the AI stack is the unknown.

## Stack Pattern (proven for facility inspection)

```
Phone MP4
  → YOLO-World (open-vocabulary, label-free edge detection)
  → 10s clip extraction (ffmpeg, -3s to +7s around trigger)
  → Dify webhook workflow:
      Node A: VLM analysis (Qwen2-VL-72B via OpenRouter)
      Node B: SOP/domain reasoning agent (Llama-3.3-70B via OpenRouter)
      Node C: Quality gate judge (same model, independent eval)
      Node D: Condition router → PASS or FAIL branch
  → Lark Base ticket (Active Incidents or Review Queue)
  → Lark IM interactive card (Acknowledge / Resolve / False Alarm)
```

## Why OpenRouter for Feasibility

Use OpenRouter API (not self-hosted models) for feasibility studies:
- Zero deployment setup — just an API key
- Model performance is identical to self-hosted for validation purposes
- Can switch models in Dify in 30 seconds if one underperforms
- Recommended models: `qwen/qwen2-vl-72b-instruct` for vision, `meta-llama/llama-3.3-70b-instruct` for reasoning/quality gate

## Quality Gate Architecture

**Do not skip the quality gate.** It is the mechanism that produces the low false-positive rate claim. Without it you're just hoping.

Three-stage pipeline before a ticket is created:
1. VLM confirms the hazard (not just detection confidence)
2. Domain agent confirms it meets escalation threshold per SOP
3. Quality gate judge independently scores the ticket on 4 criteria (evidence match, severity justified, action specific, false positive risk) — total 100 pts, PASS ≥ 70

FAIL tickets go to a Review Queue (human sees them) — not discarded. This is the human-in-the-loop mechanism AND a source of calibration data.

## Project Structure

```
~/projects/{project-name}/
├── .env                  # all API keys and IDs
├── src/
│   ├── video_scanner.py  # YOLO-World + clip extraction + webhook
│   ├── lark_writer.py    # Flask → Lark Base + IM
│   ├── demo_runner.py    # single-command end-to-end
│   └── run_tests.py      # batch test suite + metrics
├── clips/                # extracted video clips
├── test_videos/          # phone-recorded test scenarios
└── logs/                 # detections.jsonl + test_results.json
```

## YOLO-World Configuration

```python
from ultralytics import YOLOWorld
model = YOLOWorld('yolov8x-worldv2.pt')  # best accuracy variant
model.set_classes([
    # describe hazards in natural language — no training needed
    'liquid spill on floor', 'wet floor puddle',
    'object blocking fire door', 'obstruction near emergency exit',
    'unattended bag', 'abandoned luggage',
    'person lying on floor', 'person collapsed on ground',
    'boxes in walkway', 'debris blocking corridor',
])
```

Key settings:
- Frame extraction rate: 2 fps (balance coverage vs speed)
- Confidence threshold: 0.60 (tune per environment)
- Event deduplication: merge detections within 3s window
- Clip: -3s to +7s around trigger frame

## Dify Workflow Setup

1. Create Workflow app (not Chatflow) at localhost:3000
2. Add OpenRouter as custom provider: base URL `https://openrouter.ai/api/v1`
3. Add Webhook trigger node → extract all event fields as variables
4. LLM Node A (VLM): enable vision, pass clip_url as file input
5. LLM Node B (SOP agent): embed full domain SOPs in system prompt
6. LLM Node C (Quality gate): evaluate on 4 criteria, score 0-100
7. IF/ELSE node: branch on PASS/FAIL
8. HTTP Request nodes → POST to lark_writer Flask server

## Lark Base Schema (minimum viable)

Active Incidents table needs at minimum:
- incident_id, station_id, location_hint, detected_at
- incident_type (SingleSelect), severity (SingleSelect)
- assigned_team, immediate_action (Text)
- hazard_description, clip_url (URL)
- quality_score (Number), status (SingleSelect: OPEN/ACKNOWLEDGED/RESOLVED/FALSE_ALARM)
- event_id (for traceability back to scanner)

Review Queue: same schema + review_status (PENDING/CONFIRMED/DISCARDED) + reviewer_notes

## Test Suite Design

20 scenarios minimum:
- 12 positive (genuine hazards, one per subcategory + multi-hazard + low-light)
- 8 negative/control (normal operations that should NOT trigger — cleaning equipment, owner nearby, staff working, etc.)

Name files to match a manifest dict in run_tests.py — enables automated TP/TN/FP/FN counting.

## Lark Error Code Reference

| Code | Meaning | Fix |
|------|---------|-----|
| `1254045` | `FieldNameNotFound` | Fetch schema with `mcp_lark_bitable_v1_appTableField_list` and check actual field names. Primary field is often `"Text"` not your custom name. |
| `1254003` | Field value type mismatch | DateTime must be ms int. URL must be `{link, text}` dict. SingleSelect must be exact option string. |
| `99991663` | Token expired | Re-fetch tenant_access_token — cache is stale. |

## Layered Testing Strategy (bottom-up, fast)

When the full YOLO → Dify → lark_writer chain is slow to iterate on, test in layers:

1. **Layer 1 — lark_writer in isolation**: `curl -X POST http://localhost:8766/write -H "Content-Type: application/json" -d '{...}'`. Confirm Lark Base record + IM card before touching video or Dify.
2. **Layer 2 — synthetic video**: Generate with ffmpeg (gray frame + text overlay). Verifies clip extraction and clip server, even though YOLO won't fire on it.
3. **Layer 3 — real video**: Use phone-recorded footage of actual hazard scenarios (wet floor, bag, blocked door). Only at this layer does YOLO fire → Dify → full chain.

This avoids waiting 2+ minutes for model inference during Lark field debugging.

## Acceptance Criteria Template

| Metric | Target |
|--------|--------|
| YOLO recall (true positive rate) | ≥ 80% |
| False trigger rate on controls | ≤ 30% |
| VLM incident type accuracy | ≥ 85% |
| Quality gate precision (PASS tickets genuine) | ≥ 90% |
| P50 detection-to-IM latency | ≤ 45s |
| P95 latency | ≤ 90s |

## Steps

1. **Create project structure** — directories, .env, install deps (ultralytics, opencv-python, flask, requests, python-dotenv, ffmpeg-python)
2. **Create Lark Base** — two tables with full schema (use Lark API to create programmatically)
3. **Write video_scanner.py** — YOLO-World + clip extraction + webhook
4. **Write lark_writer.py** — Flask server → Lark Base + IM card
5. **Write demo_runner.py** — orchestrator for single-command demo
6. **Build Dify workflow** — 4 nodes, full prompts, test with mock payload
7. **Write run_tests.py** — batch runner + metrics vs acceptance criteria
8. **Film test scenarios** — 12 positive + 8 control
9. **Run test suite** — collect metrics, tune thresholds
10. **Demo** — single command, live tickets in Lark

## Pitfalls

- **YOLO-World model downloads on first run** (~24MB weights + 338MB CLIP model) — run `model = YOLOWorld('yolov8s-worldv2.pt')` once standalone before the demo to avoid timeout mid-video. Also auto-installs `ultralytics/CLIP` from GitHub on first use — requires internet.
- **Disk space** — ultralytics + opencv are large; check `df -h` first. Clear pip cache if needed: `rm -rf ~/.cache/pip`
- **ffmpeg required** — install system ffmpeg (`apt install ffmpeg`), not just ffmpeg-python
- **Dify vision** — must enable "vision" toggle on the LLM node AND set resolution to "high"; clip_url must be publicly reachable from Dify (use localhost clip server)
- **Quality gate prompt** — return ONLY valid JSON instruction is critical; wrap LLM output parsing with try/except JSON decode
- **Lark Base URL fields** — must be `{"link": "...", "text": "..."}` not plain string
- **OpenRouter vision** — pass clip_url as a `file` type input in Dify LLM node, not as text in the prompt
- **Lark Base primary field name** — the primary (index) field in a new Lark Base table is literally named `"Text"`, NOT whatever you expect (e.g. `"incident_id"`). Error code `1254045` = `FieldNameNotFound`. Always fetch the actual field schema with `mcp_lark_bitable_v1_appTableField_list` before writing records, and map your logical `incident_id` to the `"Text"` key in the fields dict.
- **`CLIP_SERVER_PUBLIC_HOST` must be routable from Dify** — if Dify is on Zeabur/k3s, `localhost` and `host.docker.internal` are both unreachable. Use the VM's LAN IP (GCP: `10.128.0.x`). Check with `curl -s ifconfig.me` for public IP and `ip addr` for LAN IP.
- **Dify NOT in Docker** — if Dify is deployed on Zeabur, it runs in a k3s pod. Original `.env` pointing to `localhost:3000` or `host.docker.internal` will silently fail. Verify the correct public URL (`https://<app>.zeabur.app`) and get a fresh API key from Dify Settings → API Keys.
- **`detected_at` Lark DateTime field** — Lark Base DateTime (type 5) requires a **millisecond integer** timestamp, NOT an ISO string. Use `int(datetime.fromisoformat(iso_str).timestamp() * 1000)`. Passing an ISO string causes silent field rejection (record still creates but field is blank, breaking escalation monitor).
- **Synthetic video for pipeline testing** — when real surveillance footage isn't available, generate a test MP4 with ffmpeg: `ffmpeg -f lavfi -i "color=c=gray:size=1280x720:rate=25" -vf "drawtext=text='WET FLOOR':fontsize=48:fontcolor=red:x=(w-text_w)/2:y=(h-text_h)/2" -t 20 -c:v libx264 test.mp4`. This is enough to test video_scanner → clip extraction → lark_writer, even though YOLO won't fire detections. Test the lark_writer directly via `curl POST /write` with a synthetic payload to verify Lark Base + IM independently.
- **Test lark_writer independently** — don't wait for full YOLO pipeline to validate ticket creation. Fire `POST http://localhost:8766/write` directly with a realistic JSON payload. This isolates the Lark API integration from model inference.
- **Lark API domain — feishu.cn vs larksuite.com** — [your product] (and most China-region Lark orgs) uses `open.feishu.cn`, NOT `open.larksuite.com`. Using the wrong domain returns error code `1254045 FieldNameNotFound` (not an auth error) because the token is issued by one domain and rejected by the other silently. Always check which domain the org is on: international = `open.larksuite.com`, CN/HK = `open.feishu.cn`. The BusyCow app (`cli_a97bd21895f89e18`) uses `open.feishu.cn`.
- **Lark Base Review Queue primary field** — if your Review table was created with a different locale, the primary field may be named `多行文字` (Traditional Chinese) instead of `Text`. Attempting to write `{"Text": ...}` will return `1254045`. Workaround: omit the primary field entirely (Lark auto-fills it) by setting `primary_field=''` in `build_active_fields()`. Only include primary field for the Active Incidents table where it's confirmed to be `"Text"`.
- **Dify body arrives as list** — when Dify HTTP Request node sends `Content-Type: application/json` with `{{#start.event_id#}}` variables in the body, some variable substitution failures cause the body to arrive at the downstream service as `[{...}]` (a list) instead of `{...}` (a dict). Always handle this in the receiver: `if isinstance(raw, list): raw = raw[0] if raw else {}`.
- **OpenRouter Qwen VL does NOT support `video_url`** — as of May 2026, all Qwen VL models on OpenRouter (including 72B) only support `image` modality, not `video`. `POST /v1/chat/completions` with `{"type": "video_url"}` returns HTTP 404 `"No endpoints found that support input video"`. **Workaround**: extract 5–6 frames from the clip using ffmpeg at 0.5fps, encode each as base64 JPEG, and send as sequential `image_url` content items. Qwen VL correctly understands temporal context from sequential frames.

```python
# Frame extraction for Qwen VL (replaces video_url)
import subprocess, tempfile, base64
from pathlib import Path

def extract_frames_b64(clip_path: str, fps: float = 0.5, max_frames: int = 6) -> list[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run([
            'ffmpeg', '-y', '-i', clip_path,
            '-vf', f'fps={fps}', '-frames:v', str(max_frames),
            '-q:v', '5', f'{tmpdir}/frame_%02d.jpg'
        ], capture_output=True)
        return [
            base64.b64encode(open(fp,'rb').read()).decode()
            for fp in sorted(Path(tmpdir).glob('frame_*.jpg'))
        ]

# Send to Qwen VL
content = [{"type": "text", "text": "Your prompt..."}]
for b64 in extract_frames_b64(clip_path):
    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"}})
```

- **YOLO context string to VLM** — always tell Qwen which frame number the YOLO trigger lands on: *"The 10-second clip is shown as 6 sequential frames. The YOLO trigger occurs at approximately frame 2 (the 3-second mark)."* This anchors the model and dramatically improves hazard confirmation accuracy vs. sending frames with no temporal anchor.
- **Clip sizing** — 3s pre + 7s post trigger (10s total) works better than symmetric 10+10s. The 7s post gives enough time to confirm persistence (not a passer-by). Clip files for a 720p CCTV-quality video are ~72–102KB — small enough to base64-encode inline without a public hosting URL.
