---
name: document-pptx
description: "Builds and edits PowerPoint (.pptx) slide decks and templates with PPTX-Automizer. Use when you make or build a slide deck or presentation, or repair one."
allowed-tools: Bash, Read, Write, Glob, Grep
compatibility: Claude Code + Codex. Uses runtime-specific allowed-tools / argument-hint fields.
version: "1.1"
last_validated: 2026-07-11
---

# Document PPTX

**Boundary:** when the claude.ai Slides artifact type or the official Anthropic `pptx` skill is available, prefer it for plain create/edit, generic template fill and visual QA. Use this skill for its specialist lanes:
- template inspection before automation (layouts, placeholder idx, shape names, OOXML parts)
- designer-owned template fills with PPTX-Automizer
- speaker-note extraction and damaged-deck inspection
- accessibility and EN 301 549 review

## Quick Reference

| Job | Default | Notes |
|-----|---------|-------|
| Inspect a template before any fill | `scripts/pptx_inventory.py --json` | Layout names, placeholder idx and type, shape names |
| Inspect a damaged deck or its parts | `scripts/pptx_ooxml_inspect.py` | Broken relationships, missing targets, repair dialogs |
| Extract or back up speaker notes | `scripts/pptx_extract_notes.py` | Markdown or JSON |
| Fill a designer-owned template | PPTX-Automizer | Named-element replacement only (chart data, text, table, image) |
| Python reporting or extraction | `python-pptx` | Standard charts, notes, placeholders |
| JS/TS or browser export | `PptxGenJS` | Real combo charts; 16:9 default layout |

## Scripts And Exit Codes

| Script | 0 | 1 | 2 |
|--------|---|---|---|
| `pptx_ooxml_inspect.py` | No broken relationship targets | Broken targets found (gate). `--report-only` exits 0 for well-formed packages with broken targets | File missing, invalid package or malformed relationship part |
| `pptx_inventory.py` / `pptx_extract_notes.py` | Written | n/a | File missing, unreadable, or not a `.pptx` |

## Decision Rules

- **Template first or from scratch.** Use the branded template when the deck goes to an external audience, brand or legal review is in the path, or the request names "our template". Build from scratch for internal drafts, exploratory mock-ups or data-shaped reports where speed matters more than branding. Never guess brand colours, fonts or layout names when a template exists: inventory it first. With no template and no brand requirement, a clean unbranded deck beats an invented corporate look.
- **PPTX-Automizer only for narrow fills.** It merges named elements into a designer-owned structure; it is not a general slide generator.
- **Resolve layouts by name, every time.** Layout indices are not portable between templates, and designers reorder or rename layouts between versions.
- **Guard placeholders by idx set.** `1 in slide.placeholders` is always `False`; test against `{ph.placeholder_format.idx for ph in slide.placeholders}`. See [references/pptx-template-branding.md](references/pptx-template-branding.md#layouts-and-placeholders).
- **One takeaway per slide**, and chart data traceable to one source of truth with units, timeframe and source.
- **Accessibility is part of authoring:** titles, reading order, contrast and alt text, not a final pass.

## Known Limits

- `python-pptx` has no animation API (no build or entrance effects) and no slide-transition API. Both need direct OOXML `<p:timing>`/`<p:transition>` edits; see [references/pptx-animations-transitions.md](references/pptx-animations-transitions.md) before promising motion.
- `python-pptx` cannot create a true combo chart (column plus line); it has no multi-plot chart constructor. Fill a template combo chart with `replace_data`, or use `PptxGenJS`.
- `python-pptx` has no gradient-fill API and no supported way to edit theme colours (`theme1.xml`). Both need direct XML edits with a backup first.
- The colour class is `RGBColor` (from `pptx.dml.color`), not `RgbColor`; the wrong case raises `ImportError`.
- Default slide sizes differ: python-pptx's default template is 10 × 7.5 in (4:3), PptxGenJS's default is 10 × 5.625 in (16:9). Check every shape and chart against the target size (`y + h <= slide height`); positions copied from a 4:3 example run off a 16:9 slide.
- `PptxGenJS` has no slide-transition or auto-advance option; `slide.transition` / `advanceAfter` are silently ignored. Write `<p:transition>` OOXML instead.
- PPTX-Automizer's `modifyElement(selector, callback)` takes modification callbacks (`ModifyTextHelper.setText(...)`, `ModifyTableHelper.setTable(...)`, `ModifyChartHelper.setChartData(...)`), not an options object like `{ text: ... }`.
- Blind template edits can break timing, media or repairability. Keynote or Google Slides opening a file cleanly does not confirm PowerPoint compatibility, and the reverse is also true.

- Library behaviour changes between releases. Re-test a claimed API gap or default against the installed version before relying on it, and mark it unverified when you cannot.

## Workflow

1. Classify the job: fresh deck, template fill, notes extraction, or repair.
2. Build the slide narrative before writing slide code ([assets/slide-narrative-template.md](assets/slide-narrative-template.md)).
3. Inspect the template (`pptx_inventory.py --json`, `pptx_ooxml_inspect.py --json`) before any automation change.
4. Generate or edit, then run the release gate below.

## Rendered Slide Release Gate

After the final save, reopen the deck and inventory slide count, layout names, placeholders, media relationships, chart data, and speaker notes. Render every slide to images or PDF in the declared delivery target and inspect for clipped text, font substitution, objects outside the slide, broken chart labels, low-resolution images, and unintended blank placeholders. Require an actual PowerPoint pass when PowerPoint fidelity or accessibility is an acceptance criterion; otherwise use the available target renderer and mark PowerPoint fidelity unverified.

Compare charts and headline figures with the source data after rendering, not only in the generation code. For template edits, confirm that masters and theme relationships still resolve and that the declared target viewer opens the file without a repair dialog. Record any viewer-specific variance instead of treating one viewer as proof for another.

## Navigation

**References**

- [references/pptx-layouts.md](references/pptx-layouts.md)
- [references/pptx-charts.md](references/pptx-charts.md)
- [references/pptx-template-branding.md](references/pptx-template-branding.md)
- [references/pptx-speaker-notes-delivery.md](references/pptx-speaker-notes-delivery.md)
- [references/pptx-accessibility-compliance.md](references/pptx-accessibility-compliance.md)
- [references/pptx-troubleshooting-repair.md](references/pptx-troubleshooting-repair.md)
- [references/pptx-animations-transitions.md](references/pptx-animations-transitions.md)
- [references/deck-narrative-and-visual-patterns.md](references/deck-narrative-and-visual-patterns.md) — Load when choosing a deck structure, persuasion arc, per-slide layout, slide type scale, or chart for a slide
- [references/extraction-stack.md](references/extraction-stack.md) — Load when picking an extraction tool (native parse vs Docling vs OCR) for a new LLM/RAG pipeline
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

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
