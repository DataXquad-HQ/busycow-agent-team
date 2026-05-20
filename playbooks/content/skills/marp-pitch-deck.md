---
name: marp-pitch-deck
description: "Build professional pitch decks using Marp (markdown → PDF/PPTX/HTML). Covers theme CSS authoring, layout classes, photo placeholders, and export with headless Chrome. Use when asked to create a slide deck, presentation, or pitch in Marp format."
---

# Marp Pitch Deck

Build polished, version-controllable slide decks from a single markdown file.

## When to Use

- User asks for a pitch deck, presentation, or slides
- Deck needs to be editable as plain text (version control, easy updates)
- Multiple output formats needed (PDF + PPTX + HTML from one source)
- Prefer over pptxgenjs when content is text/layout-heavy (not icon/shape-heavy)

## Stack

```
deck.md          ← single source of truth (all content)
theme.css        ← custom theme (colors, fonts, layout classes)
marp CLI         ← already installed at ~/.hermes/node/bin/marp
```

## Setup

```bash
# Marp is already installed globally
marp --version   # @marp-team/marp-cli v4.4.0
```

## Build Commands

```bash
# HTML (fastest, no Chrome needed)
marp deck.md --theme theme.css --allow-local-files --html --output deck.html

# PDF (requires Chrome path — use dynamic find to handle version changes)
CHROME_PATH=$(find ~/.cache/puppeteer/chrome -name "chrome" -type f | head -1) \
CHROME_NO_SANDBOX=true \
marp deck.md --theme theme.css --allow-local-files --pdf --output deck.pdf

# PPTX
CHROME_PATH=$(find ~/.cache/puppeteer/chrome -name "chrome" -type f | head -1) \
CHROME_NO_SANDBOX=true \
marp deck.md --theme theme.css --allow-local-files --pptx --output deck.pptx
```

