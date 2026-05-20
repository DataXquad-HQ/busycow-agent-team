---
name: facility-inspection-ai-playbook
description: Design and generate an AI-optimized facility inspection playbook — structured for Qwen-VL (severity assessment) and YOLO-World (edge detection), with ticket templates for Hermes. Covers universal FM standards research, category taxonomy (F-01~F-28), YOLO prompt maps, and two-model confidence scoring. Use when building an AI patrol robot inspection system for any facility type.
# KEY INSIGHT: Playbook has TWO layers:
# 1. LLM-readable (Lark Doc) — for Qwen-VL system prompt + Hermes ticket rules
# 2. Code-compiled (categories.py) — for YOLO-World (not LLM, cannot read docs)
#    YOLO needs: prompts list, min_conf per category, edge_action enum
#    All Part 6 playbook rules must be translated to Python code, not just docs.
#
# Two-model confidence: final = YOLO_conf × QwenVL_conf; <0.65 → downgrade; <0.50 → human review
#
# Key Deliverables (2026-05-09)
# Playbook Lark Doc: https://bytedance.larkoffice.com/docx/{{DOC_TOKEN}}
# Edge code: ~/projects/facility-inspection-edge/
#   - config/categories.py  — 28 categories, prompts, min_conf, edge_action
#   - edge/detector.py      — YOLO-World runtime, 3 dispatch queues, frame loop
#   - tests/test_detector.py — 34 unit tests (all passing)
# Standards PDFs: ~/projects/facility-inspection-standards/

triggers:
  - user mentions facility inspection, patrol robot, defect detection, FM standards
  - user asks about YOLO-World prompts for inspection
  - user wants a playbook for Qwen-VL or VLM-based inspection
  - user building AI ticketing from robot camera feed
---

# Facility Inspection AI Playbook Skill

## When to Use
Use when a client needs an AI-powered facility inspection system where:
- A patrol robot / edge camera detects defects visually
- A VLM (Qwen-VL or similar) assesses severity
- Hermes or another LLM writes structured work order tickets

This playbook design works for: transit stations (MTR), shopping malls, office buildings, hospitals, factories, mixed-use.

---

## Key Architecture Insight

```
YOLO-World (Edge)     → detects presence, bounding box, class
Qwen-VL (Cloud)       → assesses severity using Playbook rules
Hermes (Cloud)        → writes ticket from structured JSON
Playbook              → single source of truth for ALL three layers
```

**Do NOT feed raw standards PDFs to the AI.** Distill them into the Playbook first. The Playbook IS the RAG source.

---

## Standards That Inform the Playbook

### Universal (all building types)
| Standard | Key Contribution |
|---|---|
| ISO 41001:2018 | FM governance framework, PDCA cycle |
| ISO 55001:2014 | Risk-based asset inspection planning |
| UNIFORMAT II (NIST NISTIR 6389) | Building element taxonomy A–J (FREE) |
| ASTM E2018 | 3-tier urgency: Immediate / Short-term / Long-term |
| NFPA 101 | Life safety compliance items |
| APPA FCI Framework | Facility Condition Index 0–100% (FREE) |
| ERDC-CERL BCI | Distress-based defect cataloging (FREE) |

### Transit / MTR Specific (add-on)
| Standard | Key Contribution |
|---|---|
| APTA RT-FS-S-003-02 | Station inspection 1–5 rating scale + defect list (FREE) |
| FTA FCA Guidebook | TERM Scale A–J component codes (FREE) |
| FTA Report No. 0236 | Tunnel inspection best practices (FREE) |

### Free Downloads
```bash
# NIST UNIFORMAT II
curl -Lo NIST-UNIFORMAT-II.pdf "https://www.govinfo.gov/content/pkg/GOVPUB-C13-5af96252bc88826c911daac93c449927/pdf/GOVPUB-C13-5af96252bc88826c911daac93c449927.pdf"

# APPA FCI Article
curl -Lo APPA-FCI.pdf "https://www1.appa.org/files/FMArticles/FM091006_Feature_FCI.pdf"

# ERDC-CERL BCI
curl -Lo ERDC-BCI.pdf "https://railtec.illinois.edu/wp/wp-content/uploads/pdf-archive/Uzarski-and-Grussing-Building-condition-assessment-2008.pdf"
```
Note: APTA and FTA PDFs block direct curl (403). Must download via browser or use Wayback Machine.

---

## Playbook Structure (6 Parts)

