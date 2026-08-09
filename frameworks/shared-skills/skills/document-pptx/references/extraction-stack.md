# 2026 Extraction Stack — PPTX

Verified 2026-05-17. Use this note when selecting a PPTX extraction tool for LLM/RAG pipelines.

## Tier 1 — Structured multi-format extraction

**Docling** (IBM Research, MIT) — `github.com/docling-project/docling`
Produces a typed `DoclingDocument` from PPTX, PDF, DOCX, XLSX, HTML, and images.
Preferred when downstream consumers need consistent schema across multiple formats.
Handles embedded images and tables within slides.

## Tier 2 — OCR for image-embedded or exported-slide content

**Mistral OCR** — `mistral.ai/news/mistral-ocr`
REST API; understands text, tables, equations, and embedded media; ~1000 pages/$.
Use when slides are rasterized or contain image-embedded text that XML parsing misses.

## Tier 3 — Native Python extraction

**python-pptx** (already in sources) — direct XML access for structured slide content.
Use for precise per-shape extraction when Docling overhead is not justified.

## Decision rule

python-pptx for structured slides → Docling for cross-format schema → Mistral OCR for rasterized slides.
