# PPTX Troubleshooting & Repair - Unreadable Content, Broken Media, and Template Drift

Use this reference when a generated deck opens with a repair dialog, renders incorrectly, loses notes/animations, or behaves differently across PowerPoint, Google Slides, Keynote, or PDF export.

---
## Table of Contents

- [Common Symptoms](#common-symptoms)
- [Fast Triage Workflow](#fast-triage-workflow)
- [Failure Modes to Check First](#failure-modes-to-check-first)
- [Broken Internal Relationships](#broken-internal-relationships)
- [Template Drift](#template-drift)
- [Animation / Timing Fragility](#animation-timing-fragility)
- [Fonts and Media](#fonts-and-media)
- [Invalid Generator Input](#invalid-generator-input)
- [Practical Commands](#practical-commands)
- [Inventory a template before editing](#inventory-a-template-before-editing)
- [Inspect OOXML parts and broken internal targets](#inspect-ooxml-parts-and-broken-internal-targets)
- [Export notes before repair work](#export-notes-before-repair-work)
- [Repair Strategy by Generator](#repair-strategy-by-generator)
- [`python-pptx`](#python-pptx)
- [`PptxGenJS`](#pptxgenjs)
- [`PPTX-Automizer`](#pptx-automizer)
- [Do / Avoid](#do-avoid)
- [Do](#do)
- [Avoid](#avoid)
- [Related Resources](#related-resources)


## Common Symptoms

- "PowerPoint found unreadable content"
- "PowerPoint can attempt to repair the presentation"
- Missing images, charts, notes, or embedded media
- Layout shifts after opening on another machine
- Animations disappear after template-driven edits
- PDF export looks different from the editable deck

---

## Fast Triage Workflow

1. Confirm the generator and the last safe version:
   - `python-pptx`
   - `PptxGenJS`
   - `PPTX-Automizer`
   - manual PowerPoint edits after generation
2. Duplicate the broken file before testing repairs.
3. Run `python3 scripts/pptx_ooxml_inspect.py broken.pptx --list-broken-targets`.
4. If the file opens after repair, compare the repaired output to the last known-good deck and identify which slide or feature changed.
5. Rebuild the problematic slide with the smallest possible feature set.

---

## Failure Modes to Check First

### Broken Internal Relationships

- Missing chart, image, notes, or embedding targets can trigger repair.
- This often happens after low-level OOXML edits or after mixing parts from different templates.
- Use `scripts/pptx_ooxml_inspect.py` to identify missing internal targets.

### Template Drift

- The code assumes placeholder or layout positions from an older template version.
- A layout was renamed, removed, or duplicated.
- Branded templates were mixed across versions in the same deck.

Fix:
- Re-inventory the template with `scripts/pptx_inventory.py`.
- Switch to layout-name lookup or named-element replacement.

### Animation / Timing Fragility

- The slide copies successfully, but animations stop working after content replacement.
- A replaced or deleted shape was referenced by the timing tree.

Fix:
- Re-test in desktop PowerPoint.
- Keep animation slides as conservative template-copy operations.
- Prefer rebuilding the affected slide manually if motion is business-critical.

### Fonts and Media

- Fonts missing on the target machine change spacing and can overflow text boxes.
- Embedded video/audio may rely on codecs not available on the target machine.
- PDF export can flatten or omit some rich media behaviors.

Fix:
- Verify fonts on the export/presentation machine.
- Keep media formats conservative and test on target hardware.
- Export a static fallback for distribution.

### Invalid Generator Input

- Bad chart/table data shape
- Invalid image paths or corrupt media
- HTML-to-slide content that produces unsupported structure
- Unsupported option combinations that still create a file but break Office validation

Fix:
- Reduce the slide to a minimal reproducer.
- Compare against the library's own working examples.
- Reintroduce features incrementally.

---

## Practical Commands

### Inventory a template before editing

```bash
python3 scripts/pptx_inventory.py template.pptx --json
```

### Inspect OOXML parts and broken internal targets

```bash
python3 scripts/pptx_ooxml_inspect.py broken_deck.pptx --list-parts --list-broken-targets
```

### Export notes before repair work

```bash
python3 scripts/pptx_extract_notes.py broken_deck.pptx --format markdown --out notes_backup.md
```

---

## Repair Strategy by Generator

### `python-pptx`

- Suspect fragile OOXML edits first: theme edits, timing trees, direct XML patches.
- Rebuild the broken slide from a minimal clean deck when the XML has been modified by hand.

### `PptxGenJS`

- Check the official "needs repair" guide for invalid object options and unsupported content combinations.
- Re-test with a minimal slide containing only one chart/image/table at a time.

### `PPTX-Automizer`

- Verify that named elements still exist in the source template.
- If an animated or media-heavy slide broke, remove structural replacements and retry with text-only changes.
- Avoid deleting/replacing shapes that might be targets of animations or advanced rels.

---

## Do / Avoid

### Do

- Keep the last known-good deck for diffing and rollback
- Treat repair dialogs as structural problems, not as "probably harmless"
- Rebuild one broken slide instead of trying to patch a deeply corrupted file blindly
- Test in desktop PowerPoint after every repair pass

### Avoid

- Editing ZIP members by hand without a backup
- Mixing slides from different template generations without inspection
- Assuming Google Slides or Keynote behavior proves PowerPoint correctness
- Assuming repaired output is identical to the intended output

---

## Related Resources

- [pptx-template-branding.md](pptx-template-branding.md) - Template-safe editing patterns
- [pptx-animations-transitions.md](pptx-animations-transitions.md) - Motion-specific fragility and testing guidance
- [../data/sources.json](../data/sources.json) - Verified repair and OOXML source links