### PART 1 — How AI Must Use This Playbook
- Role assignment: Qwen-VL = Visual Inspector, Hermes = Ticket Writer
- **Mandatory Qwen-VL JSON output format** (every image must output this):
```json
{
  "category_id": "F-01",
  "category_name": "Structural Crack",
  "detected": true,
  "severity": "HIGH",
  "confidence": 0.87,
  "location_description": "...",
  "visual_evidence": "...",
  "threshold_met": "crack length >10cm",
  "ignore_reason": null,
  "recommended_action": "..."
}
```
- Multi-detection: one JSON per issue, CRITICAL first
- Confidence threshold: flag if ≥0.70, note if 0.50–0.69, skip if <0.50

### PART 2 — Global Rules
- **4-level severity**: CRITICAL / HIGH / MEDIUM / LOW / NO ACTION
- **SLA Matrix**: CRITICAL=1h response/4h resolution → LOW=24h/72h
- **Assignment Routing**: 7 teams (Structural / M&E / Security / Cleaning / Fire Safety / Operations / Maintenance)
- **Ticket title format**: `[SEVERITY] [CAT-ID] {Issue} — {Location}`
- **Ticket body template**: all mandatory fields listed
- **What AI must NEVER flag**: expansion joints, shadows, intentional markings, decorative patterns, scheduled maintenance barriers

### PART 3 — 28 Inspection Categories (F-01 ~ F-28)

Each category has these AI-readable fields:
- `DETECT` — visual cues for Qwen-VL
- `THRESHOLD_CRITICAL/HIGH/MEDIUM/LOW` — quantified rules (mm, cm, sqm)
- `IGNORE` — false positive prevention
- `TICKET_TITLE` — template
- `TICKET_BODY_EXTRA` — category-specific required fields
- `ASSIGN` — team routing
- `SLA` — per severity

**Category list:**
```
F-01 Structural Crack           F-15 Exposed Wiring / Electrical Hazard
F-02 Active Water Leak          F-16 Pest Sighting
F-03 Water Stain / Damp Patch   F-17 Waste Overflow / Littering
F-04 Spill / Wet Floor          F-18 Damaged CCTV / Security Camera
F-05 Damaged Floor Tile         F-19 Emergency Equipment Issue
F-06 Trip Hazard                F-20 Paint Peeling / Surface Deterioration
F-07 Damaged Handrail           F-21 Blocked Drainage / Grating
F-08 Graffiti / Vandalism       F-22 Broken Window / Glass
F-09 Broken Signage             F-23 Equipment Damage (Ticket Machine etc.)
F-10 Lighting Failure           F-24 HVAC Vent Blockage / Damage
F-11 Pathway Obstruction        F-25 Ceiling Damage / Overhead Hazard
F-12 Damaged Door / Gate        F-26 Tactile Strip Missing (Transit+)
F-13 Elevator / Escalator       F-27 Platform Edge Hazard (Transit+)
F-14 Fire Equipment Obstruction F-28 Unauthorized Access / Suspicious Item
```
F-26 and F-27 marked Transit+ (MTR only, skip for malls/offices).

### PART 4 — Hermes Ticket Creation Rules
- Deduplication: same category_id + location within 4 hours = append note, not new ticket
- Batch run output: total by severity + CRITICAL list + estimated resolution hours
- Escalation: CRITICAL unacknowledged after 30 min → auto-escalate to Building Manager
- Location format: always `LEVEL | ZONE | NEAREST LANDMARK`
- Unknown category → F-00 "Uncategorized — Human Review Required", severity=MEDIUM

### PART 5 — Playbook Maintenance
- Monthly review for first 3 months, quarterly thereafter
- >15% false positives in a category → tighten THRESHOLD, add IGNORE rules
- >5% missed real issues → loosen THRESHOLD, add DETECT cues
- Every "False Positive" ticket closed → log category_id + visual cue → feeds monthly calibration

### PART 6 — YOLO-World Edge Deployment
See section below.

---

## YOLO-World Integration (Part 6 Detail)

### What YOLO-World CAN do
- Detect object presence and bounding box in real-time
- Use open-vocabulary text prompts (no retraining)
- Run on edge device at 10–30 fps

### What YOLO-World CANNOT do
- Assess severity (no reasoning)
- Apply IGNORE rules (will flag expansion joints as cracks)
- Fill ticket fields (detection only)
- Deduplicate (handled by Hermes)

### Per-Category Prompt Map Format
```
[CAT-ID] | Min Confidence | Edge Action | Class Prompts (10 phrases)
```

**Edge Action values:**
- `ALERT` — immediate push notification + forward to Qwen-VL (life safety: F-02, F-04, F-06, F-13, F-14, F-15, F-22, F-25, F-27, F-28)
- `FORWARD` — queue for Qwen-VL batch (≤60s delay): standard findings
- `LOG` — low-priority batch every 15 min: cosmetic issues (F-17, F-20, F-24)

**Min Confidence by risk level:**
- Safety-critical (electrical, fire, security): 0.80–0.85
- Structural / trip hazard: 0.72–0.75
- Cosmetic / low risk: 0.65–0.68

