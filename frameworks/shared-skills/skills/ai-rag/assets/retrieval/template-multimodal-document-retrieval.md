# Multimodal Document Retrieval Template

Use when PDFs, tables, forms, charts, or diagrams lose meaning after plain-text extraction.

```yaml
retrieval_mode: multimodal_documents

ingestion:
  extract_text: true
  keep_page_images: true
  table_extraction: true
  layout_metadata: [page, bbox, section, table_id]

representations:
  text_index: true
  image_or_page_index: true
  cross_link_by_page_id: true

query_path:
  route:
    - if: "plain-text factual lookup"
      use: "text_or_hybrid_search"
    - if: "visual structure matters"
      use: "page_or_region_retrieval"
    - if: "uncertain"
      use: "hybrid_then_rerank"

ranking:
  candidate_k: 30
  reranking: "optional_multimodal_or_text_reranker"
  final_k: 5

grounding:
  citation_granularity: "page_or_region"
  return_preview: true
```

Checklist:

- [ ] OCR quality measured on target corpus
- [ ] Page or region IDs remain stable for citations
- [ ] Retrieval tested separately for prose, tables, and visual layouts
- [ ] Fallback exists when visual retrieval is unavailable
