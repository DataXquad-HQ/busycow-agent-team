---
name: blog-content-crew
description: >
  Use when a Growth Agent needs to produce a high-quality blog post from a brief.
  Runs a 4-agent CrewAI crew (Keyword Researcher, Context Researcher, Writer,
  Reviewer) using Tavily for real web search. Returns a finished draft ready
  for human review or a separate publishing workflow.
version: 1.0.0
author: BusyCow
metadata:
  hermes:
    tags: [growth, crewai, blog, content, inbound, gtm]
---

# Blog Content Crew

Runs a 4-agent CrewAI crew to produce a publication-ready blog post from a brief.
Uses Tavily for real web search — not model memory.

## What this packaged artifact includes

- `SKILL.md`
- `scripts/blog_crew.py`

This package artifact intentionally ships the **core drafting crew only**.
Org-specific wrappers for idea intake, CMS publishing, cron scheduling, and channel delivery
should be added separately in the target environment.

## Prerequisites

- `crewai` and `crewai-tools` installed in the active Hermes Python environment
- `tavily-python` installed in the same environment
- `TAVILY_API_KEY` in environment
- either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in environment

## Input (Brief)

```python
brief = {
    "topic": "How AI autopilot reduces pump station energy costs",
    "angle": "Use a real case study to show measurable ROI",
    "target_audience": "Water utility procurement managers",
    "keyword_direction": "smart water management, pump energy saving",
    "word_count": 1000,  # optional, default 900
    "brand_voice": "Direct, technical confidence. Not corporate. Not hype.",
}
```

## Usage

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.hermes/profiles/<agent>/skills/blog-content-crew/scripts"))
from blog_crew import run_blog_crew

result = run_blog_crew(brief)
print(result["draft"])
print(result["keywords"])
print(result["meta_description"])
```

## Output

```python
{
    "draft": "...",           # full article markdown
    "keywords": {
        "primary": "...",
        "secondary": ["...", "..."],
    },
    "meta_description": "...",  # ≤155 chars
    "reviewer_notes": "...",    # what the reviewer checked
    "passed": True,             # False if reviewer still has issues
}
```

## Quality Standard (applied by Reviewer agent)

- Hook in first sentence
- TL;DR ≤ 150 words present
- Primary keyword in title, first paragraph, and at least one H2
- Meta description ≤ 155 chars
- At least one internal-link placeholder: `[INTERNAL LINK: topic]`
- Original insight or concrete data point
- No AI filler phrases (for example: `deeply`, `notably`, `it's worth noting`, `in conclusion`)
- Brand voice stays consistent
- Usually 800–1,200 words unless the topic clearly needs more depth

## Recommended operating split

Use this skill for the **research + draft + review** stage.
Keep these as separate skills or local workflows in the target environment:
- content backlog / ideation intake
- CMS publishing
- image generation
- cron automation
- report delivery

## Pitfalls

- `TavilySearchTool()` needs `tavily-python` installed; `crewai-tools` does not always install it transitively
- CrewAI may default to OpenAI if you do not supply Anthropic credentials explicitly in the environment
- If Tavily quota is exhausted, the crew may stall or return weak research
- Treat the first output as a strong draft, not auto-publishable truth; keep a human review gate

## Installation

Copy the whole folder, not just `SKILL.md`:

```bash
cp -r artifacts/shared-skills/blog-content-crew ~/.hermes/profiles/<agent>/skills/
```

Then restart the Hermes session so the profile re-indexes the skill.
