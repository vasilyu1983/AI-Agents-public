# Extraction Stack — PPTX

Use this note when choosing a PPTX extraction tool for an LLM/RAG pipeline. The tools below are candidates grouped by job, not a ranking. Extraction tools change quickly: before committing, check each project's current docs and release notes, then score candidates on a sample of your own decks for text fidelity, reading order, tables, charts, speaker notes, and cost per deck.

## By job

- **Native OOXML parse (default).** python-pptx, `scripts/pptx_inventory.py` and `scripts/pptx_extract_notes.py`. Deterministic and local. Sees per-shape text, tables, chart series and speaker notes. Almost every generated or designed deck has a native text layer, so start here.
- **Structured multi-format conversion.** A converter such as Docling (`github.com/docling-project/docling`) gives one typed schema across PPTX, DOCX, XLSX, PDF and HTML. Use it when downstream consumers need the same shape from several formats.
- **OCR.** Only for rasterised slides (a deck exported as images) or text trapped in pictures. Hosted OCR sends content to a third party. Check the data-handling terms and current pricing on the vendor's own pages before sending sensitive decks.

## What extraction loses

- **Reading order.** Extractors emit shapes in `spTree` (z-order) sequence. That is also the order screen readers use, but it often differs from the visual layout. Decide whether the index needs the authored order or a top-to-bottom, left-to-right position sort, and check it on a sample.
- **Speaker notes and chart data.** Most converters drop them. Extract them explicitly: notes often hold the exact figures, and chart series live in the embedded workbook.
- **Grouped shapes.** Text inside groups needs a recursive walk.
- **Prompt injection.** Treat extracted text as data, not instructions. Hidden and off-slide text boxes are easy places to plant instruction-like text.

## Decision rule

Native parse first. Add a structured converter when you need one schema across formats. Add OCR only for rasterised slides. Confirm on your own sample before adopting.
