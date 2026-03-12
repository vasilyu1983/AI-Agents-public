# PDF Release Checklist (Core, Non-AI)

Purpose: ship a PDF that is readable, link-correct, and reproducible (the PDF is not the source of truth).

## Inputs

- Source file(s): doc/slide/design file + linked assets
- Release context: audience, distribution channel, confidentiality level

## Outputs

- Verified PDF ready for distribution
- Release notes: source version, export settings, and owner

## Core

### A) Source-of-Truth and Versioning

- [ ] Source document is stored and versioned (doc/ppt/design file)
- [ ] PDF filename includes date/version (e.g., `Report_2025-12-18_v2.pdf`)
- [ ] Owner and last-updated date are present in the document

### B) Export Fidelity

- [ ] Fonts are embedded (or rendering verified on a second machine)
- [ ] Images are not pixelated; charts are legible at 100% zoom
- [ ] Page size is correct (A4/Letter) and margins are intentional
- [ ] Interactive elements behave as expected (links, TOC, form fields)

### C) Links and Navigation

- [ ] All hyperlinks work (external + internal)
- [ ] Table of contents links work (if present)
- [ ] Headings/bookmarks exist for long PDFs (if supported)

### D) Accessibility (baseline)

- [ ] Text is selectable (not a scanned image unless necessary)
- [ ] Reading order is correct (test with selection or a screen reader if possible)
- [ ] Images/figures have alt text (where supported by source tool)
- [ ] Color is not the only carrier of meaning; contrast is sufficient

Adobe reference: https://helpx.adobe.com/acrobat/using/creating-accessible-pdfs.html

### E) Privacy and Compliance

- [ ] No customer PII or confidential data unless explicitly approved
- [ ] Redaction is real (not just black boxes); verify by copy/paste
- [ ] Metadata scrubbed if needed (author, comments, hidden layers)

## Decision Rules

- No-ship if: links are broken, reading order is wrong, or sensitive data is present.
- Re-export if: any formatting changed after the last PDF export.

## Risks

- PDF becomes an unmaintainable source of truth
- Hidden metadata leaks confidential info
- Accessibility failures block distribution (esp. enterprise/government buyers)

## Optional: AI / Automation

Use only if allowed by policy and data handling rules.

- Generate a link-check report and a redaction checklist; humans verify final PDF manually.
