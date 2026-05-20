# Content Playbook

Skills for creating documents, presentations, blog posts, diagrams, and multimedia content — your agent as a full content production system.

## Skills

| Skill | What it does |
|---|---|
| `writing-blog-post` | Write structured blog posts from briefings and save to content database |
| `marp-pitch-deck` | Build professional pitch decks using Marp markdown → PDF/PPTX/HTML |
| `excalidraw` | Create hand-drawn style architecture diagrams in Excalidraw JSON format |
| `powerpoint` | Create, edit, parse, or extract content from .pptx files |
| `ocr-and-documents` | Extract text from PDFs, scanned documents, and DOCX files |
| `nano-pdf` | Edit PDFs with natural-language instructions (fix typos, update titles) |
| `youtube-content` | Fetch YouTube transcripts and transform into summaries, threads, or blog posts |

## Prerequisites

- **Core playbook installed**
- **For `marp-pitch-deck`**: Marp CLI + headless Chrome (`npm install -g @marp-team/marp-cli`)
- **For `powerpoint`**: `python-pptx` (`pip install python-pptx`)
- **For `ocr-and-documents`**: `pymupdf` or `marker-pdf` for scanned docs
- **For `nano-pdf`**: `nano-pdf` CLI installed

## Use Cases

- Pitch decks and investor presentations from a brief
- Blog content from YouTube videos or raw notes
- Technical diagrams from architecture descriptions
- OCR and data extraction from uploaded documents
- PDF editing without re-exporting from source
