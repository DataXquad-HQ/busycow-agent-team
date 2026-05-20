---
name: powerpoint
description: "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill."
license: Proprietary. LICENSE.txt has complete terms
---

# Powerpoint Skill

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md) |
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |
| Additional pptxgenjs pitfalls (ShapeType, async forEach, markitdown) | Read [references/pptxgenjs-pitfalls-addendum.md](references/pptxgenjs-pitfalls-addendum.md) |

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

**Read [editing.md](editing.md) for full details.**

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

---

## Creating from Scratch

**Read [pptxgenjs.md](pptxgenjs.md) for full details.**

Use when no template or reference presentation is available.

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Consider ideas from this list for each slide.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles, thick single-side borders. Carry it across every slide.

### Color Palettes

Choose colors that match your topic — don't default to generic blue. Use these palettes as inspiration:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right side) with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side options)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines

### Typography

**Choose an interesting font pairing** — don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

## Enterprise-Quality Design Principles

After comparing a professionally designed enterprise deck (Distify.ai hospitality deck) against a developer-built pptxgenjs output, here is what separates the two:

| Element | Developer look (❌) | Enterprise look (✅) |
|---|---|---|
| **Background** | Dark navy across all slides | Mostly **white/light** — dark only for cover + closing |
| **Accent color** | Applied to everything | Used **sparingly** on 1–2 elements per slide |
| **Decoration** | Complex cards, borders, shadows everywhere | Minimal — **whitespace does the work** |
| **Photography** | None — shapes fill the space | **Real or AI-generated photos** on most slides |
| **Layout** | Many overlapping elements | Clean columns, lots of breathing room |
| **Icons** | Every item gets an icon | **Selective** — only where genuinely clarifying |
| **Charts** | Text substituting for charts | **Actual bar/line charts** with labeled data |

### The Rule of Thumb
If swapping out the colors into a completely different presentation would still "work," the design isn't specific enough. Enterprise decks feel **built for this exact topic** — the photo on the cover directly illustrates the concept, the chart uses real data, the layout has one clear visual anchor per slide.

### Photography is the #1 quality driver
- Cover slide: full-bleed photo that directly shows the concept (e.g. human + robot working together)
- Closing slide: aspirational photo of the desired future state
- Content slides: 3-column or 2×2 grid with a relevant photo per item
- **Without photos, the deck looks like a developer made it, even with beautiful shapes and colors**

