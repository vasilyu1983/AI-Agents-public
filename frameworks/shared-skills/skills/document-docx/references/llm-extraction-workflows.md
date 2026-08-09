# LLM And Extraction Workflows For DOCX

Use this when the DOCX is an input to search, RAG, indexing, or downstream HTML/Markdown/JSON pipelines rather than the final user-facing artifact.

## Table of Contents

- [Decision Guide](#decision-guide)
- [Tool Tradeoffs](#tool-tradeoffs)
- [`scripts/docx_extract.py`](#scriptsdocxextractpy)
- [`mammoth`](#mammoth)
- [`MarkItDown`](#markitdown)
- [`Docling`](#docling)
- [Recommended Workflows](#recommended-workflows)
- [Trusted DOCX -> HTML](#trusted-docx-html)
- [Trusted DOCX -> JSON For Automation](#trusted-docx-json-for-automation)
- [DOCX -> Markdown For RAG](#docx-markdown-for-rag)
- [Trust And Safety](#trust-and-safety)
- [Common Failure Modes](#common-failure-modes)
- [Related Resources](#related-resources)

## Decision Guide

| Need | Preferred Tool | Why |
|------|----------------|-----|
| Deterministic text/tables/core metadata | `scripts/docx_extract.py` | Stable JSON from local automation without changing format |
| Semantic HTML from a trusted DOCX | `mammoth` | Good structure, low layout fidelity, HTML-oriented |
| Quick Markdown for LLM/RAG | `MarkItDown` | Simple Markdown conversion and LLM-friendly output |
| Multi-format ingestion with richer outputs | `Docling` | One pipeline for DOCX plus other document formats |
| Pixel-perfect rendering | None of the above | Export PDF or keep DOCX; extraction tools are not renderers |

## Tool Tradeoffs

### `scripts/docx_extract.py`

Best for:
- Local automation
- Audits and migrations
- Extracting paragraphs, tables, core properties, and optional headers/footers/comments/images

Avoid when:
- You need Markdown or HTML
- You need visual fidelity

### `mammoth`

Best for:
- Converting trusted DOCX content into semantic HTML
- Web previews
- Content extraction where layout fidelity is secondary

Avoid when:
- The input is untrusted
- You need pixel-perfect layout
- You need tracked revisions preserved

Security note:
- Mammoth does not sanitize the generated HTML. Sanitize before rendering, indexing, or storing it in a web-facing system.

### `MarkItDown`

Best for:
- Quick DOCX-to-Markdown conversion
- LLM/RAG preprocessing
- Pipelines where Markdown is the desired intermediate representation

Avoid when:
- You need detailed OOXML metadata
- You need HTML with style-map control

### `Docling`

Best for:
- Multi-format ingestion where DOCX is one of several source types
- Structured downstream workflows that may want Markdown, HTML, JSON, or text
- Standardizing document ingestion across a broader pipeline

Avoid when:
- You only need simple, deterministic extraction from a single DOCX

## Recommended Workflows

### Trusted DOCX -> HTML

```bash
node scripts/docx_to_html.mjs input.docx output.html --style-map custom-style-map.txt --extract-images-dir assets/
```

Then:
1. Sanitize the HTML.
2. Validate external links/images.
3. Store only the sanitized output.

### Trusted DOCX -> JSON For Automation

```bash
python3 scripts/docx_extract.py input.docx --include headers footers hyperlinks comments images --out extracted.json
```

Use this when the consumer is code, not humans.

### DOCX -> Markdown For RAG

Use `MarkItDown` or `Docling` when installed in the environment. Prefer this lane when downstream chunking and retrieval matter more than preserving Word-specific structure.

Practical rule:
- Markdown is usually easier to chunk and inspect than HTML.
- HTML is better when you need explicit heading/list/table semantics.
- JSON is better when the consumer is a controlled automation pipeline.

## Trust And Safety

Treat these as untrusted inputs unless you control the source:
- `.docm`
- `.dotm`
- Documents with external links or embedded objects
- Documents from email or customer uploads

For untrusted inputs:
- Do not execute macros.
- Prefer extraction in an isolated environment.
- Sanitize HTML output.
- Record conversion warnings and extraction gaps.

## Common Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Missing images in HTML | Images were not extracted or relinked | Use `--extract-images-dir` and verify relative paths |
| Ugly HTML | Default Mammoth mappings | Provide a style map and post-process the output |
| Missing comments/hyperlinks in JSON | Optional fields not requested | Use `--include comments hyperlinks` |
| Bad Markdown chunking | Overly visual DOCX structure | Prefer heading cleanup or HTML/JSON instead of raw Markdown |
| Security risk from rendered HTML | Unsanitized conversion output | Sanitize before use |

## Related Resources

- [review-comments-workflows.md](review-comments-workflows.md) - Review metadata and comments
- [tracked-changes.md](tracked-changes.md) - Revision-specific limits
- [document-automation-pipelines.md](document-automation-pipelines.md) - Batch generation and gates
- [SKILL.md](../SKILL.md) - Parent DOCX skill