**Key pitfalls:**
- PDF/PPTX export requires Chrome — use the path above (puppeteer's bundled Chrome)
- Must set `CHROME_NO_SANDBOX=true` or Chrome will crash in this environment
- `--allow-local-files` required for local CSS themes and images
- Always output PDF/PPTX to `/tmp/` — existing files in project dir may be root-owned and cause EACCES

## Chrome Binary — Recovery Procedure

The puppeteer cache zip is often corrupt or unextracted. If `find ~/.cache/puppeteer -name "chrome" -type f` returns nothing:

```bash
# 1. Check current puppeteer version directory
ls ~/.cache/puppeteer/chrome/
# e.g. "linux-148.0.7778.167"

# 2. Download Chrome directly from Google CDN (replace version as needed)
VERSION="148.0.7778.167"
cd ~/.cache/puppeteer/chrome/linux-${VERSION}
wget -q "https://storage.googleapis.com/chrome-for-testing-public/${VERSION}/linux64/chrome-linux64.zip" -O chrome-linux64.zip

# 3. Extract with Python (unzip not available in this environment)
python3 -c "import zipfile; zipfile.ZipFile('chrome-linux64.zip').extractall('.')"

# 4. Make all binaries executable (critical — EACCES without this)
chmod +x ~/.cache/puppeteer/chrome/linux-${VERSION}/chrome-linux64/*

# 5. Verify
find ~/.cache/puppeteer/chrome -name "chrome" -type f
# → ~/.cache/puppeteer/chrome/linux-148.0.7778.167/chrome-linux64/chrome
```

**Why the zip fails with Python's zipfile**: The puppeteer-downloaded zip uses encryption flags (`\x04\x00` in header) that Python's zipfile rejects as "not a zip file" even though `file` reports it as valid zip. The wget-from-CDN zip extracts cleanly.

## Theme Architecture

Place theme CSS in `theme.css`. Marp themes use standard CSS with special selectors:

```css
/* Base slide */
section { font-family: ...; background: ...; padding: 48px 56px; width: 1280px; height: 720px; }

/* Top accent bar (::before) */
section::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: var(--navy); }

/* Slide number (::after) */
section::after { font-size: 0.7em; color: var(--slate-light); }

/* Layout variants via class */
section.cover { display: grid; grid-template-columns: 520px 1fr; }
section.dark   { background: var(--navy); color: white; }
section.split  { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
```

**Design system used in MTR deck (white + orange):**
```css
--navy:        #0F2546;
--orange:      #F97316;
--orange-lite: #FFF7ED;
--white:       #FFFFFF;
--off-white:   #F8FAFC;
--slate:       #475569;
--slate-light: #94A3B8;
--border:      #E2E8F0;
```

## Markdown Structure

```markdown
---
marp: true
theme: mtr-hit        ← must match CSS filename (without .css)
paginate: true
size: 16:9
---

<!-- _class: cover -->   ← applies section.cover CSS class to this slide

# Slide Title
content...

---                      ← slide separator

<!-- _class: dark -->    ← dark background slide

## SECTION LABEL         ← h2 renders as small orange uppercase tag
# Main Title             ← h1 renders as large navy headline

content...
```

## Layout Patterns

**Photo placeholder** (swap in real image later):
```markdown
<div style="background:#E2E8F0;border:2px dashed #94A3B8;border-radius:8px;
  display:flex;align-items:center;justify-content:center;min-height:140px;
  color:#94A3B8;font-size:0.8em;font-style:italic;text-align:center;">
📷 [ PHOTO: description of what goes here ]
</div>
```

**Split layout** (two columns):
```markdown
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;">
<div>

Left column content

</div>
<div>

Right column content

</div>
</div>
```

**Stat callout:**
```markdown
<div style="font-size:3em;font-weight:900;color:#F97316;">24/7</div>
<div style="font-size:0.9em;font-weight:600;color:#0F2546;">Continuous Coverage</div>
<div style="font-size:0.8em;color:#94A3B8;font-style:italic;">vs 2× per shift</div>
```

**Card with orange border:**
```markdown
<div style="background:white;border:2px solid #F97316;border-radius:10px;padding:20px 22px;box-shadow:0 2px 8px rgba(0,0,0,0.05);">

Card content here

</div>
```

**Orange tag chip:**
```markdown
<div style="display:inline-block;background:#F97316;color:white;font-size:0.7em;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:3px 10px;border-radius:4px;margin-bottom:8px;">TAG TEXT</div>
```

**Blockquote** renders as orange-left-bordered callout box automatically via theme CSS.

## Swapping in Real Photos

Replace photo placeholder div with:
```markdown
![Description](path/to/photo.jpg)
```

For full-bleed cover/CTA slides, position absolutely:
```markdown
<div style="position:absolute;top:0;right:0;width:50%;height:100%;
  background:url(photo.jpg) center/cover no-repeat;"></div>
```

## Reference Files

MTR deck files at:
```
~/projects/mtr-pitch-deck/marp/
  deck.md       ← 23-slide MTR HIT pitch deck (v5)
  theme.css     ← full theme (reference for future decks)
```

## Uploading to Lark Drive

After building, upload PDF + PPTX via curl, then share via MCP:

```python
import subprocess, json, os

def upload_file(path, token):
    size = os.path.getsize(path)
    name = os.path.basename(path)
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://open.larksuite.com/open-apis/drive/v1/files/upload_all",
        "-H", f"Authorization: Bearer {token}",
        "-F", f"file_name={name}",
        "-F", "parent_type=explorer",
        "-F", "parent_node=",   # empty = root My Drive
        "-F", f"size={size}",
        "-F", f"file=@{path}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    if data.get("code") == 0:
        return data["data"]["file_token"]
    raise Exception(f"Upload failed: {data}")

pdf_token  = upload_file("/tmp/deck.pdf", token)
pptx_token = upload_file("/tmp/deck.pptx", token)
```

Then share edit rights — two confirmed working methods:

**Method A: raw curl (confirmed working May 2026)**
```bash
curl -s -X POST \
  "https://open.larksuite.com/open-apis/drive/v1/permissions/{file_token}/members?type=file" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"member_type": "openid", "member_id": "ou_xxx", "perm": "edit"}'
```

**Method B: MCP tool**
```
mcp_lark_drive_v1_permissionMember_create(
  path={"token": file_token},
  params={"type": "file"},          # ← "file" not "docx"
  data={"member_type": "openid", "member_id": "ou_xxx", "perm": "edit"}
)
```

File URL pattern: `https://cjpg0xp67g6h.jp.larksuite.com/file/{file_token}`

## Key Learnings

- **Chrome path**: `~/.cache/puppeteer/chrome/linux-{VERSION}/chrome-linux64/chrome` — version number changes when puppeteer updates. Find with `find ~/.cache/puppeteer -name "chrome" -type f 2>/dev/null`.
- **`CHROME_NO_SANDBOX=true`** is mandatory in this environment (containerized). Also `chmod +x ~/.cache/puppeteer/chrome/linux-*/chrome-linux64/*` — all binaries in the folder need execute permission, not just `chrome` itself (crashpad handler also needs it).
- **Puppeteer zip may be corrupt / unextractable** — if `~/.cache/puppeteer/chrome/linux-*/` exists but is empty, or Python `zipfile` raises `BadZipFile` on the cached zip, do NOT try to extract it manually. Download fresh directly from Google's CDT CDN:
  ```bash
  VERSION="148.0.7778.167"  # match the version in the directory name
  cd ~/.cache/puppeteer/chrome/linux-$VERSION
  wget -q "https://storage.googleapis.com/chrome-for-testing-public/$VERSION/linux64/chrome-linux64.zip" -O chrome-linux64.zip
  python3 -c "import zipfile; zipfile.ZipFile('chrome-linux64.zip').extractall('.')"
  chmod +x chrome-linux64/*
  ```
  The URL pattern is always: `https://storage.googleapis.com/chrome-for-testing-public/{VERSION}/linux64/chrome-linux64.zip`
- **`unzip` not available** — use Python `zipfile` module instead. `bsdtar` also not available. `7z` not available. Python zipfile works on the CDN-downloaded zip (the puppeteer-cached zip may be encrypted/non-standard).
- **Permission denied on output PDF/PPTX**: If the existing file is root-owned (`-rw-r--r-- root root`), Marp cannot overwrite it. Workaround: output to `/tmp/` first, then copy manually or use `sudo cp`. Always check `ls -la *.pdf *.pptx` before building if files existed previously.
- Inline HTML with `style=` attributes works well for complex layouts
- Google Fonts load via `@import url(...)` in theme CSS — works in HTML export, may not load in PDF if offline
- Theme filename (without `.css`) must match the `theme:` frontmatter value
- Marp's `::before` pseudo-element is used for the top accent bar — don't use it for other purposes
- Tables render cleanly with thead/tbody styling in the CSS
- `section.dark` needs explicit overrides for every text color (p, li, strong, blockquote, td all need separate rules)
