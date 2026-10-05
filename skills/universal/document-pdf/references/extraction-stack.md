# PDF Extraction Stack

Use this note when selecting a PDF extraction tool for LLM/RAG pipelines. See `data/sources.json` for verification dates. The tools below are starting candidates by job, not a ranking. Extraction tools change quickly: before committing, check each project's current docs and release notes, and score the candidates on a sample of your own PDFs (text fidelity, reading order, tables, cost per page).

## Text-native PDF to Markdown

**PyMuPDF4LLM** — `pymupdf.readthedocs.io` (PyMuPDF4LLM section). Built on PyMuPDF, so the AGPL-3.0/commercial licence check applies
Extracts PDF as structured Markdown. Before selecting the installed release, check its [layout and OCR documentation](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) for enabled modules, model/runtime dependencies and their licences; do not assume the pipeline has no ML dependency.
Candidate entry point for text-native PDFs feeding RAG or chat pipelines.

## One schema across formats

**Docling** (IBM Research, MIT) — `github.com/docling-project/docling`
Produces a typed `DoclingDocument` from PDF, DOCX, PPTX, XLSX, HTML, and images.
Candidate when downstream consumers need a consistent schema across multiple formats.

## Scanned or image-embedded PDFs (OCR)

**Mistral OCR** — `mistral.ai/news/mistral-ocr`
Hosted REST API for text, tables, equations, and embedded media. Check `mistral.ai/pricing` at time of use; do not quote a fixed price.
Use when the native text layer is absent or unreliable. Hosted OCR sends document content to a third party, so check data-handling terms before sending sensitive PDFs.

## Decision rule

Text-native PDF → a Markdown extractor such as PyMuPDF4LLM. Cross-format schema needed → a structured converter such as Docling. Scanned or image PDF → an OCR engine (hosted, such as Mistral OCR, or local). Confirm the choice on your own sample before adopting it.
