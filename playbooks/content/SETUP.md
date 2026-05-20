# Content Playbook — Setup

## What this creates

- 7 content creation and document processing skills

## Prerequisites

- Core playbook installed (`core/SETUP.md` completed)

---

## Step 1 — Install skills

```bash
SKILLS_DIR="${HERMES_HOME:-~/.hermes}/skills/content"
mkdir -p "$SKILLS_DIR"

BASE_URL="https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/playbooks/content/skills"

for skill in writing-blog-post marp-pitch-deck excalidraw powerpoint ocr-and-documents nano-pdf youtube-content; do
  mkdir -p "$SKILLS_DIR/$skill"
  curl -fsSL "$BASE_URL/$skill.md" -o "$SKILLS_DIR/$skill/SKILL.md"
  echo "✅ $skill"
done
```

## Step 2 — Install optional dependencies

Install based on which skills you plan to use:

```bash
# Marp pitch decks (requires Node.js)
npm install -g @marp-team/marp-cli

# PowerPoint support
pip install python-pptx

# PDF text extraction
pip install pymupdf

# OCR for scanned docs
pip install marker-pdf

# nano-pdf (PDF editing)
pip install nano-pdf
```

## Verify

```bash
hermes /skills
```

Confirm all 7 skills appear.

## Next

- Try: "Build me a 10-slide pitch deck for [your product] using Marp"
- Try: "Summarize this YouTube video: [URL]"
- Try: "Extract text from this PDF: [path]"
