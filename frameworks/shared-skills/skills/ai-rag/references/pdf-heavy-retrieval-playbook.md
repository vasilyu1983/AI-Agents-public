# PDF-Heavy Retrieval Playbook

Use this when the corpus contains long PDFs, scanned pages, tables, diagrams,
forms, or page-level citations.

## Contents

- [Decision Flow](#decision-flow)
- [Retrieval Units](#retrieval-units)
- [Citation Contract](#citation-contract)
- [Evaluation Slices](#evaluation-slices)
- [Traps](#traps)

## Decision Flow

```text
PDF corpus
  -> born digital?
       yes -> extract text + page anchors
       no  -> OCR first, then inspect confidence
              AWS-native: Amazon Textract (returns form key-value pairs,
              table cells, multi-page structure; beyond generic PDF text extraction)
  -> tables or layout matter?
       yes -> preserve table/page/bbox artifacts
  -> diagrams or screenshots matter?
       yes -> add multimodal or page-image retrieval
  -> plain prose only?
       yes -> heading/page-aware chunks are usually enough
```

## Retrieval Units

Use the smallest unit that preserves the answer boundary:

- `page_chunk`: default for manuals and reports with page citations
- `section_chunk`: for PDFs with reliable headings
- `table_chunk`: for extracted tables; include row/column labels
- `figure_chunk`: for diagrams; include caption and page anchor
- `parent_child`: child chunks retrieve, parent page/section hydrates
- `page_image`: for visual-document retrieval when OCR loses layout meaning

Store:

- `source_uri`
- `document_version`
- `page_number`
- `section_path`
- `bbox` when available
- `table_id` or `figure_id` when available
- `extraction_method`: `text`, `ocr`, `table`, `vision`, `manual`
- `extraction_confidence`

## Citation Contract

Every returned PDF evidence object should support:

```json
{
  "evidence_id": "pdf:doc-id:p12:table-2",
  "source_uri": "s3://or/path/to/document.pdf",
  "document_title": "Document title",
  "document_version": "v1",
  "page_number": 12,
  "section_path": ["Section", "Subsection"],
  "anchor": "table-2",
  "bbox": [72, 120, 520, 320],
  "extraction_method": "table",
  "content": "short retrieved text or table projection"
}
```

Do not cite a PDF only by filename when page or table anchors are available.

## Evaluation Slices

Add separate judged cases for:

- page-specific answers
- table row/column lookup
- scanned OCR noise
- long document where answer is near the end
- visually grounded chart or diagram answer
- conflicting versions of the same PDF
- unanswerable question over the PDF set

## Traps

- Treating OCR text as clean source without confidence or page anchors.
- Splitting tables into unrelated lines that lose row/column meaning.
- Returning a whole 80-page PDF as one context item.
- Citing a generated summary instead of the source page.
- Ignoring duplicate versions with similar titles.
- Using multimodal retrieval for every PDF when text extraction already passes
  evals.

## Sources

- Amazon Textract (AWS-native OCR/extraction — form key-value pairs, table cells, multi-page document structure):
  [Amazon Textract documentation](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)
- Qdrant multivectors and late interaction:
  https://qdrant.tech/documentation/tutorials-search-engineering/using-multivector-representations/
- ColBERT-Att (arXiv 2603.25248, ECIR 2026 LIR workshop): late interaction + attention weights on
  query and document terms; recall gains reported on MS-MARCO, BEIR, and LoTTE. Relevant when
  standard ColBERT precision is insufficient on PDF page retrieval.
- AMES (arXiv 2603.13537, ECIR 2026 LIR workshop): approximate multimodal enterprise search via
  late interaction; cross-modal retrieval (text + image + table) without modality-specific logic;
  evaluated on ViDoRe V3. Relevant for mixed-modality PDF corpora where ColPali adds overhead.
- ECIR 2026 Late Interaction Retrieval (LIR) workshop standardized the evaluation vocabulary for
  late-interaction systems (nDCG@10, recall@100, MRR); use these metrics when comparing
  late-interaction backends for PDF retrieval.
