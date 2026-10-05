# PDF Accessibility and Compliance

Patterns for producing accessible, standards-compliant PDF documents.

---

## Contents

- [Tagged vs Untagged PDFs](#tagged-vs-untagged-pdfs)
- [PDF/UA Standard (ISO 14289)](#pdfua-standard-iso-14289)
- [Creating Tagged PDFs](#creating-tagged-pdfs)
- [Reading Order and Alt Text](#reading-order-and-alt-text)
- [EU EAA and EN 301 549](#eu-eaa-and-en-301-549)
- [Validation Tools](#validation-tools)
- [Decision Guide: When to Invest](#decision-guide-when-to-invest)
- [Checklist: PDF Accessibility Review](#checklist-pdf-accessibility-review)

---

## Tagged vs Untagged PDFs

A tagged PDF contains a logical structure tree mapping visual elements to semantic roles (headings, paragraphs, tables, figures). Screen readers depend on this tree. Without tags, assistive technology guesses reading order from character positions, which fails on multi-column layouts, tables, and sidebars.

Prefer regenerating an untagged PDF from a structured source. When the source is unavailable, [Acrobat supports adding and repairing tags](https://helpx.adobe.com/acrobat/using/creating-accessible-pdfs.html); inspect the resulting structure and reading order manually. Estimate remediation effort from representative pages rather than assigning a universal per-page time.

---

## PDF/UA Standard (ISO 14289)

Key requirements: every content element tagged or marked as artifact; tag tree reflects logical reading order; all images have alt text; tables use TH/TD with scope; document language declared; fonts embedded with Unicode mappings; no reliance on colour alone.

Two parts exist: **PDF/UA-1** (ISO 14289-1, PDF 1.7-based) and **PDF/UA-2** (ISO 14289-2:2024, PDF 2.0-based). Choose the part the recipient's validators and assistive-technology stack actually support: UA-1 has the longer tooling history; UA-2 fits when the toolchain emits PDF 2.0 and the recipient accepts it. veraPDF ships validation profiles for both, so it can run as the machine-checkable CI gate (`verapdf --flavour ua1 file.pdf`; check `verapdf --help` for the UA-2 flavour id in your release), followed by PAC or Acrobat for the checks no validator can automate (alt-text quality, reading order).

Treat PDF/UA as a technical target, not a blanket legal guarantee. It is a common route toward EN 301 549 and Section 508 expectations for PDFs, but contractual, procurement, and jurisdiction-specific requirements still need to be checked against the actual deliverable and validation results.

---

## Creating Tagged PDFs

Generate from structured source when available; remediate existing PDFs when regeneration is impractical.

### WeasyPrint — semantic HTML to tagged PDF

```bash
weasyprint report.html report.pdf --pdf-tags --pdf-variant pdf/ua-1
# For PDF/UA-2, check `weasyprint --help` for a pdf/ua-2 variant in your installed version
```

Use semantic HTML: heading elements, proper table headers, real links, `lang` on the root document, and meaningful `alt` text on informative images. If you need archival output, prefer the documented PDF/A variants instead of layering ad hoc metadata onto a generic PDF.

DOCX export also works: use built-in heading styles, alt text on images, table header rows, and the application's tagged-PDF export path. Do not rely on a visually-correct but structurally-untagged export.

---

## Reading Order and Alt Text

**Reading order** must match logical content flow. Common failures: multi-column text read across columns, headers injected mid-body, footnotes before referencing paragraphs. Prevention: generate from single-flow HTML or style-based DOCX authoring.

**Alt text**: state the information the image communicates; provide a nearby detailed description or data table for complex charts. Mark decorative images as artifacts.

---

## EU EAA and EN 301 549

The [European Commission's EAA scope](https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/european-accessibility-act-eaa_en) lists covered products and services, including consumer banking, e-books and e-commerce. EU distribution alone does not establish that a PDF is covered. Identify its product/service, applicable national implementation, exemptions and contractual accessibility obligations before making a compliance claim.

Before a conformance statement, check the [applicable directive](https://eur-lex.europa.eu/eli/dir/2019/882/oj), national law and the Official Journal references under that legislation. Determine whether a harmonised standard has been cited, which requirements it covers and which revision applies; a citation under the Web Accessibility Directive does not establish EAA presumption of conformity. Choose the technical PDF/UA or WCAG target from those requirements and the recipient's supported toolchain, and report technical validation separately from legal scope.

---

## Validation Tools

| Tool | Platform | Scope |
|------|----------|-------|
| PAC (PDF Accessibility Checker) | Check installed release | Automated checks plus inspection aids; manual judgment remains necessary |
| Adobe Acrobat Accessibility Checker | Win/macOS | Tags, reading order, alt text |
| `pdfinfo` / viewer inspection | CLI / Any | Fast checks for tags, page count, metadata |
| VoiceOver / NVDA | macOS / Windows | Manual screen reader testing |

```bash
# Quick tag presence check (Poppler)
pdfinfo report.pdf | grep Tagged
# "Tagged: yes" means tags exist — not that they are correct.
```

Always pair automated checks with at least one manual screen reader pass.

---

## Decision Guide: When to Invest

| Scenario | Level |
|----------|-------|
| PDFs supporting a covered service or procurement contract | Confirm legal/contractual scope and required technical standard; validate that target |
| Public marketing / docs | Tagged PDF + alt text + reading order |
| Internal reports | Check recipient access needs and workplace/contractual requirements; preserve structure |
| Archival / legal hold | PDF/A; add tags if public-facing |
| One-off personal exports | Match the recipient's access needs |

---

## Checklist: PDF Accessibility Review

- [ ] Document language declared (`/Lang` entry)
- [ ] PDF is tagged (`/MarkInfo` with `Marked: true`)
- [ ] Heading hierarchy correct (H1 > H2 > H3, no skipped levels)
- [ ] All meaningful images have alt text
- [ ] Decorative images marked as artifacts
- [ ] Tables use TH for headers with scope
- [ ] Reading order matches logical flow (screen reader test)
- [ ] Links have descriptive text (not raw URLs)
- [ ] Fonts embedded with Unicode mappings
- [ ] PAC or Acrobat accessibility check passes with no blocking issues

---

## Do / Avoid

### Do

- Generate tagged PDFs from semantic HTML (WeasyPrint) or styled DOCX.
- Set document language at the root level.
- Test with a real screen reader at least once per template.
- Automate validation in CI for recurring document types.

### Avoid

- Manually tagging complex untagged PDFs — regenerate from source instead.
- Using text boxes or absolute positioning in Word for layout.
- Assuming "it looks fine" means it is accessible.
- Treating accessibility as a post-release patch.

---

## Related

- [pdf-generation-patterns.md](pdf-generation-patterns.md) — Layout and generation code
- [pdf-extraction-patterns.md](pdf-extraction-patterns.md) — Text and table extraction
- [../assets/pdf-release-checklist.md](../assets/pdf-release-checklist.md) — Pre-distribution quality gate