**Sample prompts per category:**
```
F-01 (0.72, FORWARD): "crack on wall", "structural crack", "concrete crack",
  "ceiling crack", "floor crack", "column crack", "beam crack",
  "fracture on concrete", "hairline crack", "wall fracture"

F-15 (0.85, ALERT): "exposed electrical wire", "open electrical panel",
  "hanging loose wire", "frayed cable", "sparking electrical outlet",
  "exposed cable", "open junction box", "bare wire",
  "electrical burn mark", "wire on wet floor"

F-28 (0.75, ALERT): "unattended bag", "abandoned luggage",
  "suspicious package", "unattended suitcase", "abandoned backpack",
  "unattended parcel", "suspicious object left behind"
```

### YOLO → Cloud Payload Format
```json
{
  "robot_id": "ROBOT-01",
  "zone_id": "B1-NORTH",
  "timestamp": "2026-05-09T14:32:11Z",
  "category_id": "F-01",
  "class_prompt": "crack on wall",
  "confidence": 0.84,
  "bbox": [x1, y1, x2, y2],
  "frame_id": "frame_00847",
  "image_crop_base64": "...",
  "edge_action": "FORWARD"
}
```

### Two-Model Confidence Scoring
```
Final confidence = YOLO_conf × QwenVL_conf
≥ 0.65 → create ticket at assessed severity
0.50–0.64 → downgrade severity by one level
< 0.50 → flag for human review, no ticket
```

### Recommended YOLO-World Variants
- `YOLO-World-v2-S` → low-power edge device
- `YOLO-World-v2-M` → standard edge box with GPU
- Do NOT use XL on edge — latency too high

---

## Lark Doc Generation

Use `lark-docx-writer` skill to write the playbook to a Lark Doc. Key notes:
- Chunk pushes to ≤14 blocks per API call
- `time.sleep(2.5)` between push() calls for large docs
- `time.sleep(5)` after document creation before first push
- Full 28-category playbook ≈ 300+ blocks — split into Part 3 + Part 6 separate scripts if hitting timeout

## Existing Playbook
BusyCow MTR Playbook v1.0 (all 6 parts):
https://bytedance.larkoffice.com/docx/{{DOC_TOKEN}}

---

## YOLO-World Must Be Code, Not Docs

**Critical insight from production build:**
YOLO-World is NOT an LLM — it cannot read the Playbook document. Every rule in Part 6 must be compiled into Python code. The code lives at `~/projects/facility-inspection-edge/`:

```
config/categories.py   — 28 Category dataclasses (prompts, min_conf, edge_action)
edge/detector.py       — Runtime: FacilityInspector class, 3 dispatch queues, frame loop
tests/test_detector.py — 34 unit tests (all passing)
```

Key architectural pattern:
```python
# categories.py — the ONLY source of truth for YOLO
@dataclass
class Category:
    id: str           # "F-01"
    prompts: List[str]  # fed to YOLO-World.set_classes() at startup
    min_conf: float   # per-category confidence floor
    edge_action: str  # ALERT / FORWARD / LOG
    assign_to: str    # for ticket routing

ALL_PROMPTS = [p for cat in CATEGORIES for p in cat.prompts]
PROMPT_TO_CATEGORY = {p: cat for cat in CATEGORIES for p in cat.prompts}
```

The Lark Doc Playbook (Part 6) serves as human-readable documentation only. The Python code IS the runtime implementation.

## Edge Code — Key Implementation Notes

- `FacilityInspector.__init__()` calls `model.set_classes(ALL_PROMPTS)` — loads all 200+ prompts as vocabulary
- Frame loop: sample at `FRAME_RATE` fps (default 2), skip others
- Per-detection: look up `ALL_PROMPTS[class_idx]` → `PROMPT_TO_CATEGORY[prompt]` → `Category`
- Apply `category.min_conf` filter AFTER global CONF_FLOOR
- Crop bbox + 20% padding, encode as base64 JPEG for cloud
- Three worker threads (alert_worker, forward_worker, log_worker) drain separate queues
- Night mode: `apply_night_preprocessing()` boosts brightness/contrast, lowers conf floor to 0.55

## Anbot Y Robot — Camera Specs

| Parameter | Value |
|---|---|
| Body Height | 988 mm |
| Camera Height | ~1.0–1.3 m (PTZ lifting rod +300mm stroke) |
| PTZ Horizontal | 0°–348° |
| PTZ Vertical | -10° to +30° |
| Camera Type | HD Starlight Night Vision, Gimbal PTZ |
| Estimated FOV | 60°–100° H (not published by manufacturer) |
| Night Vision | Starlight sensor (low-light color) + optional Thermal |
| Data TX | 5G / WiFi, encrypted |
| Speed | ~0.5–1.0 m/s patrol |
| Onboard POV footage | ❌ Not publicly available — only external marketing videos exist |

