# 2026 Extraction Stack — XLSX

Verified 2026-05-17. Use this note when selecting an XLSX extraction tool for LLM/RAG or data pipelines.

## Tier 1 — High-performance pure-Rust reading

**calamine** — `github.com/tafia/calamine`
Pure-Rust reader for xls, xlsx, xlsb, and ods; no dependencies; Python bindings via `python-calamine`.
Preferred for high-throughput spreadsheet ingestion where openpyxl overhead is measurable.

## Tier 2 — Structured multi-format extraction

**Docling** (IBM Research, MIT) — `github.com/docling-project/docling`
Produces a typed `DoclingDocument` from XLSX, PDF, DOCX, PPTX, HTML, and images.
Preferred when downstream consumers need consistent schema across multiple formats.

## Tier 3 — OCR for image-embedded or scanned spreadsheet content

**Mistral OCR** — `mistral.ai/news/mistral-ocr`
REST API; understands text, tables, equations, and embedded media; ~1000 pages/$.
Use when Excel data is trapped in images or scanned documents rather than native cells.

## Decision rule

calamine/openpyxl for native cells → Docling for cross-format schema → Mistral OCR for image-trapped data.
