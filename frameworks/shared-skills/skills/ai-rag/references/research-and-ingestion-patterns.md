# Research And Ingestion Patterns

Use this file when the request is about turning messy external information into retrieval-ready corpora.

## Crawl, Then Retrieve

- Use crawl or extract tooling first when the source is websites, help centers, blogs, or docs portals.
- Preserve canonical URL, fetch time, title, section structure, and content type before chunking.
- Store raw capture separately from cleaned Markdown so you can re-run chunking without re-crawling everything.

## Research Loops Are Not The Same As Serving Indexes

- Research systems such as GPT Researcher-style workflows gather evidence across many sources and synthesize a report.
- Serving indexes answer repeated end-user questions under latency and citation constraints.
- Keep these outputs separate:
  - raw sources
  - normalized source documents
  - derived research reports
  - production retrieval chunks

## Pipeline Selection

| Need | Best fit |
|------|----------|
| Website to Markdown or structured extract | Firecrawl-style crawl/extract |
| Multi-source web research and report synthesis | GPT Researcher-style loop |
| Recurring SaaS or API ingestion | `dlt`-style pipeline |
| Local model and prompt iteration during setup | `simonw/llm`-style CLI workflow |
| AWS managed intelligent document processing (classify + extract mixed docs via FM) | Bedrock Data Automation (BDA) — one API, flat per-doc pricing, Textract as OCR layer for complex docs; standalone Textract preferred for high-volume standardized formats (~75% cheaper, ~95%+ accuracy) |
| Self-hosted document archive (scanned PDFs, invoices, contracts) | paperless-ngx REST API (`/api/documents/`) or consume folder — documents exit pre-OCR'd with metadata; usable as corpus source for Bedrock KB or custom RAG |

## Packaging Rules

- Tag derived content explicitly so retrieval can prefer primary sources when needed.
- Keep freshness metadata at every stage: fetched_at, normalized_at, chunked_at.
- Run retrieval evals after ingestion changes, not just after model or reranker changes.