Closest sensor match for testing: **Intel RealSense D435i** (~1.0m height, 69° H-FOV).

---

## Test Video Datasets (Walkthrough / Robot POV)

**Critical insight:** Fixed overhead CCTV footage is WRONG for Anbot Y testing. Need forward-facing moving camera at ~1.0–1.3m height.

### Best datasets for Anbot Y simulation

| Dataset | Why | Download |
|---|---|---|
| **OpenLORIS-Scene** ⭐⭐⭐⭐⭐ | Wheeled robot, D435i at 1.0m, corridor/office/cafe/market | Google Drive via https://lifelong-robotic-vision.github.io/dataset/scene.html |
| **FusionPortable corridor_day** ⭐⭐⭐⭐⭐ | 672m uninterrupted corridor at 1.1 m/s — longest indoor traverse available | Google Drive via https://fusionportable.github.io/dataset/fusionportable/ |
| **TUM RGB-D fr2/pioneer_slam** ⭐⭐⭐⭐ | Pioneer robot + Kinect in halls/corridors; CC Attribution | `wget https://cvg.cit.tum.de/data/datasets/rgbd-dataset/...` |
| **M2DGR hall + lift sequences** ⭐⭐⭐⭐ | MIT License; hall + elevator traversal (multi-floor patrol) | Google Drive via https://github.com/SJTU-ViSYS/M2DGR |

### For structural defect testing (images only — no public video)
- Surface cracks: `kaggle datasets download -d arunrk7/surface-crack-detection` (CC BY 4.0)
- Wet floor: Roboflow `wet-floor-detection-v1-qdnta`
- Graffiti: Roboflow `graffiti-video-capture`

### Fastest feasibility test setup
1. **OpenLORIS-Scene** corridor sequence → normal baseline
2. **Self-shot video at 1.0m height** in your own facility (most accurate) → defect scenarios
3. Pexels API (`https://api.pexels.com/videos/search?query=indoor+corridor`) → HD corridor B-roll

### What doesn't work
- Mall Dataset, CUHK Avenue, UCSD Ped datasets — all **fixed overhead** CCTV angle, wrong perspective
- Anbot Y YouTube demos — external third-person view, no onboard POV

---

## Decks

**MTR Pitch Deck** (12 slides, navy/teal, client-facing):
- Local: `~/projects/mtr-pitch-deck/MTR-Facility-Inspection-Patrol-Robots-Pitch-Deck.pptx`
- Lark Drive: https://cjpg0xp67g6h.jp.larksuite.com/file/SZecb0eboo7Y7AxNDpPjCuUSpHg

**Architecture Deck** (12 slides, dark slate/cyan, technical):
- Local: `~/projects/mtr-pitch-deck/Facility-Inspection-AI-System-Architecture.pptx`
- Lark Drive: https://cjpg0xp67g6h.jp.larksuite.com/file/C1bDbG5iro96GwxsbwRjd8Skpwc

Slides: Cover → System Overview (3-layer) → Data Flow (9-step) → Edge Layer detail → Cloud AI (Dify+Qwen-VL) → Orchestration (Hermes) → Playbook Integration → Deployment Architecture → APIs → Tech Stack → Security → Implementation Checklist

Build script: `~/projects/mtr-pitch-deck/build_arch.js`

---

## Pitfalls

1. **Don't RAG raw standard PDFs** — too long, wrong format, 90% irrelevant. Playbook IS the distilled RAG source.
2. **Playbook token size** — 28 categories ≈ 6,000–7,000 tokens. Fits in system prompt. No RAG chunking needed for single-facility deployment.
3. **YOLO false positives are expected** — expansion joints → cracks, shadows → stains. This is normal. Qwen-VL filters them. Do not try to fix YOLO alone.
4. **Transit+ categories** — F-26, F-27 only for rail/transit. Remove for mall/office deployments.
5. **Severity calibration** — First 30 days expect 15–20% false positive rate. Monthly calibration tightens this.
6. **APTA/FTA PDF downloads** — block curl (403). Must use browser download or archive.org.
7. **F-00 escape hatch** — always include an uncategorized bucket. Real inspection finds things no one anticipated.
8. **Don't reuse shadow option objects in pptxgenjs** — PptxGenJS mutates shadow objects in-place. Always use a factory function `const sh = () => ({...})` not a shared const.
9. **Emoji in PPTX are unreliable cross-platform** — LibreOffice renders 🔴🟡🟢 as broken boxes. Use colored shape (OVAL) + plain text instead for severity indicators.
