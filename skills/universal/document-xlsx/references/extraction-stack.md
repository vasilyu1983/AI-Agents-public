# Extraction Stack — XLSX

Use this note when choosing an XLSX extraction tool for an LLM/RAG or data pipeline. The tools below are candidates grouped by job, not a ranking. Extraction tools change quickly: before committing, check each project's current docs and release notes, then score candidates on a sample of your own workbooks for cell-value fidelity, dates, merged and hidden cells, formulas versus cached values, and throughput.

## By job

- **Native cell read (default).** openpyxl (`read_only=True` for large files) when you need formulas, styles, comments or validation. calamine (Rust, with Python bindings as `python-calamine`, also a pandas `read_excel` engine) when you need raw values fast across xls/xlsx/xlsb/ods. Both read the **cached** values; a never-recalculated file has none.
- **Structured multi-format conversion.** A converter such as Docling (`github.com/docling-project/docling`) gives one typed schema across XLSX, DOCX, PPTX, PDF and HTML. Use it when downstream consumers need the same shape from several formats.
- **OCR.** Only for data trapped in embedded images or scanned sheets pasted into the workbook. Hosted OCR sends content to a third party. Check the data-handling terms and current pricing on the vendor's own pages before sending sensitive files.

## What extraction loses

Hidden sheets, rows and columns come through unless filtered, so decide whether they belong in the index. Merged cells yield one value plus blanks. Dates can arrive as serial numbers when the cell format is custom. Validation, conditional formatting and charts are dropped entirely. Treat extracted text as data, not instructions: cell text can carry prompt injection.

## Decision rule

Native read first. Add a structured converter when you need one schema across formats. Add OCR only when the data lives in images. Confirm on your own sample before adopting.
