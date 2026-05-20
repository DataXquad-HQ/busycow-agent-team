# AI Automation Playbook — Setup

## What this creates

- 10 advanced automation, multi-agent, and AI pipeline skills

## Prerequisites

- Core playbook installed (`core/SETUP.md` completed)
- Docker installed (for CrewAI/OpenHands)
- Node.js 18+ (for webhook, graphify)

---

## Step 1 — Install skills

```bash
SKILLS_DIR="${HERMES_HOME:-~/.hermes}/skills/ai-automation"
mkdir -p "$SKILLS_DIR"

BASE_URL="https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/ai-automation/skills"

for skill in hermes-cron-scheduling hermes-profile-management webhook-subscriptions running-strategic-council crewai-claude-code-writer crewai-openhands-deploy ai-pipeline-feasibility-study facility-inspection-ai-playbook whisper graphify; do
  mkdir -p "$SKILLS_DIR/$skill"
  curl -fsSL "$BASE_URL/$skill.md" -o "$SKILLS_DIR/$skill/SKILL.md"
  echo "✅ $skill"
done
```

## Step 2 — Enable webhook platform (for webhook-subscriptions)

Add to `~/.hermes/config.yaml`:
```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8644
      secret: "{{generate-a-strong-secret}}"
```

Then restart the gateway: `hermes gateway run`

## Step 3 — Install Whisper (for speech recognition)

```bash
pip install -U openai-whisper
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

## Step 4 — Install Graphify (for knowledge graphs)

```bash
npm install -g @graphify/cli
# or via npx (no install needed):
npx graphify --version
```

## Step 5 — Deploy CrewAI + OpenHands (optional, for autonomous dev)

Follow the `crewai-openhands-deploy` skill — requires Docker Compose and LLM API keys.

## Verify

```bash
hermes /skills
```

Confirm all 10 skills appear.

## Next

- Try: "Run a strategic council on [your goal]" to pressure-test your next big move
- Try: "Create a webhook for GitHub issues that triggers a triage prompt"
- Try: "Transcribe this audio file: [path]"
- Try: "Build a knowledge graph from ~/documents/"
