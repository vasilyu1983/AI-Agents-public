---
name: document-pptx
description: "Create/edit .pptx presentations with charts, templates, and speaker notes. Use when asked for pitch decks, QBR decks, or slide automation."
allowed-tools: Bash, Read, Write, Glob, Grep
compatibility: Claude Code + Codex. Uses runtime-specific allowed-tools / argument-hint fields.
version: "1.1"
last_validated: 2026-07-11
---

# Document PPTX

Use this skill to create, edit, inspect, troubleshoot, or automate PowerPoint presentations programmatically.

Keep the skill focused on tool choice, template safety, notes and chart workflows, and repairability. Use the helper scripts and references instead of carrying long inline library manuals in `SKILL.md`.

## Quick Reference

| Need | Default Tool | When to Use |
|------|--------------|-------------|
| fresh editable deck in Python workflow | `python-pptx` | generation, extraction, notes, standard charts |
| fresh editable deck in JS/TS or browser flow | `PptxGenJS` | Node/browser export, HTML-heavy workflows |
| designer-owned branded template | `PPTX-Automizer` or template-safe library flow | replace named template elements |
| inspect masters, layouts, placeholders, and notes | `scripts/pptx_inventory.py` | before editing branded templates |
| extract or back up notes | `scripts/pptx_extract_notes.py` | speaker-note export |
| inspect damaged deck or OOXML parts | `scripts/pptx_ooxml_inspect.py` | repair dialogs, broken rels, missing targets |

## Decision Rules

- start from the audience and the decision the deck must support
- use one takeaway per slide
- prefer a branded template when brand fidelity matters
- resolve template layouts by name, not guessed index
- keep chart data traceable to one source of truth
- accessibility is part of authoring, not a final afterthought
- if animations, broken content, or unreadable-content repair are in scope, treat that as specialist troubleshooting work

## Template-First vs From-Scratch Judgment

Deciding whether to open a branded `.pptx` template or build from a blank `Presentation()` is the single highest-leverage call in this skill — get it wrong and every downstream slide inherits the mistake.

- **Use the branded template when:** the deck goes to an external audience, brand/legal review is in the approval path, the org already has a maintained `.pptx`/`.potx`, or the request mentions "our deck," "our template," or a company name.
- **Build from scratch when:** it's an internal working draft, no template exists yet, the ask is exploratory ("mock up a few options"), or the content is data/report-shaped and speed matters more than pixel-perfect branding.
- **Red flag:** never guess at brand colors, fonts, or layout names when a template is available — inventory it first (`scripts/pptx_inventory.py`). A plausible-looking hex code that isn't the actual brand color is worse than asking.
- **Escalate to PPTX-Automizer** only when a designer already owns the `.pptx`/`.potx` and the job is narrow, named-element replacement (chart data, a metric, a photo) — not general content authoring. Automizer is not a general slide-generation library; it merges into an existing structure.
- If the user has no template and no strong brand requirement, do not manufacture one — a clean, legible, unbranded deck beats an invented "corporate" look with unverified colors.

## Workflow

1. Classify the job:
   - fresh deck
   - template-fill workflow
   - notes extraction
   - troubleshooting or repair
2. Choose the tool stack.
3. Build the slide narrative before writing slide code.
4. Inspect templates before automation changes.
5. Generate or edit the deck.
6. Validate notes, data, accessibility, and repairability.

## ASCII Flow

```text
PPTX request
  |
  v
Classify job
  |-- fresh editable deck ------> build narrative + choose library
  |-- branded template fill ----> inspect masters/layouts/placeholders first
  |-- notes extraction ---------> scripts/pptx_extract_notes.py
  |-- troubleshoot / repair ----> scripts/pptx_ooxml_inspect.py
  |
  v
Choose stack
  |-- Python reporting ---------> python-pptx
  |-- JS/TS export -------------> PptxGenJS
  |-- named template elements --> PPTX-Automizer
  |
  v
Generate or edit slides
  |
  v
Validate
  |-- one takeaway per slide
  |-- chart data source + units + timeframe
  |-- speaker notes
  |-- accessibility and PowerPoint repair check
```

## Tool Selection

| Situation | Default |
|-----------|---------|
| Python-heavy reporting or extraction | `python-pptx` |
| JS/TS pipeline, browser export, or HTML-heavy content | `PptxGenJS` |
| designer-maintained branded template with named replacements | `PPTX-Automizer` |
| advanced animation editing | avoid promising full preservation; inspect and test carefully |

## Known Limits

- `python-pptx` has no animation API (no build/entrance effects) and no slide-transition API; both require direct OOXML `<p:timing>`/`<p:transition>` manipulation — see `references/pptx-animations-transitions.md` before promising motion.
- `python-pptx` cannot create a true combo chart (e.g., column + line) from scratch — it has no multi-plot chart constructor. Style a single-type chart, or use `PptxGenJS`/manual PowerPoint editing when a real combo is required.
- `python-pptx` has no native gradient-fill API and no supported way to edit theme colors (`theme1.xml`) through its object model — both require direct XML manipulation with a pre-edit backup.
- The color class is `RGBColor` (from `pptx.dml.color`), not `RgbColor` — a one-letter-case mistake here silently raises `ImportError` at runtime.
- template layout indices are not portable across branded decks — resolve layouts by name every time, including on templates you have used before (designers reorder or rename layouts between versions).
- template edits can break timing, media, or repairability if done blindly
- generated decks still need an actual PowerPoint review when fidelity or accessibility matters — Keynote/Google Slides opening cleanly does not confirm PowerPoint compatibility, and the reverse is also true.

## What Good Looks Like

- each slide supports one real decision or message
- branded decks respect masters, layouts, fonts, and colors
- charts carry units, timeframe, and source
- speaker notes capture exact figures and transitions
- titles, reading order, contrast, and alt text are present
- if the deck breaks, the structure is inspectable with the included scripts

## Navigation

**References**

- [references/pptx-layouts.md](references/pptx-layouts.md)
- [references/pptx-charts.md](references/pptx-charts.md)
- [references/pptx-template-branding.md](references/pptx-template-branding.md)
- [references/pptx-speaker-notes-delivery.md](references/pptx-speaker-notes-delivery.md)
- [references/pptx-accessibility-compliance.md](references/pptx-accessibility-compliance.md)
- [references/pptx-troubleshooting-repair.md](references/pptx-troubleshooting-repair.md)
- [references/pptx-animations-transitions.md](references/pptx-animations-transitions.md)
- [data/sources.json](data/sources.json)

**Scripts**

- [scripts/pptx_inventory.py](scripts/pptx_inventory.py)
- [scripts/pptx_extract_notes.py](scripts/pptx_extract_notes.py)
- [scripts/pptx_ooxml_inspect.py](scripts/pptx_ooxml_inspect.py)

**Templates**

- [assets/pitch-deck.md](assets/pitch-deck.md)
- [assets/quarterly-review.md](assets/quarterly-review.md)
- [assets/slide-narrative-template.md](assets/slide-narrative-template.md)

## Related Skills

- [../document-pdf/SKILL.md](../document-pdf/SKILL.md)
- [../document-xlsx/SKILL.md](../document-xlsx/SKILL.md)
- [../product-management/SKILL.md](../product-management/SKILL.md)

## Fact-Checking

- Verify current library behavior, packaged versions, and standards-sensitive claims before final advice.
- Prefer primary library docs and packaged release notes over summaries.
- If live verification is unavailable, mark version-sensitive guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