### White-background slides beat dark-background slides for enterprise
- Use dark/navy only for: cover, closing CTA, and the occasional "stat shock" slide (e.g. full-dark with huge "50%" stat)
- All other slides: white or light gray (#F8FAFC) background
- This is what makes a deck feel "designed by an agency" vs "built in code"

### What to ask the client before building
1. Do you have product/lifestyle photography, or should I use AI-generated images?
2. What is your primary brand color? (One accent color is enough — don't invent a palette)
3. Do you have a logo file? (Embed it on cover + closing)

## Cross-Platform Rendering Pitfalls (LibreOffice / export)

These issues were found via visual QA using LibreOffice PDF conversion:

- **Emoji render as broken boxes** — 🔴🟡🟢 and similar emoji fail in LibreOffice. Use colored `OVAL` shapes + plain text labels instead for severity indicators, status dots, or any colored icon that must render cross-platform.
- **Shadow option objects must be fresh per call** — PptxGenJS mutates shadow objects in-place (converts to EMU). Use a factory: `const sh = () => ({ type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.12 })`. A shared const breaks on the second use.
- **Bottom cards clip if py + h > 5.5"** — Slide height is 5.625". Cards at py=3.35 with h=1.75 = 5.1" total, safe. But py=3.5 + h=1.75 = 5.25" — gets very close. Leave 0.3" bottom margin minimum.
- **Icon fonts (react-icons) may not render** — If icon glyphs show as `?` in LibreOffice conversion, the SVG rendering failed. Always rasterize icons to PNG via `sharp` before embedding. Never embed SVG directly.
- **Large empty gaps in cards** = missing content or y-offset issue — When a card header is at y=1.6 but bullets start at y=2.85, if the tag line at y=2.48 has h=0.35, there's a 0.02" gap. Visually fine, but if the tag line is missing entirely it creates a 0.37" blank. Always verify every intermediate element is actually added.

## Working With Organiser-Provided Templates (Competition / Tender)

When the user must follow an organiser's exact PPTX template (slide layouts, colors, placeholder order):

### 1. Inspect the template first — always
```python
from pptx import Presentation
prs = Presentation('template.pptx')
# Slide layouts
for i, layout in enumerate(prs.slide_masters[0].slide_layouts):
    print(f"[{i}] '{layout.name}'")
    for ph in layout.placeholders:
        print(f"     idx={ph.placeholder_format.idx} type={ph.placeholder_format.type} name='{ph.name}'")
# Theme colors
for rel in prs.slide_masters[0].part.rels.values():
    if 'theme' in rel.reltype:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(rel._target._blob)
        ns = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
        for child in root.find(f'.//{ns}clrScheme'):
            tag = child.tag.split('}')[-1]
            for gc in child:
                val = gc.attrib.get('val') or gc.attrib.get('lastClr')
                print(f"  {tag}: #{val}")
```

### 2. Deleting existing slides (namespace-aware — the `r:id` naive approach fails)

```python
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
sldIdLst = prs.slides._sldIdLst
to_remove = list(sldIdLst)[1:]   # keep slide 0 (cover), delete rest
for elem in to_remove:
    rId = elem.get(f'{{{R_NS}}}id')
    if rId:
        try: prs.part.drop_rel(rId)
        except Exception: pass
    sldIdLst.remove(elem)
```

PITFALL: `elem.get('r:id')` returns `None` — the `r:` prefix is not how lxml stores namespace attributes. Always use the full namespace URI form `f'{{{R_NS}}}id'`.

### 3. Reading color from template shapes
```python
for run in shape.text_frame.paragraphs[0].runs:
    try:
        col = run.font.color.rgb   # RGBColor object
    except:
        col = 'inherited'          # color comes from theme/layout
```

### 4. Reading PDFs on this system
- `pdftotext`: **not installed** — do not use
- `web_extract("file:///...")`: **blocked** — "private network address"
- ✅ **Use pymupdf** (already in venv):
```python
import pymupdf
doc = pymupdf.open('/tmp/file.pdf')
for page in doc:
    print(page.get_text())
```

## Pitfalls (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements; avoid plain title + bullets
- **Don't forget text box padding** — when aligning lines or shapes with text edges, set `margin: 0` on the text box or offset the shape to account for padding
- **Don't use low-contrast elements**
- **Don't use emoji for semantic indicators** (severity dots, status icons) — LibreOffice renders 🔴🟡🟢 as broken tofu boxes. Use a colored `OVAL` shape + plain text label instead.
- **Don't hard-code panel heights for variable-length content** — compute dynamically: `const rh = items.length * lineHeight + headerOffset`. Hard-coded heights will clip content in content-heavy panels.
- **Don't use a shared title font size for long text in narrow panels** — add a conditional: `fontSize: title.length > 11 ? 13 : 18`. Titles like "ORCHESTRATION" wrap mid-word at 18pt in a 2.28" wide box.
- **Don't QA with PyMuPDF** — it strips all visual design (colors, boxes, shapes). Always use LibreOffice for PDF conversion: `libreoffice --headless --convert-to pdf file.pptx --outdir /path/` — icons AND text need strong contrast against the background; avoid light text on light backgrounds or dark text on dark backgrounds
- **NEVER use accent lines under titles** — these are a hallmark of AI-generated slides; use whitespace or background color instead

---

## QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### Visual QA

**⚠️ USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

Convert slides to images (see [Converting to Images](#converting-to-images)), then use this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### Verification Loop

1. Generate slides → Convert to images → Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

This creates `slide-01.jpg`, `slide-02.jpg`, etc.

To re-render specific slides after fixes:

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Dependencies

- `pip install "markitdown[pptx]"` - text extraction
- `pip install Pillow` - thumbnail grids
- `npm install -g pptxgenjs` - creating from scratch
- LibreOffice (`soffice`) - PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)
- Poppler (`pdftoppm`) - PDF to images
