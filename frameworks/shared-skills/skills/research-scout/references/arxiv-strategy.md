# arXiv Search Strategy

## Table of Contents

- [Discovery Path](#discovery-path)
- [Query Patterns](#query-patterns)
- [API Limits and Bulk Harvesting](#api-limits-and-bulk-harvesting)
- [Credibility Signals](#credibility-signals)
- [Biases](#biases)
- [Attribution](#attribution)

## Discovery Path

1. **Pick categories** from the canonical taxonomy at https://arxiv.org/category_taxonomy.
   - AI/ML/agents: `cs.AI`, `cs.CL`, `cs.LG`, `cs.MA`
   - IR / RAG: `cs.IR`, `cs.CL`, `cs.DB`
   - Software engineering: `cs.SE`, `cs.PL`
   - Distributed / inference: `cs.DC`, `cs.PF`
   - Security: `cs.CR`
   - Stats / evaluation: `stat.ML`
2. **Pick keywords** that name a *method or capability*, not a domain (e.g., `tool use`, `speculative decoding`, not `chatbots`).
3. Query the **API endpoint**: `http://export.arxiv.org/api/query` (note: `http`, not `https`, per arXiv API docs).
4. Sort `submittedDate` descending for scouting; `relevance` only when you know the exact terms.
5. Default `max_results=50`, paginate via `start=` if needed.

## Query Patterns

```text
# Recent agent tool-use papers in cs.AI
search_query=cat:cs.AI AND (agents OR "tool use" OR "tool calling")
sortBy=submittedDate&sortOrder=descending&start=0&max_results=50

# RAG-eval methods across cs.IR + cs.CL
search_query=(cat:cs.IR OR cat:cs.CL) AND ("retrieval evaluation" OR "RAG eval" OR "retrieval augmented evaluation")
sortBy=submittedDate&sortOrder=descending&start=0&max_results=50

# Specific paper by ID (replaces the 7-digit number)
search_query=id:2402.12345
```

Title-only filtering: prepend `ti:` (e.g., `ti:speculative decoding`). Abstract: `abs:`. Author: `au:`.

## Dedupe Across Versions

arXiv papers have versions (`v1`, `v2`, ...). When a paper appears with multiple versions in results, keep the latest `submittedDate` and discard earlier versions. Use the canonical paper ID (without version suffix) for the `paper_id` field in findings TSV.

## API Limits and Bulk Harvesting

As of 2026 arXiv enforces rate limiting (no longer best-effort):

- Keep **≥3s between requests**; on **HTTP 429** back off exponentially (30s → 60s → 120s), never tight-retry. Parallel query bursts trigger throttling fastest.
- Responses go through a CDN (Fastly): identical **GET** queries may return a slightly **stale cached** response. Accept brief lag for day-fresh scouting; **do not switch to POST to force freshness** — the API is GET-oriented and query-mangling just raises 429 risk.
- For "scan everything since date X" workloads, use **OAI-PMH** (`https://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=arXiv`) with `from`/`until` + `resumptionToken`, not the Atom search API. Honour `503 Retry-After`. See `../research-arxiv-scout/references/arxiv-api-guide.md` for the full guide.

## Credibility Signals

- **Citing-paper count** (via Semantic Scholar API, not arXiv directly) — strong corroboration signal.
- **Code link in abstract or in arXiv "Code" tab** — reproducibility upgrade.
- **Author institution diversity** — purely-corporate papers carry corporate-selection-bias risk; mixed industry+academic is safer.
- **Updated to v2+ within 3 months** of v1 — usually responds to early review feedback; positive signal.
- **Withdrawn / replaced** — check `withdrawn` flag; never include withdrawn papers.

## Biases

- **No peer review.** arXiv accepts everything in scope. Strong claims warrant independent corroboration before adoption.
- **Recency cliff.** Methods >2 years old that aren't in conference proceedings may be obsolete; check Semantic Scholar for whether the field moved.
- **English-language and Western-institution skew.** Non-English research is underrepresented.
- **Self-promotion.** Some authors aggressively post preprints with strong claims; weight by independent corroboration.

## Attribution

Per arXiv API Terms of Use (https://info.arxiv.org/help/api/tou.html), include the following acknowledgement in any output that uses arXiv data:

> Thank you to arXiv for use of its open access interoperability.

The string is also stored in `data/sources.json` under `metadata.attribution.arxiv`.
