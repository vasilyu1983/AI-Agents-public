# 2026 Extraction Stack — PDF

Verified 2026-07-11. Use this note when selecting a PDF extraction tool for LLM/RAG pipelines.

## Tier 1 — LLM-ready Markdown (no GPU)

**PyMuPDF4LLM** — `pymupdf.readthedocs.io/en/latest/pymupdf4llm/`
Extracts PDF as structured Markdown; OCR only when needed; no ML dependency.
Preferred entry point for text-native PDFs feeding RAG or chat pipelines.

## Tier 2 — Structured multi-format extraction

**Docling** (IBM Research, MIT) — `github.com/docling-project/docling`
Produces a typed `DoclingDocument` from PDF, DOCX, PPTX, XLSX, HTML, and images.
Preferred when downstream consumers need consistent schema across multiple formats.

## Tier 3 — OCR for scanned or image-embedded PDFs

**Mistral OCR** — `mistral.ai/news/mistral-ocr`
REST API; understands text, tables, equations, and embedded media. Pricing moves fast and has changed materially release-over-release (roughly $2–4 per 1,000 pages standard, ~50% off on the batch API as of mid-2026) — re-check `mistral.ai/pricing` at time of use rather than quoting a fixed number.
Use when native text layer is absent or unreliable.

## Decision rule

PyMuPDF4LLM for text-native → Docling for cross-format schema → Mistral OCR for scanned/image PDFs.
