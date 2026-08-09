# 2026 Extraction Stack — DOCX

Verified 2026-05-17. Use this note when selecting a DOCX extraction tool for LLM/RAG pipelines.

## Tier 1 — Structured multi-format extraction

**Docling** (IBM Research, MIT) — `github.com/docling-project/docling`
Produces a typed `DoclingDocument` from DOCX, PDF, PPTX, XLSX, HTML, and images.
Preferred when downstream consumers need consistent schema across multiple formats.

## Tier 2 — OCR for image-embedded or scanned content

**Mistral OCR** — `mistral.ai/news/mistral-ocr`
REST API; understands text, tables, equations, and embedded media; ~1000 pages/$.
Use when DOCX contains image-embedded text that native XML parsing cannot reach.

## Tier 3 — Lightweight Markdown extraction

**MarkItDown** (Microsoft, already in sources) — no GPU required; good for simple RAG pipelines.

## Decision rule

Native XML first (python-docx) → Docling for structured output → Mistral OCR only when scanned images are present.
